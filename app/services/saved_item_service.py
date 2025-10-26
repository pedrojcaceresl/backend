from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.saved_item import SavedItemCreate, SavedItemResponse, SavedItemWithDetails, SavedItemStats, BulkSaveRequest, BulkSaveResponse, SavedItem
from app.models.enums import SavedItemType
from app.core.database import get_database
import uuid

class SavedItemService:
    def __init__(self):
        self.db = None
        self.collection = None
        self.jobs_collection = None
        self.courses_collection = None
        self.events_collection = None
        self.users_collection = None

    async def _get_db(self):
        if not self.db:
            self.db = await get_database()
            self.collection = self.db.saved_items
            self.jobs_collection = self.db.job_vacancies
            self.courses_collection = self.db.courses
            self.events_collection = self.db.events
            self.users_collection = self.db.users
        return self.db

    async def save_item(self, user_id: str, item_data: SavedItemCreate) -> SavedItemResponse:
        """Save an item to user's saved list"""
        
        await self._get_db()  # Initialize database connection
        
        # Check if already saved
        existing = await self.collection.find_one({
            "user_id": user_id,
            "item_id": item_data.item_id,
            "item_type": item_data.item_type
        })
        
        if existing:
            raise ValueError("Este elemento ya está guardado")
        
        # Get item details based on type
        item_details = await self._get_item_details(item_data.item_type, item_data.item_id)
        if not item_details:
            raise ValueError("El elemento no existe")
        
        # Create saved item document
        saved_item_doc = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "item_id": item_data.item_id,
            "item_type": item_data.item_type,
            "saved_date": datetime.now(),
            "item_data": item_details,  # Store complete item data
            "created_at": datetime.now()
        }
        
        # Insert saved item
        await self.collection.insert_one(saved_item_doc)
        
        # Return response
        return await self._build_saved_item_response(saved_item_doc, item_details)

    async def get_user_saved_items(self, user_id: str, item_type: Optional[SavedItemType] = None, skip: int = 0, limit: int = 20) -> List[SavedItemResponse]:
        """Get user's saved items"""
        
        await self._get_db()  # Initialize database connection
        
        # Build filter
        filter_query = {"user_id": user_id}
        if item_type:
            filter_query["item_type"] = item_type
        
        # Get saved items
        cursor = self.collection.find(filter_query).sort("saved_date", -1).skip(skip).limit(limit)
        saved_items = []
        
        async for doc in cursor:
            item_details = doc.get("item_data", {})
            saved_item = await self._build_saved_item_response(doc, item_details)
            saved_items.append(saved_item)
        
        return saved_items

    async def is_item_saved(self, user_id: str, item_id: str, item_type: SavedItemType) -> bool:
        """Check if item is already saved by user"""
        
        await self._get_db()  # Initialize database connection
        
        doc = await self.collection.find_one({
            "user_id": user_id,
            "item_id": item_id,
            "item_type": item_type
        })
        
        return doc is not None

    async def unsave_item(self, user_id: str, item_id: str, item_type: SavedItemType) -> bool:
        """Remove item from saved items"""
        await self._get_db()  # Initialize database connection
        result = await self.collection.delete_one({
            "user_id": user_id,
            "item_id": item_id,
            "item_type": item_type
        })
        return result.deleted_count > 0

    async def remove_saved_item_by_id(self, saved_item_id: str, user_id: str) -> bool:
        """Remove item from saved list by saved item ID"""
        
        result = await self.collection.delete_one({
            "id": saved_item_id,
            "user_id": user_id
        })
        
        return result.deleted_count > 0

    async def get_user_saved_items_legacy(self, user_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get all saved items for user, grouped by type (legacy format)"""
        saved_items = await self.collection.find({"user_id": user_id}).to_list(length=None)
        
        result = {
            "courses": [],
            "events": [],
            "jobs": [],
            "companies": []
        }
        
        for item in saved_items:
            item_type = item["item_type"]
            if item_type == SavedItemType.COURSE:
                result["courses"].append(item["item_data"])
            elif item_type == SavedItemType.EVENT:
                result["events"].append(item["item_data"])
            elif item_type == SavedItemType.JOB:
                result["jobs"].append(item["item_data"])
            elif item_type == SavedItemType.COMPANY:
                result["companies"].append(item["item_data"])
        
        return result

    async def get_saved_items_stats(self, user_id: str) -> SavedItemStats:
        """Get saved items statistics"""
        
        await self._get_db()  # Initialize database connection
        
        pipeline = [
            {"$match": {"user_id": user_id}},
            {
                "$group": {
                    "_id": "$item_type",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        cursor = self.collection.aggregate(pipeline)
        stats_data = {stat["_id"]: stat["count"] async for stat in cursor}
        
        return SavedItemStats(
            total_saved=sum(stats_data.values()),
            saved_jobs=stats_data.get(SavedItemType.JOB, 0),
            saved_courses=stats_data.get(SavedItemType.COURSE, 0),
            saved_events=stats_data.get(SavedItemType.EVENT, 0),
            saved_companies=stats_data.get(SavedItemType.COMPANY, 0)
        )

    async def _get_item_details(self, item_type: SavedItemType, item_id: str) -> Optional[Dict[str, Any]]:
        """Get item details from appropriate collection"""
        
        if item_type == SavedItemType.JOB:
            item = await self.jobs_collection.find_one({"id": item_id})
        elif item_type == SavedItemType.COURSE:
            item = await self.courses_collection.find_one({"id": item_id})
        elif item_type == SavedItemType.EVENT:
            item = await self.events_collection.find_one({"id": item_id})
        elif item_type == SavedItemType.COMPANY:
            item = await self.users_collection.find_one({"id": item_id, "role": "empresa"})
        else:
            return None
        
        return item

    async def _build_saved_item_response(self, doc: Dict[str, Any], item_details: Dict[str, Any]) -> SavedItemResponse:
        """Build saved item response from document and item details"""
        
        # Extract common fields
        extracted_fields = await self._extract_item_fields(doc["item_type"], item_details)
        
        return SavedItemResponse(
            id=doc["id"],
            user_id=doc["user_id"],
            item_id=doc["item_id"],
            item_type=doc["item_type"],
            saved_date=doc["saved_date"],
            **extracted_fields
        )

    async def _extract_item_fields(self, item_type: SavedItemType, item_details: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant fields based on item type"""
        
        fields = {}
        
        if item_type == SavedItemType.JOB:
            fields.update({
                "item_title": item_details.get("title"),
                "item_description": item_details.get("description"),
                "company_name": item_details.get("company_name"),
                "job_type": item_details.get("job_type"),
                "modality": item_details.get("modality")
            })
            
        elif item_type == SavedItemType.COURSE:
            fields.update({
                "item_title": item_details.get("title"),
                "item_description": item_details.get("description"),
                "course_provider": item_details.get("provider"),
                "is_free": item_details.get("is_free")
            })
            
        elif item_type == SavedItemType.EVENT:
            fields.update({
                "item_title": item_details.get("title"),
                "item_description": item_details.get("description"),
                "event_date": item_details.get("date"),
                "is_free": item_details.get("is_free")
            })
            
        elif item_type == SavedItemType.COMPANY:
            fields.update({
                "item_title": item_details.get("company_name") or f"{item_details.get('first_name', '')} {item_details.get('last_name', '')}",
                "item_description": item_details.get("description"),
                "company_name": item_details.get("company_name")
            })
        
        return fields