"""Tests for merchant endpoints (/api/v1/merchants)."""
import uuid


def test_get_merchants_list_success(client, diaspora_headers, sample_merchant, unverified_merchant):
    """Test getting all verified merchants."""
    response = client.get("/api/v1/merchants", headers=diaspora_headers)
    assert response.status_code == 200
    res_data = response.get_json()
    assert res_data["success"] is True
    assert isinstance(res_data["data"], list)

    merchant_ids = [m["merchant_id"] for m in res_data["data"]]
    assert sample_merchant["merchant"].merchant_id in merchant_ids
    assert unverified_merchant["merchant"].merchant_id not in merchant_ids


def test_get_merchants_unauthorized(client):
    """Test getting merchants without token."""
    response = client.get("/api/v1/merchants")
    assert response.status_code == 401


def test_get_merchant_detail_success(client, diaspora_headers, sample_merchant):
    """Test getting specific merchant details with services."""
    merchant_id = sample_merchant["merchant"].merchant_id
    response = client.get(f"/api/v1/merchants/{merchant_id}", headers=diaspora_headers)
    assert response.status_code == 200
    res_data = response.get_json()
    assert res_data["success"] is True
    assert res_data["data"]["merchant_id"] == merchant_id
    assert res_data["data"]["business_name"] == "Chipiku Plus"
    assert "services" in res_data["data"]
    assert len(res_data["data"]["services"]) > 0


def test_get_merchant_detail_invalid_uuid(client, diaspora_headers):
    """Test getting merchant with malformed UUID string."""
    response = client.get("/api/v1/merchants/invalid-uuid-123", headers=diaspora_headers)
    assert response.status_code == 400
    res_data = response.get_json()
    assert res_data["success"] is False
    assert res_data["reason"] == "INVALID_INPUT"


def test_get_merchant_detail_not_found(client, diaspora_headers):
    """Test getting merchant with valid non-existent UUID."""
    random_uuid = str(uuid.uuid4())
    response = client.get(f"/api/v1/merchants/{random_uuid}", headers=diaspora_headers)
    assert response.status_code == 404
    res_data = response.get_json()
    assert res_data["success"] is False


def test_get_merchant_detail_unverified(client, diaspora_headers, unverified_merchant):
    """Test getting an unverified merchant returns 404."""
    merchant_id = unverified_merchant["merchant"].merchant_id
    response = client.get(f"/api/v1/merchants/{merchant_id}", headers=diaspora_headers)
    assert response.status_code == 404


def test_get_merchant_services_success(client, diaspora_headers, sample_merchant):
    """Test getting services for a valid verified merchant."""
    merchant_id = sample_merchant["merchant"].merchant_id
    response = client.get(f"/api/v1/merchants/{merchant_id}/services", headers=diaspora_headers)
    assert response.status_code == 200
    res_data = response.get_json()
    assert res_data["success"] is True
    assert isinstance(res_data["data"], list)
    assert len(res_data["data"]) == 1
    assert res_data["data"][0]["name"] == "Grocery Package"
    assert res_data["data"][0]["amount"] == 50000.00


def test_get_merchant_services_invalid_uuid(client, diaspora_headers):
    """Test getting services with malformed UUID."""
    response = client.get("/api/v1/merchants/not-a-uuid/services", headers=diaspora_headers)
    assert response.status_code == 400


def test_get_merchant_services_not_found(client, diaspora_headers):
    """Test getting services for non-existent merchant."""
    random_uuid = str(uuid.uuid4())
    response = client.get(f"/api/v1/merchants/{random_uuid}/services", headers=diaspora_headers)
    assert response.status_code == 404
