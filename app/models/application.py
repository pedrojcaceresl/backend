from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.enums import ApplicationStatus

class ApplicationBase(BaseModel):
    """Base model for applications"""
    job_id: str = Field(..., description="ID del trabajo al que se postula")
    cover_letter: Optional[str] = Field(None, description="Carta de presentación")
    resume_url: Optional[str] = Field(None, description="URL del CV subido")
    
class ApplicationCreate(ApplicationBase):
    """Model for creating applications"""
    pass

class ApplicationUpdate(BaseModel):
    """Model for updating applications"""
    status: Optional[ApplicationStatus] = None
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None

class ApplicationResponse(ApplicationBase):
    """Model for application responses"""
    id: str = Field(..., description="ID único de la postulación")
    user_id: str = Field(..., description="ID del usuario que postula")
    status: ApplicationStatus = Field(default=ApplicationStatus.APPLIED, description="Estado de la postulación")
    applied_date: datetime = Field(default_factory=datetime.now, description="Fecha de postulación")
    
    # Datos del trabajo (para mostrar en listados)
    job_title: Optional[str] = Field(None, description="Título del trabajo")
    company_name: Optional[str] = Field(None, description="Nombre de la empresa")
    job_type: Optional[str] = Field(None, description="Tipo de trabajo")
    modality: Optional[str] = Field(None, description="Modalidad")
    
    class Config:
        from_attributes = True

class ApplicationWithJobDetails(ApplicationResponse):
    """Application with complete job information"""
    job_description: Optional[str] = None
    requirements: Optional[List[str]] = None
    salary_range: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    skills_stack: Optional[List[str]] = None

class ApplicationStatusUpdate(BaseModel):
    """Model for status updates by companies"""
    status: ApplicationStatus = Field(..., description="Nuevo estado de la postulación")
    notes: Optional[str] = Field(None, description="Notas adicionales del reclutador")

class ApplicationStats(BaseModel):
    """Application statistics"""
    total_applications: int = 0
    pending_applications: int = 0
    approved_applications: int = 0
    rejected_applications: int = 0
    interviews_scheduled: int = 0