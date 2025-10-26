import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent.parent
load_dotenv(ROOT_DIR / '.env')

class Settings:
    # Database
    MONGO_URL: str = os.environ.get('MONGO_URL', '')
    DB_NAME: str = os.environ.get('DB_NAME', 'upe_program')
    
    # CORS
    CORS_ORIGINS: str = os.environ.get('CORS_ORIGINS', '*')
    
    # Auth
    SESSION_EXPIRE_DAYS: int = 7
    
    # File uploads
    UPLOAD_DIR: Path = ROOT_DIR / 'uploads'
    ALLOWED_FILE_EXTENSIONS: list = ['.pdf']
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # External API
    AUTH_API_BASE_URL: str = "https://demobackend.emergentagent.com/auth/v1/env/oauth"

# Create global settings instance
settings = Settings()