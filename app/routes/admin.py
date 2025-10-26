from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from ..controllers import UserController
from ..services import UserService
from ..core import get_database, require_admin
from ..models import User, UserCreate
from ..models.enums import UserRole

router = APIRouter(prefix="/admin", tags=["Admin"])

async def get_user_controller():
    db = await get_database()
    user_service = UserService(db)
    return UserController(user_service)

@router.get("/users", response_model=List[User])
async def get_all_users(
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    limit: int = 50,
    admin_user: User = Depends(require_admin),
    controller: UserController = Depends(get_user_controller)
):
    """Get all users (admin only)"""
    try:
        # This would need to be implemented in UserController
        return await controller.get_all_users(role, is_active, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")

@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    new_role: UserRole,
    admin_user: User = Depends(require_admin),
    controller: UserController = Depends(get_user_controller)
):
    """Update user role (admin only)"""
    try:
        # Prevent admin from changing their own role to non-admin
        if user_id == admin_user.id and new_role != UserRole.ADMIN:
            raise HTTPException(
                status_code=400, 
                detail="Admin cannot change their own role"
            )
        
        update_data = {"role": new_role}
        updated_user = await controller.update_user_by_id(user_id, update_data)
        
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
            
        return {
            "message": "User role updated successfully",
            "user": updated_user
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user role: {str(e)}")

@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    is_active: bool,
    admin_user: User = Depends(require_admin),
    controller: UserController = Depends(get_user_controller)
):
    """Activate/deactivate user (admin only)"""
    try:
        # Prevent admin from deactivating themselves
        if user_id == admin_user.id and not is_active:
            raise HTTPException(
                status_code=400, 
                detail="Admin cannot deactivate their own account"
            )
        
        update_data = {"is_active": is_active}
        updated_user = await controller.update_user_by_id(user_id, update_data)
        
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
            
        status = "activated" if is_active else "deactivated"
        return {
            "message": f"User {status} successfully",
            "user": updated_user
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user status: {str(e)}")

@router.post("/create-admin")
async def create_admin_user(
    email: str,
    name: str,
    admin_user: User = Depends(require_admin)
):
    """Create admin user (existing admin only)"""
    try:
        db = await get_database()
        user_service = UserService(db)
        
        # Check if user already exists
        existing_user = await user_service.get_user_by_email(email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Create admin user
        new_admin = User(
            email=email,
            name=name,
            role=UserRole.ADMIN,
            is_verified=True,
            is_active=True
        )
        
        created_user = await user_service.create_user(new_admin)
        if not created_user:
            raise HTTPException(status_code=500, detail="Failed to create admin user")
        
        return {
            "message": "Admin user created successfully",
            "user": created_user
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create admin user: {str(e)}")