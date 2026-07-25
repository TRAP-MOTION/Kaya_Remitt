from marshmallow import Schema, fields, validate, validates, ValidationError


class UpdateProfileSchema(Schema):
    full_name = fields.String(load_default=None, validate=validate.Length(min=1, max=100))
    phone = fields.String(load_default=None, validate=validate.Length(min=8, max=20))
    country = fields.String(load_default=None, validate=validate.Length(min=1, max=100))

    @validates("full_name")
    def validate_full_name(self, value):
        if value is not None and not value.strip():
            raise ValidationError("Full name cannot be empty.")

    @validates("phone")
    def validate_phone(self, value):
        if value is not None and not value.strip().startswith("+"):
            raise ValidationError(
                "Phone number must start with '+' followed by country code and local number."
            )
