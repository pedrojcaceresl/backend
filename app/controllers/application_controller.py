from typing import List, Optional
from fastapi import HTTPException, status
from app.models.application import (
    ApplicationCreate, 
    ApplicationUpdate, 
    ApplicationResponse, 
    ApplicationWithJobDetails,
    ApplicationStatusUpdate,
    ApplicationStats
)
from app.models.enums import ApplicationStatus
from app.services.application_service import ApplicationService
from app.core.database import get_database

class ApplicationController:
    def __init__(self):
        self.application_service = None

    def _get_service(self):
        if not self.application_service:
            self.application_service = ApplicationService()
        return self.application_service

    async def apply_to_job(self, user_id: str, application_data: ApplicationCreate) -> ApplicationResponse:
        """Submit application for a job"""
        try:
            return await self._get_service().create_application(user_id, application_data)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating application: {str(e)}"
            )

    async def get_user_applications(self, user_id: str, skip: int = 0, limit: int = 20) -> List[ApplicationResponse]:
        """Get all applications for current user"""
        try:
            return await self._get_service().get_user_applications(user_id, skip, limit)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving applications: {str(e)}"
            )

    async def get_application_detail(self, application_id: str, user_id: str) -> ApplicationWithJobDetails:
        """Get detailed application information"""
        try:
            application = await self._get_service().get_application_by_id(application_id, user_id)
            if not application:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Application not found"
                )
            return application
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving application: {str(e)}"
            )

    async def withdraw_application(self, application_id: str, user_id: str) -> dict:
        """Withdraw/cancel application"""
        try:
            success = await self._get_service().update_application_status(
                application_id, 
                ApplicationStatus.WITHDRAWN, 
                user_id=user_id
            )
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Application not found or cannot be withdrawn"
                )
            
            return {"message": "Application withdrawn successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error withdrawing application: {str(e)}"
            )

    async def delete_application(self, application_id: str, user_id: str) -> dict:
        """Delete application"""
        try:
            success = await self._get_service().delete_application(application_id, user_id)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Application not found"
                )
            
            return {"message": "Application deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting application: {str(e)}"
            )

    async def get_application_stats(self, user_id: str) -> ApplicationStats:
        """Get application statistics for user"""
        try:
            return await self._get_service().get_application_stats(user_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving application stats: {str(e)}"
            )

    # Company endpoints
    async def get_company_applications(self, company_user_id: str, job_id: Optional[str] = None, skip: int = 0, limit: int = 20) -> List[ApplicationResponse]:
        """Get applications for company's jobs"""
        try:
            return await self._get_service().get_company_applications(company_user_id, job_id, skip, limit)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving company applications: {str(e)}"
            )

    async def update_application_status_by_company(self, application_id: str, status_update: ApplicationStatusUpdate, company_user_id: str) -> dict:
        """Update application status (company action)"""
        try:
            success = await self._get_service().update_application_status(
                application_id, 
                status_update.status, 
                company_user_id=company_user_id
            )
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Application not found or you don't have permission to update it"
                )
            
            return {
                "message": "Application status updated successfully",
                "new_status": status_update.status
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating application status: {str(e)}"
            )

    async def bulk_update_applications(self, application_ids: List[str], new_status: ApplicationStatus, company_user_id: str) -> dict:
        """Bulk update application statuses"""
        try:
            updated_count = 0
            failed_count = 0
            
            for app_id in application_ids:
                success = await self._get_service().update_application_status(
                    app_id, 
                    new_status, 
                    company_user_id=company_user_id
                )
                if success:
                    updated_count += 1
                else:
                    failed_count += 1
            
            return {
                "message": f"Bulk update completed",
                "updated_count": updated_count,
                "failed_count": failed_count,
                "new_status": new_status
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error in bulk update: {str(e)}"
            )