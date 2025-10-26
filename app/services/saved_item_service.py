from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List, Dict, Any
from ..models import SavedItem

class SavedItemService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.saved_items

    async def save_item(self, saved_item: SavedItem) -> SavedItem:
        """Save an item for user"""
        await self.collection.insert_one(saved_item.dict())
        return saved_item

    async def is_item_saved(self, user_id: str, item_id: str, item_type: str) -> bool:
        """Check if item is already saved by user"""
        existing = await self.collection.find_one({
            "user_id": user_id,
            "item_id": item_id,
            "item_type": item_type
        })
        return existing is not None

    async def unsave_item(self, user_id: str, item_id: str, item_type: str) -> bool:
        """Remove item from saved items"""
        result = await self.collection.delete_one({
            "user_id": user_id,
            "item_id": item_id,
            "item_type": item_type
        })
        return result.deleted_count > 0

    async def get_user_saved_items(self, user_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get all saved items for user, grouped by type"""
        saved_items = await self.collection.find({"user_id": user_id}).to_list(length=None)
        
        result = {
            "courses": [],
            "events": [],
            "jobs": []
        }
        
        for item in saved_items:
            if item["item_type"] == "course":
                result["courses"].append(item["item_data"])
            elif item["item_type"] == "event":
                result["events"].append(item["item_data"])
            elif item["item_type"] == "job":
                result["jobs"].append(item["item_data"])
        
        return result