from marshmallow import fields, validate, validates, ValidationError

from backend.app.schemas.common import SanitizedSchema, UUID_RE


class CreatePaymentSchema(SanitizedSchema):
    _strip_fields = ("merchant_id", "service_id", "beneficiary_name")

    merchant_id = fields.String(
        required=True,
        validate=[
            validate.Length(equal=36),
            validate.Regexp(UUID_RE, error="merchant_id must be a valid UUID."),
        ],
    )
    service_id = fields.String(
        required=True,
        validate=[
            validate.Length(equal=36),
            validate.Regexp(UUID_RE, error="service_id must be a valid UUID."),
        ],
    )
    beneficiary_name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
    )
    amount = fields.Decimal(
        required=True,
        as_string=False,
        places=2,
        validate=validate.Range(min=0.01, error="amount must be a positive number."),
    )

    @validates("beneficiary_name")
    def validate_beneficiary_name(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("beneficiary_name cannot be empty.")
