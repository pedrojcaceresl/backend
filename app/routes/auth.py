from fastapi import APIRouter, Request, Response, Depends
from ..controllers import AuthController
from ..services import UserService
from ..core import get_database, require_auth
from ..models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

async def get_auth_controller():
    db = await get_database()
    user_service = UserService(db)
    return AuthController(user_service)

@router.post("/complete")
async def complete_auth(
    request: Request, 
    response: Response,
    controller: AuthController = Depends(get_auth_controller)
):
    """Complete authentication flow"""
    session_id = request.headers.get("X-Session-ID")
    return await controller.complete_auth(session_id, response)

@router.get("/me")
async def get_current_user_info(user: User = Depends(require_auth)):
    """Get current user information"""
    return user

@router.post("/logout")
async def logout(
    request: Request, 
    response: Response,
    controller: AuthController = Depends(get_auth_controller)
):
    """Logout user"""
    return await controller.logout(request, response)