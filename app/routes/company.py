from fastapi import APIRouter, Depends
from typing import Dict, List
from ..controllers import JobController
from ..services import JobService, UserService
from ..core import get_database, require_company
from ..models import User, JobApplication

router = APIRouter(prefix="/company", tags=["Company"])

async def get_job_controller():
    db = await get_database()
    job_service = JobService(db)
    user_service = UserService(db)
    return JobController(job_service, user_service)

@router.get("/applications")
async def get_company_applications(
    user: User = Depends(require_company),
    controller: JobController = Depends(get_job_controller)
):
    """Get all applications for company jobs"""
    return await controller.get_company_applications(user)

@router.put("/applications/{application_id}/status")
async def update_application_status(
    application_id: str,
    status_data: Dict[str, str],
    user: User = Depends(require_company),
    controller: JobController = Depends(get_job_controller)
):
    """Update application status"""
    return await controller.update_application_status(application_id, status_data, user)