from flask import Blueprint, jsonify, g
from backend.app.extensions import db
from backend.app.models.payment import Payment
from backend.app.models.merchant import Merchant
from backend.app.utils.auth import token_required

merchant_dashboard_bp = Blueprint("merchant_dashboard", __name__)


@merchant_dashboard_bp.route("/transactions", methods=["GET"], strict_slashes=False)
@token_required
def get_merchant_transactions():
    """GET /api/v1/merchant/transactions — Returns payments received by a merchant."""
    user = g.current_user

    if user.role != "merchant":
        return jsonify({
            "success": False,
            "message": "Access restricted to merchant accounts."
        }), 403

    # Match merchant account by email when ownership linkage is not yet modeled.
    merchant = db.session.execute(
        db.select(Merchant).filter_by(
            email=user.email,
            verification_status="Verified",
        )
    ).scalar_one_or_none()

    if not merchant:
        return jsonify({
            "success": True,
            "data": []
        }), 200

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
            "amount": round(float(payment.amount), 2),
            "status": status,
        })

    return jsonify({
        "success": True,
        "data": transactions
    }), 200
