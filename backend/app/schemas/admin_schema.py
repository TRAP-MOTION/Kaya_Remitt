from marshmallow import fields, validate

from backend.app.schemas.common import SanitizedSchema, UUID_RE


MERCHANT_STATUSES = ("Pending", "Verified", "Rejected", "Suspended")
TICKET_STATUSES = ("Open", "In Progress", "Resolved", "Closed")
TICKET_CATEGORIES = ("Support", "Complaint", "Payment", "Merchant", "Other")


class UpdateMerchantStatusSchema(SanitizedSchema):
    _strip_fields = ("verification_status", "reason")

    verification_status = fields.String(
        required=True,
        validate=validate.OneOf(MERCHANT_STATUSES),
    )
    reason = fields.String(
        load_default=None,
        allow_none=True,
        validate=validate.Length(min=1, max=500),
    )


class AccountActionSchema(SanitizedSchema):
    _strip_fields = ("reason",)

    reason = fields.String(
        load_default=None,
        allow_none=True,
        validate=validate.Length(min=1, max=500),
    )


class SendWarningSchema(SanitizedSchema):
    _strip_fields = ("user_id", "title", "message")

    user_id = fields.String(
        required=True,
        validate=[
            validate.Length(equal=36),
            validate.Regexp(UUID_RE, error="user_id must be a valid UUID."),
        ],
    )
    title = fields.String(required=True, validate=validate.Length(min=1, max=150))
    message = fields.String(required=True, validate=validate.Length(min=1, max=5000))


class UpdateSupportTicketSchema(SanitizedSchema):
    _strip_fields = ("status", "admin_response")

    status = fields.String(
        required=True,
        validate=validate.OneOf(TICKET_STATUSES),
    )
    admin_response = fields.String(
        load_default=None,
        allow_none=True,
        validate=validate.Length(min=1, max=5000),
    )


class UserIdPathSchema(SanitizedSchema):
    _strip_fields = ("user_id",)

    user_id = fields.String(
        required=True,
        validate=[
            validate.Length(equal=36),
            validate.Regexp(UUID_RE, error="user_id must be a valid UUID."),
        ],
    )


class TicketIdPathSchema(SanitizedSchema):
    _strip_fields = ("ticket_id",)

    ticket_id = fields.String(
        required=True,
        validate=[
            validate.Length(equal=36),
            validate.Regexp(UUID_RE, error="ticket_id must be a valid UUID."),
        ],
    )
