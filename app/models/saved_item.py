from pydantic import BaseModel, Field
from typing import Dict, Any
from datetime import datetime, timezone
import uuid

class SavedItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    item_id: str
    item_type: str  # 'course', 'event', 'job'
    item_data: Dict[str, Any]  # Store the full item data
    saved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))