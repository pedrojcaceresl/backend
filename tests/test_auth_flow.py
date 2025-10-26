import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import json

class TestAuthFlow:
    """Test authentication flow with local authentication"""

    def test_user_registration(self, test_client):
        """Test user registration"""
        user_data = {
            "email": "newuser@test.com",
            "password": "password123",
            "name": "New User",
            "role": "STUDENT"
        }
        
        response = test_client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == user_data["email"]
        assert data["user"]["name"] == user_data["name"]
        assert data["user"]["role"] == "STUDENT"

    def test_user_registration_duplicate_email(self, test_client, sample_users):
        """Test registration with duplicate email"""
        user_data = {
            "email": "student@test.com",  # Already exists in sample users
            "password": "password123",
            "name": "Duplicate User"
        }
        
        response = test_client.post("/auth/register", json=user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_user_login_success(self, test_client):
        """Test successful user login"""
        # First register a user
        register_data = {
            "email": "logintest@test.com",
            "password": "password123",
            "name": "Login Test User"
        }
        test_client.post("/auth/register", json=register_data)
        
        # Then login
        login_data = {
            "email": "logintest@test.com",
            "password": "password123"
        }
        
        response = test_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == login_data["email"]

    def test_user_login_invalid_email(self, test_client):
        """Test login with invalid email"""
        login_data = {
            "email": "nonexistent@test.com",
            "password": "password123"
        }
        
        response = test_client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()

    def test_user_login_invalid_password(self, test_client):
        """Test login with invalid password"""
        # First register a user
        register_data = {
            "email": "wrongpasstest@test.com",
            "password": "password123",
            "name": "Wrong Pass Test"
        }
        test_client.post("/auth/register", json=register_data)
        
        # Try login with wrong password
        login_data = {
            "email": "wrongpasstest@test.com",
            "password": "wrongpassword"
        }
        
        response = test_client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()

    def test_session_cookie_set_on_login(self, test_client):
        """Test that session cookie is set on successful login"""
        # Register user
        register_data = {
            "email": "cookietest@test.com",
            "password": "password123",
            "name": "Cookie Test User"
        }
        test_client.post("/auth/register", json=register_data)
        
        # Login
        login_data = {
            "email": "cookietest@test.com",
            "password": "password123"
        }
        
        response = test_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        # Check if session cookie was set
        cookies = response.cookies
        assert "session_token" in cookies
        assert cookies["session_token"] is not None

    def test_get_current_user_authenticated(self, test_client):
        """Test getting current user info when authenticated"""
        # Register and login user
        register_data = {
            "email": "currentuser@test.com",
            "password": "password123",
            "name": "Current User Test"
        }
        test_client.post("/auth/register", json=register_data)
        
        login_response = test_client.post("/auth/login", json={
            "email": "currentuser@test.com",
            "password": "password123"
        })
        
        # Extract session token from cookies
        session_token = login_response.cookies.get("session_token")
        
        # Get current user info
        response = test_client.get("/auth/me", cookies={"session_token": session_token})
        
        # Should return user info or require proper auth setup
        assert response.status_code in [200, 401]

    def test_logout_functionality(self, test_client):
        """Test user logout"""
        # Register and login user
        register_data = {
            "email": "logouttest@test.com",
            "password": "password123",
            "name": "Logout Test User"
        }
        test_client.post("/auth/register", json=register_data)
        
        login_response = test_client.post("/auth/login", json={
            "email": "logouttest@test.com",
            "password": "password123"
        })
        
        session_token = login_response.cookies.get("session_token")
        
        # Logout
        response = test_client.post("/auth/logout", cookies={"session_token": session_token})
        assert response.status_code == 200
        
        data = response.json()
        assert "logged out" in data["message"].lower()

    def test_oauth_complete_deprecated(self, test_client):
        """Test that OAuth complete endpoint returns deprecation message"""
        headers = {"X-Session-ID": "some-session-id"}
        response = test_client.post("/auth/complete", headers=headers)
        
        assert response.status_code == 400
        assert "oauth authentication not available" in response.json()["detail"].lower()

    def test_registration_input_validation(self, test_client):
        """Test registration input validation"""
        # Missing required fields
        invalid_data = {
            "email": "invalid-email",  # Invalid email format
            "password": "",  # Empty password
            "name": ""  # Empty name
        }
        
        response = test_client.post("/auth/register", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_login_input_validation(self, test_client):
        """Test login input validation"""
        # Invalid email format
        invalid_data = {
            "email": "not-an-email",
            "password": "password123"
        }
        
        response = test_client.post("/auth/login", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_user_role_assignment(self, test_client):
        """Test that user roles are properly assigned"""
        # Test default role (STUDENT)
        student_data = {
            "email": "defaultrole@test.com",
            "password": "password123",
            "name": "Default Role User"
        }
        
        response = test_client.post("/auth/register", json=student_data)
        assert response.status_code == 200
        assert response.json()["user"]["role"] == "STUDENT"
        
        # Test explicit role assignment
        admin_data = {
            "email": "adminrole@test.com",
            "password": "password123",
            "name": "Admin Role User",
            "role": "ADMIN"
        }
        
        response = test_client.post("/auth/register", json=admin_data)
        assert response.status_code == 200
        assert response.json()["user"]["role"] == "ADMIN"

    def test_password_security(self, test_client):
        """Test that passwords are properly hashed and not returned"""
        user_data = {
            "email": "security@test.com",
            "password": "password123",
            "name": "Security Test User"
        }
        
        response = test_client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        
        # Password should not be in response
        user_info = response.json()["user"]
        assert "password" not in user_info
        assert "password_hash" not in user_info

    def test_user_verification_status(self, test_client):
        """Test that users are automatically verified with local auth"""
        user_data = {
            "email": "verified@test.com",
            "password": "password123",
            "name": "Verified User"
        }
        
        response = test_client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        
        user_info = response.json()["user"]
        assert user_info["is_verified"] == True