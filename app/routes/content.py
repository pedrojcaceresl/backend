from fastapi import APIRouter, Depends
from typing import Optional, List
from ..controllers import ContentController  
from ..services import CourseService, EventService, SavedItemService, JobService
from ..core import get_database, require_auth
from ..models import User, Course, Event

router = APIRouter(tags=["Content"])

async def get_content_controller():
    db = await get_database()
    course_service = CourseService(db)
    event_service = EventService(db)
    saved_item_service = SavedItemService(db)
    return ContentController(course_service, event_service, saved_item_service)

async def get_job_service():
    db = await get_database()
    return JobService(db)

@router.get("/courses", response_model=List[Course])
async def get_courses(
    category: Optional[str] = None, 
    search: Optional[str] = None,
    limit: int = 20,
    controller: ContentController = Depends(get_content_controller)
):
    """Get courses with optional category and search filters"""
    return await controller.get_courses(category, limit, search)

@router.get("/events", response_model=List[Event])
async def get_events(
    category: Optional[str] = None, 
    search: Optional[str] = None,
    limit: int = 20,
    controller: ContentController = Depends(get_content_controller)
):
    """Get upcoming events with optional category and search filters"""
    return await controller.get_events(category, limit, search)

@router.post("/saved-items")
async def save_item(
    item_id: str,
    item_type: str,
    user: User = Depends(require_auth),
    controller: ContentController = Depends(get_content_controller),
    job_service: JobService = Depends(get_job_service)
):
    """Save an item for user"""
    if item_type == "job":
        # Handle job saving specially
        from ..models import SavedItem
        from ..services import SavedItemService
        
        # Check if already saved
        saved_item_service = SavedItemService(await get_database())
        if await saved_item_service.is_item_saved(user.id, item_id, item_type):
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Item already saved")
        
        # Get job data
        job_data = await job_service.get_job_by_id(item_id)
        if not job_data:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Job not found")
        
        saved_item = SavedItem(
            user_id=user.id,
            item_id=item_id,
            item_type=item_type,
            item_data=job_data.dict()
        )
        
        await saved_item_service.save_item(saved_item)
        return {"message": "Item saved successfully"}
    else:
        return await controller.save_item(item_id, item_type, user)

@router.delete("/saved-items/{item_id}")
async def unsave_item(
    item_id: str, 
    item_type: str, 
    user: User = Depends(require_auth),
    controller: ContentController = Depends(get_content_controller)
):
    """Remove item from saved items"""
    return await controller.unsave_item(item_id, item_type, user)

@router.get("/saved-items")
async def get_saved_items(
    user: User = Depends(require_auth),
    controller: ContentController = Depends(get_content_controller)
):
    """Get all saved items for user"""
    return await controller.get_saved_items(user)