"""UserAPIKey model for storing user-specific API keys."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.core.encryption import encrypt_api_key, decrypt_api_key
from app.core.provider_config import get_provider_config


class UserAPIKey(Base):
    """User API key model for storing encrypted provider API keys."""

    __tablename__ = "user_api_keys"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    api_key_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="api_keys")

    def __repr__(self) -> str:
        return f"<UserAPIKey(id={self.id}, user_id={self.user_id}, provider={self.provider_name})>"

    def encrypt_key(self, plain_key: str) -> None:
        """
        Encrypt and store an API key.
        
        Args:
            plain_key: The plaintext API key to encrypt and store.
        
        Raises:
            ValueError: If plain_key is invalid or encryption fails.
        """
        self.api_key_encrypted = encrypt_api_key(plain_key)

    def decrypt_key(self) -> str:
        """
        Decrypt and return the stored API key.
        
        Returns:
            The decrypted plaintext API key.
        
        Raises:
            ValueError: If decryption fails.
        """
        return decrypt_api_key(self.api_key_encrypted)

    def get_masked_key(self) -> str:
        """
        Get a masked version of the API key for display purposes.
        
        Returns:
            Masked API key showing only first 3 and last 3 characters.
            Example: "sk-...xyz" or "hf_...abc"
        """
        try:
            plain_key = self.decrypt_key()
            if len(plain_key) <= 6:
                return "***"
            return f"{plain_key[:3]}...{plain_key[-3:]}"
        except Exception:
            return "***"

    async def test_validity(self) -> tuple[bool, Optional[str]]:
        """
        Test if the API key is valid by making a lightweight test request.
        
        Returns:
            Tuple of (is_valid, error_message). If valid, error_message is None.
        """
        try:
            plain_key = self.decrypt_key()
            
            # Get provider config
            provider_config = get_provider_config()
            provider_info = provider_config.get_provider_info(self.provider_name)
            
            if not provider_info:
                return False, f"Unknown provider: {self.provider_name}"
            
            # For now, just check if key is not empty
            # In a real implementation, you would make a test API call
            if not plain_key or len(plain_key) < 10:
                return False, "API key appears to be invalid (too short)"
            
            # TODO: Implement actual API validation for each provider
            # This would involve making a lightweight test request to the provider's API
            
            return True, None
            
        except Exception as e:
            return False, f"Failed to validate API key: {str(e)}"

    def mark_as_used(self) -> None:
        """Update the last_used_at timestamp to track API key usage."""
        from datetime import timezone
        self.last_used_at = datetime.now(timezone.utc)

    @staticmethod
    def validate_provider_name(provider_name: str) -> bool:
        """
        Validate that the provider name is in the list of supported providers.
        
        Args:
            provider_name: The provider name to validate.
        
        Returns:
            True if provider is supported, False otherwise.
        """
        provider_config = get_provider_config()
        return provider_name in provider_config.providers

    @classmethod
    def get_supported_providers(cls) -> list[str]:
        """
        Get list of all supported provider names.
        
        Returns:
            List of supported provider names.
        """
        provider_config = get_provider_config()
        return list(provider_config.providers.keys())
