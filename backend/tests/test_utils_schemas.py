"""Unit tests for utility functions, auth helpers, and schemas."""
import pytest
from datetime import datetime, timezone, timedelta
import jwt
from flask import Flask, jsonify
from marshmallow import ValidationError

from backend.app.utils.auth import generate_token, decode_token, token_required
from backend.app.utils.validation import load_json, load_path, validation_error_response
from backend.app.schemas.common import SanitizedSchema, UuidPathSchema, VoucherIdPathSchema, MerchantIdPathSchema


def test_jwt_token_generation_and_decoding(app):
    """Test generating and decoding JWT token."""
    user_id = "test-user-123"
    with app.app_context():
        token = generate_token(user_id)
        assert isinstance(token, str)

        decoded_sub = decode_token(token)
        assert decoded_sub == user_id


def test_jwt_token_expired(app):
    """Test decoding an expired JWT token returns 'EXPIRED'."""
    with app.app_context():
        payload = {
            "exp": datetime.now(timezone.utc) - timedelta(minutes=10),
            "iat": datetime.now(timezone.utc) - timedelta(minutes=20),
            "sub": "expired-user"
        }
        token = jwt.encode(payload, app.config["JWT_SECRET_KEY"], algorithm="HS256")
        result = decode_token(token)
        assert result == "EXPIRED"


def test_jwt_token_invalid_signature(app):
    """Test decoding a token with invalid signature returns 'INVALID'."""
    with app.app_context():
        payload = {
            "exp": datetime.now(timezone.utc) + timedelta(minutes=10),
            "sub": "some-user"
        }
        token = jwt.encode(payload, "wrong-secret-key", algorithm="HS256")
        result = decode_token(token)
        assert result == "INVALID"


def test_validation_error_response_formatting(app):
    """Test converting Marshmallow ValidationError into Flask JSON response."""
    with app.app_context():
        err = ValidationError({"email": ["Invalid email address."]})
        response, status_code = validation_error_response(err)
        assert status_code == 400
        json_data = response.get_json()
        assert json_data["success"] is False
        assert json_data["reason"] == "INVALID_INPUT"
        assert json_data["message"] == "Invalid email address."


def test_sanitized_schema_stripping():
    """Test that SanitizedSchema strips whitespace from configured string fields."""
    class DummySchema(SanitizedSchema):
        _strip_fields = ("name", "code")

    schema = DummySchema()
    data = {"name": "  Alice Smith  ", "code": "  CODE123  ", "number": 42}
    result = schema._sanitize_strings(data)
    assert result["name"] == "Alice Smith"
    assert result["code"] == "CODE123"
    assert result["number"] == 42


def test_uuid_path_schema_validation():
    """Test UuidPathSchema validation for valid UUID vs invalid format."""
    schema = UuidPathSchema()

    # Valid UUID
    valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
    loaded = schema.load({"id": valid_uuid})
    assert loaded["id"] == valid_uuid

    # Invalid UUID
    with pytest.raises(ValidationError):
        schema.load({"id": "not-a-valid-uuid"})


def test_voucher_id_path_schema_validation():
    """Test VoucherIdPathSchema accepts both UUID and KAYA-prefixed codes."""
    schema = VoucherIdPathSchema()

    # Valid UUID
    valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
    assert schema.load({"voucher_id": valid_uuid})["voucher_id"] == valid_uuid

    # Valid KAYA code
    valid_code = "KAYA-A1B2C3"
    assert schema.load({"voucher_id": valid_code})["voucher_id"] == valid_code

    # Invalid string format
    with pytest.raises(ValidationError):
        schema.load({"voucher_id": "INVALID_FORMAT_CODE"})
