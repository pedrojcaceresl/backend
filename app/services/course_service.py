from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from ..models import Course

class CourseService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.courses

    async def get_courses(self, category: Optional[str] = None, limit: int = 20, search: Optional[str] = None) -> List[Course]:
        """Get courses with optional category filter and search"""
        query = {}
        if category:
            query["category"] = category
        
        # Add search functionality
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"provider": {"$regex": search, "$options": "i"}}
            ]
        
        courses_data = await self.collection.find(query).limit(limit).to_list(length=None)
        return [Course(**course) for course in courses_data]

    async def get_course_by_id(self, course_id: str) -> Optional[Course]:
        """Get course by ID"""
        course_data = await self.collection.find_one({"id": course_id})
        return Course(**course_data) if course_data else None

    async def create_course(self, course: Course) -> Course:
        """Create new course"""
        await self.collection.insert_one(course.dict())
        return course