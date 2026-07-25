from flask import Blueprint, request, jsonify, g
from backend.app.extensions import db
from backend.app.models.payment import Payment
from backend.app.models.voucher import Voucher
from backend.app.utils.auth import token_required

vouchers_bp = Blueprint("vouchers", __name__)


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

    # Ensure the payment belongs to the requesting user
    payment = db.session.execute(
        db.select(Payment).filter_by(id=payment_id, user_id=user.id)
    ).scalar_one_or_none()

    if not payment:
        return jsonify({
            "success": False,
            "message": "Payment not found."
        }), 404

    if payment.status != "COMPLETED":
        return jsonify({
            "success": False,
            "message": "A voucher can only be generated for a completed payment."
        }), 400

    # Check if a voucher already exists for this payment
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
            payment_id=payment.id,
            merchant_id=payment.merchant_id,
            amount=payment.amount,
            status="ACTIVE"
        )
        db.session.add(voucher)
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

    voucher = db.session.get(Voucher, voucher_id)

    if not voucher:
        return jsonify({
            "success": False,
            "message": "Voucher not found."
        }), 404

    if voucher.status == "REDEEMED":
        return jsonify({
            "success": False,
            "message": "This voucher has already been redeemed.",
            "data": {
                "status": "REDEEMED",
                "amount": round(float(voucher.amount), 2),
                "merchant": voucher.merchant.business_name if voucher.merchant else None
            }
        }), 400

    return jsonify({
        "success": True,
        "message": "Voucher verified successfully.",
        "data": {
            "status": "VALID",
            "amount": round(float(voucher.amount), 2),
            "merchant": voucher.merchant.business_name if voucher.merchant else None
        }
    }), 200


@vouchers_bp.route("/<voucher_id>/redeem", methods=["PATCH"], strict_slashes=False)
@token_required
def redeem_voucher(voucher_id):
    """PATCH /api/v1/vouchers/{voucher_id}/redeem — Marks a voucher as used."""
    voucher = db.session.get(Voucher, voucher_id)

    if not voucher:
        return jsonify({
            "success": False,
            "message": "Voucher not found."
        }), 404

    if voucher.status == "REDEEMED":
        return jsonify({
            "success": False,
            "message": "This voucher has already been redeemed."
        }), 400

    try:
        voucher.status = "REDEEMED"
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
