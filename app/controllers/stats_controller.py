from ..services import StatsService

class StatsController:
    def __init__(self, stats_service: StatsService):
        self.stats_service = stats_service

    async def get_platform_stats(self) -> dict:
        """Get platform statistics"""
        return await self.stats_service.get_platform_stats()