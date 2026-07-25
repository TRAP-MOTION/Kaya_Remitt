from marshmallow import fields, validate, validates, validates_schema, ValidationError, pre_load

from backend.app.schemas.common import SanitizedSchema, strip_string_fields


class UpdateProfileSchema(SanitizedSchema):
    _strip_fields = ("full_name", "country")

    full_name = fields.String(
        load_default=None,
        allow_none=True,
        validate=validate.Length(min=1, max=100),
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
        if cleaned.get("full_name") == "":
            cleaned["full_name"] = None
        return cleaned

    @validates("full_name")
    def validate_full_name(self, value, **kwargs):
        if value is not None and not value.strip():
            raise ValidationError("Full name cannot be empty.")

    @validates_schema
    def require_at_least_one_field(self, data, **kwargs):
        if not any(data.get(field) is not None for field in ("full_name", "country")):
            raise ValidationError(
                "At least one of full_name or country is required."
            )
