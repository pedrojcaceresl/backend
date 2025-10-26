import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException
from datetime import datetime, timezone

from app.controllers.user_controller import UserController
from app.services.user_service import UserService
from app.models.user import User, UserCreate
from app.models.enums import UserRole


class TestRoleManagement:
    """Test suite for role management system"""

    @pytest.fixture
    def mock_user_service(self):
        """Mock user service for testing"""
        service = Mock(spec=UserService)
        service.get_user_by_email = AsyncMock()
        service.create_user = AsyncMock()
        service.update_user = AsyncMock()
        service.get_user_by_id = AsyncMock()
        service.get_users_by_role = AsyncMock()
        return service

    @pytest.fixture
    def user_controller(self, mock_user_service):
        """Create user controller with mocked dependencies"""
        return UserController(mock_user_service)

    @pytest.fixture
    def student_user(self):
        """Sample student user"""
        return User(
            id="student-123",
            email="student@example.com",
            name="Student User",
            role=UserRole.STUDENT,
            is_active=True,
            is_verified=True
        )

    @pytest.fixture
    def company_user(self):
        """Sample company user"""
        return User(
            id="company-123",
            email="company@example.com",
            name="Company User",
            role=UserRole.COMPANY,
            is_active=True,
            is_verified=True,
            company_name="Test Company",
            company_document="12345678-9"
        )

    @pytest.fixture
    def admin_user(self):
        """Sample admin user"""
        return User(
            id="admin-123",
            email="admin@example.com",
            name="Admin User",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )

    # ROLE ENUM TESTS
    def test_user_role_enum_values(self):
        """Test that UserRole enum has correct values"""
        assert UserRole.ADMIN == "admin"
        assert UserRole.STUDENT == "estudiante"
        assert UserRole.COMPANY == "empresa"

    def test_user_role_enum_completeness(self):
        """Test that all expected roles are present"""
        expected_roles = {"admin", "estudiante", "empresa"}
        actual_roles = {role.value for role in UserRole}
        assert expected_roles == actual_roles

    # USER MODEL ROLE METHODS TESTS
    def test_user_is_admin_method(self, admin_user, student_user):
        """Test User.is_admin() method"""
        assert admin_user.is_admin() == True
        assert student_user.is_admin() == False

    def test_user_is_company_method(self, company_user, student_user):
        """Test User.is_company() method"""
        assert company_user.is_company() == True
        assert student_user.is_company() == False

    def test_user_is_student_method(self, student_user, company_user):
        """Test User.is_student() method"""
        assert student_user.is_student() == True
        assert company_user.is_student() == False

    # DEFAULT ROLE TESTS
    def test_new_user_default_role(self):
        """Test that new users get STUDENT role by default"""
        user = User(
            email="newuser@example.com",
            name="New User"
        )
        assert user.role == UserRole.STUDENT

    def test_user_create_default_role(self):
        """Test UserCreate model default role handling"""
        user_create = UserCreate()
        # Role should be optional and None by default
        assert user_create.role is None

    # ROLE ASSIGNMENT TESTS
    @pytest.mark.asyncio
    async def test_update_profile_role_assignment_student_to_company(self, user_controller, mock_user_service, student_user):
        """Test updating user role from student to company"""
        # Mock request with role change
        mock_request = Mock()
        profile_data = {
            "role": "empresa",
            "company_name": "New Company",
            "company_document": "98765432-1"
        }
        mock_request.body = AsyncMock(return_value=json.dumps(profile_data).encode())

        # Mock updated user
        updated_user = User(**student_user.dict())
        updated_user.role = UserRole.COMPANY
        updated_user.company_name = "New Company"
        updated_user.company_document = "98765432-1"
        
        mock_user_service.update_user.return_value = updated_user

        result = await user_controller.update_profile(mock_request, student_user)

        assert result.role == UserRole.COMPANY
        assert result.company_name == "New Company"
        mock_user_service.update_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_profile_role_assignment_company_to_student(self, user_controller, mock_user_service, company_user):
        """Test updating user role from company to student"""
        mock_request = Mock()
        profile_data = {
            "role": "estudiante",
            "github_url": "https://github.com/testuser",
            "skills": ["Python", "JavaScript"]
        }
        mock_request.body = AsyncMock(return_value=json.dumps(profile_data).encode())

        updated_user = User(**company_user.dict())
        updated_user.role = UserRole.STUDENT
        updated_user.github_url = "https://github.com/testuser"
        
        mock_user_service.update_user.return_value = updated_user

        result = await user_controller.update_profile(mock_request, company_user)

        assert result.role == UserRole.STUDENT
        mock_user_service.update_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_profile_invalid_role(self, user_controller, mock_user_service, student_user):
        """Test updating user with invalid role fails"""
        mock_request = Mock()
        profile_data = {
            "role": "invalid_role"
        }
        mock_request.body = AsyncMock(return_value=json.dumps(profile_data).encode())

        with pytest.raises(HTTPException) as exc_info:
            await user_controller.update_profile(mock_request, student_user)

        assert exc_info.value.status_code == 400
        assert "Invalid role" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_update_profile_role_validation(self, user_controller, mock_user_service, student_user):
        """Test that role validation works correctly"""
        mock_request = Mock()
        
        # Test with valid roles
        for valid_role in ["admin", "estudiante", "empresa"]:
            profile_data = {"role": valid_role}
            mock_request.body = AsyncMock(return_value=json.dumps(profile_data).encode())
            
            updated_user = User(**student_user.dict())
            updated_user.role = UserRole(valid_role)
            mock_user_service.update_user.return_value = updated_user
            
            # Should not raise exception
            result = await user_controller.update_profile(mock_request, student_user)
            assert result.role.value == valid_role

    # ADMIN ROLE TESTS
    def test_admin_role_creation(self):
        """Test creating user with admin role"""
        admin = User(
            email="admin@example.com",
            name="Admin User",
            role=UserRole.ADMIN
        )
        assert admin.role == UserRole.ADMIN
        assert admin.is_admin() == True
        assert admin.is_company() == False
        assert admin.is_student() == False

    # AUTHORIZATION DEPENDENCY TESTS
    @pytest.mark.asyncio
    async def test_require_admin_with_admin_user(self, admin_user):
        """Test require_admin dependency with admin user"""
        from app.core.dependencies import require_admin
        
        mock_request = Mock()
        
        with patch('app.core.dependencies.require_auth') as mock_require_auth:
            mock_require_auth.return_value = admin_user
            
            result = await require_admin(mock_request)
            assert result == admin_user

    @pytest.mark.asyncio
    async def test_require_admin_with_non_admin_user(self, student_user):
        """Test require_admin dependency fails with non-admin user"""
        from app.core.dependencies import require_admin
        
        mock_request = Mock()
        
        with patch('app.core.dependencies.require_auth') as mock_require_auth:
            mock_require_auth.return_value = student_user
            
            with pytest.raises(HTTPException) as exc_info:
                await require_admin(mock_request)
            
            assert exc_info.value.status_code == 403
            assert "Admin privileges required" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_require_company_with_company_user(self, company_user):
        """Test require_company dependency with company user"""
        from app.core.dependencies import require_company
        
        mock_request = Mock()
        
        with patch('app.core.dependencies.require_auth') as mock_require_auth:
            mock_require_auth.return_value = company_user
            
            result = await require_company(mock_request)
            assert result == company_user

    @pytest.mark.asyncio
    async def test_require_company_with_admin_user(self, admin_user):
        """Test require_company dependency fails with admin user (admin is not company)"""
        from app.core.dependencies import require_company
        
        mock_request = Mock()
        
        with patch('app.core.dependencies.require_auth') as mock_require_auth:
            mock_require_auth.return_value = admin_user
            
            with pytest.raises(HTTPException) as exc_info:
                await require_company(mock_request)
            
            assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_require_company_or_admin_with_company(self, company_user):
        """Test require_company_or_admin dependency with company user"""
        from app.core.dependencies import require_company_or_admin
        
        mock_request = Mock()
        
        with patch('app.core.dependencies.require_auth') as mock_require_auth:
            mock_require_auth.return_value = company_user
            
            result = await require_company_or_admin(mock_request)
            assert result == company_user

    @pytest.mark.asyncio
    async def test_require_company_or_admin_with_admin(self, admin_user):
        """Test require_company_or_admin dependency with admin user"""
        from app.core.dependencies import require_company_or_admin
        
        mock_request = Mock()
        
        with patch('app.core.dependencies.require_auth') as mock_require_auth:
            mock_require_auth.return_value = admin_user
            
            result = await require_company_or_admin(mock_request)
            assert result == admin_user

    @pytest.mark.asyncio
    async def test_require_company_or_admin_with_student_fails(self, student_user):
        """Test require_company_or_admin dependency fails with student user"""
        from app.core.dependencies import require_company_or_admin
        
        mock_request = Mock()
        
        with patch('app.core.dependencies.require_auth') as mock_require_auth:
            mock_require_auth.return_value = student_user
            
            with pytest.raises(HTTPException) as exc_info:
                await require_company_or_admin(mock_request)
            
            assert exc_info.value.status_code == 403

    # ENDPOINT ACCESS CONTROL TESTS
    def test_student_endpoints_accessible(self, api_client):
        """Test that student-accessible endpoints exist"""
        # These endpoints should be accessible to students (but require auth)
        student_endpoints = [
            "/api/courses",
            "/api/events", 
            "/api/jobs",
            "/api/saved-items",  # Requires auth but students can access
        ]
        
        for endpoint in student_endpoints:
            response = api_client.get(endpoint)
            # Should either be 200 (public) or 401 (requires auth, but accessible to students)
            assert response.status_code in [200, 401], f"Student endpoint {endpoint} not accessible"

    def test_company_only_endpoints_require_company_role(self, api_client):
        """Test that company-only endpoints require company role"""
        company_endpoints = [
            ("/api/jobs", "POST"),  # Create job
            ("/api/company/applications", "GET"),
        ]
        
        for endpoint, method in company_endpoints:
            if method == "GET":
                response = api_client.get(endpoint)
            elif method == "POST":
                response = api_client.post(endpoint, json={})
            
            # Should require authentication (401) or company role (403)
            assert response.status_code in [401, 403], f"Company endpoint {method} {endpoint} not properly protected"

    def test_admin_only_endpoints_require_admin_role(self, api_client):
        """Test that admin-only endpoints require admin role"""
        admin_endpoints = [
            ("/api/admin/users", "GET"),
            ("/api/admin/users/test-id/role", "PUT"),
            ("/api/admin/users/test-id/status", "PUT"),
            ("/api/admin/create-admin", "POST"),
        ]
        
        for endpoint, method in admin_endpoints:
            if method == "GET":
                response = api_client.get(endpoint)
            elif method == "POST":
                response = api_client.post(endpoint, json={})
            elif method == "PUT":
                response = api_client.put(endpoint, json={})
            
            # Should require authentication (401) or admin role (403/404)
            assert response.status_code in [401, 403, 404], f"Admin endpoint {method} {endpoint} not properly protected"

    # ROLE PERSISTENCE TESTS
    @pytest.mark.asyncio
    async def test_role_persists_after_update(self, user_controller, mock_user_service, student_user):
        """Test that role persists correctly after profile update"""
        mock_request = Mock()
        profile_data = {
            "role": "empresa",
            "bio": "Updated bio"
        }
        mock_request.body = AsyncMock(return_value=json.dumps(profile_data).encode())

        # Mock the updated user with the new role
        updated_user = User(**student_user.dict())
        updated_user.role = UserRole.COMPANY
        updated_user.bio = "Updated bio"
        updated_user.updated_at = datetime.now(timezone.utc)
        
        mock_user_service.update_user.return_value = updated_user

        result = await user_controller.update_profile(mock_request, student_user)

        # Verify the role was updated and persisted
        assert result.role == UserRole.COMPANY
        assert result.bio == "Updated bio"
        
        # Verify update_user was called with correct data
        call_args = mock_user_service.update_user.call_args
        assert call_args[0][0] == student_user.id  # user_id
        update_data = call_args[0][1]  # update_data
        assert update_data['role'] == "empresa"
        assert 'updated_at' in update_data

    # ERROR HANDLING TESTS
    @pytest.mark.asyncio
    async def test_role_update_with_empty_body(self, user_controller, mock_user_service, student_user):
        """Test role update with empty request body"""
        mock_request = Mock()
        mock_request.body = AsyncMock(return_value=b'')

        with pytest.raises(HTTPException) as exc_info:
            await user_controller.update_profile(mock_request, student_user)

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_role_update_with_invalid_json(self, user_controller, mock_user_service, student_user):
        """Test role update with invalid JSON"""
        mock_request = Mock()
        mock_request.body = AsyncMock(return_value=b'invalid json{')

        with pytest.raises(HTTPException) as exc_info:
            await user_controller.update_profile(mock_request, student_user)

        assert exc_info.value.status_code == 400
        assert "Invalid JSON" in str(exc_info.value.detail)

    # INTEGRATION TESTS
    @pytest.mark.asyncio
    async def test_complete_role_change_workflow(self, user_controller, mock_user_service):
        """Test complete workflow of changing user from student to company"""
        # Start with a student user
        student = User(
            id="test-user-123",
            email="test@example.com",
            name="Test User",
            role=UserRole.STUDENT,
            is_active=True
        )

        # Mock the profile update request
        mock_request = Mock()
        profile_data = {
            "role": "empresa",
            "company_name": "Test Company Ltd",
            "company_document": "12345678-9",
            "bio": "We are a tech company"
        }
        mock_request.body = AsyncMock(return_value=json.dumps(profile_data).encode())

        # Mock the updated user from the service
        updated_user = User(
            id=student.id,
            email=student.email,
            name=student.name,
            role=UserRole.COMPANY,
            company_name="Test Company Ltd",
            company_document="12345678-9",
            bio="We are a tech company",
            is_active=True,
            updated_at=datetime.now(timezone.utc)
        )
        mock_user_service.update_user.return_value = updated_user

        # Execute the profile update
        result = await user_controller.update_profile(mock_request, student)

        # Verify the complete transformation
        assert result.role == UserRole.COMPANY
        assert result.is_company() == True
        assert result.is_student() == False
        assert result.company_name == "Test Company Ltd"
        assert result.company_document == "12345678-9"
        assert result.bio == "We are a tech company"
        
        # Verify the service was called correctly
        mock_user_service.update_user.assert_called_once()
        call_args = mock_user_service.update_user.call_args[0]
        assert call_args[0] == student.id
        update_data = call_args[1]
        assert update_data['role'] == "empresa"
        assert update_data['company_name'] == "Test Company Ltd"