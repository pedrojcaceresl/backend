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
    current_user: User = Depends(require_auth)
):
    """
    Get all applications submitted by the current user.
    
    Returns a paginated list of applications with basic job information.
    """
    return await application_controller.get_user_applications(current_user.id, skip, limit)

@router.get("/stats", response_model=ApplicationStats, summary="Get application statistics")
async def get_application_stats(
    current_user: User = Depends(require_auth)
):
    """
    Get application statistics for the current user.
    
    Returns counts of applications by status.
    """
    return await application_controller.get_application_stats(current_user.id)

@router.get("/{application_id}", response_model=ApplicationWithJobDetails, summary="Get application details")
async def get_application_detail(
    application_id: str = Path(..., description="Application ID"),
    current_user: User = Depends(require_auth)
):
    """
    Get detailed information about a specific application.
    
    Includes complete job details and application status.
    """
    return await application_controller.get_application_detail(application_id, current_user.id)

@router.put("/{application_id}/withdraw", summary="Withdraw application")
async def withdraw_application(
    application_id: str = Path(..., description="Application ID"),
    current_user: User = Depends(require_auth)
):
    """
    Withdraw an application (sets status to 'withdrawn').
    
    Only the applicant can withdraw their own application.
    """
    return await application_controller.withdraw_application(application_id, current_user.id)

@router.delete("/{application_id}", summary="Delete application")
async def delete_application(
    application_id: str = Path(..., description="Application ID"),
    current_user: User = Depends(require_auth)
):
    """
    Delete an application completely.
    
    Only the applicant can delete their own application.
    """
    return await application_controller.delete_application(application_id, current_user.id)

# Company endpoints
@router.get("/company/received", response_model=List[ApplicationResponse], summary="Get received applications (Company)")
async def get_company_applications(
    job_id: Optional[str] = Query(None, description="Filter by specific job ID"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    current_user: User = Depends(require_company)
):
    """
    Get applications received for company's job postings.
    
    Only accessible by company users. Can filter by specific job.
    """
    return await application_controller.get_company_applications(current_user.id, job_id, skip, limit)

@router.put("/{application_id}/status", summary="Update application status (Company)")
async def update_application_status(
    application_id: str = Path(..., description="Application ID"),
    status_update: ApplicationStatusUpdate = Body(...),
    current_user: User = Depends(require_company)
):
    """
    Update the status of an application.
    
    Only accessible by company users for their own job postings.
    
    Available statuses:
    - applied: Initial status
    - in_review: Application is being reviewed
    - interview: Interview scheduled
    - offer: Job offer extended
    - accepted: Offer accepted
    - rejected: Application rejected
    """
    return await application_controller.update_application_status_by_company(
        application_id, status_update, current_user.id
    )

@router.put("/bulk/status", summary="Bulk update application statuses (Company)")
async def bulk_update_application_status(
    application_ids: List[str] = Body(..., description="List of application IDs"),
    new_status: ApplicationStatus = Body(..., description="New status to apply"),
    current_user: User = Depends(require_company)
):
    """
    Update the status of multiple applications at once.
    
    Useful for bulk actions like rejecting multiple applications.
    Only accessible by company users for their own job postings.
    """
    return await application_controller.bulk_update_applications(
        application_ids, new_status, current_user.id
    )

# Additional utility endpoints
@router.get("/job/{job_id}/applications", response_model=List[ApplicationResponse], summary="Get applications for specific job (Company)")
async def get_job_applications(
    job_id: str = Path(..., description="Job ID"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    current_user: User = Depends(require_company)
):
    """
    Get all applications for a specific job posting.
    
    Only accessible by the company that owns the job.
    """
    return await application_controller.get_company_applications(current_user.id, job_id, skip, limit)

@router.get("/status/{status}/count", summary="Count applications by status")
async def count_applications_by_status(
    status: ApplicationStatus = Path(..., description="Application status"),
    current_user: User = Depends(require_auth)
):
    """
    Count applications by specific status for the current user.
    """
    stats = await application_controller.get_application_stats(current_user.id)
    
    status_counts = {
        ApplicationStatus.APPLIED: stats.pending_applications,
        ApplicationStatus.IN_REVIEW: stats.pending_applications,
        ApplicationStatus.INTERVIEW: stats.interviews_scheduled,
        ApplicationStatus.ACCEPTED: stats.approved_applications,
        ApplicationStatus.REJECTED: stats.rejected_applications
    }
    
    return {
        "status": status,
        "count": status_counts.get(status, 0)
    }