#!/usr/bin/env python3
"""
Comprehensive API Testing Script for TechHub UPE
Tests all endpoints automatically with proper authentication
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional
from datetime import datetime

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        self.session_token = None
        self.test_results = []
        
    def log_test(self, endpoint: str, method: str, status_code: int, expected: int, details: str = ""):
        """Log test results"""
        success = status_code == expected
        result = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "expected": expected,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {method} {endpoint} - {status_code} (expected {expected}) {details}")
        
    def test_endpoint(self, endpoint: str, method: str = "GET", data: Dict = None, 
                     expected_status: int = 200, auth_required: bool = False, 
                     description: str = "") -> Optional[Dict]:
        """Test a single endpoint"""
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        # Add authentication if required
        if auth_required and self.session_token:
            headers["Authorization"] = f"Bearer {self.session_token}"
        
        try:
            if method == "GET":
                response = self.session.get(url, headers=headers)
            elif method == "POST":
                headers["Content-Type"] = "application/json"
                response = self.session.post(url, json=data, headers=headers)
            elif method == "PUT":
                headers["Content-Type"] = "application/json" 
                response = self.session.put(url, json=data, headers=headers)
            elif method == "DELETE":
                response = self.session.delete(url, headers=headers)
            else:
                self.log_test(endpoint, method, 0, expected_status, f"Unsupported method: {method}")
                return None
                
            self.log_test(endpoint, method, response.status_code, expected_status, description)
            
            # Return JSON response if available
            try:
                return response.json()
            except:
                return {"status": "no_json", "text": response.text[:100]}
                
        except Exception as e:
            self.log_test(endpoint, method, 0, expected_status, f"Error: {str(e)}")
            return None
    
    def authenticate(self):
        """Authenticate with the API"""
        print("\n🔐 Testing Authentication...")
        
        # Test user registration (should work or user already exists)
        import time
        unique_email = f"test{int(time.time())}@apitest.com"
        register_data = {
            "email": unique_email,
            "password": "testpass123",
            "name": "API Test User",
            "role": "STUDENT"  # Will be converted to "estudiante" by validator
        }
        
        response = self.test_endpoint("/api/auth/register", "POST", register_data, 
                                    expected_status=200, description="New user registration")
        
        # If registration failed (user exists), try login
        if not response or "access_token" not in response:
            login_data = {
                "email": "student@techhub.com",
                "password": "student123"
            }
            response = self.test_endpoint("/api/auth/login", "POST", login_data,
                                        expected_status=200, description="Login with test user")
        
        if response and "access_token" in response:
            self.auth_token = response["access_token"]
            self.session_token = response["access_token"]  # Use access_token for auth
            print(f"🎯 Authentication successful - Token: {self.auth_token[:20]}...")
            return True
        else:
            print("❌ Authentication failed!")
            return False
    
    def test_all_endpoints(self):
        """Test all API endpoints systematically"""
        print("🚀 Starting Comprehensive API Testing")
        print("=" * 60)
        
        # 1. Health check / Basic endpoints
        print("\n🏥 Testing Health & Basic Endpoints...")
        self.test_endpoint("/", "GET", expected_status=200, description="Root endpoint")
        self.test_endpoint("/api", "GET", expected_status=200, description="API root")
        self.test_endpoint("/docs", "GET", expected_status=200, description="API documentation")
        
        # 2. Authentication tests
        if not self.authenticate():
            print("⚠️ Cannot continue without authentication")
            return
        
        # Test auth endpoints
        self.test_endpoint("/api/auth/me", "GET", expected_status=200, auth_required=True, 
                          description="Get current user")
        
        # 3. Courses endpoints
        print("\n📚 Testing Courses Endpoints...")
        courses_response = self.test_endpoint("/api/courses", "GET", expected_status=200,
                                            description="Get all courses")
        
        # Test specific course if available
        if courses_response and isinstance(courses_response, list) and len(courses_response) > 0:
            course_id = courses_response[0].get("id")
            if course_id:
                self.test_endpoint(f"/api/courses/{course_id}", "GET", expected_status=200,
                                  description="Get specific course")
        
        # 4. Events endpoints
        print("\n📅 Testing Events Endpoints...")
        events_response = self.test_endpoint("/api/events", "GET", expected_status=200,
                                           description="Get all events")
        
        # Test specific event if available
        if events_response and isinstance(events_response, list) and len(events_response) > 0:
            event_id = events_response[0].get("id")
            if event_id:
                self.test_endpoint(f"/api/events/{event_id}", "GET", expected_status=200,
                                  description="Get specific event")
        
        # 5. Jobs endpoints
        print("\n💼 Testing Jobs Endpoints...")
        jobs_response = self.test_endpoint("/api/jobs", "GET", expected_status=200,
                                         description="Get all jobs")
        
        # Test specific job if available
        if jobs_response and isinstance(jobs_response, list) and len(jobs_response) > 0:
            job_id = jobs_response[0].get("id")
            if job_id:
                self.test_endpoint(f"/api/jobs/{job_id}", "GET", expected_status=200,
                                  description="Get specific job")
        
        # 6. Users endpoints (with authentication)
        print("\n👥 Testing Users Endpoints...")
        self.test_endpoint("/api/users", "GET", expected_status=200, auth_required=True,
                          description="Get all users")
        
        self.test_endpoint("/api/users/profile", "GET", expected_status=200, auth_required=True,
                          description="Get user profile")
        
        # 7. Stats endpoints
        print("\n📊 Testing Stats Endpoints...")
        self.test_endpoint("/api/stats/overview", "GET", expected_status=200,
                          description="Get stats overview")
        
        # 8. Company endpoints (should return 403 for non-company user)
        print("\n🏢 Testing Company Endpoints...")
        self.test_endpoint("/api/company/profile", "GET", expected_status=403, auth_required=True,
                          description="Get company profile")
        
        # 9. Saved items endpoints
        print("\n⭐ Testing Saved Items Endpoints...")
        self.test_endpoint("/api/saved-items", "GET", expected_status=200, auth_required=True,
                          description="Get saved items")
        
        # 10. Test some error cases
        print("\n⚠️ Testing Error Handling...")
        self.test_endpoint("/api/courses/nonexistent", "GET", expected_status=404,
                          description="Non-existent course")
        
        self.test_endpoint("/api/auth/me", "GET", expected_status=401,
                          description="Unauthorized access (no auth)")
        
        # 11. Logout test
        print("\n👋 Testing Logout...")
        self.test_endpoint("/api/auth/logout", "POST", expected_status=200, auth_required=True,
                          description="User logout")
    
    def generate_report(self):
        """Generate a summary report"""
        print("\n" + "=" * 60)
        print("📋 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['method']} {result['endpoint']} - {result['status_code']} {result['details']}")
        
        # Save detailed report
        with open("api_test_report.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: api_test_report.json")
        return passed_tests, failed_tests

def main():
    print("TechHub UPE - Automated API Testing")
    print("=" * 40)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        print("✅ Server is running and reachable")
    except requests.exceptions.RequestException:
        print("❌ Server is not running or not reachable")
        print("🚀 Please start the server with: python -m uvicorn main:app --reload")
        sys.exit(1)
    
    # Initialize tester
    tester = APITester()
    
    # Run all tests
    tester.test_all_endpoints()
    
    # Generate report
    passed, failed = tester.generate_report()
    
    print(f"\n🎉 Testing completed!")
    print(f"Visit http://localhost:8000/docs to explore the API interactively")
    
    # Exit with error code if tests failed
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()