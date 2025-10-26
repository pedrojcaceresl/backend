from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
import logging

from app.core import settings, connect_to_mongo, close_mongo_connection
from app.routes import routers

# Create the main app
app = FastAPI(
    title="UPE Program API",
    description="API for University Professional Enhancement Program",
    version="1.0.0"
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Add a root endpoint for /api
@api_router.get("/")
async def api_root():
    """API root endpoint"""
    return {
        "message": "TechHub UPE API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

# Include all routers in the API router
for router in routers:
    api_router.include_router(router)

# Include the API router in the main app
app.include_router(api_router)

# Add CORS middleware
# Configure CORS origins for production
cors_origins = settings.CORS_ORIGINS.split(',') if hasattr(settings, 'CORS_ORIGINS') and settings.CORS_ORIGINS else [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=cors_origins,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_db_client():
    """Initialize database connection on startup"""
    await connect_to_mongo()
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close database connection on shutdown"""
    await close_mongo_connection()
    logger.info("Application shutdown complete")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "UPE Program API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    try:
        # Verificar conexión a la base de datos
        from app.core.database import get_database
        db = get_database()
        
        # Test simple de conexión
        server_info = await db.admin.command("ping")
        
        return {
            "status": "healthy",
            "service": "tech_hub-backend",
            "version": "1.0.0",
            "database": "connected" if server_info else "disconnected",
            "environment": settings.ENVIRONMENT if hasattr(settings, 'ENVIRONMENT') else "unknown"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "tech_hub-backend",
            "version": "1.0.0",
            "database": "disconnected",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )