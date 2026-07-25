from flask import Blueprint, jsonify
from marshmallow import ValidationError
from backend.app.extensions import db
from backend.app.models.users import User
from backend.app.utils.auth import generate_token
from backend.app.utils.validation import load_json, validation_error_response
from backend.app.schemas.auth_schema import RegisterSchema, LoginSchema

auth_bp = Blueprint("auth", __name__)

_register_schema = RegisterSchema()
_login_schema = LoginSchema()


@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        validated = load_json(_register_schema)
    except ValidationError as err:
        return validation_error_response(err)

    full_name = validated["full_name"]
    email = validated["email"]
    phone = validated.get("phone")
    password = validated["password"]
    role = validated.get("role", "diaspora")
    country = validated.get("country")

    existing_email = db.session.execute(
        db.select(User).filter_by(email=email)
    ).scalar_one_or_none()
    if existing_email:
        return jsonify({
            "success": False,
            "reason": "EMAIL_ALREADY_EXISTS",
            "message": "An account with this email address already exists."
        }), 400

    try:
        user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            role=role,
            country=country,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Account created successfully.",
            "data": {
                "user_id": user.user_id,
                "role": user.role
            }
        }), 201
    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "reason": "DATABASE_ERROR",
            "message": "An error occurred while creating your account."
        }), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        validated = load_json(_login_schema)
    except ValidationError as err:
        return validation_error_response(err)

    email = validated["email"]
    password = validated["password"]

    user = db.session.execute(
        db.select(User).filter_by(email=email)
    ).scalar_one_or_none()
    if not user or not user.check_password(password):
        return jsonify({
            "success": False,
            "reason": "INVALID_CREDENTIALS",
            "message": "The email or password provided is incorrect."
        }), 401

    token = generate_token(user.user_id)

    return jsonify({
        "success": True,
        "message": "Login successful.",
        "data": {
            "token": token
        }
    }), 200
