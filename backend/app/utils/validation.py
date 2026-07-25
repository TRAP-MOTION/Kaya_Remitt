from flask import jsonify, request
from marshmallow import ValidationError, Schema


def _first_message(messages) -> str:
    """Extract the first human-readable message from Marshmallow error messages."""
    if isinstance(messages, list):
        for item in messages:
            if isinstance(item, str):
                return item
            nested = _first_message(item)
            if nested:
                return nested
        return "Invalid input."

    if isinstance(messages, dict):
        for value in messages.values():
            nested = _first_message(value)
            if nested:
                return nested
        return "Invalid input."

    if isinstance(messages, str):
        return messages

    return "Invalid input."


def validation_error_response(err: ValidationError):
    return jsonify({
        "success": False,
        "reason": "INVALID_INPUT",
        "message": _first_message(err.messages),
    }), 400


def load_json(schema: Schema):
    """Load and sanitize JSON request body with the given Marshmallow schema."""
    data = request.get_json(silent=True)
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ValidationError({"_schema": ["Request body must be a JSON object."]})
    return schema.load(data)


def load_path(schema: Schema, **params):
    """Load and sanitize path/query parameters with the given Marshmallow schema."""
    return schema.load(params)
