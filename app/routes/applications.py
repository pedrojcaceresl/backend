from fastapi import APIRouter, Depends, Query, Path, Body
from typing import List, Optional
from app.models.application import (
    ApplicationCreate, 
    ApplicationResponse, 
    ApplicationWithJobDetails,
    ApplicationStatusUpdate,
    ApplicationStats
)
from app.models.enums import ApplicationStatus
from app.models.user import User
from app.controllers.application_controller import ApplicationController
from app.core.dependencies import require_auth, require_company

# Create router
router = APIRouter(prefix="/applications", tags=["Applications"])

# Dependency for getting controller
async def get_application_controller():
    return ApplicationController()

# Student/User endpoints
@router.post("/", response_model=ApplicationResponse, summary="Apply to a job")
async def apply_to_job(
    application_data: ApplicationCreate,
    current_user: User = Depends(require_auth),
    controller: ApplicationController = Depends(get_application_controller)
):
    """
    Submit an application for a job posting.
    
    - **job_id**: ID of the job to apply for
    - **cover_letter**: Optional cover letter
    - **resume_url**: Optional URL to uploaded resume
    """
    return await controller.apply_to_job(current_user.id, application_data)

@router.get("/", response_model=List[ApplicationResponse], summary="Get my applications")
async def get_my_applications(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    current_user: User = Depends(require_auth),
    controller: ApplicationController = Depends(get_application_controller)
):
    """
    Get all applications submitted by the current user.
    
    Returns a paginated list of applications with basic job information.
    """
    return await controller.get_user_applications(current_user.id, skip, limit)

@router.get("/stats", response_model=ApplicationStats, summary="Get application statistics")
async def get_application_stats(
    current_user: User = Depends(require_auth),
    controller: ApplicationController = Depends(get_application_controller)
):
    """
    Get statistics about the current user's applications.
    
    Returns counts of applications by status.
    """
    return await controller.get_application_stats(current_user.id)

@router.get("/{application_id}", response_model=ApplicationWithJobDetails, summary="Get application details")
async def get_application_detail(
    application_id: str = Path(..., description="Application ID"),
    current_user: User = Depends(require_auth),
    controller: ApplicationController = Depends(get_application_controller)
):
    """
    Get detailed information about a specific application.
    
    Includes full job information and application status.
    """
    return await controller.get_application_detail(application_id, current_user.id)

@router.put("/{application_id}/withdraw", summary="Withdraw application")
async def withdraw_application(
    application_id: str = Path(..., description="Application ID"),
    current_user: User = Depends(require_auth),
    controller: ApplicationController = Depends(get_application_controller)
):
    """
    Withdraw a submitted application.
    
    Only allows withdrawal if application is in 'applied' or 'in_review' status.
    """
    return await controller.withdraw_application(application_id, current_user.id)

@router.delete("/{application_id}", summary="Delete application")
async def delete_application(
    application_id: str = Path(..., description="Application ID"),
    current_user: User = Depends(require_auth),
    controller: ApplicationController = Depends(get_application_controller)
):
    """
    Delete an application.
    
    Only allows deletion if application is in 'withdrawn' or 'rejected' status.
    """
    return await controller.delete_application(application_id, current_user.id)

# Company/HR endpoints
@router.get("/company/jobs/{job_id}", response_model=List[ApplicationWithJobDetails], summary="Get applications for a job")
async def get_job_applications(
    job_id: str = Path(..., description="Job ID"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    current_user: User = Depends(require_company),
    controller: ApplicationController = Depends(get_application_controller)
):
    """
    Get all applications for a specific job posting.
    
    Only accessible to company users who own the job posting.
    """
    return await controller.get_company_applications(current_user.id, job_id, skip, limit)

@router.put("/company/{application_id}/status", response_model=ApplicationResponse, summary="Update application status")
async def update_application_status(
    application_id: str = Path(..., description="Application ID"),
    status_update: ApplicationStatusUpdate = Body(...),
    current_user: User = Depends(require_company),
    controller: ApplicationController = Depends(get_application_controller)
):
    """
    Update the status of an application.
    
    Only accessible to company users. Allows updating status and adding notes.
    """
    return await controller.update_application_status_by_company(
        application_id,
        status_update.status,
        current_user.id,
        status_update.notes
    )

@router.put("/company/bulk-update", summary="Bulk update application statuses")
async def bulk_update_applications(
    updates: List[ApplicationStatusUpdate] = Body(...),
    current_user: User = Depends(require_company),
    controller: ApplicationController = Depends(get_application_controller)
):
    """
    Update multiple application statuses in bulk.
    
    Only accessible to company users.
    """
    return await controller.bulk_update_applications(
        updates,
        current_user.id
    )

@router.get("/company/jobs", response_model=List[ApplicationWithJobDetails], summary="Get all company applications")
async def get_all_company_applications(
    job_id: Optional[str] = Query(None, description="Filter by job ID"),
    skip: int = Query(0, ge=0, description="Number of items to skip"), 
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    current_user: User = Depends(require_company),
    controller: ApplicationController = Depends(get_application_controller)
):
    """
    Get all applications for jobs owned by the current company.
    
    Optionally filter by specific job ID.
    """
    return await controller.get_company_applications(current_user.id, job_id, skip, limit)

@router.get("/company/stats", response_model=ApplicationStats, summary="Get company application statistics")
async def get_company_application_stats(
    current_user: User = Depends(require_company),
    controller: ApplicationController = Depends(get_application_controller)
):
    """
    Get application statistics for all jobs owned by the current company.
    """
    stats = await controller.get_application_stats(current_user.id)
    return stats