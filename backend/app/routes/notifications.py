from flask import Blueprint, jsonify, g
from marshmallow import ValidationError
from backend.app.extensions import db
from backend.app.models.notification import Notification
from backend.app.utils.auth import token_required
from backend.app.utils.validation import load_path, validation_error_response
from backend.app.schemas.common import UuidPathSchema

notifications_bp = Blueprint("notifications", __name__)

_notification_id_schema = UuidPathSchema()


@notifications_bp.route("", methods=["GET"], strict_slashes=False)
@notifications_bp.route("/", methods=["GET"], strict_slashes=False)
@token_required
def list_notifications():
    """GET /api/v1/notifications — Returns all notifications for the current user."""
    user = g.current_user

    notifications = db.session.execute(
        db.select(Notification)
        .filter_by(user_id=user.user_id)
        .order_by(Notification.created_at.desc())
    ).scalars().all()

    return jsonify({
        "success": True,
        "data": [n.to_dict() for n in notifications],
    }), 200


@notifications_bp.route("/<notification_id>/read", methods=["PATCH"], strict_slashes=False)
@token_required
def mark_as_read(notification_id):
    """PATCH /api/v1/notifications/{notification_id}/read — Marks a notification as read."""
    user = g.current_user

    try:
        params = load_path(_notification_id_schema, id=notification_id)
    except ValidationError as err:
        return validation_error_response(err)

    notification = db.session.execute(
        db.select(Notification).filter_by(
            notification_id=params["id"],
            user_id=user.user_id,
        )
    ).scalar_one_or_none()

    if not notification:
        return jsonify({
            "success": False,
            "message": "Notification not found."
        }), 404

    if notification.is_read:
        return jsonify({
            "success": True,
            "message": "Notification already marked as read.",
            "data": notification.to_dict(),
        }), 200

    try:
        notification.is_read = True
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Notification marked as read.",
            "data": notification.to_dict(),
        }), 200
    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "An error occurred while updating the notification."
        }), 500


@notifications_bp.route("/read-all", methods=["PATCH"], strict_slashes=False)
@token_required
def mark_all_as_read():
    """PATCH /api/v1/notifications/read-all — Marks all unread notifications as read."""
    user = g.current_user

    try:
        db.session.execute(
            db.update(Notification)
            .where(
                Notification.user_id == user.user_id,
                Notification.is_read == False,  # noqa: E712
            )
            .values(is_read=True)
        )
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "All notifications marked as read.",
        }), 200
    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "An error occurred while updating notifications."
        }), 500
