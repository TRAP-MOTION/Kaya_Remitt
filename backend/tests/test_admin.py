"""Tests for admin dashboard endpoints (/api/v1/admin)."""
import uuid


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


def test_admin_deactivate_and_activate_user(client, admin_headers, diaspora_user):
    deactivate = client.patch(
        f"/api/v1/admin/users/{diaspora_user.user_id}/deactivate",
        json={"reason": "Suspicious activity"},
        headers=admin_headers,
    )
    assert deactivate.status_code == 200
    assert deactivate.get_json()["data"]["account_status"] == "Inactive"

    login = client.post(
        "/api/v1/auth/login",
        json={"email": diaspora_user.email, "password": "Password123!"},
    )
    assert login.status_code == 403

    activate = client.patch(
        f"/api/v1/admin/users/{diaspora_user.user_id}/activate",
        json={"reason": "Issue resolved"},
        headers=admin_headers,
    )
    assert activate.status_code == 200
    assert activate.get_json()["data"]["account_status"] == "Active"


def test_admin_cannot_deactivate_self(client, admin_headers, admin_user):
    response = client.patch(
        f"/api/v1/admin/users/{admin_user.user_id}/deactivate",
        json={},
        headers=admin_headers,
    )
    assert response.status_code == 400


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
    assert create.get_json()["data"]["title"] == "Account Warning"

    listed = client.get("/api/v1/admin/warnings", headers=admin_headers)
    assert listed.status_code == 200
    assert len(listed.get_json()["data"]) == 1

    filtered = client.get(
        f"/api/v1/admin/warnings?user_id={diaspora_user.user_id}",
        headers=admin_headers,
    )
    assert filtered.status_code == 200
    assert len(filtered.get_json()["data"]) == 1


def test_admin_support_list_get_update(
    client, admin_headers, sample_support_ticket
):
    listed = client.get("/api/v1/admin/support", headers=admin_headers)
    assert listed.status_code == 200
    assert len(listed.get_json()["data"]) == 1

    detail = client.get(
        f"/api/v1/admin/support/{sample_support_ticket.ticket_id}",
        headers=admin_headers,
    )
    assert detail.status_code == 200
    assert detail.get_json()["data"]["subject"] == "Merchant refused voucher"

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


def test_admin_support_not_found(client, admin_headers):
    response = client.get(
        f"/api/v1/admin/support/{uuid.uuid4()}",
        headers=admin_headers,
    )
    assert response.status_code == 404
