"""Test configuration and fixtures."""

from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base import Base, get_db
from app.main import app

# Test database URL (in-memory SQLite with StaticPool for thread safety)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite://"

# Create test engine with StaticPool to share the same in-memory DB across threads
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session factory
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    # Create tables
    Base.metadata.create_all(bind=test_engine)

    # Create session
    session = TestSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Create a test client with test database dependency override."""

    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def db_session(db: Session) -> Generator[Session, None, None]:
    """Alias for 'db' fixture — used by test_additional_tools.py."""
    yield db


@pytest.fixture(scope="function")
def test_user(db: Session):
    """Create and return a test User ORM object in the database."""
    from app.models.user import User
    from app.core.security import get_password_hash

    user = User(
        email="testuser@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_user_data() -> dict[str, str]:
    """Test user data fixture."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
    }


@pytest.fixture
def test_user_token(client: TestClient, test_user_data: dict[str, str]) -> str:
    """Create a test user and return authentication token."""
    # Register user
    resp = client.post("/api/v1/auth/signup", json=test_user_data)
    assert resp.status_code in (200, 201), f"Signup failed: {resp.text}"

    # Login to get token
    response = client.post(
        "/api/v1/auth/signin",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        },
    )
    assert response.status_code == 200, f"Signin failed: {response.text}"
    return response.json()["access_token"]
