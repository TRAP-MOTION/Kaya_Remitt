"""Tests for digital voucher endpoints (/api/v1/vouchers)."""
import uuid


def test_generate_voucher_success(client, diaspora_headers, sample_payment):
    """Test generating a digital voucher after a completed payment."""
    payload = {"payment_id": sample_payment.payment_id}
    response = client.post("/api/v1/vouchers", json=payload, headers=diaspora_headers)
    assert response.status_code == 201
    res_data = response.get_json()
    assert res_data["success"] is True
    assert "voucher_id" in res_data["data"]
    assert res_data["data"]["status"] == "ACTIVE"
    assert res_data["data"]["merchant"] == "Chipiku Plus"
    assert res_data["data"]["amount"] == 50000.00


def test_generate_voucher_idempotent(client, diaspora_headers, sample_voucher, sample_payment):
    """Test idempotency when generating a voucher for a payment that already has one."""
    payload = {"payment_id": sample_payment.payment_id}
    response = client.post("/api/v1/vouchers", json=payload, headers=diaspora_headers)
    assert response.status_code == 200
    res_data = response.get_json()
    assert res_data["success"] is True
    assert res_data["data"]["voucher_id"] == sample_voucher.voucher_code


def test_generate_voucher_payment_not_found(client, diaspora_headers):
    """Test voucher generation with non-existent payment ID."""
    random_uuid = str(uuid.uuid4())
    payload = {"payment_id": random_uuid}
    response = client.post("/api/v1/vouchers", json=payload, headers=diaspora_headers)
    assert response.status_code == 404
    res_data = response.get_json()
    assert res_data["success"] is False


def test_verify_voucher_active(client, diaspora_headers, sample_voucher):
    """Test verifying an active voucher."""
    payload = {"voucher_id": sample_voucher.voucher_code}
    response = client.post("/api/v1/vouchers/verify", json=payload, headers=diaspora_headers)
    assert response.status_code == 200
    res_data = response.get_json()
    assert res_data["success"] is True
    assert res_data["message"] == "Voucher verified successfully."
    assert res_data["data"]["status"] == "VALID"
    assert res_data["data"]["amount"] == 50000.00
    assert res_data["data"]["merchant"] == "Chipiku Plus"


def test_verify_voucher_not_found(client, diaspora_headers):
    """Test verifying a non-existent voucher."""
    payload = {"voucher_id": "KAYA-NONEXISTENT"}
    response = client.post("/api/v1/vouchers/verify", json=payload, headers=diaspora_headers)
    assert response.status_code == 404


def test_redeem_voucher_success(client, diaspora_headers, sample_voucher):
    """Test redeeming an active voucher."""
    voucher_code = sample_voucher.voucher_code
    response = client.patch(f"/api/v1/vouchers/{voucher_code}/redeem", headers=diaspora_headers)
    assert response.status_code == 200
    res_data = response.get_json()
    assert res_data["success"] is True
    assert res_data["message"] == "Voucher redeemed successfully."
    assert res_data["data"]["status"] == "REDEEMED"


def test_verify_voucher_after_redemption(client, diaspora_headers, sample_voucher):
    """Test verifying a voucher that has already been redeemed."""
    voucher_code = sample_voucher.voucher_code

    # Redeem first
    client.patch(f"/api/v1/vouchers/{voucher_code}/redeem", headers=diaspora_headers)

    # Verify redeemed voucher
    payload = {"voucher_id": voucher_code}
    response = client.post("/api/v1/vouchers/verify", json=payload, headers=diaspora_headers)
    assert response.status_code == 400
    res_data = response.get_json()
    assert res_data["success"] is False
    assert res_data["message"] == "This voucher has already been redeemed."
    assert res_data["data"]["status"] == "REDEEMED"


def test_redeem_voucher_already_redeemed(client, diaspora_headers, sample_voucher):
    """Test redeeming an already redeemed voucher returns 400."""
    voucher_code = sample_voucher.voucher_code

    # Redeem twice
    client.patch(f"/api/v1/vouchers/{voucher_code}/redeem", headers=diaspora_headers)
    response = client.patch(f"/api/v1/vouchers/{voucher_code}/redeem", headers=diaspora_headers)
    assert response.status_code == 400
    res_data = response.get_json()
    assert res_data["success"] is False
    assert res_data["message"] == "This voucher has already been redeemed."


def test_redeem_voucher_not_found(client, diaspora_headers):
    """Test redeeming a non-existent voucher code."""
    response = client.patch("/api/v1/vouchers/KAYA-INVALID/redeem", headers=diaspora_headers)
    assert response.status_code == 404
