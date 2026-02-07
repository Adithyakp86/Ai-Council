"""Authentication endpoints for user registration, login, and token management."""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    hash_password,
    validate_password_strength,
    verify_password,
)
from app.core.config import settings
from app.core.middleware import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])


# Pydantic schemas
class UserRegister(BaseModel):
    """User registration request schema."""
    email: EmailStr
    password: str
    name: str
    
    @field_validator('email')
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """Validate email format."""
        if not v or '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower()


class UserLogin(BaseModel):
    """User login request schema."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema."""
    token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserResponse(BaseModel):
    """User response schema."""
    model_config = {"from_attributes": True}
    
    id: str
    email: str
    name: str
    role: str
    is_active: bool
    created_at: str


class TokenRefreshResponse(BaseModel):
    """Token refresh response schema."""
    token: str
    token_type: str = "bearer"
    expires_in: int


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Token and user information
        
    Raises:
        HTTPException: If email already exists or password is weak
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password strength
    is_valid, error_message = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Determine if this is the first user (make them admin)
    user_count = db.query(User).count()
    role = "admin" if user_count == 0 else "user"
    
    # Create user
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        name=user_data.name,
        role=role,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(new_user.id)},
        expires_delta=timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    )
    
    return {
        "token": access_token,
        "user": {
            "id": str(new_user.id),
            "email": new_user.email,
            "name": new_user.name,
            "role": new_user.role
        }
    }


@router.post("/login", response_model=dict)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token.
    
    Args:
        credentials: User login credentials
        db: Database session
        
    Returns:
        Token and user information
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    )
    
    return {
        "token": access_token,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
    }


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    current_user: User = Depends(get_current_user)
):
    """
    Refresh an access token.
    
    This endpoint allows users to get a new token before their current one expires.
    The user must provide a valid (non-expired) token to get a new one.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        New access token with fresh expiration
    """
    # Create new access token
    new_token = create_access_token(
        data={"sub": str(current_user.id)},
        expires_delta=timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    )
    
    return TokenRefreshResponse(
        token=new_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60 * 60  # Convert days to seconds
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout user.
    
    Note: Since we're using stateless JWT tokens, logout is handled client-side
    by removing the token. This endpoint exists for API consistency and could
    be extended to implement token blacklisting if needed.
    
    Args:
        current_user: Current authenticated user
    """
    # In a stateless JWT system, logout is handled client-side
    # This endpoint validates the token and could be extended to blacklist tokens
    return None


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat()
    )
