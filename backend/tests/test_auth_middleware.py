"""Tests for authentication middleware."""

import pytest
from datetime import timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.middleware import get_current_user, get_current_admin_user, get_optional_user
from app.core.security import create_access_token
from app.models.user import User


class MockCredentials:
    """Mock HTTPAuthorizationCredentials for testing."""
    def __init__(self, token: str):
        self.credentials = token


@pytest.mark.asyncio
async def test_get_current_user_with_valid_token(test_db: Session, test_user: User):
    """Test get_current_user with a valid token."""
    # Create a valid token for the test user
    token = create_access_token(
        data={"sub": str(test_user.id)},
        expires_delta=timedelta(days=7)
    )
    
    credentials = MockCredentials(token)
    
    # Call the middleware
    user = await get_current_user(credentials, test_db)
    
    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email


@pytest.mark.asyncio
async def test_get_current_user_with_invalid_token(test_db: Session):
    """Test get_current_user with an invalid token."""
    credentials = MockCredentials("invalid_token")
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials, test_db)
    
    assert exc_info.value.status_code == 401
    assert "Invalid or expired token" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_with_expired_token(test_db: Session, test_user: User):
    """Test get_current_user with an expired token."""
    # Create an expired token (negative expiration)
    token = create_access_token(
        data={"sub": str(test_user.id)},
        expires_delta=timedelta(seconds=-1)
    )
    
    credentials = MockCredentials(token)
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials, test_db)
    
    assert exc_info.value.status_code == 401
    assert "Invalid or expired token" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_with_nonexistent_user(test_db: Session):
    """Test get_current_user with a token for a non-existent user."""
    # Create a token with a random UUID
    token = create_access_token(
        data={"sub": "00000000-0000-0000-0000-000000000000"},
        expires_delta=timedelta(days=7)
    )
    
    credentials = MockCredentials(token)
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials, test_db)
    
    assert exc_info.value.status_code == 401
    assert "User not found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_with_inactive_user(test_db: Session, test_user: User):
    """Test get_current_user with an inactive user."""
    # Deactivate the user
    test_user.is_active = False
    test_db.commit()
    
    token = create_access_token(
        data={"sub": str(test_user.id)},
        expires_delta=timedelta(days=7)
    )
    
    credentials = MockCredentials(token)
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials, test_db)
    
    assert exc_info.value.status_code == 403
    assert "User account is disabled" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_with_missing_user_id(test_db: Session):
    """Test get_current_user with a token missing user_id."""
    # Create a token without 'sub' field
    token = create_access_token(
        data={"other_field": "value"},
        expires_delta=timedelta(days=7)
    )
    
    credentials = MockCredentials(token)
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials, test_db)
    
    assert exc_info.value.status_code == 401
    assert "Invalid token payload" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_with_invalid_user_id_format(test_db: Session):
    """Test get_current_user with an invalid UUID format."""
    token = create_access_token(
        data={"sub": "not-a-valid-uuid"},
        expires_delta=timedelta(days=7)
    )
    
    credentials = MockCredentials(token)
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials, test_db)
    
    assert exc_info.value.status_code == 401
    assert "Invalid user ID in token" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_admin_user_with_admin(test_db: Session, test_admin: User):
    """Test get_current_admin_user with an admin user."""
    user = await get_current_admin_user(test_admin)
    
    assert user is not None
    assert user.id == test_admin.id
    assert user.role == "admin"


@pytest.mark.asyncio
async def test_get_current_admin_user_with_regular_user(test_db: Session, test_user: User):
    """Test get_current_admin_user with a regular user."""
    with pytest.raises(HTTPException) as exc_info:
        await get_current_admin_user(test_user)
    
    assert exc_info.value.status_code == 403
    assert "Admin access required" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_optional_user_with_valid_token(test_db: Session, test_user: User):
    """Test get_optional_user with a valid token."""
    token = create_access_token(
        data={"sub": str(test_user.id)},
        expires_delta=timedelta(days=7)
    )
    
    credentials = MockCredentials(token)
    
    user = await get_optional_user(credentials, test_db)
    
    assert user is not None
    assert user.id == test_user.id


@pytest.mark.asyncio
async def test_get_optional_user_with_no_token(test_db: Session):
    """Test get_optional_user with no token."""
    user = await get_optional_user(None, test_db)
    
    assert user is None


@pytest.mark.asyncio
async def test_get_optional_user_with_invalid_token(test_db: Session):
    """Test get_optional_user with an invalid token."""
    credentials = MockCredentials("invalid_token")
    
    user = await get_optional_user(credentials, test_db)
    
    assert user is None
