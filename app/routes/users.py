from fastapi import APIRouter, Request, Depends, UploadFile, File
from ..controllers import UserController
from ..services import UserService
from ..core import get_database, require_auth
from ..models import User

router = APIRouter(prefix="/users", tags=["Users"])

async def get_user_controller():
    db = await get_database()
    user_service = UserService(db)
    return UserController(user_service)

@router.put("/profile")
async def update_profile(
    request: Request, 
    user: User = Depends(require_auth),
    controller: UserController = Depends(get_user_controller)
):
    """Update user profile"""
    return await controller.update_profile(request, user)

@router.post("/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = "cv",  # cv, certificate, degree
    user: User = Depends(require_auth),
    controller: UserController = Depends(get_user_controller)
):
    """Upload file for user"""
    return await controller.upload_file(file, file_type, user)