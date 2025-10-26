import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent.parent
load_dotenv(ROOT_DIR / '.env')

class Settings:
    # Environment
    ENVIRONMENT: str = os.environ.get('ENVIRONMENT', 'development')
    
    # Database - Compatible with both local and Render
    MONGO_URL: str = os.environ.get('MONGO_URL', os.environ.get('MONGODB_URL', ''))
    DB_NAME: str = os.environ.get('DB_NAME', os.environ.get('DATABASE_NAME', 'tech_hub'))
    
    # CORS - Support for production domains
    CORS_ORIGINS: str = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173')
    
    # JWT Configuration
    JWT_SECRET_KEY: str = os.environ.get('JWT_SECRET_KEY', 'default-secret-change-me')
    JWT_ALGORITHM: str = os.environ.get('JWT_ALGORITHM', 'HS256')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES', '1440'))
    
    # Auth Mode
    AUTH_MODE: str = os.environ.get('AUTH_MODE', 'local')  # 'local' or 'oauth'
    
    # Session (legacy compatibility)
    SESSION_EXPIRE_DAYS: int = 7
    
    # Server Configuration
    HOST: str = os.environ.get('HOST', '0.0.0.0')
    PORT: int = int(os.environ.get('PORT', '8000'))
    
    # File uploads
    UPLOAD_DIR: Path = ROOT_DIR / os.environ.get('UPLOAD_DIR', 'uploads')
    ALLOWED_FILE_EXTENSIONS: list = ['.pdf', '.doc', '.docx', '.txt']
    MAX_FILE_SIZE: int = int(os.environ.get('MAX_FILE_SIZE', str(10 * 1024 * 1024)))  # 10MB default
    
    # Logging
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Security
    FORCE_HTTPS: bool = os.environ.get('FORCE_HTTPS', 'false').lower() == 'true'

# Create global settings instance
settings = Settings()