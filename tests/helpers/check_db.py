#!/usr/bin/env python3

import asyncio
import os
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def check_database():
    """Check database content"""
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    # Check users
    users_count = await db.users.count_documents({})
    print(f"👥 Users in database: {users_count}")
    
    if users_count > 0:
        users = await db.users.find({}).limit(5).to_list(5)
        for user in users:
            print(f"  - {user.get('email', 'No email')} ({user.get('role', 'No role')})")
    
    # Check other collections
    jobs_count = await db.job_vacancies.count_documents({})
    courses_count = await db.courses.count_documents({})
    events_count = await db.events.count_documents({})
    
    print(f"💼 Jobs: {jobs_count}")
    print(f"📚 Courses: {courses_count}")
    print(f"📅 Events: {events_count}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_database())