"""
Pytest configuration and shared fixtures for TechHub UPE backend tests
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock, patch

# Add the parent directory to sys.path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import FastAPI testing utilities
try:
    from fastapi.testclient import TestClient
    from httpx import AsyncClient
except ImportError:
    # Fallback for when FastAPI is not available during static analysis
    TestClient = None
    AsyncClient = None

# Import app modules
try:
    from app.main import app
    from app.core.database import Database
    from app.models.user import User
    from app.models.enums import UserRole
    from app.services.user_service import UserService
except ImportError:
    # Handle import errors during static analysis
    app = None
    Database = None
    User = None
    UserRole = None
    UserService = None


# PYTEST CONFIGURATION
def pytest_configure(config):
    """Configure pytest with custom markers and settings"""
    config.addinivalue_line("markers", "asyncio: mark test as async")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "auth: mark test as authentication related")
    config.addinivalue_line("markers", "roles: mark test as role management related")
    config.addinivalue_line("markers", "upload: mark test as file upload related")
    config.addinivalue_line("markers", "content: mark test as content verification related")
    config.addinivalue_line("markers", "slow: mark test as slow running")


def pytest_collection_modifyitems(config, items):
    """Modify test items during collection"""
    for item in items:
        # Auto-mark async tests
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)
        
        # Auto-mark integration tests
        if "api_client" in item.fixturenames:
            item.add_marker(pytest.mark.integration)


# BASIC FIXTURES
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def api_client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI application"""
    if TestClient is None or app is None:
        pytest.skip("FastAPI not available")
    
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI application"""
    if AsyncClient is None or app is None:
        pytest.skip("FastAPI not available")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# DATABASE FIXTURES
@pytest.fixture
async def mock_database():
    """Mock database for testing"""
    mock_db = Mock()
    mock_db.courses = Mock()
    mock_db.events = Mock()
    mock_db.jobs = Mock()
    mock_db.users = Mock()
    mock_db.sessions = Mock()
    mock_db.saved_items = Mock()
    return mock_db


@pytest.fixture
async def test_database():
    """Create a test database instance"""
    if Database is None:
        pytest.skip("Database not available")
    
    # Use test database configuration
    test_db = Database()
    test_db.client = Mock()
    test_db.db = Mock()
    
    yield test_db
    
    # Cleanup would go here if using real database


# USER FIXTURES
@pytest.fixture
def sample_student_user():
    """Create a sample student user for testing"""
    if User is None or UserRole is None:
        pytest.skip("User models not available")
    
    return User(
        id="test-student-123",
        email="student@techhub.edu.py",
        name="Test Student",
        role=UserRole.STUDENT,
        is_active=True,
        is_verified=True,
        skills=["Python", "JavaScript"],
        github_url="https://github.com/teststudent",
        linkedin_url="https://linkedin.com/in/teststudent"
    )


@pytest.fixture
def sample_company_user():
    """Create a sample company user for testing"""
    if User is None or UserRole is None:
        pytest.skip("User models not available")
    
    return User(
        id="test-company-123",
        email="company@testcorp.com",
        name="Test Company Representative",
        role=UserRole.COMPANY,
        is_active=True,
        is_verified=True,
        company_name="Test Corporation",
        company_document="12345678-9"
    )


@pytest.fixture
def sample_admin_user():
    """Create a sample admin user for testing"""
    if User is None or UserRole is None:
        pytest.skip("User models not available")
    
    return User(
        id="test-admin-123",
        email="admin@techhub.edu.py",
        name="Test Administrator",
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True
    )


# AUTHENTICATION FIXTURES
@pytest.fixture
def mock_auth_session():
    """Mock authentication session for testing"""
    return {
        "session_id": "test-session-123",
        "user_id": "test-user-123",
        "expires_at": "2025-12-31T23:59:59Z",
        "token": "test-token-123"
    }


@pytest.fixture
def authenticated_client(api_client, sample_student_user):
    """Create an authenticated test client"""
    if api_client is None:
        pytest.skip("API client not available")
    
    # Mock authentication
    with patch('app.core.dependencies.get_current_user') as mock_get_user:
        mock_get_user.return_value = sample_student_user
        yield api_client


@pytest.fixture
def authenticated_company_client(api_client, sample_company_user):
    """Create an authenticated company test client"""
    if api_client is None:
        pytest.skip("API client not available")
    
    with patch('app.core.dependencies.get_current_user') as mock_get_user:
        mock_get_user.return_value = sample_company_user
        yield api_client


@pytest.fixture
def authenticated_admin_client(api_client, sample_admin_user):
    """Create an authenticated admin test client"""
    if api_client is None:
        pytest.skip("API client not available")
    
    with patch('app.core.dependencies.get_current_user') as mock_get_user:
        mock_get_user.return_value = sample_admin_user
        yield api_client


# SERVICE FIXTURES
@pytest.fixture
def mock_user_service():
    """Create a mock user service for testing"""
    if UserService is None:
        pytest.skip("UserService not available")
    
    service = Mock(spec=UserService)
    service.create_user = AsyncMock()
    service.get_user_by_id = AsyncMock()
    service.get_user_by_email = AsyncMock()
    service.update_user = AsyncMock()
    service.delete_user = AsyncMock()
    service.get_users_by_role = AsyncMock()
    service.create_session = AsyncMock()
    service.get_session_by_token = AsyncMock()
    service.delete_session = AsyncMock()
    service.update_user_files = AsyncMock()
    return service


# CONTENT FIXTURES
@pytest.fixture
def sample_course_data():
    """Sample course data for testing"""
    return {
        "id": "course-123",
        "title": "Python Programming Fundamentals",
        "description": "Learn Python programming from scratch",
        "provider": "TechHub Academy",
        "url": "https://techhub.edu.py/courses/python",
        "category": "programacion",
        "duration": "8 weeks",
        "level": "beginner",
        "is_free": True
    }


@pytest.fixture
def sample_event_data():
    """Sample event data for testing"""
    return {
        "id": "event-123",
        "title": "Tech Meetup Asunción",
        "description": "Monthly tech meetup in Asunción",
        "organizer": "TechHub Community",
        "url": "https://techhub.edu.py/events/meetup",
        "event_date": "2025-11-15T18:00:00Z",
        "location": "Asunción, Paraguay",
        "category": "meetup",
        "is_free": True
    }


@pytest.fixture
def sample_job_data():
    """Sample job data for testing"""
    return {
        "id": "job-123",
        "title": "Junior Python Developer",
        "company_id": "company-123",
        "company_name": "TechCorp Paraguay",
        "description": "Entry-level Python developer position",
        "requirements": ["Python", "FastAPI", "PostgreSQL"],
        "modality": "remoto",
        "job_type": "junior",
        "seniority_level": "junior",
        "skills_stack": ["Python", "FastAPI", "PostgreSQL"],
        "city": "Ciudad del Este",
        "country": "Paraguay",
        "salary_range": "2,000,000 - 3,000,000 PYG",
        "apply_type": "external",
        "apply_url": "https://techcorp.com/careers/python-dev"
    }


# FILE UPLOAD FIXTURES
@pytest.fixture
def temp_upload_dir(tmp_path):
    """Create a temporary upload directory for testing"""
    upload_dir = tmp_path / "test_uploads"
    upload_dir.mkdir(exist_ok=True)
    return upload_dir


@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing file uploads"""
    return b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj

xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000074 00000 n 
0000000120 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
178
%%EOF"""


# CONFIGURATION FIXTURES
@pytest.fixture
def mock_settings():
    """Mock application settings for testing"""
    settings = Mock()
    settings.MONGO_URL = "mongodb://localhost:27017"
    settings.DB_NAME = "test_upe_program"
    settings.CORS_ORIGINS = "*"
    settings.SESSION_EXPIRE_DAYS = 7
    settings.UPLOAD_DIR = Path("/tmp/test_uploads")
    settings.ALLOWED_FILE_EXTENSIONS = ['.pdf']
    settings.MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    settings.AUTH_API_BASE_URL = "https://test.emergentagent.com/auth/v1/env/oauth"
    return settings


# ENVIRONMENT FIXTURES
@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables"""
    test_env = {
        "TESTING": "true",
        "MONGO_URL": "mongodb://localhost:27017",
        "DB_NAME": "test_upe_program",
        "CORS_ORIGINS": "*"
    }
    
    with patch.dict(os.environ, test_env):
        yield


# CLEANUP FIXTURES
@pytest.fixture(autouse=True)
async def cleanup_after_test():
    """Cleanup after each test"""
    yield
    # Cleanup code would go here
    # For example: clear test database, remove temp files, etc.


# MARKERS FOR DIFFERENT TEST TYPES
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.auth = pytest.mark.auth
pytest.mark.roles = pytest.mark.roles
pytest.mark.upload = pytest.mark.upload
pytest.mark.content = pytest.mark.content
pytest.mark.slow = pytest.mark.slow


# HELPER FUNCTIONS
def create_test_user(role: str = "estudiante", **kwargs):
    """Helper function to create test users"""
    if User is None or UserRole is None:
        return None
    
    default_data = {
        "email": f"test-{role}@example.com",
        "name": f"Test {role.title()}",
        "role": UserRole(role),
        "is_active": True,
        "is_verified": True
    }
    default_data.update(kwargs)
    
    return User(**default_data)


def assert_api_error(response, expected_status: int, expected_message: str = None):
    """Helper function to assert API error responses"""
    assert response.status_code == expected_status
    if expected_message:
        response_data = response.json()
        assert expected_message.lower() in response_data.get("detail", "").lower()


def assert_api_success(response, expected_status: int = 200):
    """Helper function to assert API success responses"""
    assert response.status_code == expected_status
    response_data = response.json()
    return response_data