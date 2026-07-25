from flask import Blueprint, request, jsonify, g
from backend.app.extensions import db
from backend.app.models.merchant import Merchant
from backend.app.models.service import Service
from backend.app.models.payment import Payment
from backend.app.utils.auth import token_required

payments_bp = Blueprint("payments", __name__)


@payments_bp.route("", methods=["POST"], strict_slashes=False)
@payments_bp.route("/", methods=["POST"], strict_slashes=False)
@token_required
def create_payment():
    """POST /api/v1/payments — Creates a payment for a merchant service."""
    user = g.current_user
    data = request.get_json() or {}

    merchant_id = data.get("merchant_id")
    service_id = data.get("service_id")
    beneficiary_name = data.get("beneficiary_name")
    amount = data.get("amount")

    # Validate required fields
    if not all([merchant_id, service_id, beneficiary_name, amount is not None]):
        return jsonify({
            "success": False,
            "message": "merchant_id, service_id, beneficiary_name, and amount are required."
        }), 400

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "amount must be a positive number."
        }), 400

    # Validate merchant exists and is verified
    merchant = db.session.get(Merchant, merchant_id)
    if not merchant or not merchant.verified:
        return jsonify({
            "success": False,
            "message": "Merchant not found or not verified."
        }), 404

    # Validate service belongs to the merchant
    service = db.session.execute(
        db.select(Service).filter_by(id=service_id, merchant_id=merchant_id)
    ).scalar_one_or_none()

    if not service:
        return jsonify({
            "success": False,
            "message": "Service not found for this merchant."
        }), 404

    try:
        payment = Payment(
            user_id=user.id,
            merchant_id=merchant_id,
            service_id=service_id,
            beneficiary_name=str(beneficiary_name).strip(),
            amount=amount,
            status="COMPLETED"
        )
        db.session.add(payment)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Payment created successfully.",
            "data": {
                "payment_id": payment.id,
                "status": payment.status
            }
        }), 201
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
        .filter_by(user_id=user.id)
        .order_by(Payment.created_at.desc())
    ).scalars().all()

    return jsonify({
        "success": True,
        "data": [p.to_dict() for p in payments]
    }), 200
