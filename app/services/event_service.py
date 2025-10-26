from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from datetime import datetime, timezone
from ..models import Event

class EventService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.events

    async def get_events(self, category: Optional[str] = None, limit: int = 20) -> List[Event]:
        """Get upcoming events with optional category filter"""
        query = {"event_date": {"$gte": datetime.now(timezone.utc)}}
        if category:
            query["category"] = category
        
        events_data = await self.collection.find(query).sort("event_date", 1).limit(limit).to_list(length=None)
        return [Event(**event) for event in events_data]

    async def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """Get event by ID"""
        event_data = await self.collection.find_one({"id": event_id})
        return Event(**event_data) if event_data else None

    async def create_event(self, event: Event) -> Event:
        """Create new event"""
        await self.collection.insert_one(event.dict())
        return event