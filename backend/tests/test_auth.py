"""Tests for authentication endpoints (/api/v1/auth/register and /api/v1/auth/login)."""

def test_register_success(client):
    """Test successful user registration with default 'diaspora' role."""
    payload = {
        "full_name": "Chifundo Phiri",
        "email": "chifundo@example.com",
        "password": "Password123!",
        "country": "South Africa"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    res_data = response.get_json()
    assert res_data["success"] is True
    assert res_data["message"] == "Account created successfully."
    assert "user_id" in res_data["data"]
    assert res_data["data"]["role"] == "diaspora"


def test_register_merchant_role(client):
    """Test user registration with explicit 'merchant' role."""
    payload = {
        "full_name": "Merchant Store Owner",
        "email": "owner@store.mw",
        "password": "SecurePassword123!",
        "role": "merchant",
        "country": "Malawi"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    res_data = response.get_json()
    assert res_data["success"] is True
    assert res_data["data"]["role"] == "merchant"


def test_register_duplicate_email(client, diaspora_user):
    """Test registration failure when email already exists."""
    payload = {
        "full_name": "John Banda Copy",
        "email": diaspora_user.email,
        "password": "Password123!",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    res_data = response.get_json()
    assert res_data["success"] is False
    assert res_data["reason"] == "EMAIL_ALREADY_EXISTS"


def test_register_missing_fields(client):
    """Test registration with missing required fields."""
    response = client.post("/api/v1/auth/register", json={})
    assert response.status_code == 400
    res_data = response.get_json()
    assert res_data["success"] is False
    assert res_data["reason"] == "INVALID_INPUT"


def test_register_invalid_email(client):
    """Test registration with invalid email format."""
    payload = {
        "full_name": "Test User",
        "email": "not-an-email",
        "password": "Password123!",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    res_data = response.get_json()
    assert res_data["success"] is False


def test_register_short_password(client):
    """Test registration with password shorter than min length."""
    payload = {
        "full_name": "Test User",
        "email": "test@example.com",
        "password": "123",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    res_data = response.get_json()
    assert res_data["success"] is False


def test_login_success(client, diaspora_user):
    """Test successful login returning JWT token."""
    payload = {
        "email": diaspora_user.email,
        "password": "Password123!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    res_data = response.get_json()
    assert res_data["success"] is True
    assert res_data["message"] == "Login successful."
    assert "token" in res_data["data"]
    assert isinstance(res_data["data"]["token"], str)


def test_login_wrong_password(client, diaspora_user):
    """Test login failure with incorrect password."""
    payload = {
        "email": diaspora_user.email,
        "password": "WrongPassword!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    res_data = response.get_json()
    assert res_data["success"] is False
    assert res_data["reason"] == "INVALID_CREDENTIALS"


def test_login_non_existent_email(client):
    """Test login failure with unregistered email."""
    payload = {
        "email": "nobody@example.com",
        "password": "Password123!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    res_data = response.get_json()
    assert res_data["success"] is False
    assert res_data["reason"] == "INVALID_CREDENTIALS"


def test_login_invalid_payload(client):
    """Test login with missing fields."""
    response = client.post("/api/v1/auth/login", json={})
    assert response.status_code == 400
    res_data = response.get_json()
    assert res_data["success"] is False
    assert res_data["reason"] == "INVALID_INPUT"
