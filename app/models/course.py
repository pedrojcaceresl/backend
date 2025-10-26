from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
import uuid

class Course(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    provider: str
    url: str
    language: str = "es"
    has_spanish_subtitles: bool = False
    category: str
    is_free: bool = True
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))