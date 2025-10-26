from fastapi import HTTPException, Request, Response, Depends
from datetime import datetime, timezone, timedelta
from ..models import User, Session
from ..models.auth import UserRegister, UserLogin, TokenResponse, PasswordUpdate
from ..models.enums import UserRole
from ..services import UserService
from ..core import settings
from ..utils.auth import auth_utils
from typing import Optional

class AuthController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def register(self, user_data: UserRegister) -> TokenResponse:
        """Register a new user"""
        try:
            # Check if user already exists
            existing_user = await self.user_service.get_user_by_email(user_data.email)
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered")
            
            # Hash password
            password_hash = auth_utils.hash_password(user_data.password)
            
            # Create user
            user = User(
                email=user_data.email,
                name=user_data.name,
                password_hash=password_hash,
                role=UserRole(user_data.role) if user_data.role else UserRole.STUDENT,
                is_verified=True,  # Auto-verify for local auth
                is_active=True
            )
            
            created_user = await self.user_service.create_user(user)
            if not created_user:
                raise HTTPException(status_code=500, detail="Failed to create user")
            
            # Create session token
            session_token = auth_utils.generate_session_token()
            
            # Create session
            session = Session(
                user_id=created_user.id,
                session_token=session_token,
                expires_at=datetime.now(timezone.utc) + timedelta(days=settings.SESSION_EXPIRE_DAYS)
            )
            
            created_session = await self.user_service.create_session(session)
            if not created_session:
                raise HTTPException(status_code=500, detail="Failed to create session")
            
            # Create JWT token
            access_token = auth_utils.create_access_token(
                data={"sub": created_user.email, "user_id": created_user.id}
            )
            
            return TokenResponse(
                access_token=access_token,
                user={
                    "id": created_user.id,
                    "email": created_user.email,
                    "name": created_user.name,
                    "role": created_user.role.value,
                    "is_verified": created_user.is_verified
                }
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

    async def login(self, user_data: UserLogin, response: Response) -> TokenResponse:
        """Login user with email and password"""
        try:
            # Find user by email
            user = await self.user_service.get_user_by_email(user_data.email)
            if not user:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Check if user has password (for OAuth users)
            if not user.password_hash:
                raise HTTPException(
                    status_code=400, 
                    detail="This account uses OAuth authentication. Please use the OAuth login."
                )
            
            # Verify password
            if not auth_utils.verify_password(user_data.password, user.password_hash):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Check if user is active
            if not user.is_active:
                raise HTTPException(status_code=401, detail="Account is disabled")
            
            # Create session token
            session_token = auth_utils.generate_session_token()
            
            # Create session
            session = Session(
                user_id=user.id,
                session_token=session_token,
                expires_at=datetime.now(timezone.utc) + timedelta(days=settings.SESSION_EXPIRE_DAYS)
            )
            
            created_session = await self.user_service.create_session(session)
            if not created_session:
                raise HTTPException(status_code=500, detail="Failed to create session")
            
            # Set secure cookie
            response.set_cookie(
                key="session_token",
                value=session_token,
                path="/",
                httponly=True,
                secure=False,  # Set to False for development (HTTP)
                samesite="lax",
                max_age=settings.SESSION_EXPIRE_DAYS*24*60*60
            )
            
            # Create JWT token
            access_token = auth_utils.create_access_token(
                data={"sub": user.email, "user_id": user.id}
            )
            
            return TokenResponse(
                access_token=access_token,
                user={
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "role": user.role.value,
                    "is_verified": user.is_verified
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

    async def complete_auth(self, session_id: str, response: Response) -> dict:
        """Legacy OAuth completion - kept for compatibility"""
        raise HTTPException(
            status_code=400, 
            detail="OAuth authentication not available. Please use /auth/login endpoint."
        )

    async def logout(self, request: Request, response: Response) -> dict:
        """Logout user"""
        session_token = request.cookies.get("session_token")
        if session_token:
            await self.user_service.delete_session(session_token)
        
        response.delete_cookie("session_token", path="/", samesite="lax")
        return {"message": "Logged out successfully"}

    async def change_password(self, request: Request, password_data: PasswordUpdate) -> dict:
        """Change user password"""
        try:
            # Get current user from session
            session_token = request.cookies.get("session_token")
            if not session_token:
                raise HTTPException(status_code=401, detail="Not authenticated")
            
            session = await self.user_service.get_session(session_token)
            if not session:
                raise HTTPException(status_code=401, detail="Invalid session")
            
            user = await self.user_service.get_user_by_id(session.user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Verify current password
            if not user.password_hash:
                raise HTTPException(status_code=400, detail="Password not set for this account")
            
            if not auth_utils.verify_password(password_data.current_password, user.password_hash):
                raise HTTPException(status_code=401, detail="Current password is incorrect")
            
            # Hash new password
            new_password_hash = auth_utils.hash_password(password_data.new_password)
            
            # Update user
            await self.user_service.update_user(user.id, {"password_hash": new_password_hash})
            
            return {"message": "Password changed successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Password change failed: {str(e)}")

    async def get_current_user(self, request: Request) -> User:
        """Get current authenticated user"""
        session_token = request.cookies.get("session_token")
        if not session_token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        session = await self.user_service.get_session(session_token)
        if not session:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        user = await self.user_service.get_user_by_id(session.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user