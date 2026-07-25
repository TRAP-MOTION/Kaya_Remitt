from marshmallow import fields, validate, validates, ValidationError, pre_load

from backend.app.schemas.common import SanitizedSchema, PHONE_RE, strip_string_fields


class RegisterSchema(SanitizedSchema):
    _strip_fields = ("full_name", "email", "phone", "password", "role", "country")

    full_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    phone = fields.String(
        load_default=None,
        allow_none=True,
        validate=[
            validate.Length(min=8, max=20),
            validate.Regexp(
                PHONE_RE,
                error="Phone number must start with '+' followed by country code and local number.",
            ),
        ],
    )
    password = fields.String(required=True, validate=validate.Length(min=6, max=128))
    role = fields.String(
        load_default="diaspora",
        validate=validate.OneOf(["diaspora", "merchant"]),
    )
    country = fields.String(
        load_default=None,
        allow_none=True,
        validate=validate.Length(min=1, max=100),
    )

    @pre_load
    def normalize(self, data, **kwargs):
        data = strip_string_fields(data, self._strip_fields)
        if not isinstance(data, dict):
            return data
        cleaned = dict(data)
        if isinstance(cleaned.get("email"), str):
            cleaned["email"] = cleaned["email"].lower()
        if cleaned.get("country") == "":
            cleaned["country"] = None
        if cleaned.get("phone") == "":
            cleaned["phone"] = None
        return cleaned

    @validates("full_name")
    def validate_full_name(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Full name cannot be empty.")


class LoginSchema(SanitizedSchema):
    _strip_fields = ("email", "password")

    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=1, max=128))

    @pre_load
    def normalize_email(self, data, **kwargs):
        data = strip_string_fields(data, self._strip_fields)
        if not isinstance(data, dict):
            return data
        cleaned = dict(data)
        if isinstance(cleaned.get("email"), str):
            cleaned["email"] = cleaned["email"].lower()
        return cleaned
