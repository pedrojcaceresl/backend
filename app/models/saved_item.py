from datetime import datetime, timezone
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field
from app.models.enums import SavedItemType
import uuid

class SavedItemBase(BaseModel):
    """Base model for saved items"""
    item_type: SavedItemType = Field(..., description="Tipo de elemento (job, course, event, company)")
    item_id: str = Field(..., description="ID del elemento guardado")

class SavedItemCreate(SavedItemBase):
    """Model for creating saved items"""
    pass

class SavedItem(BaseModel):
    """Complete saved item model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    item_id: str
    item_type: SavedItemType  # Using enum instead of string
    item_data: Dict[str, Any]  # Store the full item data
    saved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SavedItemResponse(SavedItemBase):
    """Model for saved item responses"""
    id: str = Field(..., description="ID único del elemento guardado")
    user_id: str = Field(..., description="ID del usuario")
    saved_date: datetime = Field(default_factory=datetime.now, description="Fecha cuando se guardó")
    
    # Datos del elemento guardado (para mostrar en listados)
    item_title: Optional[str] = Field(None, description="Título del elemento")
    item_description: Optional[str] = Field(None, description="Descripción")
    item_image: Optional[str] = Field(None, description="Imagen del elemento")
    
    # Datos específicos según el tipo
    company_name: Optional[str] = Field(None, description="Nombre de empresa (para jobs)")
    job_type: Optional[str] = Field(None, description="Tipo de trabajo")
    modality: Optional[str] = Field(None, description="Modalidad de trabajo")
    event_date: Optional[datetime] = Field(None, description="Fecha del evento")
    course_provider: Optional[str] = Field(None, description="Proveedor del curso")
    is_free: Optional[bool] = Field(None, description="Si es gratis")
    
    class Config:
        from_attributes = True

class SavedItemWithDetails(SavedItemResponse):
    """Saved item with complete information"""
    item_data: Dict[str, Any] = Field(default_factory=dict, description="Datos completos del elemento")

class SavedItemStats(BaseModel):
    """Saved items statistics"""
    total_saved: int = 0
    saved_jobs: int = 0
    saved_courses: int = 0
    saved_events: int = 0
    saved_companies: int = 0

class BulkSaveRequest(BaseModel):
    """Model for bulk saving items"""
    items: List[SavedItemCreate] = Field(..., description="Lista de elementos a guardar")

class BulkSaveResponse(BaseModel):
    """Response for bulk save operations"""
    saved_count: int = Field(..., description="Número de elementos guardados")
    skipped_count: int = Field(..., description="Número de elementos omitidos (ya guardados)")
    errors: List[str] = Field(default_factory=list, description="Errores encontrados")