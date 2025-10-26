from fastapi import HTTPException, Request, Depends
from datetime import datetime, timezone
from typing import Optional
from ..models import User, UserRole
from ..services import UserService
from .database import get_database

async def get_current_user(request: Request) -> Optional[User]:
    """Get current user from JWT token"""
    token = None
    
    # Check Authorization header first
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    # Fallback to cookies
    if not token:
        token = request.cookies.get("session_token")
    
    if not token:
        return None
    
    # Import auth_utils
    from ..utils.auth import auth_utils
    
    # Verify JWT token
    payload = auth_utils.verify_token(token)
    if not payload:
        return None
    
    # Get user from database
    db = await get_database()
    user_service = UserService(db)
    
    user_email = payload.get("sub")
    if not user_email:
        return None
    
    user = await user_service.get_user_by_email(user_email)
    return user

async def require_auth(request: Request) -> User:
    """Require authenticated user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    return user

async def require_admin(request: Request) -> User:
    """Require admin account"""
    user = await require_auth(request)
    if not user.is_admin():
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user

async def require_company(request: Request) -> User:
    """Require company account"""
    user = await require_auth(request)
    if not user.is_company():
        raise HTTPException(status_code=403, detail="Company account required")
    return user

async def require_student(request: Request) -> User:
    """Require student account"""
    user = await require_auth(request)
    if not user.is_student():
        raise HTTPException(status_code=403, detail="Student account required")
    return user

async def require_company_or_admin(request: Request) -> User:
    """Require company or admin account"""
    user = await require_auth(request)
    if not (user.is_company() or user.is_admin()):
        raise HTTPException(status_code=403, detail="Company or admin account required")
    return user

# Dependency for getting database
async def get_user_service():
    """Get UserService instance"""
    db = await get_database()
    return UserService(db)