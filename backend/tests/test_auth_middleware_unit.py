"""Unit tests for authentication middleware without database dependencies."""

import pytest
from datetime import timedelta
from unittest.mock import Mock, patch
from fastapi import HTTPException
from uuid import uuid4

from app.core.middleware import get_current_user, get_current_admin_user
from app.core.security import create_access_token


class MockCredentials:
    """Mock HTTPAuthorizationCredentials for testing."""
    def __init__(self, token: str):
        self.credentials = token


class MockUser:
    """Mock User model for testing."""
    def __init__(self, id, email, name, role, is_active=True):
        self.id = id
        self.email = email
        self.name = name
        self.role = role
        self.is_active = is_active


@pytest.mark.asyncio
async def test_get_current_user_with_valid_token():
    """Test get_current_user with a valid token."""
    user_id = uuid4()
    mock_user = MockUser(
        id=user_id,
        email="test@example.com",
        name="Test User",
        role="user"
    )
    
    # Create a valid token
    token = create_access_token(
        data={"sub": str(user_id)},
        expires_delta=timedelta(days=7)
    )
    
    credentials = MockCredentials(token)
    
    # Mock the database query
    mock_db = Mock()
    mock_query = Mock()
    mock_filter = Mock()
    mock_filter.first.return_value = mock_user
    mock_query.filter.return_value = mock_filter
    mock_db.query.return_value = mock_query
    
    # Call the middleware
    user = await get_current_user(credentials, mock_db)
    
    assert user is not None
    assert user.id == user_id
    assert user.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_current_user_with_invalid_token():
    """Test get_current_user with an invalid token."""
    credentials = MockCredentials("invalid_token")
    mock_db = Mock()
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials, mock_db)
    
    assert exc_info.value.status_code == 401
    assert "Invalid or expired token" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_with_expired_token():
    """Test get_current_user with an expired token."""
    user_id = uuid4()
    
    # Create an expired token (negative expiration)
    token = create_access_token(
        data={"sub": str(user_id)},
        expires_delta=timedelta(seconds=-1)
    )
    
    credentials = MockCredentials(token)
    mock_db = Mock()
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials, mock_db)
    
    assert exc_info.value.status_code == 401
    assert "Invalid or expired token" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_with_nonexistent_user():
    """Test get_current_user with a token for a non-existent user."""
    user_id = uuid4()
    
    # Create a token
    token = create_access_token(
        data={"sub": str(user_id)},
        expires_delta=timedelta(days=7)
    )
    
    credentials = MockCredentials(token)
    
    # Mock the database query to return None (user not found)
    mock_db = Mock()
    mock_query = Mock()
    mock_filter = Mock()
    mock_filter.first.return_value = None
    mock_query.filter.return_value = mock_filter
    mock_db.query.return_value = mock_query
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials, mock_db)
    
    assert exc_info.value.status_code == 401
    assert "User not found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_with_inactive_user():
    """Test get_current_user with an inactive user."""
    user_id = uuid4()
    mock_user = MockUser(
        id=user_id,
        email="test@example.com",
        name="Test User",
        role="user",
        is_active=False
    )
    
    token = create_access_token(
        data={"sub": str(user_id)},
        expires_delta=timedelta(days=7)
    )
    
    credentials = MockCredentials(token)
    
    # Mock the database query
    mock_db = Mock()
    mock_query = Mock()
    mock_filter = Mock()
    mock_filter.first.return_value = mock_user
    mock_query.filter.return_value = mock_filter
    mock_db.query.return_value = mock_query
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials, mock_db)
    
    assert exc_info.value.status_code == 403
    assert "User account is disabled" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_with_missing_user_id():
    """Test get_current_user with a token missing user_id."""
    # Create a token without 'sub' field
    token = create_access_token(
        data={"other_field": "value"},
        expires_delta=timedelta(days=7)
    )
    
    credentials = MockCredentials(token)
    mock_db = Mock()
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials, mock_db)
    
    assert exc_info.value.status_code == 401
    assert "Invalid token payload" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_with_invalid_user_id_format():
    """Test get_current_user with an invalid UUID format."""
    token = create_access_token(
        data={"sub": "not-a-valid-uuid"},
        expires_delta=timedelta(days=7)
    )
    
    credentials = MockCredentials(token)
    mock_db = Mock()
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials, mock_db)
    
    assert exc_info.value.status_code == 401
    assert "Invalid user ID in token" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_admin_user_with_admin():
    """Test get_current_admin_user with an admin user."""
    user_id = uuid4()
    mock_admin = MockUser(
        id=user_id,
        email="admin@example.com",
        name="Admin User",
        role="admin"
    )
    
    user = await get_current_admin_user(mock_admin)
    
    assert user is not None
    assert user.id == user_id
    assert user.role == "admin"


@pytest.mark.asyncio
async def test_get_current_admin_user_with_regular_user():
    """Test get_current_admin_user with a regular user."""
    user_id = uuid4()
    mock_user = MockUser(
        id=user_id,
        email="user@example.com",
        name="Regular User",
        role="user"
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_admin_user(mock_user)
    
    assert exc_info.value.status_code == 403
    assert "Admin access required" in exc_info.value.detail


def test_middleware_module_exports():
    """Test that the middleware module exports the expected functions."""
    from app.core import middleware
    
    assert hasattr(middleware, 'get_current_user')
    assert hasattr(middleware, 'get_current_active_user')
    assert hasattr(middleware, 'get_current_admin_user')
    assert hasattr(middleware, 'get_optional_user')
    assert hasattr(middleware, 'security')
