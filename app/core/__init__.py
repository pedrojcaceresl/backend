# Re-export core components
from .config import settings
from .database import get_database, connect_to_mongo, close_mongo_connection
from .dependencies import get_current_user, require_auth, require_company, require_student

__all__ = [
    'settings',
    'get_database',
    'connect_to_mongo', 
    'close_mongo_connection',
    'get_current_user',
    'require_auth',
    'require_company',
    'require_student'
]