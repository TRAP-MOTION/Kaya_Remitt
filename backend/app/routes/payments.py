from flask import Blueprint, jsonify, g
from marshmallow import ValidationError
from backend.app.extensions import db
from backend.app.models.merchant import Merchant
from backend.app.models.service import Service
from backend.app.models.payment import Payment
from backend.app.models.transaction import Transaction
from backend.app.models.notification import Notification
from backend.app.models.users import User
from backend.app.utils.auth import token_required
from backend.app.utils.validation import load_json, load_path, validation_error_response
from backend.app.schemas.payment_schema import CreatePaymentSchema
from backend.app.schemas.common import UuidPathSchema
from backend.app.utils.payments_paychangu import initiate_checkout, PayChanguError

payments_bp = Blueprint("payments", __name__)

_create_payment_schema = CreatePaymentSchema()
_payment_id_schema = UuidPathSchema()


@payments_bp.route("", methods=["POST"], strict_slashes=False)
@payments_bp.route("/", methods=["POST"], strict_slashes=False)
@token_required
def create_payment():
    """POST /api/v1/payments — Creates a payment request; notifies merchant to accept/deny."""
    user = g.current_user

    try:
        validated = load_json(_create_payment_schema)
    except ValidationError as err:
        return validation_error_response(err)

    merchant_id = validated["merchant_id"]
    service_id = validated["service_id"]
    beneficiary_name = validated["beneficiary_name"]
    amount = validated["amount"]

    merchant = db.session.get(Merchant, merchant_id)
    if not merchant or not merchant.verified:
        return jsonify({
            "success": False,
            "message": "Merchant not found or not verified."
        }), 404

    service = db.session.execute(
        db.select(Service).filter_by(
            service_id=service_id,
            merchant_id=merchant_id,
            availability=True,
        )
    ).scalar_one_or_none()

    if not service:
        return jsonify({
            "success": False,
            "message": "Service not found for this merchant."
        }), 404

    try:
        payment = Payment(
            user_id=user.user_id,
            merchant_id=merchant_id,
            service_id=service_id,
            beneficiary_name=beneficiary_name,
            amount=amount,
            payment_status="AwaitingAcceptance",
        )
        db.session.add(payment)
        db.session.flush()

        db.session.add(Transaction(
            payment_id=payment.payment_id,
            action="PAYMENT_REQUESTED",
            performed_by=user.user_id,
            status="AwaitingAcceptance",
        ))

        db.session.add(Notification(
            user_id=user.user_id,
            title="Payment Requested",
            message=(
                f"Your payment of {float(amount):,.2f} to {merchant.business_name} "
                f"for {beneficiary_name} has been submitted. Awaiting merchant approval."
            ),
            category="Payment",
        ))

        merchant_user = db.session.execute(
            db.select(User).filter_by(email=merchant.email, role="merchant")
        ).scalar_one_or_none()

        if merchant_user:
            db.session.add(Notification(
                user_id=merchant_user.user_id,
                title="New Payment Request",
                message=(
                    f"A payment of {float(amount):,.2f} for '{service.service_name}' "
                    f"on behalf of {beneficiary_name} is awaiting your approval."
                ),
                category="Payment",
            ))

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Payment created successfully.",
            "data": {
                "payment_id": payment.payment_id,
                "status": payment.payment_status,
            }
        }), 201
    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "An error occurred while creating your payment."
        }), 500


@payments_bp.route("/<payment_id>/checkout", methods=["POST"], strict_slashes=False)
@token_required
def initiate_payment_checkout(payment_id):
    """POST /api/v1/payments/{payment_id}/checkout — PayChangu checkout for Accepted payments."""
    user = g.current_user

    try:
        params = load_path(_payment_id_schema, id=payment_id)
    except ValidationError as err:
        return validation_error_response(err)

    payment = db.session.execute(
        db.select(Payment).filter_by(
            payment_id=params["id"],
            user_id=user.user_id,
        )
    ).scalar_one_or_none()

    if not payment:
        return jsonify({
            "success": False,
            "message": "Payment not found."
        }), 404

    if payment.payment_status == "Denied":
        return jsonify({
            "success": False,
            "message": "This payment was denied by the merchant."
        }), 400

    if payment.payment_status == "COMPLETED":
        return jsonify({
            "success": False,
            "message": "This payment has already been completed."
        }), 400

    if payment.payment_status == "AwaitingAcceptance":
        return jsonify({
            "success": False,
            "message": "This payment is still awaiting merchant approval."
        }), 400

    if payment.payment_status == "Pending":
        # Checkout already initiated — re-issue checkout URL
        try:
            checkout_url = initiate_checkout(payment, user)
            db.session.commit()
            return jsonify({
                "success": True,
                "message": "Checkout initiated successfully.",
                "data": {
                    "payment_id": payment.payment_id,
                    "status": payment.payment_status,
                    "checkout_url": checkout_url,
                }
            }), 200
        except PayChanguError as exc:
            db.session.rollback()
            return jsonify({"success": False, "message": str(exc)}), 502

    if payment.payment_status != "Accepted":
        return jsonify({
            "success": False,
            "message": f"Payment cannot be checked out. Current status: {payment.payment_status}."
        }), 400

    try:
        checkout_url = initiate_checkout(payment, user)
        payment.payment_status = "Pending"

        db.session.add(Transaction(
            payment_id=payment.payment_id,
            action="CHECKOUT_INITIATED",
            performed_by=user.user_id,
            status="Pending",
        ))
        db.session.add(Notification(
            user_id=user.user_id,
            title="Checkout Ready",
            message=(
                f"Your payment of {float(payment.amount):,.2f} to "
                f"{payment.merchant.business_name if payment.merchant else 'merchant'} "
                f"is ready. Complete checkout to finalize."
            ),
            category="Payment",
        ))
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Checkout initiated successfully.",
            "data": {
                "payment_id": payment.payment_id,
                "status": payment.payment_status,
                "checkout_url": checkout_url,
            }
        }), 200
    except PayChanguError as exc:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(exc),
        }), 502
    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "An error occurred while initiating checkout."
        }), 500


@payments_bp.route("/history", methods=["GET"], strict_slashes=False)
@token_required
def get_payment_history():
    """GET /api/v1/payments/history — Returns the current user's payment history."""
    user = g.current_user

    payments = db.session.execute(
        db.select(Payment)
        .filter_by(user_id=user.user_id)
        .order_by(Payment.created_at.desc())
    ).scalars().all()

    return jsonify({
        "success": True,
        "data": [p.to_dict() for p in payments]
    }), 200
