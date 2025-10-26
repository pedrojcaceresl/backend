from typing import List, Optional
from fastapi import HTTPException, status
from app.models.saved_item import (
    SavedItemCreate, 
    SavedItemResponse, 
    SavedItemWithDetails,
    SavedItemStats,
    BulkSaveRequest,
    BulkSaveResponse
)
from app.models.enums import SavedItemType
from app.services.saved_item_service import SavedItemService
from app.core.database import get_database

class SavedItemController:
    def __init__(self):
        self.saved_item_service = None

    def _get_service(self):
        if not self.saved_item_service:
            self.saved_item_service = SavedItemService()
        return self.saved_item_service

    async def save_item(self, user_id: str, item_data: SavedItemCreate) -> SavedItemResponse:
        """Save an item to user's favorites"""
        try:
            return await self._get_service().save_item(user_id, item_data)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error saving item: {str(e)}"
            )

    async def get_saved_items(self, user_id: str, item_type: Optional[SavedItemType] = None, skip: int = 0, limit: int = 20) -> List[SavedItemResponse]:
        """Get user's saved items"""
        try:
            return await self._get_service().get_user_saved_items(user_id, item_type, skip, limit)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving saved items: {str(e)}"
            )

    async def get_saved_items_legacy(self, user_id: str) -> dict:
        """Get saved items grouped by type (legacy format for backward compatibility)"""
        try:
            return await self._get_service().get_user_saved_items_legacy(user_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving saved items: {str(e)}"
            )

    async def remove_saved_item(self, saved_item_id: str, user_id: str) -> dict:
        """Remove item from saved list by saved item ID"""
        try:
            success = await self._get_service().remove_saved_item_by_id(saved_item_id, user_id)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Saved item not found"
                )
            
            return {"message": "Item removed from saved list successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error removing saved item: {str(e)}"
            )

    async def unsave_item(self, user_id: str, item_id: str, item_type: SavedItemType) -> dict:
        """Remove item from saved list by item ID and type"""
        try:
            success = await self._get_service().unsave_item(user_id, item_id, item_type)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Item not found in saved list"
                )
            
            return {"message": "Item removed from saved list successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error removing item from saved list: {str(e)}"
            )

    async def check_if_saved(self, user_id: str, item_id: str, item_type: SavedItemType) -> dict:
        """Check if item is saved by user"""
        try:
            is_saved = await self._get_service().is_item_saved(user_id, item_id, item_type)
            return {
                "is_saved": is_saved,
                "item_id": item_id,
                "item_type": item_type
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error checking saved status: {str(e)}"
            )

    async def get_saved_item_stats(self, user_id: str) -> SavedItemStats:
        """Get saved items statistics"""
        try:
            return await self._get_service().get_saved_items_stats(user_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving saved items stats: {str(e)}"
            )

    async def bulk_save_items(self, user_id: str, bulk_request: BulkSaveRequest) -> BulkSaveResponse:
        """Save multiple items at once"""
        try:
            if not bulk_request.items:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No items provided for bulk save"
                )
            
            return await self._get_service().bulk_save_items(user_id, bulk_request)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error in bulk save operation: {str(e)}"
            )

    async def toggle_save_item(self, user_id: str, item_id: str, item_type: SavedItemType) -> dict:
        """Toggle save status of an item (save if not saved, unsave if saved)"""
        try:
            is_saved = await self._get_service().is_item_saved(user_id, item_id, item_type)
            
            if is_saved:
                # Unsave the item
                success = await self._get_service().unsave_item(user_id, item_id, item_type)
                if success:
                    return {
                        "message": "Item removed from saved list",
                        "action": "unsaved",
                        "is_saved": False
                    }
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to remove item from saved list"
                    )
            else:
                # Save the item
                item_data = SavedItemCreate(item_id=item_id, item_type=item_type)
                saved_item = await self._get_service().save_item(user_id, item_data)
                return {
                    "message": "Item added to saved list",
                    "action": "saved",
                    "is_saved": True,
                    "saved_item": saved_item
                }
        
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error toggling save status: {str(e)}"
            )

    async def clear_saved_items(self, user_id: str, item_type: Optional[SavedItemType] = None) -> dict:
        """Clear all saved items or items of specific type"""
        try:
            # Get items to delete
            items_to_delete = await self._get_service().get_user_saved_items(
                user_id, item_type, skip=0, limit=1000  # Get all items
            )
            
            deleted_count = 0
            for item in items_to_delete:
                success = await self._get_service().remove_saved_item_by_id(item.id, user_id)
                if success:
                    deleted_count += 1
            
            message = f"Cleared {deleted_count} saved items"
            if item_type:
                message += f" of type {item_type}"
            
            return {
                "message": message,
                "deleted_count": deleted_count
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error clearing saved items: {str(e)}"
            )