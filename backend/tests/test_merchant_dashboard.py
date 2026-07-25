"""Tests for merchant dashboard endpoints (/api/v1/merchant/transactions)."""

def test_merchant_transactions_forbidden_for_diaspora(client, diaspora_headers):
    """Test that users with role='diaspora' receive 403 Forbidden on merchant dashboard."""
    response = client.get("/api/v1/merchant/transactions", headers=diaspora_headers)
    assert response.status_code == 403
    res_data = response.get_json()
    assert res_data["success"] is False
    assert res_data["message"] == "Access restricted to merchant accounts."


def test_merchant_transactions_unauthenticated(client):
    """Test accessing merchant dashboard without token."""
    response = client.get("/api/v1/merchant/transactions")
    assert response.status_code == 401


def test_merchant_transactions_success(client, merchant_headers, sample_payment):
    """Test user with role='merchant' getting transaction list."""
    response = client.get("/api/v1/merchant/transactions", headers=merchant_headers)
    assert response.status_code == 200
    res_data = response.get_json()
    assert res_data["success"] is True
    assert isinstance(res_data["data"], list)
    assert len(res_data["data"]) == 1
    assert res_data["data"][0]["transaction_id"] == sample_payment.payment_id
    assert res_data["data"][0]["amount"] == 50000.00
    assert res_data["data"][0]["status"] == "COMPLETED"


def test_merchant_transactions_redeemed_status(client, merchant_headers, sample_voucher, diaspora_headers):
    """Test that transaction status updates to 'REDEEMED' when voucher is redeemed."""
    voucher_code = sample_voucher.voucher_code

    # Redeem voucher
    client.patch(f"/api/v1/vouchers/{voucher_code}/redeem", headers=diaspora_headers)

    # Check merchant transactions
    response = client.get("/api/v1/merchant/transactions", headers=merchant_headers)
    assert response.status_code == 200
    res_data = response.get_json()
    assert res_data["success"] is True
    assert res_data["data"][0]["status"] == "REDEEMED"
