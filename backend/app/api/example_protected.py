"""Example protected endpoints demonstrating authentication middleware usage."""

from fastapi import APIRouter, Depends

from app.core.middleware import get_current_user, get_current_admin_user, get_optional_user
from app.models.user import User

router = APIRouter(prefix="/example", tags=["example"])


@router.get("/protected")
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    """
    Example protected endpoint that requires authentication.
    
    This endpoint demonstrates how to use the authentication middleware.
    Only authenticated users with valid tokens can access this endpoint.
    
    Args:
        current_user: Current authenticated user (injected by middleware)
        
    Returns:
        User information and a success message
    """
    return {
        "message": "This is a protected endpoint",
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "name": current_user.name,
            "role": current_user.role
        }
    }


@router.get("/admin-only")
async def admin_only_endpoint(current_user: User = Depends(get_current_admin_user)):
    """
    Example admin-only endpoint.
    
    This endpoint demonstrates how to restrict access to admin users only.
    Returns 403 Forbidden if the user is not an admin.
    
    Args:
        current_user: Current authenticated admin user (injected by middleware)
        
    Returns:
        Admin-specific information
    """
    return {
        "message": "This is an admin-only endpoint",
        "admin": {
            "id": str(current_user.id),
            "email": current_user.email,
            "name": current_user.name
        }
    }


@router.get("/optional-auth")
async def optional_auth_endpoint(current_user: User = Depends(get_optional_user)):
    """
    Example endpoint with optional authentication.
    
    This endpoint can be accessed by both authenticated and unauthenticated users.
    The response varies based on whether the user is authenticated.
    
    Args:
        current_user: Current user if authenticated, None otherwise
        
    Returns:
        Different responses based on authentication status
    """
    if current_user:
        return {
            "message": "Welcome back!",
            "authenticated": True,
            "user": {
                "id": str(current_user.id),
                "email": current_user.email,
                "name": current_user.name
            }
        }
    else:
        return {
            "message": "Welcome, guest!",
            "authenticated": False
        }
