from fastapi import APIRouter, Depends
from typing import Optional, List, Dict, Any
from ..controllers import JobController
from ..services import JobService, UserService
from ..core import get_database, require_auth, require_company
from ..models import User, JobVacancy, JobApplication, JobModality, JobType

router = APIRouter(prefix="/jobs", tags=["Jobs"])

async def get_job_controller():
    db = await get_database()
    job_service = JobService(db)
    user_service = UserService(db)
    return JobController(job_service, user_service)

@router.get("", response_model=List[JobVacancy])
async def get_jobs(
    modality: Optional[JobModality] = None,
    job_type: Optional[JobType] = None,
    skills: Optional[str] = None,
    limit: int = 20,
    controller: JobController = Depends(get_job_controller)
):
    """Get job vacancies with filters"""
    return await controller.get_jobs(modality, job_type, skills, limit)

@router.post("", response_model=JobVacancy)
async def create_job(
    job_data: JobVacancy, 
    user: User = Depends(require_company),
    controller: JobController = Depends(get_job_controller)
):
    """Create new job vacancy (company only)"""
    return await controller.create_job(job_data, user)

@router.get("/{job_id}", response_model=JobVacancy)
async def get_job(
    job_id: str,
    controller: JobController = Depends(get_job_controller)
):
    """Get job by ID"""
    return await controller.get_job_by_id(job_id)

@router.post("/{job_id}/apply")
async def apply_to_job(
    job_id: str,
    application_data: Dict[str, Any],
    user: User = Depends(require_auth),
    controller: JobController = Depends(get_job_controller)
):
    """Apply to job vacancy"""
    return await controller.apply_to_job(job_id, application_data, user)

@router.get("/feed/company")
async def get_company_jobs_feed(
    limit: int = 20,
    controller: JobController = Depends(get_job_controller)
):
    """Get jobs for social feed"""
    return await controller.get_company_jobs_feed(limit)