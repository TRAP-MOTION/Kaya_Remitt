from datetime import datetime, timezone
from flask import Blueprint, jsonify, request, g
from marshmallow import ValidationError

from backend.app.extensions import db
from backend.app.models.users import User
from backend.app.models.merchant import Merchant
from backend.app.models.notification import Notification
from backend.app.models.support_ticket import SupportTicket
from backend.app.utils.auth import admin_required
from backend.app.utils.validation import load_json, load_path, validation_error_response
from backend.app.schemas.admin_schema import (
    UpdateMerchantStatusSchema,
    AccountActionSchema,
    SendWarningSchema,
    UpdateSupportTicketSchema,
    UserIdPathSchema,
    TicketIdPathSchema,
    TICKET_STATUSES,
    TICKET_CATEGORIES,
)
from backend.app.schemas.common import MerchantIdPathSchema, UUID_RE
import re

admin_bp = Blueprint("admin", __name__)

_merchant_status_schema = UpdateMerchantStatusSchema()
_account_action_schema = AccountActionSchema()
_send_warning_schema = SendWarningSchema()
_update_ticket_schema = UpdateSupportTicketSchema()
_merchant_id_schema = MerchantIdPathSchema()
_user_id_schema = UserIdPathSchema()
_ticket_id_schema = TicketIdPathSchema()

_UUID_PATTERN = re.compile(UUID_RE)


def _optional_uuid_query(name: str):
    value = request.args.get(name)
    if value is None or value == "":
        return None, None
    value = value.strip()
    if not _UUID_PATTERN.match(value):
        return None, (
            jsonify({
                "success": False,
                "reason": "INVALID_INPUT",
                "message": f"{name} must be a valid UUID.",
            }),
            400,
        )
    return value, None


@admin_bp.route("/merchants/<merchant_id>/status", methods=["PATCH"], strict_slashes=False)
@admin_required
def update_merchant_status(merchant_id):
    try:
        params = load_path(_merchant_id_schema, merchant_id=merchant_id)
        validated = load_json(_merchant_status_schema)
    except ValidationError as err:
        return validation_error_response(err)

    merchant = db.session.get(Merchant, params["merchant_id"])
    if not merchant:
        return jsonify({
            "success": False,
            "message": "Merchant not found."
        }), 404

    merchant.verification_status = validated["verification_status"]
    merchant.updated_at = datetime.now(timezone.utc)

    reason = validated.get("reason")
    if reason:
        # Optional audit note stored as a system notification for admin trail context
        db.session.add(Notification(
            user_id=g.current_user.user_id,
            title="Merchant Status Updated",
            message=(
                f"Merchant {merchant.business_name} set to "
                f"{merchant.verification_status}. Reason: {reason}"
            ),
            category="Admin",
        ))

    try:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Merchant status updated successfully.",
            "data": merchant.to_admin_status_dict(),
        }), 200
    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "An error occurred while updating merchant status."
        }), 500


@admin_bp.route("/users/<user_id>/deactivate", methods=["PATCH"], strict_slashes=False)
@admin_required
def deactivate_user(user_id):
    try:
        params = load_path(_user_id_schema, user_id=user_id)
        validated = load_json(_account_action_schema)
    except ValidationError as err:
        return validation_error_response(err)

    user = db.session.get(User, params["user_id"])
    if not user:
        return jsonify({
            "success": False,
            "message": "User not found."
        }), 404

    if user.user_id == g.current_user.user_id:
        return jsonify({
            "success": False,
            "message": "You cannot deactivate your own admin account."
        }), 400

    if user.role == "admin":
        return jsonify({
            "success": False,
            "message": "Admin accounts cannot be deactivated via this endpoint."
        }), 400

    user.account_status = "Inactive"
    reason = validated.get("reason")
    if reason:
        db.session.add(Notification(
            user_id=user.user_id,
            title="Account Deactivated",
            message=reason,
            category="Warning",
        ))

    try:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Account deactivated successfully.",
            "data": {
                "user_id": user.user_id,
                "email": user.email,
                "account_status": user.account_status,
            }
        }), 200
    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "An error occurred while deactivating the account."
        }), 500


@admin_bp.route("/users/<user_id>/activate", methods=["PATCH"], strict_slashes=False)
@admin_required
def activate_user(user_id):
    try:
        params = load_path(_user_id_schema, user_id=user_id)
        validated = load_json(_account_action_schema)
    except ValidationError as err:
        return validation_error_response(err)

    user = db.session.get(User, params["user_id"])
    if not user:
        return jsonify({
            "success": False,
            "message": "User not found."
        }), 404

    user.account_status = "Active"
    reason = validated.get("reason")
    if reason:
        db.session.add(Notification(
            user_id=user.user_id,
            title="Account Activated",
            message=reason,
            category="General",
        ))

    try:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Account activated successfully.",
            "data": {
                "user_id": user.user_id,
                "email": user.email,
                "account_status": user.account_status,
            }
        }), 200
    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "An error occurred while activating the account."
        }), 500


@admin_bp.route("/warnings", methods=["POST"], strict_slashes=False)
@admin_required
def send_warning():
    try:
        validated = load_json(_send_warning_schema)
    except ValidationError as err:
        return validation_error_response(err)

    user = db.session.get(User, validated["user_id"])
    if not user:
        return jsonify({
            "success": False,
            "message": "User not found."
        }), 404

    notification = Notification(
        user_id=user.user_id,
        title=validated["title"],
        message=validated["message"],
        category="Warning",
    )
    db.session.add(notification)

    try:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Warning notification sent successfully.",
            "data": notification.to_dict(),
        }), 201
    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "An error occurred while sending the warning."
        }), 500


@admin_bp.route("/warnings", methods=["GET"], strict_slashes=False)
@admin_required
def list_warnings():
    user_id, error = _optional_uuid_query("user_id")
    if error:
        return error

    stmt = db.select(Notification).filter_by(category="Warning")
    if user_id:
        stmt = stmt.filter_by(user_id=user_id)
    stmt = stmt.order_by(Notification.created_at.desc())

    warnings = db.session.execute(stmt).scalars().all()
    return jsonify({
        "success": True,
        "data": [n.to_dict() for n in warnings],
    }), 200


@admin_bp.route("/support", methods=["GET"], strict_slashes=False)
@admin_required
def list_support_tickets():
    status = request.args.get("status")
    category = request.args.get("category")
    user_id, error = _optional_uuid_query("user_id")
    if error:
        return error

    if status is not None and status != "":
        status = status.strip()
        if status not in TICKET_STATUSES:
            return jsonify({
                "success": False,
                "reason": "INVALID_INPUT",
                "message": f"status must be one of: {', '.join(TICKET_STATUSES)}",
            }), 400

    if category is not None and category != "":
        category = category.strip()
        if category not in TICKET_CATEGORIES:
            return jsonify({
                "success": False,
                "reason": "INVALID_INPUT",
                "message": f"category must be one of: {', '.join(TICKET_CATEGORIES)}",
            }), 400

    stmt = db.select(SupportTicket)
    if status:
        stmt = stmt.filter_by(status=status)
    if category:
        stmt = stmt.filter_by(category=category)
    if user_id:
        stmt = stmt.filter_by(user_id=user_id)
    stmt = stmt.order_by(SupportTicket.created_at.desc())

    tickets = db.session.execute(stmt).scalars().all()
    return jsonify({
        "success": True,
        "data": [t.to_summary_dict() for t in tickets],
    }), 200


@admin_bp.route("/support/<ticket_id>", methods=["GET"], strict_slashes=False)
@admin_required
def get_support_ticket(ticket_id):
    try:
        params = load_path(_ticket_id_schema, ticket_id=ticket_id)
    except ValidationError as err:
        return validation_error_response(err)

    ticket = db.session.get(SupportTicket, params["ticket_id"])
    if not ticket:
        return jsonify({
            "success": False,
            "message": "Support ticket not found."
        }), 404

    return jsonify({
        "success": True,
        "data": ticket.to_dict(),
    }), 200


@admin_bp.route("/support/<ticket_id>", methods=["PATCH"], strict_slashes=False)
@admin_required
def update_support_ticket(ticket_id):
    try:
        params = load_path(_ticket_id_schema, ticket_id=ticket_id)
        validated = load_json(_update_ticket_schema)
    except ValidationError as err:
        return validation_error_response(err)

    ticket = db.session.get(SupportTicket, params["ticket_id"])
    if not ticket:
        return jsonify({
            "success": False,
            "message": "Support ticket not found."
        }), 404

    ticket.status = validated["status"]
    if validated.get("admin_response") is not None:
        ticket.admin_response = validated["admin_response"]
    ticket.updated_at = datetime.now(timezone.utc)

    try:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Support ticket updated successfully.",
            "data": {
                "ticket_id": ticket.ticket_id,
                "status": ticket.status,
                "admin_response": ticket.admin_response,
                "updated_at": ticket.to_dict()["updated_at"],
            }
        }), 200
    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "An error occurred while updating the support ticket."
        }), 500
