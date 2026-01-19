"""Tests for user management endpoints."""

from fastapi.testclient import TestClient


def test_get_current_user(
    client: TestClient, test_user_data: dict[str, str], test_user_token: str
) -> None:
    """Test getting current user profile."""
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["full_name"] == test_user_data["full_name"]
    assert "id" in data
    assert "hashed_password" not in data


def test_update_user_profile(
    client: TestClient, test_user_token: str
) -> None:
    """Test updating user profile."""
    response = client.patch(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={"full_name": "Updated Name"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"


def test_update_user_password(
    client: TestClient, test_user_data: dict[str, str], test_user_token: str
) -> None:
    """Test updating user password."""
    new_password = "newpassword123"

    # Update password
    response = client.patch(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={"password": new_password},
    )

    assert response.status_code == 200

    # Login with new password
    response = client.post(
        "/api/v1/auth/signin",
        json={
            "email": test_user_data["email"],
            "password": new_password,
        },
    )

    assert response.status_code == 200


def test_delete_user_account(
    client: TestClient, test_user_data: dict[str, str], test_user_token: str
) -> None:
    """Test deleting user account."""
    # Delete account
    response = client.delete(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )

    assert response.status_code == 204

    # Try to login with deleted account
    response = client.post(
        "/api/v1/auth/signin",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        },
    )

    assert response.status_code == 401


def test_health_check(client: TestClient) -> None:
    """Test health check endpoint."""
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


