import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException
from datetime import datetime, timezone, timedelta
import json

from app.controllers.auth_controller import AuthController
from app.services.user_service import UserService
from app.models.user import User, Session
from app.models.enums import UserRole


class TestAuthenticationFlow:
    """Test suite for authentication flow and security"""

    @pytest.fixture
    def mock_user_service(self):
        """Mock user service for testing"""
        service = Mock(spec=UserService)
        service.get_user_by_email = AsyncMock()
        service.create_user = AsyncMock()
        service.update_user = AsyncMock()
        service.create_session = AsyncMock()
        service.get_session_by_token = AsyncMock()
        service.delete_session = AsyncMock()
        return service

    @pytest.fixture
    def auth_controller(self, mock_user_service):
        """Create auth controller with mocked dependencies"""
        return AuthController(mock_user_service)

    @pytest.fixture
    def sample_auth_data(self):
        """Sample authentication data from external service"""
        return {
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/picture.jpg",
            "session_token": "sample-session-token-123"
        }

    @pytest.fixture
    def sample_user(self):
        """Sample user for testing"""
        return User(
            id="user-123",
            email="test@example.com",
            name="Test User",
            role=UserRole.STUDENT,
            is_verified=True,
            is_active=True
        )

    # AUTHENTICATION COMPLETION TESTS
    @pytest.mark.asyncio
    async def test_complete_auth_success_new_user(self, auth_controller, mock_user_service, sample_auth_data, api_client):
        """Test successful authentication for new user"""
        # Mock external auth service response
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_auth_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            # Mock user service responses
            mock_user_service.get_user_by_email.return_value = None  # New user
            
            created_user = User(
                id="new-user-123",
                email=sample_auth_data["email"],
                name=sample_auth_data["name"],
                role=UserRole.STUDENT
            )
            mock_user_service.create_user.return_value = created_user
            
            created_session = Session(
                id="session-123",
                user_id=created_user.id,
                session_token=sample_auth_data["session_token"],
                expires_at=datetime.now(timezone.utc) + timedelta(days=7)
            )
            mock_user_service.create_session.return_value = created_session

            # Mock response object
            mock_response_obj = Mock()
            mock_response_obj.set_cookie = Mock()

            # Test the authentication completion
            result = await auth_controller.complete_auth("test-session-id", mock_response_obj)

            # Assertions
            assert result["message"] == "Authentication completed successfully"
            assert result["user"].email == sample_auth_data["email"]
            assert result["user"].role == UserRole.STUDENT  # Default role for new users
            
            # Verify user creation was called
            mock_user_service.create_user.assert_called_once()
            created_user_arg = mock_user_service.create_user.call_args[0][0]
            assert created_user_arg.email == sample_auth_data["email"]
            assert created_user_arg.role == UserRole.STUDENT
            assert created_user_arg.is_verified == True

            # Verify session creation was called
            mock_user_service.create_session.assert_called_once()
            
            # Verify cookie was set
            mock_response_obj.set_cookie.assert_called_once()

    @pytest.mark.asyncio
    async def test_complete_auth_success_existing_user(self, auth_controller, mock_user_service, sample_auth_data, sample_user):
        """Test successful authentication for existing user"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_auth_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            # Mock existing user
            mock_user_service.get_user_by_email.return_value = sample_user
            mock_user_service.update_user.return_value = sample_user
            
            created_session = Session(
                id="session-123",
                user_id=sample_user.id,
                session_token=sample_auth_data["session_token"],
                expires_at=datetime.now(timezone.utc) + timedelta(days=7)
            )
            mock_user_service.create_session.return_value = created_session

            mock_response_obj = Mock()
            mock_response_obj.set_cookie = Mock()

            result = await auth_controller.complete_auth("test-session-id", mock_response_obj)

            # Assertions
            assert result["message"] == "Authentication completed successfully"
            assert result["user"].id == sample_user.id
            
            # Should not create new user
            mock_user_service.create_user.assert_not_called()
            
            # Should create session
            mock_user_service.create_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_complete_auth_missing_session_id(self, auth_controller):
        """Test authentication fails with missing session ID"""
        mock_response_obj = Mock()
        
        with pytest.raises(HTTPException) as exc_info:
            await auth_controller.complete_auth(None, mock_response_obj)
        
        assert exc_info.value.status_code == 400
        assert "Session ID required" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_complete_auth_external_service_error(self, auth_controller):
        """Test authentication fails with external service error"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("External service unavailable")
            
            mock_response_obj = Mock()
            
            with pytest.raises(HTTPException) as exc_info:
                await auth_controller.complete_auth("test-session-id", mock_response_obj)
            
            assert exc_info.value.status_code == 500
            assert "Authentication failed" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_complete_auth_missing_email(self, auth_controller):
        """Test authentication fails with missing email in auth data"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"name": "Test User"}  # Missing email
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            mock_response_obj = Mock()
            
            with pytest.raises(HTTPException) as exc_info:
                await auth_controller.complete_auth("test-session-id", mock_response_obj)
            
            assert exc_info.value.status_code == 400
            assert "Missing required user data" in str(exc_info.value.detail)

    # LOGOUT TESTS
    @pytest.mark.asyncio
    async def test_logout_success(self, auth_controller, mock_user_service):
        """Test successful logout"""
        mock_request = Mock()
        mock_request.cookies = {"session_token": "test-token"}
        
        mock_response_obj = Mock()
        mock_response_obj.delete_cookie = Mock()
        
        mock_user_service.delete_session.return_value = True

        result = await auth_controller.logout(mock_request, mock_response_obj)

        assert result["message"] == "Logged out successfully"
        mock_user_service.delete_session.assert_called_once_with("test-token")
        mock_response_obj.delete_cookie.assert_called_once()

    @pytest.mark.asyncio
    async def test_logout_no_session_token(self, auth_controller, mock_user_service):
        """Test logout without session token"""
        mock_request = Mock()
        mock_request.cookies = {}
        
        mock_response_obj = Mock()
        mock_response_obj.delete_cookie = Mock()

        result = await auth_controller.logout(mock_request, mock_response_obj)

        assert result["message"] == "Logged out successfully"
        mock_user_service.delete_session.assert_not_called()
        mock_response_obj.delete_cookie.assert_called_once()

    # AUTHENTICATION DEPENDENCIES TESTS
    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self, mock_user_service, sample_user):
        """Test getting current user with valid token"""
        from app.core.dependencies import get_current_user
        
        mock_request = Mock()
        mock_request.cookies = {"session_token": "valid-token"}
        
        # Mock session
        mock_session = Session(
            id="session-123",
            user_id=sample_user.id,
            session_token="valid-token",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        
        with patch('app.core.dependencies.get_database') as mock_get_db, \
             patch('app.core.dependencies.UserService') as mock_user_service_class:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_service_instance = Mock()
            mock_service_instance.get_session_by_token = AsyncMock(return_value=mock_session)
            mock_service_instance.get_user_by_id = AsyncMock(return_value=sample_user)
            mock_user_service_class.return_value = mock_service_instance
            
            result = await get_current_user(mock_request)
            
            assert result == sample_user

    @pytest.mark.asyncio
    async def test_get_current_user_expired_token(self, mock_user_service):
        """Test getting current user with expired token"""
        from app.core.dependencies import get_current_user
        
        mock_request = Mock()
        mock_request.cookies = {"session_token": "expired-token"}
        
        # Mock expired session
        mock_session = Session(
            id="session-123",
            user_id="user-123",
            session_token="expired-token",
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1)  # Expired
        )
        
        with patch('app.core.dependencies.get_database') as mock_get_db, \
             patch('app.core.dependencies.UserService') as mock_user_service_class:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_service_instance = Mock()
            mock_service_instance.get_session_by_token = AsyncMock(return_value=mock_session)
            mock_user_service_class.return_value = mock_service_instance
            
            result = await get_current_user(mock_request)
            
            assert result is None

    @pytest.mark.asyncio
    async def test_require_auth_success(self, sample_user):
        """Test require_auth with valid authentication"""
        from app.core.dependencies import require_auth
        
        mock_request = Mock()
        
        with patch('app.core.dependencies.get_current_user') as mock_get_user:
            mock_get_user.return_value = sample_user
            
            result = await require_auth(mock_request)
            
            assert result == sample_user

    @pytest.mark.asyncio
    async def test_require_auth_failure(self):
        """Test require_auth without authentication"""
        from app.core.dependencies import require_auth
        
        mock_request = Mock()
        
        with patch('app.core.dependencies.get_current_user') as mock_get_user:
            mock_get_user.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await require_auth(mock_request)
            
            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_require_auth_inactive_user(self):
        """Test require_auth with inactive user"""
        from app.core.dependencies import require_auth
        
        inactive_user = User(
            id="user-123",
            email="test@example.com",
            name="Test User",
            role=UserRole.STUDENT,
            is_active=False  # Inactive user
        )
        
        mock_request = Mock()
        
        with patch('app.core.dependencies.get_current_user') as mock_get_user:
            mock_get_user.return_value = inactive_user
            
            with pytest.raises(HTTPException) as exc_info:
                await require_auth(mock_request)
            
            assert exc_info.value.status_code == 403
            assert "inactive" in str(exc_info.value.detail).lower()

    # ROLE-BASED AUTHENTICATION TESTS
    @pytest.mark.asyncio
    async def test_require_admin_success(self):
        """Test require_admin with admin user"""
        from app.core.dependencies import require_admin
        
        admin_user = User(
            id="admin-123",
            email="admin@example.com",
            name="Admin User",
            role=UserRole.ADMIN,
            is_active=True
        )
        
        mock_request = Mock()
        
        with patch('app.core.dependencies.require_auth') as mock_require_auth:
            mock_require_auth.return_value = admin_user
            
            result = await require_admin(mock_request)
            
            assert result == admin_user

    @pytest.mark.asyncio
    async def test_require_admin_failure(self, sample_user):
        """Test require_admin with non-admin user"""
        from app.core.dependencies import require_admin
        
        mock_request = Mock()
        
        with patch('app.core.dependencies.require_auth') as mock_require_auth:
            mock_require_auth.return_value = sample_user  # Student user
            
            with pytest.raises(HTTPException) as exc_info:
                await require_admin(mock_request)
            
            assert exc_info.value.status_code == 403
            assert "Admin" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_require_company_success(self):
        """Test require_company with company user"""
        from app.core.dependencies import require_company
        
        company_user = User(
            id="company-123",
            email="company@example.com",
            name="Company User",
            role=UserRole.COMPANY,
            is_active=True
        )
        
        mock_request = Mock()
        
        with patch('app.core.dependencies.require_auth') as mock_require_auth:
            mock_require_auth.return_value = company_user
            
            result = await require_company(mock_request)
            
            assert result == company_user

    @pytest.mark.asyncio
    async def test_require_company_failure(self, sample_user):
        """Test require_company with non-company user"""
        from app.core.dependencies import require_company
        
        mock_request = Mock()
        
        with patch('app.core.dependencies.require_auth') as mock_require_auth:
            mock_require_auth.return_value = sample_user  # Student user
            
            with pytest.raises(HTTPException) as exc_info:
                await require_company(mock_request)
            
            assert exc_info.value.status_code == 403
            assert "Company" in str(exc_info.value.detail)

    # ENDPOINT SECURITY TESTS
    def test_protected_endpoints_require_auth(self, api_client):
        """Test that protected endpoints require authentication"""
        protected_endpoints = [
            ("/api/auth/me", "GET"),
            ("/api/users/profile", "PUT"),
            ("/api/saved-items", "GET"),
            ("/api/saved-items", "POST"),
            ("/api/jobs", "POST"),  # Company only
            ("/api/company/applications", "GET"),  # Company only
        ]
        
        for endpoint, method in protected_endpoints:
            if method == "GET":
                response = api_client.get(endpoint)
            elif method == "POST":
                response = api_client.post(endpoint, json={})
            elif method == "PUT":
                response = api_client.put(endpoint, json={})
            
            assert response.status_code == 401, f"Endpoint {method} {endpoint} should require authentication"

    # SECURITY EDGE CASES
    @pytest.mark.asyncio
    async def test_session_token_from_header(self):
        """Test authentication via Authorization header"""
        from app.core.dependencies import get_current_user
        
        mock_request = Mock()
        mock_request.cookies = {}
        mock_request.headers = {"Authorization": "Bearer test-token"}
        
        # Mock session and user
        mock_session = Session(
            id="session-123",
            user_id="user-123",
            session_token="test-token",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        
        mock_user = User(
            id="user-123",
            email="test@example.com",
            name="Test User",
            role=UserRole.STUDENT
        )
        
        with patch('app.core.dependencies.get_database') as mock_get_db, \
             patch('app.core.dependencies.UserService') as mock_user_service_class:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_service_instance = Mock()
            mock_service_instance.get_session_by_token = AsyncMock(return_value=mock_session)
            mock_service_instance.get_user_by_id = AsyncMock(return_value=mock_user)
            mock_user_service_class.return_value = mock_service_instance
            
            result = await get_current_user(mock_request)
            
            assert result == mock_user

    @pytest.mark.asyncio
    async def test_malformed_auth_header(self):
        """Test handling of malformed Authorization header"""
        from app.core.dependencies import get_current_user
        
        mock_request = Mock()
        mock_request.cookies = {}
        mock_request.headers = {"Authorization": "InvalidFormat"}
        
        with patch('app.core.dependencies.get_database') as mock_get_db, \
             patch('app.core.dependencies.UserService') as mock_user_service_class:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_service_instance = Mock()
            mock_user_service_class.return_value = mock_service_instance
            
            result = await get_current_user(mock_request)
            
            assert result is None

    def test_auth_endpoints_status_codes(self, api_client):
        """Test various authentication endpoints return correct status codes"""
        # Test auth/me without authentication
        response = api_client.get("/api/auth/me")
        assert response.status_code == 401
        
        # Test auth/complete without session ID
        response = api_client.post("/api/auth/complete")
        assert response.status_code == 400
        
        # Test auth/logout (should work without authentication)
        response = api_client.post("/api/auth/logout")
        assert response.status_code == 200