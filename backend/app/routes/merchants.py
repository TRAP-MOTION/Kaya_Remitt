from flask import Blueprint, jsonify
from backend.app.extensions import db
from backend.app.models.merchant import Merchant
from backend.app.models.service import Service
from backend.app.utils.auth import token_required

merchants_bp = Blueprint("merchants", __name__)


@merchants_bp.route("", methods=["GET"], strict_slashes=False)
@merchants_bp.route("/", methods=["GET"], strict_slashes=False)
@token_required
def get_merchants():
    """GET /api/v1/merchants — Returns all verified merchants."""
    merchants = db.session.execute(
        db.select(Merchant).filter_by(verified=True).order_by(Merchant.business_name)
    ).scalars().all()

    return jsonify({
        "success": True,
        "data": [m.to_dict() for m in merchants]
    }), 200


@merchants_bp.route("/<merchant_id>", methods=["GET"], strict_slashes=False)
@token_required
def get_merchant(merchant_id):
    """GET /api/v1/merchants/{merchant_id} — Returns merchant detail + services."""
    merchant = db.session.get(Merchant, merchant_id)

    if not merchant or not merchant.verified:
        return jsonify({
            "success": False,
            "message": "Merchant not found."
        }), 404

    return jsonify({
        "success": True,
        "data": merchant.to_dict(include_services=True)
    }), 200


@merchants_bp.route("/<merchant_id>/services", methods=["GET"], strict_slashes=False)
@token_required
def get_merchant_services(merchant_id):
    """GET /api/v1/merchants/{merchant_id}/services — Returns services for a merchant."""
    merchant = db.session.get(Merchant, merchant_id)

    if not merchant or not merchant.verified:
        return jsonify({
            "success": False,
            "message": "Merchant not found."
        }), 404

    services = db.session.execute(
        db.select(Service).filter_by(merchant_id=merchant_id)
    ).scalars().all()

    return jsonify({
        "success": True,
        "data": [s.to_dict() for s in services]
    }), 200
