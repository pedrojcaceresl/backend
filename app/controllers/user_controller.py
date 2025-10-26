from fastapi import HTTPException, Request, UploadFile
from pathlib import Path
from datetime import datetime, timezone
import uuid
import json
from ..models import User, UserCreate
from ..services import UserService
from ..core import settings

class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def update_profile(self, request: Request, user: User) -> User:
        """Update user profile"""
        # Get raw request body to debug
        body = await request.body()
        print(f"=== RAW REQUEST BODY ===")
        print(f"Raw body: {body}")
        
        # Parse JSON manually to see exact data
        raw_data = json.loads(body)
        print(f"Parsed JSON: {raw_data}")
        print(f"Role in raw JSON: {raw_data.get('role', 'NOT PRESENT')}")
        
        # Try to create UserCreate object
        try:
            profile_data = UserCreate(**raw_data)
            print(f"UserCreate object created successfully: {profile_data}")
            print(f"Role in UserCreate: {profile_data.role}")
        except Exception as e:
            print(f"Error creating UserCreate: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")
        
        update_data = profile_data.dict(exclude_unset=True)
        
        # Debug logs
        print(f"=== PROFILE UPDATE DEBUG ===")
        print(f"Updating profile for user {user.id}")
        print(f"Current user role: {user.role}")
        print(f"Update data (exclude_unset): {update_data}")
        print(f"Role in update_data: {update_data.get('role', 'NOT PRESENT')}")
        
        # FORCE role processing if it exists in the raw data
        if 'role' in raw_data and raw_data['role'] is not None:
            update_data['role'] = raw_data['role']
            print(f"FORCING role assignment: {raw_data['role']}")
        
        # If no role is provided in update, preserve current role
        if 'role' not in update_data or update_data['role'] is None:
            print(f"No role in update data, preserving current role: {user.role}")
        else:
            print(f"Changing role from {user.role} to {update_data['role']}")
        
        # Perform the update
        updated_user = await self.user_service.update_user(user.id, update_data)
        print(f"Updated user role after database update: {updated_user.role if updated_user else 'None'}")
        print(f"=== END PROFILE UPDATE DEBUG ===")
        
        if not updated_user:
            raise HTTPException(status_code=500, detail="Failed to update profile")
        
        return updated_user

    async def upload_file(self, file: UploadFile, file_type: str, user: User) -> dict:
        """Upload file for user"""
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Create uploads directory if it doesn't exist
        uploads_dir = settings.UPLOAD_DIR / user.id
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1]
        unique_filename = f"{file_type}_{uuid.uuid4()}.{file_extension}"
        file_path = uploads_dir / unique_filename
        
        # Save file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Update user profile with file path
        file_info = {
            "filename": file.filename,
            "file_path": str(file_path),
            "uploaded_at": datetime.now(timezone.utc)
        }
        
        success = await self.user_service.update_user_files(user.id, file_type, file_info)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update user profile")
        
        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "file_type": file_type,
            "file_path": str(file_path)
        }