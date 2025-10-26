from fastapi import HTTPException, Request, Depends
from datetime import datetime, timezone
from typing import Optional
from ..models import User, UserRole
from ..services import UserService
from .database import get_database

async def get_current_user(request: Request) -> Optional[User]:
    """Get current user from session token"""
    session_token = request.cookies.get("session_token")
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.split(" ")[1]
    
    if not session_token:
        return None
    
    db = await get_database()
    user_service = UserService(db)
    
    session = await user_service.get_session_by_token(session_token)
    if not session:
        return None
    
    # Handle timezone comparison
    expires_at = session.expires_at
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
    
    # Make sure both datetimes are timezone-aware
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        return None
    
    user = await user_service.get_user_by_id(session.user_id)
    return user

async def require_auth(request: Request) -> User:
    """Require authenticated user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

async def require_company(request: Request) -> User:
    """Require company account"""
    user = await require_auth(request)
    if user.role != UserRole.COMPANY:
        raise HTTPException(status_code=403, detail="Company account required")
    return user

async def require_student(request: Request) -> User:
    """Require student account"""
    user = await require_auth(request)
    if user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Student account required")
    return user

# Dependency for getting database
async def get_user_service():
    """Get UserService instance"""
    db = await get_database()
    return UserService(db)