from motor.motor_asyncio import AsyncIOMotorDatabase

class StatsService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_platform_stats(self) -> dict:
        """Get platform statistics"""
        try:
            # Count all collections
            events_count = await self.db.events.count_documents({})
            jobs_count = await self.db.job_vacancies.count_documents({})
            courses_count = await self.db.courses.count_documents({})
            users_count = await self.db.users.count_documents({})
            
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