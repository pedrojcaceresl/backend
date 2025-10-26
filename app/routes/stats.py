from fastapi import APIRouter, Depends
from ..controllers import StatsController
from ..services import StatsService
from ..core import get_database

router = APIRouter(prefix="/stats", tags=["Statistics"])

async def get_stats_controller():
    db = await get_database()
    stats_service = StatsService(db)
    return StatsController(stats_service)

@router.get("")
async def get_platform_stats(
    controller: StatsController = Depends(get_stats_controller)
):
    """Get platform statistics"""
    return await controller.get_platform_stats()

@router.get("/overview")
async def get_stats_overview(
    controller: StatsController = Depends(get_stats_controller)
):
    """Get overall statistics overview"""
    return await controller.get_platform_stats()  # Using the same method for now