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

# PUT SPECIFIC ROUTES FIRST TO AVOID CONFLICTS
@router.get("/stats", response_model=SavedItemStats, summary="Get saved items statistics")
async def get_saved_items_stats(
    current_user: User = Depends(require_auth)
):
    """
    Get statistics about user's saved items.
    
    Returns counts by item type.
    """
    return await saved_item_controller.get_saved_items_stats(current_user.id)

@router.get("/legacy", summary="Get saved items (Legacy format)")
async def get_saved_items_legacy(
    current_user: User = Depends(require_auth)
):
    """
    Get user's saved items in legacy format (grouped by type).
    
    Returns saved items grouped by type for backwards compatibility.
    """
    return await saved_item_controller.get_saved_items_legacy(current_user.id)

@router.get("/check/{item_type}/{item_id}", summary="Check if item is saved")
async def check_if_saved(
    item_type: SavedItemType = Path(..., description="Type of item"),
    item_id: str = Path(..., description="ID of the item"),
    current_user: User = Depends(require_auth)
):
    """
    Check if a specific item is already saved by the user.
    """
    return await saved_item_controller.check_if_saved(current_user.id, item_id, item_type)

@router.post("/toggle/{item_type}/{item_id}", summary="Toggle save status")
async def toggle_save_status(
    item_type: SavedItemType = Path(..., description="Type of item"),
    item_id: str = Path(..., description="ID of the item"),
    current_user: User = Depends(require_auth)
):
    """
    Toggle the save status of an item (save if not saved, unsave if saved).
    """
    return await saved_item_controller.toggle_save_status(current_user.id, item_id, item_type)

@router.post("/bulk", response_model=BulkSaveResponse, summary="Bulk save items")
async def bulk_save_items(
    bulk_request: BulkSaveRequest,
    current_user: User = Depends(require_auth)
):
    """
    Save multiple items at once.
    
    Useful for saving multiple selections or importing saved items.
    """
    return await saved_item_controller.bulk_save_items(current_user.id, bulk_request)

# GENERAL ENDPOINTS (PUT AFTER SPECIFIC ONES)
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

@router.delete("/{saved_item_id}", summary="Remove saved item")
async def remove_saved_item(
    saved_item_id: str = Path(..., description="Saved item ID"),
    current_user: User = Depends(require_auth)
):
    """
    Remove a specific saved item by its ID.
    """
    return await saved_item_controller.remove_saved_item(saved_item_id, current_user.id)

@router.delete("/unsave/{item_type}/{item_id}", summary="Unsave item by type and ID")
async def unsave_item(
    item_type: SavedItemType = Path(..., description="Type of item"),
    item_id: str = Path(..., description="ID of the item"),
    current_user: User = Depends(require_auth)
):
    """
    Remove an item from saved items using item type and ID.
    """
    return await saved_item_controller.unsave_item(current_user.id, item_id, item_type)