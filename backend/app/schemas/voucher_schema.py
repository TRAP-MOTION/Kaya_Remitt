from marshmallow import fields, validate

from backend.app.schemas.common import (
    SanitizedSchema,
    UUID_RE,
    VOUCHER_IDENTIFIER_RE,
)


class GenerateVoucherSchema(SanitizedSchema):
    _strip_fields = ("payment_id",)

    payment_id = fields.String(
        required=True,
        validate=[
            validate.Length(equal=36),
            validate.Regexp(UUID_RE, error="payment_id must be a valid UUID."),
        ],
    )


class VerifyVoucherSchema(SanitizedSchema):
    _strip_fields = ("voucher_id",)

    voucher_id = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, max=100),
            validate.Regexp(
                VOUCHER_IDENTIFIER_RE,
                error="voucher_id must be a valid UUID or voucher code.",
            ),
        ],
    )
