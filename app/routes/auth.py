from fastapi import APIRouter, Request, Response, Depends
from ..controllers.auth_controller_local import AuthController
from ..models.auth import UserRegister, UserLogin, PasswordUpdate
from ..services import UserService
from ..core import get_database, require_auth
from ..models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

async def get_auth_controller():
    db = await get_database()
    user_service = UserService(db)
    return AuthController(user_service)

@router.post("/register")
async def register(
    user_data: UserRegister,
    controller: AuthController = Depends(get_auth_controller)
):
    """Register a new user"""
    return await controller.register(user_data)

@router.post("/login")
async def login(
    user_data: UserLogin,
    response: Response,
    controller: AuthController = Depends(get_auth_controller)
):
    """Login with email and password"""
    return await controller.login(user_data, response)

@router.post("/complete")
async def complete_auth(
    request: Request, 
    response: Response,
    controller: AuthController = Depends(get_auth_controller)
):
    """Complete authentication flow (Legacy OAuth - deprecated)"""
    session_id = request.headers.get("X-Session-ID")
    return await controller.complete_auth(session_id, response)

@router.get("/me")
async def get_current_user_info(user: User = Depends(require_auth)):
    """Get current user information"""
    return user

@router.post("/change-password")
async def change_password(
    password_data: PasswordUpdate,
    request: Request,
    controller: AuthController = Depends(get_auth_controller)
):
    """Change user password"""
    return await controller.change_password(request, password_data)

@router.post("/logout")
async def logout(
    request: Request, 
    response: Response,
    controller: AuthController = Depends(get_auth_controller)
):
    """Logout user"""
    return await controller.logout(request, response)