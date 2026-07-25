"""Shared Marshmallow helpers for input sanitization and ID validation."""
from marshmallow import EXCLUDE, Schema, fields, pre_load, validate

UUID_RE = (
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)

# Accept either a UUID primary key or a public voucher code (e.g. KAYA-A1B2C3)
VOUCHER_IDENTIFIER_RE = (
    r"^("
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
    r"|KAYA-[A-Za-z0-9]{6,}"
    r")$"
)

PHONE_RE = r"^\+[1-9]\d{7,18}$"


def strip_string_fields(data, keys):
    """Return a shallow copy with listed string fields stripped."""
    if not isinstance(data, dict):
        return data
    cleaned = dict(data)
    for key in keys:
        if key in cleaned and isinstance(cleaned[key], str):
            cleaned[key] = cleaned[key].strip()
    return cleaned


class SanitizedSchema(Schema):
    """Base schema that strips whitespace from configured string fields."""

    class Meta:
        unknown = EXCLUDE

    _strip_fields: tuple[str, ...] = ()

    @pre_load
    def _sanitize_strings(self, data, **kwargs):
        return strip_string_fields(data, self._strip_fields)


class UuidPathSchema(SanitizedSchema):
    """Validate a UUID path parameter."""

    _strip_fields = ("id",)

    id = fields.String(
        required=True,
        validate=[
            validate.Length(min=36, max=36),
            validate.Regexp(UUID_RE, error="Must be a valid UUID."),
        ],
    )


class MerchantIdPathSchema(SanitizedSchema):
    _strip_fields = ("merchant_id",)

    merchant_id = fields.String(
        required=True,
        validate=[
            validate.Length(min=36, max=36),
            validate.Regexp(UUID_RE, error="merchant_id must be a valid UUID."),
        ],
    )


class VoucherIdPathSchema(SanitizedSchema):
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
