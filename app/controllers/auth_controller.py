from fastapi import HTTPException, Request, Response
from datetime import datetime, timezone, timedelta
import requests
from ..models import User, Session
from ..models.enums import UserRole
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
            # Get session data from external auth service
            auth_response = requests.get(
                f"{settings.AUTH_API_BASE_URL}/session-data",
                headers={"X-Session-ID": session_id}
            )
            auth_response.raise_for_status()
            auth_data = auth_response.json()
            
            # Validate required fields
            if not auth_data.get("email") or not auth_data.get("name"):
                raise HTTPException(status_code=400, detail="Missing required user data")
            
            # Check if user exists
            existing_user = await self.user_service.get_user_by_email(auth_data["email"])
            
            if not existing_user:
                # Create new user with STUDENT role by default
                user = User(
                    email=auth_data["email"],
                    name=auth_data["name"],
                    picture=auth_data.get("picture"),
                    role=UserRole.STUDENT,  # Default role
                    is_verified=True,  # Users authenticated via OAuth are verified
                    is_active=True
                )
                created_user = await self.user_service.create_user(user)
                if not created_user:
                    raise HTTPException(status_code=500, detail="Failed to create user")
                user = created_user
            else:
                # Update existing user info if needed
                update_data = {}
                if existing_user.name != auth_data["name"]:
                    update_data["name"] = auth_data["name"]
                if existing_user.picture != auth_data.get("picture"):
                    update_data["picture"] = auth_data.get("picture")
                if not existing_user.is_verified:
                    update_data["is_verified"] = True
                    
                if update_data:
                    user = await self.user_service.update_user(existing_user.id, update_data)
                else:
                    user = existing_user
            
            # Validate session token
            if not auth_data.get("session_token"):
                raise HTTPException(status_code=400, detail="Missing session token")
            
            # Create internal session
            session = Session(
                user_id=user.id,
                session_token=auth_data["session_token"],
                expires_at=datetime.now(timezone.utc) + timedelta(days=settings.SESSION_EXPIRE_DAYS)
            )
            
            created_session = await self.user_service.create_session(session)
            if not created_session:
                raise HTTPException(status_code=500, detail="Failed to create session")
            
            # Set secure cookie
            response.set_cookie(
                key="session_token",
                value=session.session_token,
                path="/",
                httponly=True,
                secure=False,  # Set to False for development (HTTP)
                samesite="lax",
                max_age=settings.SESSION_EXPIRE_DAYS*24*60*60
            )
            
            return {
                "user": user,
                "message": "Authentication completed successfully"
            }
        
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"External auth service error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")

    async def logout(self, request: Request, response: Response) -> dict:
        """Logout user"""
        session_token = request.cookies.get("session_token")
        if session_token:
            await self.user_service.delete_session(session_token)
        
        response.delete_cookie("session_token", path="/", samesite="lax")
        return {"message": "Logged out successfully"}