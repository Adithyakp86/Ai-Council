# Authentication Middleware Implementation

## Overview

The authentication middleware has been successfully implemented in `backend/app/core/middleware.py`. This module provides JWT-based authentication for FastAPI endpoints.

## Features

### 1. JWT Authentication Dependency (`get_current_user`)

The main authentication middleware that:
- Extracts JWT token from the Authorization header (Bearer token)
- Validates and decodes the token
- Retrieves the user from the database
- Returns 401 for missing, invalid, or expired tokens
- Returns 403 for disabled user accounts

**Usage:**
```python
from fastapi import APIRouter, Depends
from app.core.middleware import get_current_user
from app.models.user import User

@router.get("/protected")
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    return {"user_id": str(current_user.id)}
```

### 2. Active User Dependency (`get_current_active_user`)

An alias for `get_current_user` that explicitly checks for active users.

### 3. Admin User Dependency (`get_current_admin_user`)

Extends `get_current_user` to verify admin role:
- Returns 403 if the user is not an admin
- Useful for admin-only endpoints

**Usage:**
```python
@router.get("/admin")
async def admin_endpoint(current_user: User = Depends(get_current_admin_user)):
    return {"message": "Admin access granted"}
```

### 4. Optional Authentication (`get_optional_user`)

Allows endpoints to work with both authenticated and unauthenticated users:
- Returns User object if valid token is provided
- Returns None if no token or invalid token
- Does not raise errors for missing/invalid tokens

**Usage:**
```python
@router.get("/public")
async def public_endpoint(current_user: User = Depends(get_optional_user)):
    if current_user:
        return {"message": f"Hello, {current_user.name}"}
    return {"message": "Hello, guest"}
```

## Error Handling

The middleware returns appropriate HTTP status codes:

| Scenario | Status Code | Detail |
|----------|-------------|--------|
| Missing token | 401 | Invalid or expired token |
| Invalid token | 401 | Invalid or expired token |
| Expired token | 401 | Invalid or expired token |
| Invalid token payload | 401 | Invalid token payload |
| Invalid user ID format | 401 | Invalid user ID in token |
| User not found | 401 | User not found |
| Inactive user account | 403 | User account is disabled |
| Non-admin accessing admin endpoint | 403 | Admin access required |

## Requirements Satisfied

✅ **Requirement 9.2**: WHEN a request includes a valid Authentication_Token in the Authorization header, THE System SHALL authenticate the User

✅ **Requirement 9.3**: WHEN a request includes an invalid or expired Authentication_Token, THE System SHALL return a 401 Unauthorized error

## Integration

The middleware is already integrated into the authentication endpoints in `backend/app/api/auth.py`:
- `/api/v1/auth/refresh` - Uses `get_current_user`
- `/api/v1/auth/logout` - Uses `get_current_user`
- `/api/v1/auth/me` - Uses `get_current_user`

## Testing

Comprehensive unit tests are provided in `backend/tests/test_auth_middleware_unit.py`:
- ✅ Valid token authentication
- ✅ Invalid token rejection
- ✅ Expired token rejection
- ✅ Non-existent user handling
- ✅ Inactive user handling
- ✅ Missing user ID in token
- ✅ Invalid user ID format
- ✅ Admin user verification
- ✅ Non-admin rejection for admin endpoints
- ✅ Module exports verification

All tests pass successfully.

## Example Usage

See `backend/app/api/example_protected.py` for complete examples of:
- Protected endpoints requiring authentication
- Admin-only endpoints
- Endpoints with optional authentication

## Security Features

1. **Token Validation**: Verifies JWT signature and expiration
2. **User Verification**: Checks user exists and is active
3. **Role-Based Access**: Supports admin-only endpoints
4. **Secure Headers**: Returns proper WWW-Authenticate headers
5. **Error Messages**: Provides clear error messages without exposing sensitive information

## Next Steps

The authentication middleware is ready for use in:
- Council processing endpoints (Task 8)
- Request history endpoints (Task 11)
- User dashboard endpoints (Task 12)
- Admin endpoints (Task 13)
- System monitoring endpoints (Task 14)
