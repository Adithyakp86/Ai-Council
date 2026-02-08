"""Tests for UserAPIKey model."""
import pytest
from datetime import datetime
from cryptography.fernet import Fernet
import os

from app.models.user_api_key import UserAPIKey
from app.models.user import User


class TestUserAPIKeyModel:
    """Tests for the UserAPIKey model."""
    
    def setup_method(self):
        """Set up test encryption key."""
        # Set a test encryption key
        self.test_key = Fernet.generate_key().decode()
        os.environ["ENCRYPTION_KEY"] = self.test_key
        
        # Reset encryption service
        import app.core.encryption
        app.core.encryption._encryption_service = None
    
    def teardown_method(self):
        """Clean up after tests."""
        if "ENCRYPTION_KEY" in os.environ:
            del os.environ["ENCRYPTION_KEY"]
        
        import app.core.encryption
        app.core.encryption._encryption_service = None
    
    def test_encrypt_key(self):
        """Test encrypting an API key."""
        api_key_record = UserAPIKey(
            provider_name="gemini",
            is_active=True
        )
        
        plain_key = "test-api-key-1234567890"
        api_key_record.encrypt_key(plain_key)
        
        # Encrypted key should not equal plain key
        assert api_key_record.api_key_encrypted != plain_key
        assert len(api_key_record.api_key_encrypted) > 0
    
    def test_decrypt_key(self):
        """Test decrypting an API key."""
        api_key_record = UserAPIKey(
            provider_name="gemini",
            is_active=True
        )
        
        plain_key = "test-api-key-1234567890"
        api_key_record.encrypt_key(plain_key)
        
        # Decrypt should return original key
        decrypted = api_key_record.decrypt_key()
        assert decrypted == plain_key
    
    def test_get_masked_key(self):
        """Test getting a masked version of the API key."""
        api_key_record = UserAPIKey(
            provider_name="gemini",
            is_active=True
        )
        
        plain_key = "sk-test-1234567890abcdef"
        api_key_record.encrypt_key(plain_key)
        
        masked = api_key_record.get_masked_key()
        
        # Should show first 3 and last 3 characters
        assert masked == "sk-...def"
        assert "test" not in masked
        assert "1234567890" not in masked
    
    def test_get_masked_key_short_key(self):
        """Test masking a very short key."""
        api_key_record = UserAPIKey(
            provider_name="gemini",
            is_active=True
        )
        
        plain_key = "short"
        api_key_record.encrypt_key(plain_key)
        
        masked = api_key_record.get_masked_key()
        
        # Short keys should be fully masked
        assert masked == "***"
    
    def test_mark_as_used(self):
        """Test marking an API key as used."""
        api_key_record = UserAPIKey(
            provider_name="gemini",
            is_active=True
        )
        
        # Initially last_used_at should be None
        assert api_key_record.last_used_at is None
        
        # Mark as used
        api_key_record.mark_as_used()
        
        # last_used_at should now be set
        assert api_key_record.last_used_at is not None
        assert isinstance(api_key_record.last_used_at, datetime)
    
    def test_validate_provider_name(self):
        """Test validating provider names."""
        # Valid providers
        assert UserAPIKey.validate_provider_name("gemini") is True
        assert UserAPIKey.validate_provider_name("huggingface") is True
        assert UserAPIKey.validate_provider_name("openai") is True
        assert UserAPIKey.validate_provider_name("ollama") is True
        
        # Invalid provider
        assert UserAPIKey.validate_provider_name("invalid_provider") is False
        assert UserAPIKey.validate_provider_name("") is False
    
    def test_get_supported_providers(self):
        """Test getting list of supported providers."""
        providers = UserAPIKey.get_supported_providers()
        
        # Should return a list
        assert isinstance(providers, list)
        assert len(providers) > 0
        
        # Should include known providers
        assert "gemini" in providers
        assert "huggingface" in providers
        assert "openai" in providers
        assert "ollama" in providers
    
    @pytest.mark.asyncio
    async def test_test_validity_basic(self):
        """Test basic API key validity check."""
        api_key_record = UserAPIKey(
            provider_name="gemini",
            is_active=True
        )
        
        # Valid key (long enough)
        api_key_record.encrypt_key("test-api-key-1234567890")
        is_valid, error = await api_key_record.test_validity()
        assert is_valid is True
        assert error is None
        
        # Invalid key (too short)
        api_key_record.encrypt_key("short")
        is_valid, error = await api_key_record.test_validity()
        assert is_valid is False
        assert "too short" in error.lower()
    
    @pytest.mark.asyncio
    async def test_test_validity_unknown_provider(self):
        """Test validity check with unknown provider."""
        api_key_record = UserAPIKey(
            provider_name="unknown_provider",
            is_active=True
        )
        
        api_key_record.encrypt_key("test-api-key-1234567890")
        is_valid, error = await api_key_record.test_validity()
        
        assert is_valid is False
        assert "unknown provider" in error.lower()
    
    def test_repr(self):
        """Test string representation of UserAPIKey."""
        from uuid import uuid4
        
        user_id = uuid4()
        api_key_id = uuid4()
        
        api_key_record = UserAPIKey(
            id=api_key_id,
            user_id=user_id,
            provider_name="gemini",
            is_active=True
        )
        
        repr_str = repr(api_key_record)
        
        assert "UserAPIKey" in repr_str
        assert str(api_key_id) in repr_str
        assert str(user_id) in repr_str
        assert "gemini" in repr_str


class TestUserAPIKeyEncryption:
    """Security-focused tests for UserAPIKey encryption."""
    
    def setup_method(self):
        """Set up test encryption key."""
        self.test_key = Fernet.generate_key().decode()
        os.environ["ENCRYPTION_KEY"] = self.test_key
        
        import app.core.encryption
        app.core.encryption._encryption_service = None
    
    def teardown_method(self):
        """Clean up after tests."""
        if "ENCRYPTION_KEY" in os.environ:
            del os.environ["ENCRYPTION_KEY"]
        
        import app.core.encryption
        app.core.encryption._encryption_service = None
    
    def test_encrypted_key_does_not_contain_plaintext(self):
        """Test that encrypted key doesn't contain plaintext."""
        api_key_record = UserAPIKey(
            provider_name="gemini",
            is_active=True
        )
        
        plain_key = "sk-very-secret-key-1234567890"
        api_key_record.encrypt_key(plain_key)
        
        # Encrypted key should not contain any part of the plaintext
        assert "sk-very" not in api_key_record.api_key_encrypted
        assert "secret" not in api_key_record.api_key_encrypted
        assert "1234567890" not in api_key_record.api_key_encrypted
    
    def test_multiple_encryptions_produce_different_ciphertexts(self):
        """Test that encrypting the same key multiple times produces different ciphertexts."""
        plain_key = "sk-test-1234567890"
        
        api_key1 = UserAPIKey(provider_name="gemini", is_active=True)
        api_key1.encrypt_key(plain_key)
        
        api_key2 = UserAPIKey(provider_name="gemini", is_active=True)
        api_key2.encrypt_key(plain_key)
        
        # Ciphertexts should be different
        assert api_key1.api_key_encrypted != api_key2.api_key_encrypted
        
        # But both should decrypt to the same value
        assert api_key1.decrypt_key() == plain_key
        assert api_key2.decrypt_key() == plain_key
