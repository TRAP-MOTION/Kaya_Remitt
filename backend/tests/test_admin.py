"""Tests for admin dashboard endpoints (/api/v1/admin)."""
import uuid

from backend.app.models.users import User
from backend.app.models.support_ticket import SupportTicket


def test_admin_update_merchant_status(client, admin_headers, unverified_merchant):
    merchant = unverified_merchant["merchant"]
    response = client.patch(
        f"/api/v1/admin/merchants/{merchant.merchant_id}/status",
        json={"verification_status": "Verified", "reason": "Docs approved"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["verification_status"] == "Verified"
    assert data["data"]["business_name"] == "Pending Tech Store"
    assert "updated_at" in data["data"]


def test_admin_update_merchant_status_suspended(client, admin_headers, sample_merchant):
    merchant = sample_merchant["merchant"]
    response = client.patch(
        f"/api/v1/admin/merchants/{merchant.merchant_id}/status",
        json={"verification_status": "Suspended"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.get_json()["data"]["verification_status"] == "Suspended"


def test_admin_update_merchant_status_invalid_value(
    client, admin_headers, unverified_merchant
):
    merchant = unverified_merchant["merchant"]
    response = client.patch(
        f"/api/v1/admin/merchants/{merchant.merchant_id}/status",
        json={"verification_status": "Approved"},
        headers=admin_headers,
    )
    assert response.status_code == 400
    assert response.get_json()["success"] is False


def test_admin_update_merchant_status_not_found(client, admin_headers):
    response = client.patch(
        f"/api/v1/admin/merchants/{uuid.uuid4()}/status",
        json={"verification_status": "Verified"},
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_admin_update_merchant_status_unauthenticated(client, unverified_merchant):
    merchant = unverified_merchant["merchant"]
    response = client.patch(
        f"/api/v1/admin/merchants/{merchant.merchant_id}/status",
        json={"verification_status": "Verified"},
    )
    assert response.status_code == 401


def test_admin_update_merchant_status_forbidden_for_diaspora(
    client, diaspora_headers, unverified_merchant
):
    merchant = unverified_merchant["merchant"]
    response = client.patch(
        f"/api/v1/admin/merchants/{merchant.merchant_id}/status",
        json={"verification_status": "Verified"},
        headers=diaspora_headers,
    )
    assert response.status_code == 403
    assert response.get_json()["message"] == "Access restricted to admin accounts."


def test_admin_update_merchant_status_forbidden_for_merchant(
    client, merchant_headers, unverified_merchant
):
    merchant = unverified_merchant["merchant"]
    response = client.patch(
        f"/api/v1/admin/merchants/{merchant.merchant_id}/status",
        json={"verification_status": "Rejected"},
        headers=merchant_headers,
    )
    assert response.status_code == 403


def test_admin_deactivate_and_activate_user(client, admin_headers, diaspora_user):
    deactivate = client.patch(
        f"/api/v1/admin/users/{diaspora_user.user_id}/deactivate",
        json={"reason": "Suspicious activity"},
        headers=admin_headers,
    )
    assert deactivate.status_code == 200
    assert deactivate.get_json()["data"]["account_status"] == "Inactive"
    assert deactivate.get_json()["data"]["email"] == diaspora_user.email

    login = client.post(
        "/api/v1/auth/login",
        json={"email": diaspora_user.email, "password": "Password123!"},
    )
    assert login.status_code == 403
    assert login.get_json()["reason"] == "ACCOUNT_INACTIVE"

    activate = client.patch(
        f"/api/v1/admin/users/{diaspora_user.user_id}/activate",
        json={"reason": "Issue resolved"},
        headers=admin_headers,
    )
    assert activate.status_code == 200
    assert activate.get_json()["data"]["account_status"] == "Active"

    login_again = client.post(
        "/api/v1/auth/login",
        json={"email": diaspora_user.email, "password": "Password123!"},
    )
    assert login_again.status_code == 200


def test_admin_deactivated_user_token_rejected(
    client, admin_headers, diaspora_user, diaspora_headers
):
    client.patch(
        f"/api/v1/admin/users/{diaspora_user.user_id}/deactivate",
        json={},
        headers=admin_headers,
    )
    response = client.get("/api/v1/profile", headers=diaspora_headers)
    assert response.status_code == 403
    assert response.get_json()["reason"] == "ACCOUNT_INACTIVE"


def test_admin_cannot_deactivate_self(client, admin_headers, admin_user):
    response = client.patch(
        f"/api/v1/admin/users/{admin_user.user_id}/deactivate",
        json={},
        headers=admin_headers,
    )
    assert response.status_code == 400
    assert "own admin account" in response.get_json()["message"]


def test_admin_cannot_deactivate_another_admin(client, admin_headers, db_session):
    other_admin = User(
        full_name="Second Admin",
        email="admin2@kayaremit.test",
        role="admin",
        account_status="Active",
    )
    other_admin.set_password("AdminPass123!")
    db_session.add(other_admin)
    db_session.commit()

    response = client.patch(
        f"/api/v1/admin/users/{other_admin.user_id}/deactivate",
        json={"reason": "test"},
        headers=admin_headers,
    )
    assert response.status_code == 400
    assert "Admin accounts cannot be deactivated" in response.get_json()["message"]


def test_admin_deactivate_user_not_found(client, admin_headers):
    response = client.patch(
        f"/api/v1/admin/users/{uuid.uuid4()}/deactivate",
        json={},
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_admin_activate_user_not_found(client, admin_headers):
    response = client.patch(
        f"/api/v1/admin/users/{uuid.uuid4()}/activate",
        json={},
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_admin_send_and_list_warnings(client, admin_headers, diaspora_user):
    create = client.post(
        "/api/v1/admin/warnings",
        json={
            "user_id": diaspora_user.user_id,
            "title": "Account Warning",
            "message": "Please review your recent activity.",
        },
        headers=admin_headers,
    )
    assert create.status_code == 201
    body = create.get_json()
    assert body["success"] is True
    assert body["data"]["title"] == "Account Warning"
    assert body["data"]["user_id"] == diaspora_user.user_id
    assert body["data"]["is_read"] is False

    listed = client.get("/api/v1/admin/warnings", headers=admin_headers)
    assert listed.status_code == 200
    assert len(listed.get_json()["data"]) == 1

    filtered = client.get(
        f"/api/v1/admin/warnings?user_id={diaspora_user.user_id}",
        headers=admin_headers,
    )
    assert filtered.status_code == 200
    assert len(filtered.get_json()["data"]) == 1

    other_filter = client.get(
        f"/api/v1/admin/warnings?user_id={uuid.uuid4()}",
        headers=admin_headers,
    )
    assert other_filter.status_code == 200
    assert other_filter.get_json()["data"] == []


def test_admin_send_warning_user_not_found(client, admin_headers):
    response = client.post(
        "/api/v1/admin/warnings",
        json={
            "user_id": str(uuid.uuid4()),
            "title": "Warning",
            "message": "Hello",
        },
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_admin_send_warning_invalid_payload(client, admin_headers, diaspora_user):
    response = client.post(
        "/api/v1/admin/warnings",
        json={"user_id": diaspora_user.user_id, "title": "Only title"},
        headers=admin_headers,
    )
    assert response.status_code == 400


def test_admin_list_warnings_invalid_user_id_query(client, admin_headers):
    response = client.get(
        "/api/v1/admin/warnings?user_id=not-a-uuid",
        headers=admin_headers,
    )
    assert response.status_code == 400


def test_admin_send_warning_forbidden_for_diaspora(client, diaspora_headers, diaspora_user):
    response = client.post(
        "/api/v1/admin/warnings",
        json={
            "user_id": diaspora_user.user_id,
            "title": "Warning",
            "message": "Nope",
        },
        headers=diaspora_headers,
    )
    assert response.status_code == 403


def test_admin_support_list_get_update(client, admin_headers, sample_support_ticket):
    listed = client.get("/api/v1/admin/support", headers=admin_headers)
    assert listed.status_code == 200
    assert len(listed.get_json()["data"]) == 1
    assert listed.get_json()["data"][0]["status"] == "Open"

    detail = client.get(
        f"/api/v1/admin/support/{sample_support_ticket.ticket_id}",
        headers=admin_headers,
    )
    assert detail.status_code == 200
    detail_data = detail.get_json()["data"]
    assert detail_data["subject"] == "Merchant refused voucher"
    assert detail_data["description"]
    assert detail_data["admin_response"] is None

    updated = client.patch(
        f"/api/v1/admin/support/{sample_support_ticket.ticket_id}",
        json={
            "status": "Resolved",
            "admin_response": "Merchant confirmed the voucher.",
        },
        headers=admin_headers,
    )
    assert updated.status_code == 200
    body = updated.get_json()["data"]
    assert body["status"] == "Resolved"
    assert "confirmed" in body["admin_response"]
    assert "updated_at" in body


def test_admin_support_filter_by_status_and_category(
    client, admin_headers, db_session, diaspora_user, sample_support_ticket
):
    payment_ticket = SupportTicket(
        user_id=diaspora_user.user_id,
        category="Payment",
        subject="Payment stuck",
        description="Checkout completed but voucher failed.",
        status="In Progress",
    )
    db_session.add(payment_ticket)
    db_session.commit()

    by_status = client.get(
        "/api/v1/admin/support?status=Open",
        headers=admin_headers,
    )
    assert by_status.status_code == 200
    assert len(by_status.get_json()["data"]) == 1
    assert by_status.get_json()["data"][0]["ticket_id"] == sample_support_ticket.ticket_id

    by_category = client.get(
        "/api/v1/admin/support?category=Payment",
        headers=admin_headers,
    )
    assert by_category.status_code == 200
    assert len(by_category.get_json()["data"]) == 1
    assert by_category.get_json()["data"][0]["category"] == "Payment"

    by_user = client.get(
        f"/api/v1/admin/support?user_id={diaspora_user.user_id}",
        headers=admin_headers,
    )
    assert by_user.status_code == 200
    assert len(by_user.get_json()["data"]) == 2


def test_admin_support_invalid_status_filter(client, admin_headers):
    response = client.get(
        "/api/v1/admin/support?status=Waiting",
        headers=admin_headers,
    )
    assert response.status_code == 400


def test_admin_support_invalid_category_filter(client, admin_headers):
    response = client.get(
        "/api/v1/admin/support?category=Billing",
        headers=admin_headers,
    )
    assert response.status_code == 400


def test_admin_support_update_invalid_status(client, admin_headers, sample_support_ticket):
    response = client.patch(
        f"/api/v1/admin/support/{sample_support_ticket.ticket_id}",
        json={"status": "Done"},
        headers=admin_headers,
    )
    assert response.status_code == 400


def test_admin_support_not_found(client, admin_headers):
    response = client.get(
        f"/api/v1/admin/support/{uuid.uuid4()}",
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_admin_support_update_not_found(client, admin_headers):
    response = client.patch(
        f"/api/v1/admin/support/{uuid.uuid4()}",
        json={"status": "Closed"},
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_admin_support_forbidden_for_merchant(client, merchant_headers):
    response = client.get("/api/v1/admin/support", headers=merchant_headers)
    assert response.status_code == 403
