"""Tests for notification endpoints (/api/v1/notifications)."""
import uuid

from backend.app.extensions import db
from backend.app.models.notification import Notification


def _seed_notifications(db_session, user_id):
    n1 = Notification(
        user_id=user_id,
        title="Payment Accepted",
        message="Your payment was accepted.",
        category="Payment",
        is_read=False,
    )
    n2 = Notification(
        user_id=user_id,
        title="Warning",
        message="Account warning from admin.",
        category="Warning",
        is_read=False,
    )
    n3 = Notification(
        user_id=user_id,
        title="Already Read",
        message="This was already read.",
        category="General",
        is_read=True,
    )
    db_session.add_all([n1, n2, n3])
    db_session.commit()
    return n1, n2, n3


def test_list_notifications(client, diaspora_headers, db_session, diaspora_user):
    """Authenticated user can list their notifications."""
    _seed_notifications(db_session, diaspora_user.user_id)

    response = client.get("/api/v1/notifications", headers=diaspora_headers)
    assert response.status_code == 200
    res_data = response.get_json()
    assert res_data["success"] is True
    assert len(res_data["data"]) == 3
    assert all("notification_id" in n for n in res_data["data"])
    assert all("is_read" in n for n in res_data["data"])


def test_list_notifications_empty(client, diaspora_headers):
    """User with no notifications gets an empty list."""
    response = client.get("/api/v1/notifications", headers=diaspora_headers)
    assert response.status_code == 200
    assert response.get_json()["data"] == []


def test_list_notifications_unauthenticated(client):
    """Unauthenticated request returns 401."""
    response = client.get("/api/v1/notifications")
    assert response.status_code == 401


def test_mark_notification_as_read(client, diaspora_headers, db_session, diaspora_user):
    """Marking a notification as read updates is_read."""
    n1, _, _ = _seed_notifications(db_session, diaspora_user.user_id)

    response = client.patch(
        f"/api/v1/notifications/{n1.notification_id}/read",
        headers=diaspora_headers,
    )
    assert response.status_code == 200
    res_data = response.get_json()
    assert res_data["success"] is True
    assert res_data["data"]["is_read"] is True

    db_session.refresh(n1)
    assert n1.is_read is True


def test_mark_notification_already_read(client, diaspora_headers, db_session, diaspora_user):
    """Marking an already-read notification is idempotent."""
    _, _, n3 = _seed_notifications(db_session, diaspora_user.user_id)

    response = client.patch(
        f"/api/v1/notifications/{n3.notification_id}/read",
        headers=diaspora_headers,
    )
    assert response.status_code == 200
    assert "already" in response.get_json()["message"].lower()


def test_mark_notification_not_found(client, diaspora_headers):
    """Marking a non-existent notification returns 404."""
    response = client.patch(
        f"/api/v1/notifications/{uuid.uuid4()}/read",
        headers=diaspora_headers,
    )
    assert response.status_code == 404


def test_mark_notification_other_user(
    client, diaspora_headers, merchant_headers, db_session, merchant_user
):
    """Users cannot mark another user's notification as read."""
    note = Notification(
        user_id=merchant_user.user_id,
        title="Merchant Note",
        message="Private to merchant.",
        category="Payment",
    )
    db_session.add(note)
    db_session.commit()

    response = client.patch(
        f"/api/v1/notifications/{note.notification_id}/read",
        headers=diaspora_headers,
    )
    assert response.status_code == 404


def test_mark_all_as_read(client, diaspora_headers, db_session, diaspora_user):
    """Mark all unread notifications as read."""
    n1, n2, n3 = _seed_notifications(db_session, diaspora_user.user_id)

    response = client.patch(
        "/api/v1/notifications/read-all",
        headers=diaspora_headers,
    )
    assert response.status_code == 200
    assert response.get_json()["success"] is True

    db_session.refresh(n1)
    db_session.refresh(n2)
    db_session.refresh(n3)
    assert n1.is_read is True
    assert n2.is_read is True
    assert n3.is_read is True
