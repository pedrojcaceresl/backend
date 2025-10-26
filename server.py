from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends, UploadFile, File
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import requests
import asyncio
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class UserRole(str, Enum):
    STUDENT = "estudiante"
    COMPANY = "empresa"

class JobType(str, Enum):
    PRACTICA = "practica"
    PASANTIA = "pasantia"
    JUNIOR = "junior"
    MEDIO = "medio"
    SENIOR = "senior"

class JobModality(str, Enum):
    REMOTO = "remoto"
    PRESENCIAL = "presencial"
    HIBRIDO = "hibrido"

class ApplicationStatus(str, Enum):
    NUEVO = "nuevo"
    EN_REVISION = "en_revision"
    ENTREVISTA = "entrevista"
    OFERTA = "oferta"
    RECHAZADO = "rechazado"

class ApplyType(str, Enum):
    INTERNO = "interno"
    EXTERNO = "externo"

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    picture: Optional[str] = None
    role: UserRole = UserRole.STUDENT
    is_verified: bool = False
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    skills: List[str] = []
    bio: Optional[str] = None
    company_name: Optional[str] = None
    company_document: Optional[str] = None
    cv_file_path: Optional[str] = None
    certificate_files: List[Dict[str, Any]] = []
    degree_files: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    role: Optional[UserRole] = None  # Changed to allow explicit role assignment
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    skills: List[str] = []
    bio: Optional[str] = None
    company_name: Optional[str] = None
    company_document: Optional[str] = None

class Session(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Course(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    provider: str
    url: str
    language: str = "es"
    has_spanish_subtitles: bool = False
    category: str
    is_free: bool = True
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Event(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    organizer: str
    url: str
    event_date: datetime
    location: str
    is_online: bool = True
    category: str
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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

class SavedItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    item_id: str
    item_type: str  # 'course', 'event', 'job'
    item_data: Dict[str, Any]  # Store the full item data
    saved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class JobApplication(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str
    student_id: str
    student_name: str
    student_email: str
    cv_url: Optional[str] = None
    cover_letter: Optional[str] = None
    answers: Dict[str, str] = {}
    status: ApplicationStatus = ApplicationStatus.NUEVO
    notes: Optional[str] = None
    applied_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Authentication dependency
async def get_current_user(request: Request) -> Optional[User]:
    session_token = request.cookies.get("session_token")
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.split(" ")[1]
    
    if not session_token:
        return None
    
    session = await db.sessions.find_one({"session_token": session_token})
    if not session:
        return None
    
    # Handle timezone comparison
    expires_at = session["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
    elif not isinstance(expires_at, datetime):
        return None
    
    # Make sure both datetimes are timezone-aware
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        return None
    
    user = await db.users.find_one({"id": session["user_id"]})
    return User(**user) if user else None

async def require_auth(request: Request) -> User:
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

async def require_company(request: Request) -> User:
    user = await require_auth(request)
    if user.role != UserRole.COMPANY:
        raise HTTPException(status_code=403, detail="Company account required")
    return user

# Authentication endpoints
@api_router.post("/auth/complete")
async def complete_auth(request: Request, response: Response):
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    try:
        auth_response = requests.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": session_id}
        )
        auth_response.raise_for_status()
        auth_data = auth_response.json()
        
        # Check if user exists
        existing_user = await db.users.find_one({"email": auth_data["email"]})
        if not existing_user:
            # Create new user
            user = User(
                email=auth_data["email"],
                name=auth_data["name"],
                picture=auth_data.get("picture")
            )
            await db.users.insert_one(user.dict())
        else:
            user = User(**existing_user)
        
        # Create session
        session = Session(
            user_id=user.id,
            session_token=auth_data["session_token"],
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        await db.sessions.insert_one(session.dict())
        
        # Set cookie with proper development settings
        response.set_cookie(
            key="session_token",
            value=session.session_token,
            path="/",
            httponly=True,
            secure=False,  # Set to False for development (HTTP)
            samesite="lax",  # Changed from "none" to "lax" for same-origin requests
            max_age=7*24*60*60
        )
        
        return {"user": user, "message": "Authentication completed"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

@api_router.get("/auth/me")
async def get_current_user_info(user: User = Depends(require_auth)):
    return user

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.sessions.delete_one({"session_token": session_token})
    
    response.delete_cookie("session_token", path="/", samesite="lax")
    return {"message": "Logged out successfully"}

# User endpoints
@api_router.put("/users/profile")
async def update_profile(request: Request, user: User = Depends(require_auth)):
    # Get raw request body to debug
    body = await request.body()
    print(f"=== RAW REQUEST BODY ===")
    print(f"Raw body: {body}")
    
    # Parse JSON manually to see exact data
    import json
    raw_data = json.loads(body)
    print(f"Parsed JSON: {raw_data}")
    print(f"Role in raw JSON: {raw_data.get('role', 'NOT PRESENT')}")
    
    # Try to create UserCreate object
    try:
        profile_data = UserCreate(**raw_data)
        print(f"UserCreate object created successfully: {profile_data}")
        print(f"Role in UserCreate: {profile_data.role}")
    except Exception as e:
        print(f"Error creating UserCreate: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")
    
    update_data = profile_data.dict(exclude_unset=True)
    
    # Debug logs
    print(f"=== PROFILE UPDATE DEBUG ===")
    print(f"Updating profile for user {user.id}")
    print(f"Current user role: {user.role}")
    print(f"Update data (exclude_unset): {update_data}")
    print(f"Role in update_data: {update_data.get('role', 'NOT PRESENT')}")
    
    # FORCE role processing if it exists in the raw data
    if 'role' in raw_data and raw_data['role'] is not None:
        update_data['role'] = raw_data['role']
        print(f"FORCING role assignment: {raw_data['role']}")
    
    # If no role is provided in update, preserve current role
    if 'role' not in update_data or update_data['role'] is None:
        print(f"No role in update data, preserving current role: {user.role}")
    else:
        print(f"Changing role from {user.role} to {update_data['role']}")
    
    # Perform the update
    result = await db.users.update_one({"id": user.id}, {"$set": update_data})
    print(f"Update result: {result.modified_count} documents modified")
    
    updated_user = await db.users.find_one({"id": user.id})
    print(f"Updated user role after database update: {updated_user.get('role')}")
    print(f"Full updated user data: {updated_user}")
    print(f"=== END PROFILE UPDATE DEBUG ===")
    
    return User(**updated_user)

# File upload endpoints
@api_router.post("/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = "cv",  # cv, certificate, degree
    user: User = Depends(require_auth)
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Create uploads directory if it doesn't exist
    uploads_dir = Path("uploads") / user.id
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1]
    unique_filename = f"{file_type}_{uuid.uuid4()}.{file_extension}"
    file_path = uploads_dir / unique_filename
    
    # Save file
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Update user profile with file path
    file_field = f"{file_type}_file_path"
    if file_type == "certificate":
        # For certificates, we store an array
        existing_user = await db.users.find_one({"id": user.id})
        certificates = existing_user.get("certificate_files", [])
        certificates.append({
            "filename": file.filename,
            "file_path": str(file_path),
            "uploaded_at": datetime.now(timezone.utc)
        })
        await db.users.update_one({"id": user.id}, {"$set": {"certificate_files": certificates}})
    elif file_type == "degree":
        # For degrees, we store an array
        existing_user = await db.users.find_one({"id": user.id})
        degrees = existing_user.get("degree_files", [])
        degrees.append({
            "filename": file.filename,
            "file_path": str(file_path),
            "uploaded_at": datetime.now(timezone.utc)
        })
        await db.users.update_one({"id": user.id}, {"$set": {"degree_files": degrees}})
    else:
        # For CV, single file
        await db.users.update_one({"id": user.id}, {"$set": {"cv_file_path": str(file_path)}})
    
    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "file_type": file_type,
        "file_path": str(file_path)
    }

# Saved items endpoints
@api_router.post("/saved-items")
async def save_item(
    item_id: str,
    item_type: str,
    user: User = Depends(require_auth)
):
    # Check if already saved
    existing = await db.saved_items.find_one({
        "user_id": user.id,
        "item_id": item_id,
        "item_type": item_type
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="Item already saved")
    
    # Get the item data
    if item_type == "course":
        item_data = await db.courses.find_one({"id": item_id})
    elif item_type == "event":
        item_data = await db.events.find_one({"id": item_id})
    elif item_type == "job":
        item_data = await db.job_vacancies.find_one({"id": item_id})
    else:
        raise HTTPException(status_code=400, detail="Invalid item type")
    
    if not item_data:
        raise HTTPException(status_code=404, detail="Item not found")
    
    saved_item = SavedItem(
        user_id=user.id,
        item_id=item_id,
        item_type=item_type,
        item_data=item_data
    )
    
    await db.saved_items.insert_one(saved_item.dict())
    return {"message": "Item saved successfully"}

@api_router.delete("/saved-items/{item_id}")
async def unsave_item(item_id: str, item_type: str, user: User = Depends(require_auth)):
    result = await db.saved_items.delete_one({
        "user_id": user.id,
        "item_id": item_id,
        "item_type": item_type
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Saved item not found")
    
    return {"message": "Item removed from saved"}

@api_router.get("/saved-items")
async def get_saved_items(user: User = Depends(require_auth)):
    saved_items = await db.saved_items.find({"user_id": user.id}).to_list(length=None)
    
    # Group by type
    result = {
        "courses": [],
        "events": [],
        "jobs": []
    }
    
    for item in saved_items:
        if item["item_type"] == "course":
            result["courses"].append(item["item_data"])
        elif item["item_type"] == "event":
            result["events"].append(item["item_data"])
        elif item["item_type"] == "job":
            result["jobs"].append(item["item_data"])
    
    return result

# Courses endpoints
@api_router.get("/courses", response_model=List[Course])
async def get_courses(category: Optional[str] = None, limit: int = 20):
    query = {}
    if category:
        query["category"] = category
    
    courses = await db.courses.find(query).limit(limit).to_list(length=None)
    return [Course(**course) for course in courses]

# Events endpoints
@api_router.get("/events", response_model=List[Event])
async def get_events(category: Optional[str] = None, limit: int = 20):
    query = {"event_date": {"$gte": datetime.now(timezone.utc)}}
    if category:
        query["category"] = category
    
    events = await db.events.find(query).sort("event_date", 1).limit(limit).to_list(length=None)
    return [Event(**event) for event in events]

# Job vacancies endpoints
@api_router.get("/jobs", response_model=List[JobVacancy])
async def get_jobs(
    modality: Optional[JobModality] = None,
    job_type: Optional[JobType] = None,
    skills: Optional[str] = None,
    limit: int = 20
):
    query = {"is_active": True}
    if modality:
        query["modality"] = modality
    if job_type:
        query["job_type"] = job_type
    if skills:
        skill_list = [s.strip() for s in skills.split(",")]
        query["skills_stack"] = {"$in": skill_list}
    
    jobs = await db.job_vacancies.find(query).sort("created_at", -1).limit(limit).to_list(length=None)
    return [JobVacancy(**job) for job in jobs]

@api_router.post("/jobs", response_model=JobVacancy)
async def create_job(job_data: JobVacancy, user: User = Depends(require_company)):
    job_data.company_id = user.id
    job_data.company_name = user.company_name or user.name
    
    job_dict = job_data.dict()
    await db.job_vacancies.insert_one(job_dict)
    return job_data

@api_router.get("/jobs/{job_id}", response_model=JobVacancy)
async def get_job(job_id: str):
    job = await db.job_vacancies.find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobVacancy(**job)

@api_router.post("/jobs/{job_id}/apply")
async def apply_to_job(
    job_id: str,
    application_data: Dict[str, Any],
    user: User = Depends(require_auth)
):
    job = await db.job_vacancies.find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job["apply_type"] == ApplyType.EXTERNO:
        return {"redirect_url": job["apply_url"]}
    
    # Check if already applied
    existing_application = await db.job_applications.find_one({
        "job_id": job_id,
        "student_id": user.id
    })
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
    
    await db.job_applications.insert_one(application.dict())
    return {"message": "Application submitted successfully"}

# Company ATS endpoints
@api_router.get("/company/applications")
async def get_company_applications(user: User = Depends(require_company)):
    # Get all jobs from this company
    company_jobs = await db.job_vacancies.find({"company_id": user.id}).to_list(length=None)
    job_ids = [job["id"] for job in company_jobs]
    
    applications = await db.job_applications.find(
        {"job_id": {"$in": job_ids}}
    ).sort("applied_at", -1).to_list(length=None)
    
    return [JobApplication(**app) for app in applications]

# Statistics endpoints
@api_router.get("/stats")
async def get_platform_stats():
    try:
        # Count events
        events_count = await db.events.count_documents({})
        
        # Count job vacancies
        jobs_count = await db.job_vacancies.count_documents({})
        
        # Count courses
        courses_count = await db.courses.count_documents({})
        
        # Count users (companies + students)
        users_count = await db.users.count_documents({})
        
        return {
            "events": events_count,
            "jobs": jobs_count,
            "courses": courses_count,
            "users": users_count
        }
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {
            "events": 0,
            "jobs": 0,
            "courses": 0,
            "users": 0
        }

# Company Jobs Feed endpoint (for social feed)
@api_router.get("/company/jobs/feed")
async def get_company_jobs_feed(user: User = Depends(require_auth)):
    # Get all jobs posted by companies (for social feed view)
    # Sort by creation date to show newest first
    jobs = await db.job_vacancies.find({
        "apply_type": "interno"  # Only show internal jobs in feed
    }).sort("created_at", -1).limit(20).to_list(length=None)
    
    return [JobVacancy(**job) for job in jobs]

@api_router.put("/company/applications/{application_id}/status")
async def update_application_status(
    application_id: str,
    status_data: Dict[str, str],
    user: User = Depends(require_company)
):
    application = await db.job_applications.find_one({"id": application_id})
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Verify the job belongs to this company
    job = await db.job_vacancies.find_one({"id": application["job_id"]})
    if job["company_id"] != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_data = {}
    if "status" in status_data:
        update_data["status"] = status_data["status"]
    if "notes" in status_data:
        update_data["notes"] = status_data["notes"]
    
    await db.job_applications.update_one(
        {"id": application_id},
        {"$set": update_data}
    )
    
    return {"message": "Application updated successfully"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()