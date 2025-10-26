from fastapi import HTTPException
from typing import Optional, List, Dict, Any
from ..models import Course, Event, SavedItem, User
from ..services import CourseService, EventService, SavedItemService

class ContentController:
    def __init__(
        self, 
        course_service: CourseService,
        event_service: EventService,
        saved_item_service: SavedItemService
    ):
        self.course_service = course_service
        self.event_service = event_service
        self.saved_item_service = saved_item_service

    async def get_courses(self, category: Optional[str] = None, limit: int = 20, search: Optional[str] = None) -> List[Course]:
        """Get courses with optional filters"""
        try:
            # Validate and clean parameters
            if limit <= 0:
                limit = 20
            if limit > 100:  # Prevent excessive queries
                limit = 100
                
            # Clean category filter - handle "todas las categorías" case
            if category and category.lower() in ["todas", "todas las categorias", "all", ""]:
                category = None
                
            return await self.course_service.get_courses(category, limit, search)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get courses: {str(e)}")

    async def get_course_by_id(self, course_id: str) -> Course:
        """Get a specific course by ID"""
        try:
            course = await self.course_service.get_course_by_id(course_id)
            if not course:
                raise HTTPException(status_code=404, detail="Course not found")
            return course
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get course: {str(e)}")

    async def get_events(self, category: Optional[str] = None, limit: int = 20, search: Optional[str] = None) -> List[Event]:
        """Get upcoming events with optional filters"""
        try:
            # Validate and clean parameters
            if limit <= 0:
                limit = 20
            if limit > 100:  # Prevent excessive queries
                limit = 100
                
            # Clean category filter - handle "todas las categorías" case
            if category and category.lower() in ["todas", "todas las categorias", "all", ""]:
                category = None
                
            return await self.event_service.get_events(category, limit, search)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get events: {str(e)}")

    async def get_event_by_id(self, event_id: str) -> Event:
        """Get a specific event by ID"""
        try:
            event = await self.event_service.get_event_by_id(event_id)
            if not event:
                raise HTTPException(status_code=404, detail="Event not found")
            return event
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get event: {str(e)}")

    async def save_item(self, item_id: str, item_type: str, user: User) -> Dict[str, str]:
        """Save an item for user"""
        # Check if already saved
        if await self.saved_item_service.is_item_saved(user.id, item_id, item_type):
            raise HTTPException(status_code=400, detail="Item already saved")
        
        # Get the item data
        item_data = None
        if item_type == "course":
            item_data = await self.course_service.get_course_by_id(item_id)
        elif item_type == "event":
            item_data = await self.event_service.get_event_by_id(item_id)
        elif item_type == "job":
            # This would need JobService import - we'll handle it in routes
            raise HTTPException(status_code=400, detail="Job saving handled separately")
        else:
            raise HTTPException(status_code=400, detail="Invalid item type")
        
        if not item_data:
            raise HTTPException(status_code=404, detail="Item not found")
        
        saved_item = SavedItem(
            user_id=user.id,
            item_id=item_id,
            item_type=item_type,
            item_data=item_data.dict()
        )
        
        await self.saved_item_service.save_item(saved_item)
        return {"message": "Item saved successfully"}

    async def unsave_item(self, item_id: str, item_type: str, user: User) -> Dict[str, str]:
        """Remove item from saved items"""
        success = await self.saved_item_service.unsave_item(user.id, item_id, item_type)
        if not success:
            raise HTTPException(status_code=404, detail="Saved item not found")
        
        return {"message": "Item removed from saved"}

    async def get_saved_items(self, user: User) -> Dict[str, List[Dict[str, Any]]]:
        """Get all saved items for user"""
        return await self.saved_item_service.get_user_saved_items(user.id)