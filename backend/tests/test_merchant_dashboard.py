"""Tests for merchant dashboard endpoints (/api/v1/merchant)."""
import uuid

from backend.app.extensions import db
from backend.app.models.payment import Payment
from backend.app.models.notification import Notification


def test_merchant_transactions_forbidden_for_diaspora(client, diaspora_headers):
    """Users with role='diaspora' receive 403 on merchant dashboard."""
    response = client.get("/api/v1/merchant/transactions", headers=diaspora_headers)
    assert response.status_code == 403
    res_data = response.get_json()
    assert res_data["success"] is False
    assert res_data["message"] == "Access restricted to merchant accounts."


def test_merchant_transactions_unauthenticated(client):
    """Accessing merchant dashboard without token returns 401."""
    response = client.get("/api/v1/merchant/transactions")
    assert response.status_code == 401


def test_merchant_transactions_success(client, merchant_headers, sample_payment):
    """Merchant sees payments directed at their business."""
    response = client.get("/api/v1/merchant/transactions", headers=merchant_headers)
    assert response.status_code == 200
    res_data = response.get_json()
    assert res_data["success"] is True
    assert isinstance(res_data["data"], list)
    assert len(res_data["data"]) == 1
    assert res_data["data"][0]["transaction_id"] == sample_payment.payment_id
    assert res_data["data"][0]["amount"] == 50000.00
    assert res_data["data"][0]["status"] == "COMPLETED"


def test_merchant_transactions_redeemed_status(
    client, merchant_headers, sample_voucher, diaspora_headers
):
    """Transaction status updates to REDEEMED when voucher is redeemed."""
    voucher_code = sample_voucher.voucher_code
    client.patch(f"/api/v1/vouchers/{voucher_code}/redeem", headers=diaspora_headers)

    response = client.get("/api/v1/merchant/transactions", headers=merchant_headers)
    assert response.status_code == 200
    res_data = response.get_json()
    assert res_data["success"] is True
    assert res_data["data"][0]["status"] == "REDEEMED"


def test_accept_payment_success(
    client, merchant_headers, db_session, diaspora_user, sample_merchant
):
    """Merchant can accept an AwaitingAcceptance payment; user is notified."""
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

    response = client.patch(
        f"/api/v1/merchant/payments/{payment.payment_id}/accept",
        headers=merchant_headers,
    )
    assert response.status_code == 200
    res_data = response.get_json()
    assert res_data["success"] is True
    assert res_data["data"]["status"] == "Accepted"

    db_session.refresh(payment)
    assert payment.payment_status == "Accepted"

    notes = db_session.execute(
        db.select(Notification).filter_by(
            user_id=diaspora_user.user_id, title="Payment Accepted"
        )
    ).scalars().all()
    assert len(notes) == 1


def test_deny_payment_success(
    client, merchant_headers, db_session, diaspora_user, sample_merchant
):
    """Merchant can deny an AwaitingAcceptance payment; user is notified."""
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

    response = client.patch(
        f"/api/v1/merchant/payments/{payment.payment_id}/deny",
        headers=merchant_headers,
    )
    assert response.status_code == 200
    res_data = response.get_json()
    assert res_data["success"] is True
    assert res_data["data"]["status"] == "Denied"

    db_session.refresh(payment)
    assert payment.payment_status == "Denied"

    notes = db_session.execute(
        db.select(Notification).filter_by(
            user_id=diaspora_user.user_id, title="Payment Denied"
        )
    ).scalars().all()
    assert len(notes) == 1


def test_accept_payment_wrong_status(
    client, merchant_headers, db_session, diaspora_user, sample_merchant
):
    """Cannot accept a payment that is not AwaitingAcceptance."""
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

    response = client.patch(
        f"/api/v1/merchant/payments/{payment.payment_id}/accept",
        headers=merchant_headers,
    )
    assert response.status_code == 400


def test_accept_payment_not_found(
    client, merchant_headers, db_session, diaspora_user, sample_merchant
):
    """Accepting a non-existent payment UUID returns 404 (merchant is verified)."""
    response = client.patch(
        f"/api/v1/merchant/payments/{uuid.uuid4()}/accept",
        headers=merchant_headers,
    )
    assert response.status_code == 404


def test_accept_payment_forbidden_for_diaspora(
    client, diaspora_headers, sample_payment
):
    """Diaspora users cannot accept payments."""
    response = client.patch(
        f"/api/v1/merchant/payments/{sample_payment.payment_id}/accept",
        headers=diaspora_headers,
    )
    assert response.status_code == 403
