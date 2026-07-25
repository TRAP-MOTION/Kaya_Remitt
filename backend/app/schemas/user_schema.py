from marshmallow import fields, validate, validates, validates_schema, ValidationError, pre_load

from backend.app.schemas.common import SanitizedSchema, PHONE_RE, strip_string_fields


class UpdateProfileSchema(SanitizedSchema):
    _strip_fields = ("full_name", "phone", "country")

    full_name = fields.String(
        load_default=None,
        allow_none=True,
        validate=validate.Length(min=1, max=100),
    )
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
        if cleaned.get("country") == "":
            cleaned["country"] = None
        # Treat blank optional strings as omitted
        for key in ("full_name", "phone"):
            if cleaned.get(key) == "":
                cleaned[key] = None
        return cleaned

    @validates("full_name")
    def validate_full_name(self, value, **kwargs):
        if value is not None and not value.strip():
            raise ValidationError("Full name cannot be empty.")

    @validates_schema
    def require_at_least_one_field(self, data, **kwargs):
        if not any(data.get(field) is not None for field in ("full_name", "phone", "country")):
            raise ValidationError(
                "At least one of full_name, phone, or country is required."
            )
