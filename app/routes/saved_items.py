from fastapi import APIRouter, Depends, Query, Path, Body
from typing import List, Optional
from app.models.saved_item import (
    SavedItemCreate, 
    SavedItemResponse, 
    SavedItemStats,
    BulkSaveRequest,
    BulkSaveResponse
)
from app.models.enums import SavedItemType
from app.models.user import User
from app.controllers.saved_item_controller import SavedItemController
from app.core.dependencies import require_auth

# Create router
router = APIRouter(prefix="/saved-items", tags=["Saved Items"])

# Initialize controller
saved_item_controller = SavedItemController()

@router.post("/", response_model=SavedItemResponse, summary="Save an item")
async def save_item(
    item_data: SavedItemCreate,
    current_user: User = Depends(require_auth)
):
    """
    Save an item (job, course, event, or company) to user's favorites.
    
    - **item_type**: Type of item (job, course, event, company)
    - **item_id**: ID of the item to save
    """
    return await saved_item_controller.save_item(current_user.id, item_data)

@router.get("/", response_model=List[SavedItemResponse], summary="Get saved items")
async def get_saved_items(
    item_type: Optional[SavedItemType] = Query(None, description="Filter by item type"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    current_user: User = Depends(require_auth)
):
    """
    Get user's saved items with optional filtering by type.
    
    Returns a paginated list of saved items with basic information.
    """
    return await saved_item_controller.get_saved_items(current_user.id, item_type, skip, limit)

@router.get("/legacy", summary="Get saved items (Legacy format)")
async def get_saved_items_legacy(
    current_user: User = Depends(require_auth)
):
    """
    Get saved items grouped by type in legacy format.
    
    Returns: {courses: [...], events: [...], jobs: [...], companies: [...]}
    
    Maintained for backward compatibility.
    """
    return await saved_item_controller.get_saved_items_legacy(current_user.id)

@router.get("/stats", response_model=SavedItemStats, summary="Get saved items statistics")
async def get_saved_items_stats(
    current_user: User = Depends(require_auth)
):
    """
    Get statistics about user's saved items.
    
    Returns counts by item type and total count.
    """
    return await saved_item_controller.get_saved_item_stats(current_user.id)

@router.delete("/{saved_item_id}", summary="Remove saved item")
async def remove_saved_item(
    saved_item_id: str = Path(..., description="Saved item ID"),
    current_user: User = Depends(require_auth)
):
    """
    Remove an item from saved list using the saved item ID.
    
    This removes the specific saved item record.
    """
    return await saved_item_controller.remove_saved_item(saved_item_id, current_user.id)

@router.delete("/item/{item_type}/{item_id}", summary="Unsave item by ID and type")
async def unsave_item(
    item_type: SavedItemType = Path(..., description="Type of item"),
    item_id: str = Path(..., description="Item ID"),
    current_user: User = Depends(require_auth)
):
    """
    Remove an item from saved list using item ID and type.
    
    Alternative way to remove saved items when you know the original item.
    """
    return await saved_item_controller.unsave_item(current_user.id, item_id, item_type)

@router.get("/check/{item_type}/{item_id}", summary="Check if item is saved")
async def check_if_saved(
    item_type: SavedItemType = Path(..., description="Type of item"),
    item_id: str = Path(..., description="Item ID"),
    current_user: User = Depends(require_auth)
):
    """
    Check if a specific item is saved by the user.
    
    Useful for UI to show saved/unsaved state.
    """
    return await saved_item_controller.check_if_saved(current_user.id, item_id, item_type)

@router.post("/toggle/{item_type}/{item_id}", summary="Toggle save status")
async def toggle_save_item(
    item_type: SavedItemType = Path(..., description="Type of item"),
    item_id: str = Path(..., description="Item ID"),
    current_user: User = Depends(require_auth)
):
    """
    Toggle the save status of an item.
    
    - If item is saved: removes it from saved list
    - If item is not saved: adds it to saved list
    
    Convenient for save/unsave buttons in UI.
    """
    return await saved_item_controller.toggle_save_item(current_user.id, item_id, item_type)

@router.post("/bulk", response_model=BulkSaveResponse, summary="Bulk save items")
async def bulk_save_items(
    bulk_request: BulkSaveRequest,
    current_user: User = Depends(require_auth)
):
    """
    Save multiple items at once.
    
    Useful for importing favorites or bulk actions.
    Returns summary of successful and failed saves.
    """
    return await saved_item_controller.bulk_save_items(current_user.id, bulk_request)

@router.delete("/clear", summary="Clear saved items")
async def clear_saved_items(
    item_type: Optional[SavedItemType] = Query(None, description="Clear only items of this type"),
    current_user: User = Depends(require_auth)
):
    """
    Clear all saved items or items of a specific type.
    
    - If item_type is provided: clears only items of that type
    - If item_type is None: clears all saved items
    
    Use with caution - this action cannot be undone.
    """
    return await saved_item_controller.clear_saved_items(current_user.id, item_type)

# Specific type endpoints for convenience
@router.get("/jobs", response_model=List[SavedItemResponse], summary="Get saved jobs")
async def get_saved_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_auth)
):
    """Get only saved jobs."""
    return await saved_item_controller.get_saved_items(current_user.id, SavedItemType.JOB, skip, limit)

@router.get("/courses", response_model=List[SavedItemResponse], summary="Get saved courses")
async def get_saved_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_auth)
):
    """Get only saved courses."""
    return await saved_item_controller.get_saved_items(current_user.id, SavedItemType.COURSE, skip, limit)

@router.get("/events", response_model=List[SavedItemResponse], summary="Get saved events")
async def get_saved_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_auth)
):
    """Get only saved events."""
    return await saved_item_controller.get_saved_items(current_user.id, SavedItemType.EVENT, skip, limit)

@router.get("/companies", response_model=List[SavedItemResponse], summary="Get saved companies")
async def get_saved_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_auth)
):
    """Get only saved companies."""
    return await saved_item_controller.get_saved_items(current_user.id, SavedItemType.COMPANY, skip, limit)