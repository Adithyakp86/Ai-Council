"""Integration tests for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db
from app.models.base import Base
from app.models.user import User

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after."""
    # Only create User table for auth tests (avoid Response table with JSONB)
    from app.models.user import User
    User.__table__.create(bind=engine, checkfirst=True)
    yield
    User.__table__.drop(bind=engine, checkfirst=True)


def test_register_new_user():
    """Test successful user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "SecurePass123",
            "name": "New User"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    
    assert "token" in data
    assert "user" in data
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["name"] == "New User"
    assert data["user"]["role"] == "admin"  # First user is admin


def test_register_duplicate_email():
    """Test that duplicate email registration fails."""
    # Register first user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "SecurePass123",
            "name": "First User"
        }
    )
    
    # Try to register with same email
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "DifferentPass456",
            "name": "Second User"
        }
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_register_weak_password():
    """Test that weak passwords are rejected."""
    # Too short
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user1@example.com",
            "password": "Short1",
            "name": "User One"
        }
    )
    assert response.status_code == 400
    assert "8 characters" in response.json()["detail"]
    
    # No uppercase
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user2@example.com",
            "password": "nouppercase123",
            "name": "User Two"
        }
    )
    assert response.status_code == 400
    assert "uppercase" in response.json()["detail"].lower()
    
    # No digit
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user3@example.com",
            "password": "NoDigitHere",
            "name": "User Three"
        }
    )
    assert response.status_code == 400
    assert "digit" in response.json()["detail"].lower()


def test_login_success():
    """Test successful login."""
    # Register user first
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "loginuser@example.com",
            "password": "LoginPass123",
            "name": "Login User"
        }
    )
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "loginuser@example.com",
            "password": "LoginPass123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "token" in data
    assert "user" in data
    assert data["user"]["email"] == "loginuser@example.com"


def test_login_invalid_email():
    """Test login with non-existent email."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "SomePass123"
        }
    )
    
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_login_invalid_password():
    """Test login with wrong password."""
    # Register user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrongpass@example.com",
            "password": "CorrectPass123",
            "name": "Wrong Pass User"
        }
    )
    
    # Try to login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrongpass@example.com",
            "password": "WrongPass456"
        }
    )
    
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_get_current_user():
    """Test getting current user information."""
    # Register and get token
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "currentuser@example.com",
            "password": "CurrentPass123",
            "name": "Current User"
        }
    )
    token = register_response.json()["token"]
    
    # Get current user info
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["email"] == "currentuser@example.com"
    assert data["name"] == "Current User"
    assert data["role"] == "admin"
    assert data["is_active"] is True
    assert "created_at" in data


def test_get_current_user_without_token():
    """Test that accessing /me without token fails."""
    response = client.get("/api/v1/auth/me")
    
    assert response.status_code == 401  # FastAPI HTTPBearer returns 401


def test_get_current_user_with_invalid_token():
    """Test that accessing /me with invalid token fails."""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    
    assert response.status_code == 401


def test_refresh_token():
    """Test token refresh endpoint."""
    # Register and get token
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "refreshuser@example.com",
            "password": "RefreshPass123",
            "name": "Refresh User"
        }
    )
    old_token = register_response.json()["token"]
    
    # Refresh token
    response = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {old_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 7 * 24 * 60 * 60  # 7 days in seconds
    # Token should be valid (may be same if called within same second)
    assert len(data["token"]) > 0


def test_refresh_token_without_auth():
    """Test that refresh endpoint requires authentication."""
    response = client.post("/api/v1/auth/refresh")
    
    assert response.status_code == 401


def test_logout():
    """Test logout endpoint."""
    # Register and get token
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "logoutuser@example.com",
            "password": "LogoutPass123",
            "name": "Logout User"
        }
    )
    token = register_response.json()["token"]
    
    # Logout
    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 204


def test_second_user_is_not_admin():
    """Test that second registered user gets 'user' role, not 'admin'."""
    # Register first user (will be admin)
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "firstuser@example.com",
            "password": "FirstPass123",
            "name": "First User"
        }
    )
    
    # Register second user
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "seconduser@example.com",
            "password": "SecondPass123",
            "name": "Second User"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["role"] == "user"  # Second user should not be admin
