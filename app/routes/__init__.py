# Import all routers for easy access
from .auth import router as auth_router
from .users import router as users_router
from .jobs import router as jobs_router
from .content import router as content_router
from .company import router as company_router
from .stats import router as stats_router
from .admin import router as admin_router

# List of all routers to be included in main app
routers = [
    auth_router,
    users_router,
    jobs_router,
    content_router,
    company_router,
    stats_router,
    admin_router
]

__all__ = [
    'auth_router',
    'users_router', 
    'jobs_router',
    'content_router',
    'company_router',
    'stats_router',
    'admin_router',
    'routers'
]