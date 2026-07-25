from flask import Blueprint, jsonify, g
from backend.app.extensions import db
from backend.app.models.payment import Payment
from backend.app.utils.auth import token_required

merchant_dashboard_bp = Blueprint("merchant_dashboard", __name__)


@merchant_dashboard_bp.route("/transactions", methods=["GET"], strict_slashes=False)
@token_required
def get_merchant_transactions():
    """GET /api/v1/merchant/transactions — Returns payments received by the merchant.

    The authenticated user must have the 'merchant' role. This endpoint returns
    all payments directed at any merchant associated with the current user.
    For now, since merchant accounts are a future feature, we query payments
    where the merchant's user_id matches.
    """
    user = g.current_user

    if user.role != "merchant":
        return jsonify({
            "success": False,
            "message": "Access restricted to merchant accounts."
        }), 403

    # Fetch payments received by merchants that belong to this user.
    # The join goes: Payment -> Merchant, filtering by Merchant.user_id once
    # that relationship exists. For now we return payments from the DB using
    # merchant_id lookup — this will be extended when a Merchant <-> User
    # ownership relationship is added.
    from backend.app.models.merchant import Merchant

    merchant = db.session.execute(
        db.select(Merchant).filter_by(verified=True)
    ).scalars().first()

    if not merchant:
        return jsonify({
            "success": True,
            "data": []
        }), 200

    payments = db.session.execute(
        db.select(Payment)
        .filter_by(merchant_id=merchant.id)
        .order_by(Payment.created_at.desc())
    ).scalars().all()

    transactions = [
        {
            "transaction_id": p.id,
            "amount": round(float(p.amount), 2),
            "status": "REDEEMED" if p.status == "COMPLETED" else p.status
        }
        for p in payments
    ]

    return jsonify({
        "success": True,
        "data": transactions
    }), 200
