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
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=settings.CORS_ORIGINS.split(','),
    allow_methods=["*"],
    allow_headers=["*"],
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
    """Health check endpoint"""
    return {"status": "healthy", "service": "upe-program-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )