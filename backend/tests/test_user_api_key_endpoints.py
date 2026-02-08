"""Tests for user API key management endpoints."""
import pytest
from httpx import AsyncClient
from cryptography.fernet import Fernet
import os

from app.main import app
from app.models.user import User
from app.models.user_api_key import UserAPIKey
from app.core.security import create_access_token


@pytest.fixture
def setup_encryption():
    """Set up encryption key for tests."""
    test_key = Fernet.generate_key().decode()
    os.environ["ENCRYPTION_KEY"] = test_key
    
    import app.core.encryption
    app.core.encryption._encryption_service = None
    
    yield
    
    if "ENCRYPTION_KEY" in os.environ:
        del os.environ["ENCRYPTION_KEY"]
    app.core.encryption._encryption_service = None


@pytest.mark.asyncio
class TestUserAPIKeyEndpoints:
    """Tests for user API key management endpoints."""
    
    async def test_create_api_key(self, async_client: AsyncClient, test_user: User, setup_encryption):
        """Test creating a new API key."""
        token = create_access_token({"sub": str(test_user.id)})
        
        response = await async_client.post(
            "/api/v1/user/api-keys",
            json={
                "provider_name": "gemini",
                "api_key": "test-api-key-1234567890"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["provider_name"] == "gemini"
        assert data["api_key_masked"] == "tes...890"
        assert data["is_active"] is True
    
    async def test_create_api_key_invalid_provider(self, async_client: AsyncClient, test_user: User, setup_encryption):
        """Test creating an API key with invalid provider."""
        token = create_access_token({"sub": str(test_user.id)})
        
        response = await async_client.post(
            "/api/v1/user/api-keys",
            json={
                "provider_name": "invalid_provider",
                "api_key": "test-api-key-1234567890"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 422  # Validation error
    
    async def test_create_api_key_replaces_existing(self, async_client: AsyncClient, test_user: User, test_db, setup_encryption):
        """Test that creating an API key replaces existing one."""
        token = create_access_token({"sub": str(test_user.id)})
        
        # Create first key
        response1 = await async_client.post(
            "/api/v1/user/api-keys",
            json={
                "provider_name": "gemini",
                "api_key": "old-api-key-1234567890"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response1.status_code == 201
        key_id_1 = response1.json()["id"]
        
        # Create second key for same provider
        response2 = await async_client.post(
            "/api/v1/user/api-keys",
            json={
                "provider_name": "gemini",
                "api_key": "new-api-key-0987654321"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response2.status_code == 201
        key_id_2 = response2.json()["id"]
        
        # Should be the same key (updated)
        assert key_id_1 == key_id_2
        assert response2.json()["api_key_masked"] == "new...321"
    
    async def test_list_api_keys(self, async_client: AsyncClient, test_user: User, test_db, setup_encryption):
        """Test listing user's API keys."""
        token = create_access_token({"sub": str(test_user.id)})
        
        # Create multiple keys
        await async_client.post(
            "/api/v1/user/api-keys",
            json={"provider_name": "gemini", "api_key": "gemini-key-1234567890"},
            headers={"Authorization": f"Bearer {token}"}
        )
        await async_client.post(
            "/api/v1/user/api-keys",
            json={"provider_name": "openai", "api_key": "openai-key-0987654321"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # List keys
        response = await async_client.get(
            "/api/v1/user/api-keys",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["api_keys"]) == 2
        
        # Check that keys are masked
        providers = {key["provider_name"] for key in data["api_keys"]}
        assert providers == {"gemini", "openai"}
        
        for key in data["api_keys"]:
            assert "..." in key["api_key_masked"]
    
    async def test_update_api_key(self, async_client: AsyncClient, test_user: User, test_db, setup_encryption):
        """Test updating an existing API key."""
        token = create_access_token({"sub": str(test_user.id)})
        
        # Create key
        await async_client.post(
            "/api/v1/user/api-keys",
            json={"provider_name": "gemini", "api_key": "old-key-1234567890"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Update key
        response = await async_client.put(
            "/api/v1/user/api-keys/gemini",
            json={"api_key": "new-key-0987654321"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["provider_name"] == "gemini"
        assert data["api_key_masked"] == "new...321"
    
    async def test_update_nonexistent_api_key(self, async_client: AsyncClient, test_user: User, setup_encryption):
        """Test updating a non-existent API key."""
        token = create_access_token({"sub": str(test_user.id)})
        
        response = await async_client.put(
            "/api/v1/user/api-keys/gemini",
            json={"api_key": "new-key-1234567890"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
    
    async def test_delete_api_key(self, async_client: AsyncClient, test_user: User, test_db, setup_encryption):
        """Test deleting an API key."""
        token = create_access_token({"sub": str(test_user.id)})
        
        # Create key
        await async_client.post(
            "/api/v1/user/api-keys",
            json={"provider_name": "gemini", "api_key": "test-key-1234567890"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Delete key
        response = await async_client.delete(
            "/api/v1/user/api-keys/gemini",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 204
        
        # Verify key is deleted
        list_response = await async_client.get(
            "/api/v1/user/api-keys",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert list_response.json()["total"] == 0
    
    async def test_delete_nonexistent_api_key(self, async_client: AsyncClient, test_user: User, setup_encryption):
        """Test deleting a non-existent API key."""
        token = create_access_token({"sub": str(test_user.id)})
        
        response = await async_client.delete(
            "/api/v1/user/api-keys/gemini",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
    
    async def test_test_api_key(self, async_client: AsyncClient, test_user: User, test_db, setup_encryption):
        """Test testing an API key's validity."""
        token = create_access_token({"sub": str(test_user.id)})
        
        # Create key
        await async_client.post(
            "/api/v1/user/api-keys",
            json={"provider_name": "gemini", "api_key": "test-key-1234567890"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Test key
        response = await async_client.post(
            "/api/v1/user/api-keys/gemini/test",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["provider_name"] == "gemini"
        assert "is_valid" in data
    
    async def test_test_nonexistent_api_key(self, async_client: AsyncClient, test_user: User, setup_encryption):
        """Test testing a non-existent API key."""
        token = create_access_token({"sub": str(test_user.id)})
        
        response = await async_client.post(
            "/api/v1/user/api-keys/gemini/test",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
    
    async def test_unauthorized_access(self, async_client: AsyncClient, setup_encryption):
        """Test that endpoints require authentication."""
        # Try to list keys without auth
        response = await async_client.get("/api/v1/user/api-keys")
        assert response.status_code == 401
        
        # Try to create key without auth
        response = await async_client.post(
            "/api/v1/user/api-keys",
            json={"provider_name": "gemini", "api_key": "test-key"}
        )
        assert response.status_code == 401
    
    async def test_user_isolation(self, async_client: AsyncClient, test_user: User, test_db, setup_encryption):
        """Test that users can only access their own API keys."""
        # Create first user's key
        token1 = create_access_token({"sub": str(test_user.id)})
        await async_client.post(
            "/api/v1/user/api-keys",
            json={"provider_name": "gemini", "api_key": "user1-key-1234567890"},
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        # Create second user
        from uuid import uuid4
        user2_id = uuid4()
        token2 = create_access_token({"sub": str(user2_id)})
        
        # Second user should not see first user's keys
        response = await async_client.get(
            "/api/v1/user/api-keys",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert response.status_code == 200
        assert response.json()["total"] == 0

    async def test_test_new_api_key(self, async_client: AsyncClient, test_user: User, setup_encryption):
        """Test testing a new API key before saving it."""
        token = create_access_token({"sub": str(test_user.id)})
        
        # Test a new key without saving
        response = await async_client.post(
            "/api/v1/user/api-keys/test-new",
            json={
                "provider_name": "gemini",
                "api_key": "test-key-1234567890"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["provider_name"] == "gemini"
        assert "is_valid" in data
        
        # Verify the key was not saved
        list_response = await async_client.get(
            "/api/v1/user/api-keys",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert list_response.json()["total"] == 0
    
    async def test_test_new_api_key_invalid_provider(self, async_client: AsyncClient, test_user: User, setup_encryption):
        """Test testing a new API key with invalid provider."""
        token = create_access_token({"sub": str(test_user.id)})
        
        response = await async_client.post(
            "/api/v1/user/api-keys/test-new",
            json={
                "provider_name": "invalid_provider",
                "api_key": "test-key-1234567890"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 422  # Validation error
