"""Tests for user profile endpoints (/api/v1/profile)."""

def test_get_profile_success(client, diaspora_user, diaspora_headers):
    """Test getting profile for an authenticated user."""
    response = client.get("/api/v1/profile", headers=diaspora_headers)
    assert response.status_code == 200
    res_data = response.get_json()
    assert res_data["success"] is True
    assert res_data["data"]["user_id"] == diaspora_user.user_id
    assert res_data["data"]["email"] == diaspora_user.email
    assert res_data["data"]["full_name"] == diaspora_user.full_name
    assert res_data["data"]["country"] == diaspora_user.country


def test_get_profile_unauthorized(client):
    """Test accessing profile without Authorization header."""
    response = client.get("/api/v1/profile")
    assert response.status_code == 401
    res_data = response.get_json()
    assert res_data["success"] is False
    assert res_data["reason"] == "UNAUTHORIZED"


def test_get_profile_invalid_token(client):
    """Test accessing profile with malformed token."""
    headers = {"Authorization": "Bearer invalid_token_value"}
    response = client.get("/api/v1/profile", headers=headers)
    assert response.status_code == 401
    res_data = response.get_json()
    assert res_data["success"] is False


def test_update_profile_success(client, diaspora_user, diaspora_headers):
    """Test successfully updating profile fields (full_name and country)."""
    payload = {
        "full_name": "John Banda Updated",
        "country": "Canada"
    }
    response = client.put("/api/v1/profile", json=payload, headers=diaspora_headers)
    assert response.status_code == 200
    res_data = response.get_json()
    assert res_data["success"] is True
    assert res_data["message"] == "Profile updated successfully."
    assert res_data["data"]["full_name"] == "John Banda Updated"
    assert res_data["data"]["country"] == "Canada"


def test_update_profile_empty_full_name(client, diaspora_headers):
    """Test profile update validation error when full_name is empty string."""
    payload = {
        "full_name": "   ",
    }
    response = client.put("/api/v1/profile", json=payload, headers=diaspora_headers)
    assert response.status_code == 400
    res_data = response.get_json()
    assert res_data["success"] is False
    assert res_data["reason"] == "INVALID_INPUT"
