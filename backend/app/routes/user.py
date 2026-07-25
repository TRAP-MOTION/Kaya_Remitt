from flask import Blueprint, jsonify, g
from marshmallow import ValidationError
from backend.app.extensions import db
from backend.app.utils.auth import token_required
from backend.app.utils.validation import load_json, validation_error_response
from backend.app.schemas.user_schema import UpdateProfileSchema

user_bp = Blueprint("user", __name__)

_update_profile_schema = UpdateProfileSchema()


@user_bp.route("/profile", methods=["GET"])
@token_required
def get_profile():
    user = g.current_user
    return jsonify({
        "success": True,
        "message": "Profile retrieved successfully.",
        "data": user.to_dict()
    }), 200


@user_bp.route("/profile", methods=["PUT"])
@token_required
def update_profile():
    user = g.current_user

    try:
        validated = load_json(_update_profile_schema)
    except ValidationError as err:
        return validation_error_response(err)

    full_name = validated.get("full_name")
    phone = validated.get("phone")
    country = validated.get("country")

    if full_name is not None:
        user.full_name = full_name

    if phone is not None:
        user.phone = phone

    if country is not None:
        user.country = country

    try:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Profile updated successfully.",
            "data": user.to_dict()
        }), 200
    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "reason": "DATABASE_ERROR",
            "message": "An error occurred while updating your profile."
        }), 500
