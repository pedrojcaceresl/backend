from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.application import ApplicationCreate, ApplicationUpdate, ApplicationResponse, ApplicationWithJobDetails, ApplicationStats
from app.models.enums import ApplicationStatus
from app.core.database import get_database
import uuid

class ApplicationService:
    def __init__(self):
        self.db = None
        self.collection = None
        self.jobs_collection = None
        self.users_collection = None

    async def _get_db(self):
        if not self.db:
            self.db = await get_database()
            self.collection = self.db.applications
            self.jobs_collection = self.db.job_vacancies
            self.users_collection = self.db.users
        return self.db

    async def create_application(self, user_id: str, application_data: ApplicationCreate) -> ApplicationResponse:
        """Create a new job application"""
        
        await self._get_db()  # Initialize database connection
        
        # Check if user already applied to this job
        existing = await self.collection.find_one({
            "user_id": user_id,
            "job_id": application_data.job_id
        })
        
        if existing:
            raise ValueError("Ya has postulado a este trabajo")
        
        # Verify job exists and is active
        job = await self.jobs_collection.find_one({
            "id": application_data.job_id,
            "is_active": True
        })
        
        if not job:
            raise ValueError("El trabajo no existe o no está disponible")
        
        # Create application document
        application_doc = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "job_id": application_data.job_id,
            "status": ApplicationStatus.APPLIED,
            "cover_letter": application_data.cover_letter,
            "resume_url": application_data.resume_url,
            "applied_date": datetime.now(),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Insert application
        await self.collection.insert_one(application_doc)
        
        # Return response with job details
        return ApplicationResponse(
            id=application_doc["id"],
            user_id=user_id,
            job_id=application_data.job_id,
            status=ApplicationStatus.APPLIED,
            cover_letter=application_data.cover_letter,
            resume_url=application_data.resume_url,
            applied_date=application_doc["applied_date"],
            job_title=job.get("title"),
            company_name=job.get("company_name"),
            job_type=job.get("job_type"),
            modality=job.get("modality")
        )

    async def get_user_applications(self, user_id: str, skip: int = 0, limit: int = 20) -> List[ApplicationResponse]:
        """Get all applications for a user"""
        
        await self._get_db()  # Initialize database connection
        
        # Create aggregation pipeline to join with job data
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$sort": {"applied_date": -1}},
            {"$skip": skip},
            {"$limit": limit},
            {
                "$lookup": {
                    "from": "job_vacancies",
                    "localField": "job_id",
                    "foreignField": "id",
                    "as": "job_info"
                }
            },
            {"$unwind": {"path": "$job_info", "preserveNullAndEmptyArrays": True}}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        applications = []
        
        async for doc in cursor:
            job_info = doc.get("job_info", {})
            
            application = ApplicationResponse(
                id=doc["id"],
                user_id=doc["user_id"],
                job_id=doc["job_id"],
                status=doc["status"],
                cover_letter=doc.get("cover_letter"),
                resume_url=doc.get("resume_url"),
                applied_date=doc["applied_date"],
                job_title=job_info.get("title"),
                company_name=job_info.get("company_name"),
                job_type=job_info.get("job_type"),
                modality=job_info.get("modality")
            )
            applications.append(application)
        
        return applications

    async def get_application_by_id(self, application_id: str, user_id: str) -> Optional[ApplicationWithJobDetails]:
        """Get application details with job information"""
        
        await self._get_db()  # Initialize database connection
        
        pipeline = [
            {"$match": {"id": application_id, "user_id": user_id}},
            {
                "$lookup": {
                    "from": "job_vacancies",
                    "localField": "job_id",
                    "foreignField": "id",
                    "as": "job_info"
                }
            },
            {"$unwind": {"path": "$job_info", "preserveNullAndEmptyArrays": True}}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        doc = await cursor.to_list(length=1)
        
        if not doc:
            return None
        
        doc = doc[0]
        job_info = doc.get("job_info", {})
        
        return ApplicationWithJobDetails(
            id=doc["id"],
            user_id=doc["user_id"],
            job_id=doc["job_id"],
            status=doc["status"],
            cover_letter=doc.get("cover_letter"),
            resume_url=doc.get("resume_url"),
            applied_date=doc["applied_date"],
            job_title=job_info.get("title"),
            company_name=job_info.get("company_name"),
            job_type=job_info.get("job_type"),
            modality=job_info.get("modality"),
            job_description=job_info.get("description"),
            requirements=job_info.get("requirements", []),
            salary_range=job_info.get("salary_range"),
            city=job_info.get("city"),
            country=job_info.get("country"),
            skills_stack=job_info.get("skills_stack", [])
        )

    async def update_application_status(self, application_id: str, status: ApplicationStatus, user_id: str = None, company_user_id: str = None) -> bool:
        """Update application status - can be done by user (withdraw) or company (status change)"""
        
        await self._get_db()  # Initialize database connection
        
        # Get application
        application = await self.collection.find_one({"id": application_id})
        if not application:
            return False
        
        # If user is withdrawing
        if user_id and application["user_id"] == user_id:
            if status == ApplicationStatus.WITHDRAWN:
                await self.collection.update_one(
                    {"id": application_id},
                    {
                        "$set": {
                            "status": status,
                            "updated_at": datetime.now()
                        }
                    }
                )
                return True
        
        # If company is updating status
        if company_user_id:
            # Verify the company owns this job
            job = await self.jobs_collection.find_one({"id": application["job_id"]})
            if job and job.get("company_id") == company_user_id:
                await self.collection.update_one(
                    {"id": application_id},
                    {
                        "$set": {
                            "status": status,
                            "updated_at": datetime.now()
                        }
                    }
                )
                return True
        
        return False

    async def delete_application(self, application_id: str, user_id: str) -> bool:
        """Delete/withdraw application (only by the applicant)"""
        
        await self._get_db()  # Initialize database connection
        
        result = await self.collection.delete_one({
            "id": application_id,
            "user_id": user_id
        })
        
        return result.deleted_count > 0

    async def get_company_applications(self, company_user_id: str, job_id: str = None, skip: int = 0, limit: int = 20) -> List[ApplicationResponse]:
        """Get applications for company's jobs"""
        
        await self._get_db()  # Initialize database connection
        
        # First get company's jobs
        job_filter = {"company_id": company_user_id}
        if job_id:
            job_filter["id"] = job_id
        
        company_jobs = await self.jobs_collection.find(job_filter).to_list(length=None)
        job_ids = [job["id"] for job in company_jobs]
        
        if not job_ids:
            return []
        
        # Get applications for these jobs
        pipeline = [
            {"$match": {"job_id": {"$in": job_ids}}},
            {"$sort": {"applied_date": -1}},
            {"$skip": skip},
            {"$limit": limit},
            {
                "$lookup": {
                    "from": "job_vacancies",
                    "localField": "job_id",
                    "foreignField": "id",
                    "as": "job_info"
                }
            },
            {"$unwind": {"path": "$job_info", "preserveNullAndEmptyArrays": True}},
            {
                "$lookup": {
                    "from": "users",
                    "localField": "user_id",
                    "foreignField": "id",
                    "as": "user_info"
                }
            },
            {"$unwind": {"path": "$user_info", "preserveNullAndEmptyArrays": True}}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        applications = []
        
        async for doc in cursor:
            job_info = doc.get("job_info", {})
            user_info = doc.get("user_info", {})
            
            application = ApplicationResponse(
                id=doc["id"],
                user_id=doc["user_id"],
                job_id=doc["job_id"],
                status=doc["status"],
                cover_letter=doc.get("cover_letter"),
                resume_url=doc.get("resume_url"),
                applied_date=doc["applied_date"],
                job_title=job_info.get("title"),
                company_name=job_info.get("company_name"),
                job_type=job_info.get("job_type"),
                modality=job_info.get("modality")
            )
            # Add user info for company view
            application.applicant_name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}"
            application.applicant_email = user_info.get('email')
            
            applications.append(application)
        
        return applications

    async def get_application_stats(self, user_id: str) -> ApplicationStats:
        """Get application statistics for user"""
        
        await self._get_db()  # Initialize database connection
        
        pipeline = [
            {"$match": {"user_id": user_id}},
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        cursor = self.collection.aggregate(pipeline)
        stats_data = {stat["_id"]: stat["count"] async for stat in cursor}
        
        return ApplicationStats(
            total_applications=sum(stats_data.values()),
            pending_applications=stats_data.get(ApplicationStatus.APPLIED, 0) + stats_data.get(ApplicationStatus.IN_REVIEW, 0),
            approved_applications=stats_data.get(ApplicationStatus.ACCEPTED, 0),
            rejected_applications=stats_data.get(ApplicationStatus.REJECTED, 0),
            interviews_scheduled=stats_data.get(ApplicationStatus.INTERVIEW, 0)
        )