from fastapi import HTTPException, Request, UploadFile
from pathlib import Path
from datetime import datetime, timezone
import uuid
import json
from ..models import User, UserCreate
from ..models.enums import UserRole
from ..services import UserService
from ..core import settings

class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def update_profile(self, request: Request, user: User) -> User:
        """Update user profile"""
        try:
            # Get raw request body
            body = await request.body()
            if not body:
                raise HTTPException(status_code=400, detail="Empty request body")
            
            # Parse JSON data
            raw_data = json.loads(body)
            
            # Validate and create UserCreate object
            profile_data = UserCreate(**raw_data)
            update_data = profile_data.dict(exclude_unset=True, exclude_none=True)
            
            # Handle role assignment explicitly
            if 'role' in raw_data and raw_data['role'] is not None:
                # Validate role value
                if raw_data['role'] in [role.value for role in UserRole]:
                    update_data['role'] = raw_data['role']
                else:
                    raise HTTPException(status_code=400, detail=f"Invalid role: {raw_data['role']}")
            
            # Add update timestamp
            update_data['updated_at'] = datetime.now(timezone.utc)
            
            # Perform the update
            updated_user = await self.user_service.update_user(user.id, update_data)
            
            if not updated_user:
                raise HTTPException(status_code=500, detail="Failed to update profile")
            
            return updated_user
            
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

    async def upload_file(self, file: UploadFile, file_type: str, user: User) -> dict:
        """Upload file for user"""
        try:
            # Validate file type
            valid_file_types = ["cv", "certificate", "degree"]
            if file_type not in valid_file_types:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid file type. Must be one of: {', '.join(valid_file_types)}"
                )
            
            # Validate file extension
            if not file.filename:
                raise HTTPException(status_code=400, detail="No filename provided")
                
            file_extension = file.filename.split('.')[-1].lower()
            if file_extension not in ['pdf']:
                raise HTTPException(
                    status_code=400, 
                    detail="Only PDF files are allowed"
                )
            
            # Check file size
            content = await file.read()
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE // (1024*1024)}MB"
                )
            
            # Create uploads directory if it doesn't exist
            uploads_dir = settings.UPLOAD_DIR / user.id
            uploads_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate unique filename
            unique_filename = f"{file_type}_{uuid.uuid4()}.{file_extension}"
            file_path = uploads_dir / unique_filename
            
            # Save file
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Prepare file info
            file_info = {
                "filename": file.filename,
                "file_path": str(file_path),
                "file_size": len(content),
                "uploaded_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Update user profile with file path
            success = await self.user_service.update_user_files(user.id, file_type, file_info)
            if not success:
                # Clean up uploaded file if database update fails
                if file_path.exists():
                    file_path.unlink()
                raise HTTPException(status_code=500, detail="Failed to update user profile")
            
            return {
                "success": True,
                "message": "File uploaded successfully",
                "filename": file.filename,
                "file_type": file_type,
                "file_size": len(content),
                "file_path": str(file_path)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")