"""Pydantic schemas for user API key management."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class APIKeyCreate(BaseModel):
    """Schema for creating a new API key."""
    
    provider_name: str = Field(..., description="Name of the AI provider (e.g., 'gemini', 'openai')")
    api_key: str = Field(..., min_length=10, description="The API key to store (will be encrypted)")
    
    @field_validator('provider_name')
    @classmethod
    def validate_provider_name(cls, v: str) -> str:
        """Validate that the provider name is supported."""
        from app.models.user_api_key import UserAPIKey
        
        if not UserAPIKey.validate_provider_name(v):
            supported = UserAPIKey.get_supported_providers()
            raise ValueError(
                f"Unsupported provider: {v}. "
                f"Supported providers: {', '.join(supported)}"
            )
        return v


class APIKeyUpdate(BaseModel):
    """Schema for updating an existing API key."""
    
    api_key: str = Field(..., min_length=10, description="The new API key to store (will be encrypted)")
    is_active: Optional[bool] = Field(None, description="Whether the API key is active")


class APIKeyResponse(BaseModel):
    """Schema for API key response (with masked key)."""
    
    id: UUID
    provider_name: str
    api_key_masked: str = Field(..., description="Masked API key (e.g., 'sk-...xyz')")
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True
    }


class APIKeyTestResponse(BaseModel):
    """Schema for API key test response."""
    
    is_valid: bool
    error_message: Optional[str] = None
    provider_name: str


class APIKeyListResponse(BaseModel):
    """Schema for listing user's API keys."""
    
    api_keys: list[APIKeyResponse]
    total: int
