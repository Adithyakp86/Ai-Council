"""
API Key Encryption Module

Provides secure encryption and decryption of user API keys using Fernet symmetric encryption.
"""
import os
from cryptography.fernet import Fernet
from typing import Optional


class EncryptionService:
    """Service for encrypting and decrypting sensitive data like API keys."""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize the encryption service.
        
        Args:
            encryption_key: Base64-encoded Fernet key. If None, loads from ENCRYPTION_KEY env var.
        
        Raises:
            ValueError: If encryption key is not provided or invalid.
        """
        if encryption_key is None:
            encryption_key = os.getenv("ENCRYPTION_KEY")
        
        if not encryption_key:
            raise ValueError(
                "ENCRYPTION_KEY environment variable is required. "
                "Generate one with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )
        
        try:
            self.cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
        except Exception as e:
            raise ValueError(f"Invalid encryption key: {e}")
    
    def encrypt_api_key(self, plain_key: str) -> str:
        """
        Encrypt an API key.
        
        Args:
            plain_key: The plaintext API key to encrypt.
        
        Returns:
            The encrypted API key as a base64-encoded string.
        
        Raises:
            ValueError: If plain_key is empty or invalid.
        """
        if not plain_key or not isinstance(plain_key, str):
            raise ValueError("API key must be a non-empty string")
        
        try:
            encrypted_bytes = self.cipher.encrypt(plain_key.encode())
            return encrypted_bytes.decode()
        except Exception as e:
            raise ValueError(f"Failed to encrypt API key: {e}")
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """
        Decrypt an API key.
        
        Args:
            encrypted_key: The encrypted API key (base64-encoded string).
        
        Returns:
            The decrypted plaintext API key.
        
        Raises:
            ValueError: If encrypted_key is invalid or decryption fails.
        """
        if not encrypted_key or not isinstance(encrypted_key, str):
            raise ValueError("Encrypted key must be a non-empty string")
        
        try:
            decrypted_bytes = self.cipher.decrypt(encrypted_key.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt API key: {e}")
    
    def rotate_key(self, old_key: str, new_encryption_key: str) -> str:
        """
        Rotate an encrypted API key to use a new encryption key.
        
        This is useful for security updates where the encryption key needs to be changed.
        
        Args:
            old_key: The API key encrypted with the old encryption key.
            new_encryption_key: The new Fernet encryption key to use.
        
        Returns:
            The API key re-encrypted with the new encryption key.
        
        Raises:
            ValueError: If decryption or re-encryption fails.
        """
        # Decrypt with current key
        plaintext = self.decrypt_api_key(old_key)
        
        # Create new cipher with new key
        new_service = EncryptionService(new_encryption_key)
        
        # Re-encrypt with new key
        return new_service.encrypt_api_key(plaintext)


# Global encryption service instance
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """
    Get the global encryption service instance.
    
    Returns:
        The global EncryptionService instance.
    """
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service


def encrypt_api_key(plain_key: str) -> str:
    """
    Convenience function to encrypt an API key using the global encryption service.
    
    Args:
        plain_key: The plaintext API key to encrypt.
    
    Returns:
        The encrypted API key as a base64-encoded string.
    """
    return get_encryption_service().encrypt_api_key(plain_key)


def decrypt_api_key(encrypted_key: str) -> str:
    """
    Convenience function to decrypt an API key using the global encryption service.
    
    Args:
        encrypted_key: The encrypted API key (base64-encoded string).
    
    Returns:
        The decrypted plaintext API key.
    """
    return get_encryption_service().decrypt_api_key(encrypted_key)
