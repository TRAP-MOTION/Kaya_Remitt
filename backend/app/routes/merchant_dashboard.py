from flask import Blueprint, jsonify, g
from marshmallow import ValidationError
from backend.app.extensions import db
from backend.app.models.payment import Payment
from backend.app.models.transaction import Transaction
from backend.app.models.notification import Notification
from backend.app.utils.auth import token_required
from backend.app.utils.merchant_access import get_merchant_for_user
from backend.app.utils.validation import load_path, validation_error_response
from backend.app.schemas.common import UuidPathSchema

merchant_dashboard_bp = Blueprint("merchant_dashboard", __name__)

_payment_id_schema = UuidPathSchema()


@merchant_dashboard_bp.route("/transactions", methods=["GET"], strict_slashes=False)
@token_required
def get_merchant_transactions():
    """GET /api/v1/merchant/transactions — Returns all payments directed at the merchant."""
    user = g.current_user

    if user.role != "merchant":
        return jsonify({
            "success": False,
            "message": "Access restricted to merchant accounts."
        }), 403

    merchant = get_merchant_for_user(user)
    if not merchant:
        return jsonify({"success": True, "data": []}), 200

    payments = db.session.execute(
        db.select(Payment)
        .filter_by(merchant_id=merchant.merchant_id)
        .order_by(Payment.created_at.desc())
    ).scalars().all()

    transactions = []
    for payment in payments:
        status = payment.payment_status
        if payment.voucher and payment.voucher.status.lower() == "redeemed":
            status = "REDEEMED"
        transactions.append({
            "transaction_id": payment.payment_id,
            "beneficiary_name": payment.beneficiary_name,
            "service": payment.service.service_name if payment.service else None,
            "amount": round(float(payment.amount), 2),
            "status": status,
        })

    return jsonify({"success": True, "data": transactions}), 200


@merchant_dashboard_bp.route(
    "/payments/<payment_id>/accept", methods=["PATCH"], strict_slashes=False
)
@token_required
def accept_payment(payment_id):
    """PATCH /api/v1/merchant/payments/{payment_id}/accept — Merchant accepts a payment."""
    user = g.current_user

    if user.role != "merchant":
        return jsonify({
            "success": False,
            "message": "Access restricted to merchant accounts."
        }), 403

    try:
        params = load_path(_payment_id_schema, id=payment_id)
    except ValidationError as err:
        return validation_error_response(err)

    merchant = get_merchant_for_user(user)
    if not merchant:
        return jsonify({
            "success": False,
            "message": "No verified merchant account found for this user."
        }), 403

    payment = db.session.execute(
        db.select(Payment).filter_by(
            payment_id=params["id"],
            merchant_id=merchant.merchant_id,
        )
    ).scalar_one_or_none()

    if not payment:
        return jsonify({"success": False, "message": "Payment not found."}), 404

    if payment.payment_status != "AwaitingAcceptance":
        return jsonify({
            "success": False,
            "message": f"Payment cannot be accepted. Current status: {payment.payment_status}."
        }), 400

    try:
        payment.payment_status = "Accepted"
        db.session.add(Transaction(
            payment_id=payment.payment_id,
            action="PAYMENT_ACCEPTED",
            performed_by=user.user_id,
            status="Accepted",
        ))
        # Notify the diaspora user
        db.session.add(Notification(
            user_id=payment.user_id,
            title="Payment Accepted",
            message=(
                f"Your payment of {float(payment.amount):,.2f} to "
                f"{merchant.business_name} has been accepted. "
                f"You can now proceed to checkout."
            ),
            category="Payment",
        ))
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Payment accepted successfully.",
            "data": {
                "payment_id": payment.payment_id,
                "status": payment.payment_status,
            }
        }), 200
    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "An error occurred while accepting the payment."
        }), 500


@merchant_dashboard_bp.route(
    "/payments/<payment_id>/deny", methods=["PATCH"], strict_slashes=False
)
@token_required
def deny_payment(payment_id):
    """PATCH /api/v1/merchant/payments/{payment_id}/deny — Merchant denies a payment."""
    user = g.current_user

    if user.role != "merchant":
        return jsonify({
            "success": False,
            "message": "Access restricted to merchant accounts."
        }), 403

    try:
        params = load_path(_payment_id_schema, id=payment_id)
    except ValidationError as err:
        return validation_error_response(err)

    merchant = get_merchant_for_user(user)
    if not merchant:
        return jsonify({
            "success": False,
            "message": "No verified merchant account found for this user."
        }), 403

    payment = db.session.execute(
        db.select(Payment).filter_by(
            payment_id=params["id"],
            merchant_id=merchant.merchant_id,
        )
    ).scalar_one_or_none()

    if not payment:
        return jsonify({"success": False, "message": "Payment not found."}), 404

    if payment.payment_status != "AwaitingAcceptance":
        return jsonify({
            "success": False,
            "message": f"Payment cannot be denied. Current status: {payment.payment_status}."
        }), 400

    try:
        payment.payment_status = "Denied"
        db.session.add(Transaction(
            payment_id=payment.payment_id,
            action="PAYMENT_DENIED",
            performed_by=user.user_id,
            status="Denied",
        ))
        # Notify the diaspora user
        db.session.add(Notification(
            user_id=payment.user_id,
            title="Payment Denied",
            message=(
                f"Your payment of {float(payment.amount):,.2f} to "
                f"{merchant.business_name} was denied by the merchant."
            ),
            category="Payment",
        ))
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Payment denied.",
            "data": {
                "payment_id": payment.payment_id,
                "status": payment.payment_status,
            }
        }), 200
    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "An error occurred while denying the payment."
        }), 500
