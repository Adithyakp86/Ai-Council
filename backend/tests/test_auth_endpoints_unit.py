"""Unit tests for authentication endpoints.

These tests focus on endpoint logic with mocked dependencies,
unlike test_auth_endpoints.py which contains integration tests.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
from datetime import datetime, timezone
import uuid

from app.api.auth import (
    register,
    login,
    UserRegister,
    UserLogin,
)
from app.models.user import User


class TestRegisterEndpoint:
    """Unit tests for the register endpoint."""
    
    @pytest.mark.asyncio
    async def test_successful_registration_creates_user(self):
        """Test that successful registration creates a user and returns token."""
        # Arrange
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None  # No existing user
        mock_db.query.return_value.count.return_value = 0  # First user (admin)
        
        user_data = UserRegister(
            email="newuser@example.com",
            password="SecurePass123",
            name="New User"
        )
        
        # Mock the created user
        mock_user = User(
            id=uuid.uuid4(),
            email="newuser@example.com",
            password_hash="hashed_password",
            name="New User",
            role="admin",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        with patch('app.api.auth.hash_password', return_value="hashed_password"), \
             patch('app.api.auth.validate_password_strength', return_value=(True, "")), \
             patch('app.api.auth.create_access_token', return_value="test_token_123"):
            
            # Mock db.refresh to set the user attributes
            def mock_refresh(user):
                user.id = mock_user.id
                user.email = mock_user.email
                user.name = mock_user.name
                user.role = mock_user.role
            
            mock_db.refresh = mock_refresh
            
            # Act
            result = await register(user_data, mock_db)
            
            # Assert
            assert "token" in result
            assert "user" in result
            assert result["token"] == "test_token_123"
            assert result["user"]["email"] == "newuser@example.com"
            assert result["user"]["name"] == "New User"
            assert result["user"]["role"] == "admin"
            
            # Verify user was added to database
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_duplicate_email_registration_fails(self):
        """Test that registering with an existing email fails."""
        # Arrange
        mock_db = Mock()
        existing_user = User(
            id=uuid.uuid4(),
            email="existing@example.com",
            password_hash="hashed",
            name="Existing User",
            role="user",
            is_active=True
        )
        mock_db.query.return_value.filter.return_value.first.return_value = existing_user
        
        user_data = UserRegister(
            email="existing@example.com",
            password="SecurePass123",
            name="New User"
        )
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await register(user_data, mock_db)
        
        assert exc_info.value.status_code == 400
        assert "already registered" in exc_info.value.detail.lower()
        
        # Verify no user was added
        mock_db.add.assert_not_called()
        mock_db.commit.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_weak_password_registration_fails(self):
        """Test that registration with weak password fails."""
        # Arrange
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        user_data = UserRegister(
            email="newuser@example.com",
            password="weak",
            name="New User"
        )
        
        with patch('app.api.auth.validate_password_strength', 
                   return_value=(False, "Password must be at least 8 characters long")):
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await register(user_data, mock_db)
            
            assert exc_info.value.status_code == 400
            assert "8 characters" in exc_info.value.detail
            
            # Verify no user was added
            mock_db.add.assert_not_called()
            mock_db.commit.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_second_user_gets_user_role(self):
        """Test that second registered user gets 'user' role, not 'admin'."""
        # Arrange
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.query.return_value.count.return_value = 1  # Already one user exists
        
        user_data = UserRegister(
            email="seconduser@example.com",
            password="SecurePass123",
            name="Second User"
        )
        
        mock_user = User(
            id=uuid.uuid4(),
            email="seconduser@example.com",
            password_hash="hashed_password",
            name="Second User",
            role="user",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        with patch('app.api.auth.hash_password', return_value="hashed_password"), \
             patch('app.api.auth.validate_password_strength', return_value=(True, "")), \
             patch('app.api.auth.create_access_token', return_value="test_token_456"):
            
            def mock_refresh(user):
                user.id = mock_user.id
                user.email = mock_user.email
                user.name = mock_user.name
                user.role = mock_user.role
            
            mock_db.refresh = mock_refresh
            
            # Act
            result = await register(user_data, mock_db)
            
            # Assert
            assert result["user"]["role"] == "user"


class TestLoginEndpoint:
    """Unit tests for the login endpoint."""
    
    @pytest.mark.asyncio
    async def test_successful_login_returns_token(self):
        """Test that successful login returns a valid token."""
        # Arrange
        mock_db = Mock()
        mock_user = User(
            id=uuid.uuid4(),
            email="loginuser@example.com",
            password_hash="hashed_password",
            name="Login User",
            role="user",
            is_active=True
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        credentials = UserLogin(
            email="loginuser@example.com",
            password="CorrectPass123"
        )
        
        with patch('app.api.auth.verify_password', return_value=True), \
             patch('app.api.auth.create_access_token', return_value="login_token_789"):
            
            # Act
            result = await login(credentials, mock_db)
            
            # Assert
            assert "token" in result
            assert "user" in result
            assert result["token"] == "login_token_789"
            assert result["user"]["email"] == "loginuser@example.com"
            assert result["user"]["name"] == "Login User"
    
    @pytest.mark.asyncio
    async def test_login_with_nonexistent_email_fails(self):
        """Test that login with non-existent email fails."""
        # Arrange
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        credentials = UserLogin(
            email="nonexistent@example.com",
            password="SomePass123"
        )
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await login(credentials, mock_db)
        
        assert exc_info.value.status_code == 401
        assert "invalid" in exc_info.value.detail.lower()
    
    @pytest.mark.asyncio
    async def test_login_with_invalid_password_fails(self):
        """Test that login with wrong password fails."""
        # Arrange
        mock_db = Mock()
        mock_user = User(
            id=uuid.uuid4(),
            email="user@example.com",
            password_hash="hashed_password",
            name="User",
            role="user",
            is_active=True
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        credentials = UserLogin(
            email="user@example.com",
            password="WrongPassword123"
        )
        
        with patch('app.api.auth.verify_password', return_value=False):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await login(credentials, mock_db)
            
            assert exc_info.value.status_code == 401
            assert "invalid" in exc_info.value.detail.lower()
    
    @pytest.mark.asyncio
    async def test_login_with_inactive_account_fails(self):
        """Test that login with disabled account fails."""
        # Arrange
        mock_db = Mock()
        mock_user = User(
            id=uuid.uuid4(),
            email="disabled@example.com",
            password_hash="hashed_password",
            name="Disabled User",
            role="user",
            is_active=False  # Account is disabled
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        credentials = UserLogin(
            email="disabled@example.com",
            password="CorrectPass123"
        )
        
        with patch('app.api.auth.verify_password', return_value=True):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await login(credentials, mock_db)
            
            assert exc_info.value.status_code == 403
            assert "disabled" in exc_info.value.detail.lower()
