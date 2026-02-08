"""API endpoints for user API key management."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.user_api_key import (
    APIKeyCreate,
    APIKeyUpdate,
    APIKeyResponse,
    APIKeyTestResponse,
    APIKeyListResponse,
)
from app.core.database import get_db
from app.core.middleware import get_current_user
from app.models.user import User
from app.models.user_api_key import UserAPIKey


router = APIRouter(prefix="/user/api-keys", tags=["user-api-keys"])


@router.post("", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIKeyResponse:
    """
    Create a new API key for a provider.
    
    If an API key already exists for this provider, it will be replaced.
    """
    # Check if API key already exists for this provider
    result = await db.execute(
        select(UserAPIKey).where(
            UserAPIKey.user_id == current_user.id,
            UserAPIKey.provider_name == api_key_data.provider_name,
        )
    )
    existing_key = result.scalar_one_or_none()
    
    if existing_key:
        # Update existing key
        existing_key.encrypt_key(api_key_data.api_key)
        existing_key.is_active = True
        from datetime import datetime, timezone
        existing_key.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(existing_key)
        
        return APIKeyResponse(
            id=existing_key.id,
            provider_name=existing_key.provider_name,
            api_key_masked=existing_key.get_masked_key(),
            is_active=existing_key.is_active,
            created_at=existing_key.created_at,
            updated_at=existing_key.updated_at,
            last_used_at=existing_key.last_used_at,
        )
    
    # Create new API key
    new_key = UserAPIKey(
        user_id=current_user.id,
        provider_name=api_key_data.provider_name,
        is_active=True,
    )
    new_key.encrypt_key(api_key_data.api_key)
    
    db.add(new_key)
    await db.commit()
    await db.refresh(new_key)
    
    return APIKeyResponse(
        id=new_key.id,
        provider_name=new_key.provider_name,
        api_key_masked=new_key.get_masked_key(),
        is_active=new_key.is_active,
        created_at=new_key.created_at,
        updated_at=new_key.updated_at,
        last_used_at=new_key.last_used_at,
    )


@router.get("", response_model=APIKeyListResponse)
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIKeyListResponse:
    """
    List all API keys for the current user (with masked keys).
    """
    result = await db.execute(
        select(UserAPIKey)
        .where(UserAPIKey.user_id == current_user.id)
        .order_by(UserAPIKey.created_at.desc())
    )
    api_keys = result.scalars().all()
    
    return APIKeyListResponse(
        api_keys=[
            APIKeyResponse(
                id=key.id,
                provider_name=key.provider_name,
                api_key_masked=key.get_masked_key(),
                is_active=key.is_active,
                created_at=key.created_at,
                updated_at=key.updated_at,
                last_used_at=key.last_used_at,
            )
            for key in api_keys
        ],
        total=len(api_keys),
    )


@router.put("/{provider_name}", response_model=APIKeyResponse)
async def update_api_key(
    provider_name: str,
    api_key_data: APIKeyUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIKeyResponse:
    """
    Update an existing API key for a provider.
    """
    # Validate provider name
    if not UserAPIKey.validate_provider_name(provider_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider_name}",
        )
    
    # Find existing key
    result = await db.execute(
        select(UserAPIKey).where(
            UserAPIKey.user_id == current_user.id,
            UserAPIKey.provider_name == provider_name,
        )
    )
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No API key found for provider: {provider_name}",
        )
    
    # Update the key
    api_key.encrypt_key(api_key_data.api_key)
    if api_key_data.is_active is not None:
        api_key.is_active = api_key_data.is_active
    
    from datetime import datetime, timezone
    api_key.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(api_key)
    
    return APIKeyResponse(
        id=api_key.id,
        provider_name=api_key.provider_name,
        api_key_masked=api_key.get_masked_key(),
        is_active=api_key.is_active,
        created_at=api_key.created_at,
        updated_at=api_key.updated_at,
        last_used_at=api_key.last_used_at,
    )


@router.delete("/{provider_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    provider_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete an API key for a provider.
    """
    # Find existing key
    result = await db.execute(
        select(UserAPIKey).where(
            UserAPIKey.user_id == current_user.id,
            UserAPIKey.provider_name == provider_name,
        )
    )
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No API key found for provider: {provider_name}",
        )
    
    await db.delete(api_key)
    await db.commit()


@router.post("/{provider_name}/test", response_model=APIKeyTestResponse)
async def test_api_key(
    provider_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIKeyTestResponse:
    """
    Test the validity of an API key for a provider.
    """
    # Validate provider name
    if not UserAPIKey.validate_provider_name(provider_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider_name}",
        )
    
    # Find existing key
    result = await db.execute(
        select(UserAPIKey).where(
            UserAPIKey.user_id == current_user.id,
            UserAPIKey.provider_name == provider_name,
        )
    )
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No API key found for provider: {provider_name}",
        )
    
    # Test the key
    is_valid, error_message = await api_key.test_validity()
    
    return APIKeyTestResponse(
        is_valid=is_valid,
        error_message=error_message,
        provider_name=provider_name,
    )


@router.post("/test-new", response_model=APIKeyTestResponse)
async def test_new_api_key(
    api_key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIKeyTestResponse:
    """
    Test the validity of a new API key before saving it.
    
    This endpoint allows users to validate their API key without storing it.
    """
    # Validate provider name
    if not UserAPIKey.validate_provider_name(api_key_data.provider_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {api_key_data.provider_name}",
        )
    
    # Create a temporary UserAPIKey instance for testing (don't save to DB)
    temp_key = UserAPIKey(
        user_id=current_user.id,
        provider_name=api_key_data.provider_name,
        is_active=True,
    )
    temp_key.encrypt_key(api_key_data.api_key)
    
    # Test the key
    is_valid, error_message = await temp_key.test_validity()
    
    return APIKeyTestResponse(
        is_valid=is_valid,
        error_message=error_message,
        provider_name=api_key_data.provider_name,
    )
