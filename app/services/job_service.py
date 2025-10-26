from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from ..models import JobVacancy, JobApplication, ApplicationStatus, ApplyType

class JobService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.vacancies_collection = db.job_vacancies
        self.applications_collection = db.job_applications

    async def get_jobs(self, filters: Dict[str, Any] = None, limit: int = 20) -> List[JobVacancy]:
        """Get job vacancies with optional filters"""
        query = {"is_active": True}
        if filters:
            query.update(filters)
        
        jobs_data = await self.vacancies_collection.find(query).sort("created_at", -1).limit(limit).to_list(length=None)
        return [JobVacancy(**job) for job in jobs_data]

    async def get_job_by_id(self, job_id: str) -> Optional[JobVacancy]:
        """Get job by ID"""
        job_data = await self.vacancies_collection.find_one({"id": job_id})
        return JobVacancy(**job_data) if job_data else None

    async def create_job(self, job: JobVacancy) -> JobVacancy:
        """Create new job vacancy"""
        await self.vacancies_collection.insert_one(job.dict())
        return job

    async def get_company_jobs_feed(self, limit: int = 20) -> List[JobVacancy]:
        """Get jobs for social feed (internal jobs only)"""
        jobs_data = await self.vacancies_collection.find({
            "apply_type": ApplyType.INTERNO
        }).sort("created_at", -1).limit(limit).to_list(length=None)
        
        return [JobVacancy(**job) for job in jobs_data]

    async def apply_to_job(self, application: JobApplication) -> JobApplication:
        """Submit job application"""
        await self.applications_collection.insert_one(application.dict())
        return application

    async def get_application(self, job_id: str, student_id: str) -> Optional[JobApplication]:
        """Check if student already applied to job"""
        app_data = await self.applications_collection.find_one({
            "job_id": job_id,
            "student_id": student_id
        })
        return JobApplication(**app_data) if app_data else None

    async def get_company_applications(self, company_id: str) -> List[JobApplication]:
        """Get all applications for company jobs"""
        # First get all job IDs for this company
        company_jobs = await self.vacancies_collection.find({"company_id": company_id}).to_list(length=None)
        job_ids = [job["id"] for job in company_jobs]
        
        # Get applications for these jobs
        applications_data = await self.applications_collection.find(
            {"job_id": {"$in": job_ids}}
        ).sort("applied_at", -1).to_list(length=None)
        
        return [JobApplication(**app) for app in applications_data]

    async def update_application_status(self, application_id: str, update_data: Dict[str, Any]) -> bool:
        """Update application status"""
        result = await self.applications_collection.update_one(
            {"id": application_id},
            {"$set": update_data}
        )
        return result.modified_count > 0

    async def get_application_by_id(self, application_id: str) -> Optional[JobApplication]:
        """Get application by ID"""
        app_data = await self.applications_collection.find_one({"id": application_id})
        return JobApplication(**app_data) if app_data else None