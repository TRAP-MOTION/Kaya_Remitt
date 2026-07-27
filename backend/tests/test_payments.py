"""Tests for payment endpoints (/api/v1/payments)."""
import uuid
from unittest.mock import patch

from backend.app.extensions import db
from backend.app.models.payment import Payment
from backend.app.models.notification import Notification


def test_create_payment_success(
    client, diaspora_headers, sample_merchant, db_session, diaspora_user, merchant_user
):
    """Payment creation leaves status AwaitingAcceptance and notifies both parties."""
    merchant = sample_merchant["merchant"]
    service = sample_merchant["service"]

    payload = {
        "merchant_id": merchant.merchant_id,
        "service_id": service.service_id,
        "beneficiary_name": "Mary Banda",
        "amount": 50000.00,
    }

    response = client.post("/api/v1/payments", json=payload, headers=diaspora_headers)

    assert response.status_code == 201
    res_data = response.get_json()
    assert res_data["success"] is True
    assert res_data["message"] == "Payment created successfully."
    assert "payment_id" in res_data["data"]
    assert res_data["data"]["status"] == "AwaitingAcceptance"
    assert "checkout_url" not in res_data["data"]

    diaspora_notes = db_session.execute(
        db.select(Notification).filter_by(
            user_id=diaspora_user.user_id, category="Payment"
        )
    ).scalars().all()
    assert any(n.title == "Payment Requested" for n in diaspora_notes)

    merchant_notes = db_session.execute(
        db.select(Notification).filter_by(
            user_id=merchant_user.user_id, category="Payment"
        )
    ).scalars().all()
    assert any(n.title == "New Payment Request" for n in merchant_notes)


def test_checkout_requires_accepted(
    client, diaspora_headers, db_session, diaspora_user, sample_merchant
):
    """Checkout is blocked while payment is still AwaitingAcceptance."""
    merchant = sample_merchant["merchant"]
    service = sample_merchant["service"]
    payment = Payment(
        user_id=diaspora_user.user_id,
        merchant_id=merchant.merchant_id,
        service_id=service.service_id,
        beneficiary_name="Mary Banda",
        amount=50000.00,
        payment_status="AwaitingAcceptance",
    )
    db_session.add(payment)
    db_session.commit()

    response = client.post(
        f"/api/v1/payments/{payment.payment_id}/checkout",
        headers=diaspora_headers,
    )
    assert response.status_code == 400
    assert "awaiting merchant approval" in response.get_json()["message"].lower()


def test_checkout_accepted_success(
    client, diaspora_headers, db_session, diaspora_user, sample_merchant
):
    """Accepted payment can start PayChangu checkout and moves to Pending."""
    merchant = sample_merchant["merchant"]
    service = sample_merchant["service"]
    payment = Payment(
        user_id=diaspora_user.user_id,
        merchant_id=merchant.merchant_id,
        service_id=service.service_id,
        beneficiary_name="Mary Banda",
        amount=50000.00,
        payment_status="Accepted",
    )
    db_session.add(payment)
    db_session.commit()

    checkout_url = "https://checkout.paychangu.com/test-session"
    with patch(
        "backend.app.routes.payments.initiate_checkout",
        return_value=checkout_url,
    ):
        response = client.post(
            f"/api/v1/payments/{payment.payment_id}/checkout",
            headers=diaspora_headers,
        )

    assert response.status_code == 200
    res_data = response.get_json()
    assert res_data["success"] is True
    assert res_data["data"]["status"] == "Pending"
    assert res_data["data"]["checkout_url"] == checkout_url

    db_session.refresh(payment)
    assert payment.payment_status == "Pending"


def test_checkout_denied_blocked(
    client, diaspora_headers, db_session, diaspora_user, sample_merchant
):
    """Denied payments cannot be checked out."""
    merchant = sample_merchant["merchant"]
    service = sample_merchant["service"]
    payment = Payment(
        user_id=diaspora_user.user_id,
        merchant_id=merchant.merchant_id,
        service_id=service.service_id,
        beneficiary_name="Mary Banda",
        amount=50000.00,
        payment_status="Denied",
    )
    db_session.add(payment)
    db_session.commit()

    response = client.post(
        f"/api/v1/payments/{payment.payment_id}/checkout",
        headers=diaspora_headers,
    )
    assert response.status_code == 400
    assert "denied" in response.get_json()["message"].lower()


def test_checkout_paychangu_failure(
    client, diaspora_headers, db_session, diaspora_user, sample_merchant
):
    """Checkout returns 502 when PayChangu initiate fails."""
    from backend.app.utils.payments_paychangu import PayChanguError

    merchant = sample_merchant["merchant"]
    service = sample_merchant["service"]
    payment = Payment(
        user_id=diaspora_user.user_id,
        merchant_id=merchant.merchant_id,
        service_id=service.service_id,
        beneficiary_name="Mary Banda",
        amount=50000.00,
        payment_status="Accepted",
    )
    db_session.add(payment)
    db_session.commit()

    with patch(
        "backend.app.routes.payments.initiate_checkout",
        side_effect=PayChanguError("Failed to initiate PayChangu checkout: boom"),
    ):
        response = client.post(
            f"/api/v1/payments/{payment.payment_id}/checkout",
            headers=diaspora_headers,
        )

    assert response.status_code == 502
    assert response.get_json()["success"] is False


def test_create_payment_unauthenticated(client, sample_merchant):
    """Test creating payment without authentication header."""
    merchant = sample_merchant["merchant"]
    service = sample_merchant["service"]

    payload = {
        "merchant_id": merchant.merchant_id,
        "service_id": service.service_id,
        "beneficiary_name": "Mary Banda",
        "amount": 50000.00,
    }
    response = client.post("/api/v1/payments", json=payload)
    assert response.status_code == 401


def test_create_payment_non_existent_merchant(client, diaspora_headers, sample_merchant):
    """Test creating payment with non-existent merchant ID."""
    random_uuid = str(uuid.uuid4())
    service = sample_merchant["service"]

    payload = {
        "merchant_id": random_uuid,
        "service_id": service.service_id,
        "beneficiary_name": "Mary Banda",
        "amount": 50000.00,
    }
    response = client.post("/api/v1/payments", json=payload, headers=diaspora_headers)
    assert response.status_code == 404
    res_data = response.get_json()
    assert res_data["success"] is False


def test_create_payment_unverified_merchant(client, diaspora_headers, unverified_merchant):
    """Test creating payment for an unverified merchant returns 404."""
    merchant = unverified_merchant["merchant"]
    service = unverified_merchant["service"]

    payload = {
        "merchant_id": merchant.merchant_id,
        "service_id": service.service_id,
        "beneficiary_name": "Mary Banda",
        "amount": 150000.00,
    }
    response = client.post("/api/v1/payments", json=payload, headers=diaspora_headers)
    assert response.status_code == 404


def test_create_payment_invalid_service(client, diaspora_headers, sample_merchant):
    """Test creating payment with non-existent service ID for merchant."""
    merchant = sample_merchant["merchant"]
    random_service_id = str(uuid.uuid4())

    payload = {
        "merchant_id": merchant.merchant_id,
        "service_id": random_service_id,
        "beneficiary_name": "Mary Banda",
        "amount": 50000.00,
    }
    response = client.post("/api/v1/payments", json=payload, headers=diaspora_headers)
    assert response.status_code == 404


def test_create_payment_invalid_amount(client, diaspora_headers, sample_merchant):
    """Test creating payment with zero or negative amount."""
    merchant = sample_merchant["merchant"]
    service = sample_merchant["service"]

    payload = {
        "merchant_id": merchant.merchant_id,
        "service_id": service.service_id,
        "beneficiary_name": "Mary Banda",
        "amount": -50.00,
    }
    response = client.post("/api/v1/payments", json=payload, headers=diaspora_headers)
    assert response.status_code == 400
    res_data = response.get_json()
    assert res_data["success"] is False


def test_create_payment_missing_required_fields(client, diaspora_headers):
    """Test creating payment with missing required fields."""
    payload = {
        "merchant_id": str(uuid.uuid4()),
    }
    response = client.post("/api/v1/payments", json=payload, headers=diaspora_headers)
    assert response.status_code == 400


def test_get_payment_history_success(client, diaspora_headers, sample_payment):
    """Test retrieving payment history for user with payments."""
    response = client.get("/api/v1/payments/history", headers=diaspora_headers)
    assert response.status_code == 200
    res_data = response.get_json()
    assert res_data["success"] is True
    assert isinstance(res_data["data"], list)
    assert len(res_data["data"]) == 1
    assert res_data["data"][0]["payment_id"] == sample_payment.payment_id
    assert res_data["data"][0]["beneficiary_name"] == "Mary Banda"


def test_get_payment_history_empty(client, merchant_headers):
    """Test retrieving payment history for user with no payments."""
    response = client.get("/api/v1/payments/history", headers=merchant_headers)
    assert response.status_code == 200
    res_data = response.get_json()
    assert res_data["success"] is True
    assert res_data["data"] == []
