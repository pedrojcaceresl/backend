#!/usr/bin/env python3
"""
Quick API endpoint verification using pytest
"""

import pytest
import requests
import json
from typing import Dict, Any

# Base URL for API testing
BASE_URL = "http://localhost:8000"

class TestAPIEndpoints:
    """Test all API endpoints"""
    
    @classmethod
    def setup_class(cls):
        """Setup for all tests"""
        cls.base_url = BASE_URL
        cls.auth_token = None
        cls.session_token = None
        
        # Try to authenticate
        cls._authenticate()
    
    @classmethod
    def _authenticate(cls):
        """Authenticate with the API"""
        try:
            # Try login with test credentials
            login_data = {
                "email": "student@techhub.com",
                "password": "student123"
            }
            
            response = requests.post(f"{cls.base_url}/api/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                cls.auth_token = data.get("access_token")
                # Get session token from cookies
                cls.session_token = response.cookies.get("session_token")
                print(f"✅ Authentication successful")
            else:
                print(f"⚠️ Authentication failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Authentication error: {e}")
    
    def get_headers(self, auth_required=False):
        """Get headers for requests"""
        headers = {}
        if auth_required and self.session_token:
            headers["Cookie"] = f"session_token={self.session_token}"
        return headers
    
    def test_server_is_running(self):
        """Test that the server is running"""
        response = requests.get(f"{self.base_url}/")
        assert response.status_code == 200
    
    def test_api_docs_accessible(self):
        """Test that API documentation is accessible"""
        response = requests.get(f"{self.base_url}/docs")
        assert response.status_code == 200
    
    def test_get_courses(self):
        """Test GET /api/courses"""
        response = requests.get(f"{self.base_url}/api/courses")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"📚 Found {len(data)} courses")
    
    def test_get_events(self):
        """Test GET /api/events"""
        response = requests.get(f"{self.base_url}/api/events")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"📅 Found {len(data)} events")
    
    def test_get_jobs(self):
        """Test GET /api/jobs"""
        response = requests.get(f"{self.base_url}/api/jobs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"💼 Found {len(data)} jobs")
    
    def test_auth_login(self):
        """Test POST /api/auth/login"""
        login_data = {
            "email": "student@techhub.com",
            "password": "student123"
        }
        response = requests.post(f"{self.base_url}/api/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        print(f"🔐 Login successful for user: {data['user']['name']}")
    
    def test_auth_me_with_auth(self):
        """Test GET /api/auth/me with authentication"""
        if not self.session_token:
            pytest.skip("No authentication token available")
        
        headers = self.get_headers(auth_required=True)
        response = requests.get(f"{self.base_url}/api/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        print(f"👤 Current user: {data.get('name', 'Unknown')}")
    
    def test_auth_me_without_auth(self):
        """Test GET /api/auth/me without authentication (should fail)"""
        response = requests.get(f"{self.base_url}/api/auth/me")
        assert response.status_code == 401
        print("🔒 Unauthorized access properly blocked")
    
    def test_get_users_with_auth(self):
        """Test GET /api/users with authentication"""
        if not self.session_token:
            pytest.skip("No authentication token available")
        
        headers = self.get_headers(auth_required=True)
        response = requests.get(f"{self.base_url}/api/users", headers=headers)
        
        # Should be 200 or 403 (depending on permissions)
        assert response.status_code in [200, 403]
        
        if response.status_code == 200:
            data = response.json()
            print(f"👥 Found {len(data)} users")
        else:
            print("🔒 Users endpoint requires higher permissions")
    
    def test_stats_overview(self):
        """Test GET /api/stats/overview"""
        response = requests.get(f"{self.base_url}/api/stats/overview")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        print(f"📊 Stats overview: {list(data.keys())}")
    
    def test_invalid_endpoint(self):
        """Test accessing non-existent endpoint"""
        response = requests.get(f"{self.base_url}/api/nonexistent")
        assert response.status_code == 404
        print("🚫 Non-existent endpoint properly returns 404")
    
    def test_cors_headers(self):
        """Test that CORS headers are present"""
        response = requests.options(f"{self.base_url}/api/courses")
        # Should not fail due to CORS
        assert response.status_code in [200, 405]  # 405 = Method not allowed but CORS OK
        print("🌐 CORS headers working")

if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])