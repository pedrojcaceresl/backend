from fastapi import HTTPException
from typing import Optional, List, Dict, Any
from ..models import JobVacancy, JobApplication, User, JobModality, JobType, ApplyType
from ..services import JobService, UserService

class JobController:
    def __init__(self, job_service: JobService, user_service: UserService):
        self.job_service = job_service
        self.user_service = user_service

    async def get_jobs(
        self,
        modality: Optional[JobModality] = None,
        job_type: Optional[JobType] = None,
        skills: Optional[str] = None,
        city: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 20
    ) -> List[JobVacancy]:
        """Get job vacancies with filters"""
        filters = {}
        if modality:
            filters["modality"] = modality
        if job_type:
            filters["job_type"] = job_type
        if city:
            filters["city"] = city
        if skills:
            skill_list = [s.strip() for s in skills.split(",")]
            filters["skills_stack"] = {"$in": skill_list}
        if search:
            filters["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"company_name": {"$regex": search, "$options": "i"}}
            ]
        
        return await self.job_service.get_jobs(filters, limit)

    async def get_job_by_id(self, job_id: str) -> JobVacancy:
        """Get single job by ID"""
        job = await self.job_service.get_job_by_id(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job

    async def create_job(self, job_data: JobVacancy, user: User) -> JobVacancy:
        """Create new job vacancy (company only)"""
        job_data.company_id = user.id
        job_data.company_name = user.company_name or user.name
        
        return await self.job_service.create_job(job_data)

    async def apply_to_job(
        self,
        job_id: str,
        application_data: Dict[str, Any],
        user: User
    ) -> Dict[str, Any]:
        """Apply to job vacancy"""
        job = await self.job_service.get_job_by_id(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.apply_type == ApplyType.EXTERNO:
            return {"redirect_url": job.apply_url}
        
        # Check if already applied
        existing_application = await self.job_service.get_application(job_id, user.id)
        if existing_application:
            raise HTTPException(status_code=400, detail="Already applied to this job")
        
        application = JobApplication(
            job_id=job_id,
            student_id=user.id,
            student_name=user.name,
            student_email=user.email,
            cv_url=application_data.get("cv_url"),
            cover_letter=application_data.get("cover_letter"),
            answers=application_data.get("answers", {})
        )
        
        await self.job_service.apply_to_job(application)
        return {"message": "Application submitted successfully"}

    async def get_company_applications(self, user: User) -> List[JobApplication]:
        """Get all applications for company jobs"""
        return await self.job_service.get_company_applications(user.id)

    async def get_company_jobs_feed(self, limit: int = 20) -> List[JobVacancy]:
        """Get jobs for social feed"""
        return await self.job_service.get_company_jobs_feed(limit)

    async def update_application_status(
        self,
        application_id: str,
        status_data: Dict[str, str],
        user: User
    ) -> Dict[str, str]:
        """Update application status (company only)"""
        application = await self.job_service.get_application_by_id(application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Verify the job belongs to this company
        job = await self.job_service.get_job_by_id(application.job_id)
        if not job or job.company_id != user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        update_data = {}
        if "status" in status_data:
            update_data["status"] = status_data["status"]
        if "notes" in status_data:
            update_data["notes"] = status_data["notes"]
        
        success = await self.job_service.update_application_status(application_id, update_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update application")
        
        return {"message": "Application updated successfully"}