from flask import Blueprint, jsonify, g
from marshmallow import ValidationError
from backend.app.extensions import db
from backend.app.models.merchant import Merchant
from backend.app.models.service import Service
from backend.app.models.payment import Payment
from backend.app.models.transaction import Transaction
from backend.app.models.notification import Notification
from backend.app.utils.auth import token_required
from backend.app.utils.validation import load_json, validation_error_response
from backend.app.schemas.payment_schema import CreatePaymentSchema
from backend.app.utils.payments_paychangu import initiate_checkout, PayChanguError

payments_bp = Blueprint("payments", __name__)

_create_payment_schema = CreatePaymentSchema()


@payments_bp.route("", methods=["POST"], strict_slashes=False)
@payments_bp.route("/", methods=["POST"], strict_slashes=False)
@token_required
def create_payment():
    """POST /api/v1/payments — Creates a payment and returns a PayChangu checkout URL."""
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
            payment_status="Pending",
        )
        db.session.add(payment)
        db.session.flush()

        checkout_url = initiate_checkout(payment, user)

        db.session.add(Transaction(
            payment_id=payment.payment_id,
            action="CHECKOUT_INITIATED",
            performed_by=user.user_id,
            status="Pending",
        ))
        db.session.add(Notification(
            user_id=user.user_id,
            title="Payment Initiated",
            message=(
                f"Your payment of {float(amount):,.2f} to {merchant.business_name} "
                f"for {beneficiary_name} is ready. Complete checkout to continue."
            ),
        ))
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Payment created successfully.",
            "data": {
                "payment_id": payment.payment_id,
                "status": payment.payment_status,
                "checkout_url": checkout_url,
            }
        }), 201
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
            "message": "An error occurred while creating your payment."
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
