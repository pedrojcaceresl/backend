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
    JWT_SECRET_KEY: str = os.environ.get('JWT_SECRET_KEY', 'default-secret-change-me')
    AUTH_MODE: str = os.environ.get('AUTH_MODE', 'local')  # 'local' or 'oauth'
    
    # File uploads
    UPLOAD_DIR: Path = ROOT_DIR / 'uploads'
    ALLOWED_FILE_EXTENSIONS: list = ['.pdf']
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

# Create global settings instance
settings = Settings()