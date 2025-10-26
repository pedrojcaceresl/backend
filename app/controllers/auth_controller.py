from fastapi import HTTPException, Request, Response
from datetime import datetime, timezone, timedelta
import requests
from ..models import User, Session
from ..services import UserService
from ..core import settings

class AuthController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def complete_auth(self, session_id: str, response: Response) -> dict:
        """Complete authentication flow"""
        if not session_id:
            raise HTTPException(status_code=400, detail="Session ID required")
        
        try:
            auth_response = requests.get(
                f"{settings.AUTH_API_BASE_URL}/session-data",
                headers={"X-Session-ID": session_id}
            )
            auth_response.raise_for_status()
            auth_data = auth_response.json()
            
            # Check if user exists
            existing_user = await self.user_service.get_user_by_email(auth_data["email"])
            if not existing_user:
                # Create new user
                user = User(
                    email=auth_data["email"],
                    name=auth_data["name"],
                    picture=auth_data.get("picture")
                )
                await self.user_service.create_user(user)
            else:
                user = existing_user
            
            # Create session
            session = Session(
                user_id=user.id,
                session_token=auth_data["session_token"],
                expires_at=datetime.now(timezone.utc) + timedelta(days=settings.SESSION_EXPIRE_DAYS)
            )
            await self.user_service.create_session(session)
            
            # Set cookie with proper development settings
            response.set_cookie(
                key="session_token",
                value=session.session_token,
                path="/",
                httponly=True,
                secure=False,  # Set to False for development (HTTP)
                samesite="lax",  # Changed from "none" to "lax" for same-origin requests
                max_age=settings.SESSION_EXPIRE_DAYS*24*60*60
            )
            
            return {"user": user, "message": "Authentication completed"}
        
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

    async def logout(self, request: Request, response: Response) -> dict:
        """Logout user"""
        session_token = request.cookies.get("session_token")
        if session_token:
            await self.user_service.delete_session(session_token)
        
        response.delete_cookie("session_token", path="/", samesite="lax")
        return {"message": "Logged out successfully"}