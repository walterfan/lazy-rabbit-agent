"""Tests for authentication endpoints."""

from fastapi.testclient import TestClient


def test_signup_success(client: TestClient) -> None:
    """Test successful user registration."""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "newuser@example.com",
            "password": "securepassword123",
            "full_name": "New User",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["full_name"] == "New User"
    assert "id" in data["user"]
    assert "hashed_password" not in data["user"]
    assert data["message"] == "User created successfully"


def test_signup_duplicate_email(client: TestClient, test_user_data: dict[str, str]) -> None:
    """Test registration with duplicate email fails."""
    # First registration
    client.post("/api/v1/auth/signup", json=test_user_data)

    # Second registration with same email
    response = client.post("/api/v1/auth/signup", json=test_user_data)

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_signup_invalid_email(client: TestClient) -> None:
    """Test registration with invalid email format."""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "not-an-email",
            "password": "password123",
        },
    )

    assert response.status_code == 422


def test_signup_short_password(client: TestClient) -> None:
    """Test registration with password shorter than 8 characters."""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "user@example.com",
            "password": "short",
        },
    )

    assert response.status_code == 422


def test_signin_success(client: TestClient, test_user_data: dict[str, str]) -> None:
    """Test successful login."""
    # Register user first
    client.post("/api/v1/auth/signup", json=test_user_data)

    # Login
    response = client.post(
        "/api/v1/auth/signin",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == test_user_data["email"]


def test_signin_wrong_password(client: TestClient, test_user_data: dict[str, str]) -> None:
    """Test login with incorrect password."""
    # Register user first
    client.post("/api/v1/auth/signup", json=test_user_data)

    # Login with wrong password
    response = client.post(
        "/api/v1/auth/signin",
        json={
            "email": test_user_data["email"],
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_signin_nonexistent_user(client: TestClient) -> None:
    """Test login with non-existent email."""
    response = client.post(
        "/api/v1/auth/signin",
        json={
            "email": "nonexistent@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_protected_endpoint_without_token(client: TestClient) -> None:
    """Test accessing protected endpoint without authentication."""
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401


def test_protected_endpoint_with_invalid_token(client: TestClient) -> None:
    """Test accessing protected endpoint with invalid token."""
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


