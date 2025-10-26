import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

def generate_unique_id() -> str:
    """Generate a unique UUID string"""
    return str(uuid.uuid4())

def get_current_utc_time() -> datetime:
    """Get current UTC time"""
    return datetime.now(timezone.utc)

def ensure_directory_exists(directory_path: Path) -> None:
    """Ensure directory exists, create if it doesn't"""
    directory_path.mkdir(parents=True, exist_ok=True)

def is_valid_file_extension(filename: str, allowed_extensions: list) -> bool:
    """Check if file has a valid extension"""
    file_extension = '.' + filename.split('.')[-1].lower()
    return file_extension in allowed_extensions

def parse_skills_string(skills_str: Optional[str]) -> list:
    """Parse comma-separated skills string into list"""
    if not skills_str:
        return []
    return [skill.strip() for skill in skills_str.split(",")]