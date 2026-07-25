from flask import Blueprint, jsonify
from marshmallow import ValidationError
from backend.app.extensions import db
from backend.app.models.merchant import Merchant
from backend.app.models.service import Service
from backend.app.utils.auth import token_required
from backend.app.utils.validation import load_path, validation_error_response
from backend.app.schemas.common import MerchantIdPathSchema

merchants_bp = Blueprint("merchants", __name__)

_merchant_id_schema = MerchantIdPathSchema()


@merchants_bp.route("", methods=["GET"], strict_slashes=False)
@merchants_bp.route("/", methods=["GET"], strict_slashes=False)
@token_required
def get_merchants():
    """GET /api/v1/merchants — Returns all verified merchants."""
    merchants = db.session.execute(
        db.select(Merchant)
        .filter_by(verification_status="Verified")
        .order_by(Merchant.business_name)
    ).scalars().all()

    return jsonify({
        "success": True,
        "data": [m.to_dict() for m in merchants]
    }), 200


@merchants_bp.route("/<merchant_id>", methods=["GET"], strict_slashes=False)
@token_required
def get_merchant(merchant_id):
    """GET /api/v1/merchants/{merchant_id} — Returns merchant detail + services."""
    try:
        params = load_path(_merchant_id_schema, merchant_id=merchant_id)
    except ValidationError as err:
        return validation_error_response(err)

    merchant = db.session.get(Merchant, params["merchant_id"])

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
    try:
        params = load_path(_merchant_id_schema, merchant_id=merchant_id)
    except ValidationError as err:
        return validation_error_response(err)

    merchant_id = params["merchant_id"]
    merchant = db.session.get(Merchant, merchant_id)

    if not merchant or not merchant.verified:
        return jsonify({
            "success": False,
            "message": "Merchant not found."
        }), 404

    services = db.session.execute(
        db.select(Service).filter_by(merchant_id=merchant_id, availability=True)
    ).scalars().all()

    return jsonify({
        "success": True,
        "data": [s.to_dict() for s in services]
    }), 200
