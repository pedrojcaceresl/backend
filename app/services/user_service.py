from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from ..models import User, UserCreate, Session

class UserService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.users
        self.sessions_collection = db.sessions

    async def get_all_users(self) -> List[User]:
        """Get all users"""
        users_data = await self.collection.find({}).to_list(length=None)
        return [User(**user) for user in users_data]

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        user_data = await self.collection.find_one({"email": email})
        return User(**user_data) if user_data else None

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        user_data = await self.collection.find_one({"id": user_id})
        return User(**user_data) if user_data else None

    async def create_user(self, user: User) -> User:
        """Create new user"""
        await self.collection.insert_one(user.dict())
        return user

    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[User]:
        """Update user profile"""
        result = await self.collection.update_one(
            {"id": user_id}, 
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            updated_user = await self.collection.find_one({"id": user_id})
            return User(**updated_user) if updated_user else None
        return None

    async def create_session(self, session: Session) -> Session:
        """Create new session"""
        await self.sessions_collection.insert_one(session.dict())
        return session

    async def get_session_by_token(self, session_token: str) -> Optional[Session]:
        """Get session by token"""
        session_data = await self.sessions_collection.find_one({"session_token": session_token})
        return Session(**session_data) if session_data else None

    async def delete_session(self, session_token: str) -> bool:
        """Delete session"""
        result = await self.sessions_collection.delete_one({"session_token": session_token})
        return result.deleted_count > 0

    async def update_user_files(self, user_id: str, file_type: str, file_info: Dict[str, Any]) -> bool:
        """Update user file information"""
        if file_type == "certificate":
            # Add to certificate_files array
            result = await self.collection.update_one(
                {"id": user_id},
                {"$push": {"certificate_files": file_info}}
            )
        elif file_type == "degree":
            # Add to degree_files array
            result = await self.collection.update_one(
                {"id": user_id},
                {"$push": {"degree_files": file_info}}
            )
        else:
            # For CV, single file
            result = await self.collection.update_one(
                {"id": user_id},
                {"$set": {"cv_file_path": file_info["file_path"]}}
            )
        
        return result.modified_count > 0