from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
import uuid
from .enums import JobModality, JobType, ApplyType, ApplicationStatus

class JobVacancy(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    company_id: str
    company_name: str
    description: str
    requirements: List[str] = []
    modality: JobModality
    job_type: JobType
    seniority_level: str
    skills_stack: List[str] = []
    city: Optional[str] = None
    country: str = "Paraguay"
    salary_range: Optional[str] = None
    apply_type: ApplyType
    apply_url: Optional[str] = None
    is_active: bool = True
    knockout_questions: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class JobApplication(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str
    student_id: str
    student_name: str
    student_email: str
    cv_url: Optional[str] = None
    cover_letter: Optional[str] = None
    answers: dict = {}
    status: ApplicationStatus = ApplicationStatus.APPLIED
    notes: Optional[str] = None
    applied_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))