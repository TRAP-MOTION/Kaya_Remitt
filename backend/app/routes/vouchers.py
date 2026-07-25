from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, g
from backend.app.extensions import db
from backend.app.models.payment import Payment
from backend.app.models.voucher import Voucher
from backend.app.models.transaction import Transaction
from backend.app.models.notification import Notification
from backend.app.utils.auth import token_required

vouchers_bp = Blueprint("vouchers", __name__)


def _find_voucher(voucher_identifier):
    """Look up a voucher by voucher_id (UUID) or voucher_code."""
    voucher = db.session.get(Voucher, voucher_identifier)
    if voucher:
        return voucher
    return db.session.execute(
        db.select(Voucher).filter_by(voucher_code=voucher_identifier)
    ).scalar_one_or_none()


@vouchers_bp.route("", methods=["POST"], strict_slashes=False)
@vouchers_bp.route("/", methods=["POST"], strict_slashes=False)
@token_required
def generate_voucher():
    """POST /api/v1/vouchers — Generates a digital voucher after a successful payment."""
    user = g.current_user
    data = request.get_json() or {}

    payment_id = data.get("payment_id")
    if not payment_id:
        return jsonify({
            "success": False,
            "message": "payment_id is required."
        }), 400

    payment = db.session.execute(
        db.select(Payment).filter_by(payment_id=payment_id, user_id=user.user_id)
    ).scalar_one_or_none()

    if not payment:
        return jsonify({
            "success": False,
            "message": "Payment not found."
        }), 404

    if payment.payment_status != "COMPLETED":
        return jsonify({
            "success": False,
            "message": "A voucher can only be generated for a completed payment."
        }), 400

    existing = db.session.execute(
        db.select(Voucher).filter_by(payment_id=payment_id)
    ).scalar_one_or_none()

    if existing:
        return jsonify({
            "success": True,
            "data": existing.to_dict()
        }), 200

    try:
        voucher = Voucher(
            payment_id=payment.payment_id,
            status="Active",
        )
        db.session.add(voucher)
        db.session.flush()

        db.session.add(Transaction(
            payment_id=payment.payment_id,
            action="VOUCHER_ISSUED",
            performed_by=user.user_id,
            status="Active",
        ))
        db.session.add(Notification(
            user_id=user.user_id,
            title="Voucher Issued",
            message=f"A voucher ({voucher.voucher_code}) has been issued for your payment.",
        ))
        db.session.commit()

        return jsonify({
            "success": True,
            "data": voucher.to_dict()
        }), 201
    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "An error occurred while generating the voucher."
        }), 500


@vouchers_bp.route("/verify", methods=["POST"], strict_slashes=False)
@token_required
def verify_voucher():
    """POST /api/v1/vouchers/verify — Allows merchants to check whether a voucher is valid."""
    data = request.get_json() or {}

    voucher_id = data.get("voucher_id")
    if not voucher_id:
        return jsonify({
            "success": False,
            "message": "voucher_id is required."
        }), 400

    voucher = _find_voucher(voucher_id)

    if not voucher:
        return jsonify({
            "success": False,
            "message": "Voucher not found."
        }), 404

    merchant_name = None
    amount = None
    if voucher.payment:
        amount = round(float(voucher.payment.amount), 2)
        if voucher.payment.merchant:
            merchant_name = voucher.payment.merchant.business_name

    if voucher.status.lower() == "redeemed":
        return jsonify({
            "success": False,
            "message": "This voucher has already been redeemed.",
            "data": {
                "status": "REDEEMED",
                "amount": amount,
                "merchant": merchant_name,
            }
        }), 400

    return jsonify({
        "success": True,
        "message": "Voucher verified successfully.",
        "data": {
            "status": "VALID",
            "amount": amount,
            "merchant": merchant_name,
        }
    }), 200


@vouchers_bp.route("/<voucher_id>/redeem", methods=["PATCH"], strict_slashes=False)
@token_required
def redeem_voucher(voucher_id):
    """PATCH /api/v1/vouchers/{voucher_id}/redeem — Marks a voucher as used."""
    user = g.current_user
    voucher = _find_voucher(voucher_id)

    if not voucher:
        return jsonify({
            "success": False,
            "message": "Voucher not found."
        }), 404

    if voucher.status.lower() == "redeemed":
        return jsonify({
            "success": False,
            "message": "This voucher has already been redeemed."
        }), 400

    try:
        voucher.status = "Redeemed"
        voucher.redeemed_at = datetime.now(timezone.utc)

        db.session.add(Transaction(
            payment_id=voucher.payment_id,
            action="VOUCHER_REDEEMED",
            performed_by=user.user_id,
            status="Redeemed",
        ))

        if voucher.payment:
            db.session.add(Notification(
                user_id=voucher.payment.user_id,
                title="Voucher Redeemed",
                message=f"Your voucher ({voucher.voucher_code}) has been redeemed.",
            ))

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Voucher redeemed successfully.",
            "data": {
                "status": "REDEEMED"
            }
        }), 200
    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "An error occurred while redeeming the voucher."
        }), 500
