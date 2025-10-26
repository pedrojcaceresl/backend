from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
import uuid

class Event(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    organizer: str
    date: datetime  # Changed from event_date to match database
    location: str
    category: str
    is_free: Optional[bool] = True
    max_attendees: Optional[int] = None
    url: Optional[str] = None
    is_online: Optional[bool] = None
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))