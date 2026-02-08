"""
Tests for API key encryption functionality.
"""
import pytest
from cryptography.fernet import Fernet
from app.core.encryption import EncryptionService, encrypt_api_key, decrypt_api_key


class TestEncryptionService:
    """Tests for the EncryptionService class."""
    
    def test_encrypt_decrypt_roundtrip(self):
        """Test that encryption and decryption work correctly."""
        # Generate a test key
        test_key = Fernet.generate_key().decode()
        service = EncryptionService(test_key)
        
        # Test API key
        original_key = "sk-test-1234567890abcdef"
        
        # Encrypt
        encrypted = service.encrypt_api_key(original_key)
        assert encrypted != original_key
        assert len(encrypted) > 0
        
        # Decrypt
        decrypted = service.decrypt_api_key(encrypted)
        assert decrypted == original_key
    
    def test_encrypt_different_keys_produce_different_ciphertexts(self):
        """Test that encrypting the same key twice produces different ciphertexts."""
        test_key = Fernet.generate_key().decode()
        service = EncryptionService(test_key)
        
        original_key = "sk-test-1234567890abcdef"
        
        # Encrypt twice
        encrypted1 = service.encrypt_api_key(original_key)
        encrypted2 = service.encrypt_api_key(original_key)
        
        # Ciphertexts should be different (Fernet includes timestamp)
        assert encrypted1 != encrypted2
        
        # But both should decrypt to the same value
        assert service.decrypt_api_key(encrypted1) == original_key
        assert service.decrypt_api_key(encrypted2) == original_key
    
    def test_encrypt_empty_key_raises_error(self):
        """Test that encrypting an empty key raises an error."""
        test_key = Fernet.generate_key().decode()
        service = EncryptionService(test_key)
        
        with pytest.raises(ValueError, match="API key must be a non-empty string"):
            service.encrypt_api_key("")
    
    def test_decrypt_invalid_key_raises_error(self):
        """Test that decrypting an invalid key raises an error."""
        test_key = Fernet.generate_key().decode()
        service = EncryptionService(test_key)
        
        with pytest.raises(ValueError, match="Failed to decrypt API key"):
            service.decrypt_api_key("invalid-encrypted-key")
    
    def test_decrypt_with_wrong_encryption_key_raises_error(self):
        """Test that decrypting with a different encryption key fails."""
        # Encrypt with one key
        key1 = Fernet.generate_key().decode()
        service1 = EncryptionService(key1)
        encrypted = service1.encrypt_api_key("sk-test-1234567890abcdef")
        
        # Try to decrypt with a different key
        key2 = Fernet.generate_key().decode()
        service2 = EncryptionService(key2)
        
        with pytest.raises(ValueError, match="Failed to decrypt API key"):
            service2.decrypt_api_key(encrypted)
    
    def test_key_rotation(self):
        """Test that key rotation works correctly."""
        # Original encryption key
        old_key = Fernet.generate_key().decode()
        service = EncryptionService(old_key)
        
        # Encrypt with old key
        original_api_key = "sk-test-1234567890abcdef"
        encrypted_with_old = service.encrypt_api_key(original_api_key)
        
        # Rotate to new key
        new_key = Fernet.generate_key().decode()
        encrypted_with_new = service.rotate_key(encrypted_with_old, new_key)
        
        # Verify old key can't decrypt new encryption
        with pytest.raises(ValueError):
            service.decrypt_api_key(encrypted_with_new)
        
        # Verify new key can decrypt
        new_service = EncryptionService(new_key)
        decrypted = new_service.decrypt_api_key(encrypted_with_new)
        assert decrypted == original_api_key
    
    def test_initialization_without_key_raises_error(self):
        """Test that initializing without a key raises an error."""
        import os
        # Temporarily remove ENCRYPTION_KEY from environment
        old_key = os.environ.get("ENCRYPTION_KEY")
        if "ENCRYPTION_KEY" in os.environ:
            del os.environ["ENCRYPTION_KEY"]
        
        try:
            with pytest.raises(ValueError, match="ENCRYPTION_KEY environment variable is required"):
                EncryptionService()
        finally:
            # Restore old key
            if old_key:
                os.environ["ENCRYPTION_KEY"] = old_key
    
    def test_convenience_functions(self):
        """Test the convenience functions for encryption/decryption."""
        import os
        # Set a test encryption key
        test_key = Fernet.generate_key().decode()
        os.environ["ENCRYPTION_KEY"] = test_key
        
        # Reset global service
        import app.core.encryption
        app.core.encryption._encryption_service = None
        
        try:
            original_key = "sk-test-1234567890abcdef"
            
            # Test convenience functions
            encrypted = encrypt_api_key(original_key)
            decrypted = decrypt_api_key(encrypted)
            
            assert decrypted == original_key
        finally:
            # Clean up
            if "ENCRYPTION_KEY" in os.environ:
                del os.environ["ENCRYPTION_KEY"]
            app.core.encryption._encryption_service = None


class TestEncryptionSecurity:
    """Security-focused tests for encryption."""
    
    def test_encrypted_key_does_not_contain_plaintext(self):
        """Test that the encrypted key doesn't contain the plaintext."""
        test_key = Fernet.generate_key().decode()
        service = EncryptionService(test_key)
        
        original_key = "sk-test-very-secret-key-1234567890"
        encrypted = service.encrypt_api_key(original_key)
        
        # Encrypted key should not contain any part of the original
        assert "sk-test" not in encrypted
        assert "secret" not in encrypted
        assert "1234567890" not in encrypted
    
    def test_encryption_produces_different_output_each_time(self):
        """Test that encryption is non-deterministic (includes IV/timestamp)."""
        test_key = Fernet.generate_key().decode()
        service = EncryptionService(test_key)
        
        original_key = "sk-test-1234567890abcdef"
        
        # Encrypt multiple times
        encrypted_keys = [service.encrypt_api_key(original_key) for _ in range(5)]
        
        # All should be different
        assert len(set(encrypted_keys)) == 5
        
        # But all should decrypt to the same value
        for encrypted in encrypted_keys:
            assert service.decrypt_api_key(encrypted) == original_key
