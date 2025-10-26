from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

class Database:
    def __init__(self):
        self.client = None
        self.db = None

database = Database()

async def get_database():
    """Get database instance"""
    return database.db

def get_database_client():
    """Get database client instance"""
    return database.client

async def connect_to_mongo():
    """Create database connection"""
    database.client = AsyncIOMotorClient(settings.MONGO_URL)
    database.db = database.client[settings.DB_NAME]
    print(f"Connected to MongoDB: {settings.DB_NAME}")

async def close_mongo_connection():
    """Close database connection"""
    database.client.close()
    print("Disconnected from MongoDB")