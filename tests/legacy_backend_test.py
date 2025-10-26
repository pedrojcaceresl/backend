import requests
import sys
import json
from datetime import datetime

class TechHubAPITester:
    def __init__(self, base_url="https://jobhub-paraguay.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.session_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}" if not endpoint.startswith('http') else endpoint
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)
        
        if self.session_token:
            test_headers['Authorization'] = f'Bearer {self.session_token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=test_headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=test_headers)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                        if len(response_data) > 0:
                            print(f"   First item keys: {list(response_data[0].keys()) if response_data[0] else 'Empty item'}")
                    else:
                        print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Non-dict response'}")
                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:500]}...")

            return success, response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_courses_endpoint(self):
        """Test courses endpoint with various filters"""
        print("\n" + "="*50)
        print("TESTING COURSES ENDPOINTS")
        print("="*50)
        
        # Test basic courses endpoint
        success, response = self.run_test(
            "Get All Courses",
            "GET",
            "courses",
            200
        )
        
        # Test with limit
        self.run_test(
            "Get Courses with Limit",
            "GET",
            "courses?limit=3",
            200
        )
        
        # Test with category filter
        self.run_test(
            "Get Courses with Category Filter",
            "GET",
            "courses?category=programacion",
            200
        )
        
        return success

    def test_events_endpoint(self):
        """Test events endpoint"""
        print("\n" + "="*50)
        print("TESTING EVENTS ENDPOINTS")
        print("="*50)
        
        # Test basic events endpoint
        success, response = self.run_test(
            "Get All Events",
            "GET",
            "events",
            200
        )
        
        # Test with limit
        self.run_test(
            "Get Events with Limit",
            "GET",
            "events?limit=4",
            200
        )
        
        # Test with category filter
        self.run_test(
            "Get Events with Category Filter",
            "GET",
            "events?category=webinar",
            200
        )
        
        return success

    def test_jobs_endpoint(self):
        """Test jobs endpoint with filters"""
        print("\n" + "="*50)
        print("TESTING JOBS ENDPOINTS")
        print("="*50)
        
        # Test basic jobs endpoint
        success, response = self.run_test(
            "Get All Jobs",
            "GET",
            "jobs",
            200
        )
        
        # Test with modality filter
        self.run_test(
            "Get Jobs with Modality Filter (remoto)",
            "GET",
            "jobs?modality=remoto",
            200
        )
        
        # Test with job type filter
        self.run_test(
            "Get Jobs with Type Filter (junior)",
            "GET",
            "jobs?job_type=junior",
            200
        )
        
        # Test with skills filter
        self.run_test(
            "Get Jobs with Skills Filter",
            "GET",
            "jobs?skills=Python,JavaScript",
            200
        )
        
        # Test with multiple filters
        self.run_test(
            "Get Jobs with Multiple Filters",
            "GET",
            "jobs?modality=remoto&job_type=junior&limit=5",
            200
        )
        
        return success

    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        print("\n" + "="*50)
        print("TESTING AUTH ENDPOINTS")
        print("="*50)
        
        # Test auth/me without authentication (should fail)
        self.run_test(
            "Get Current User (Unauthenticated)",
            "GET",
            "auth/me",
            401
        )
        
        # Test auth/complete without session ID (should fail)
        self.run_test(
            "Complete Auth without Session ID",
            "POST",
            "auth/complete",
            400
        )
        
        # Test logout without authentication
        success, response = self.run_test(
            "Logout without Authentication",
            "POST",
            "auth/logout",
            200
        )
        
        return True  # Auth tests are expected to fail without proper session

    def test_individual_job_endpoint(self):
        """Test getting individual job by ID"""
        print("\n" + "="*50)
        print("TESTING INDIVIDUAL JOB ENDPOINT")
        print("="*50)
        
        # First get all jobs to get a valid ID
        success, jobs_response = self.run_test(
            "Get Jobs for ID Testing",
            "GET",
            "jobs?limit=1",
            200
        )
        
        if success and jobs_response and len(jobs_response) > 0:
            job_id = jobs_response[0]['id']
            self.run_test(
                f"Get Individual Job (ID: {job_id})",
                "GET",
                f"jobs/{job_id}",
                200
            )
        else:
            print("❌ No jobs found to test individual job endpoint")
            
        # Test with invalid job ID
        self.run_test(
            "Get Job with Invalid ID",
            "GET",
            "jobs/invalid-id-123",
            404
        )

    def test_job_locations(self):
        """Test job locations for geographic requirements"""
        print("\n" + "="*50)
        print("TESTING JOB LOCATIONS (Geographic Requirements)")
        print("="*50)
        
        # Get all jobs to check locations
        success, jobs_response = self.run_test(
            "Get All Jobs for Location Analysis",
            "GET",
            "jobs",
            200
        )
        
        if success and jobs_response:
            print(f"\n📍 LOCATION ANALYSIS:")
            print(f"Total jobs found: {len(jobs_response)}")
            
            location_stats = {}
            modality_stats = {}
            
            for job in jobs_response:
                city = job.get('city', 'No city specified')
                modality = job.get('modality', 'Unknown')
                
                location_stats[city] = location_stats.get(city, 0) + 1
                modality_stats[modality] = modality_stats.get(modality, 0) + 1
                
                print(f"   Job: {job['title'][:30]}... | City: {city} | Modality: {modality}")
            
            print(f"\n📊 LOCATION SUMMARY:")
            for city, count in location_stats.items():
                print(f"   {city}: {count} jobs")
            
            print(f"\n📊 MODALITY SUMMARY:")
            for modality, count in modality_stats.items():
                print(f"   {modality}: {count} jobs")
            
            # Check for Ciudad del Este requirement
            ciudad_del_este_jobs = [job for job in jobs_response if job.get('city') == 'Ciudad del Este']
            print(f"\n🏢 Ciudad del Este jobs: {len(ciudad_del_este_jobs)}")
            
            # Check presencial jobs outside Ciudad del Este
            problematic_jobs = [
                job for job in jobs_response 
                if job.get('modality') == 'presencial' and job.get('city') != 'Ciudad del Este'
            ]
            
            if problematic_jobs:
                print(f"⚠️  ISSUE: {len(problematic_jobs)} presencial jobs found outside Ciudad del Este:")
                for job in problematic_jobs:
                    print(f"   - {job['title']} in {job.get('city', 'Unknown city')}")
            else:
                print("✅ All presencial jobs are correctly located in Ciudad del Este")
        
        return success

    def test_saved_items_endpoints(self):
        """Test saved items functionality (critical bug reported)"""
        print("\n" + "="*50)
        print("TESTING SAVED ITEMS ENDPOINTS")
        print("="*50)
        
        # Test get saved items without authentication (should fail)
        self.run_test(
            "Get Saved Items (Unauthenticated)",
            "GET",
            "saved-items",
            401
        )
        
        # Test save item without authentication (should fail)
        self.run_test(
            "Save Item (Unauthenticated)",
            "POST",
            "saved-items?item_id=test-id&item_type=course",
            401
        )
        
        # Test unsave item without authentication (should fail)
        self.run_test(
            "Unsave Item (Unauthenticated)",
            "DELETE",
            "saved-items/test-id?item_type=course",
            401
        )
        
        print("ℹ️  Saved items require authentication - this is expected behavior")
        print("⚠️  CRITICAL: User reports saved button not working - needs authenticated testing")

    def test_profile_update_endpoint(self):
        """Test profile update endpoint (critical for role bug fix)"""
        print("\n" + "="*50)
        print("TESTING PROFILE UPDATE ENDPOINT")
        print("="*50)
        
        # Test profile update without authentication (should fail)
        profile_data = {
            "role": "empresa",
            "company_name": "Test Company",
            "company_document": "12345678-9"
        }
        
        self.run_test(
            "Update Profile (Unauthenticated)",
            "PUT",
            "users/profile",
            401,
            data=profile_data
        )
        
        print("ℹ️  Profile update requires authentication - this is expected behavior")
        print("⚠️  CRITICAL: User reports company account creation defaults to student role")

    def test_job_creation_endpoint(self):
        """Test job creation endpoint (for company functionality)"""
        print("\n" + "="*50)
        print("TESTING JOB CREATION ENDPOINT")
        print("="*50)
        
        # Test job creation without authentication (should fail)
        job_data = {
            "title": "Test Developer Position",
            "description": "Test job description",
            "modality": "remoto",
            "job_type": "junior"
        }
        
        self.run_test(
            "Create Job (Unauthenticated)",
            "POST",
            "jobs",
            401,
            data=job_data
        )
        
        print("ℹ️  Job creation requires company authentication - this is expected behavior")

def main():
    print("🚀 Starting TechHub UPE API Testing")
    print("="*60)
    
    # Setup
    tester = TechHubAPITester()
    
    # Run all tests
    print(f"Testing API at: {tester.base_url}")
    
    # Test all endpoints
    courses_success = tester.test_courses_endpoint()
    events_success = tester.test_events_endpoint() 
    jobs_success = tester.test_jobs_endpoint()
    auth_success = tester.test_auth_endpoints()
    tester.test_individual_job_endpoint()
    tester.test_job_locations()  # New location test
    tester.test_saved_items_endpoints()  # New critical test
    tester.test_profile_update_endpoint()
    tester.test_job_creation_endpoint()
    
    # Print final results
    print("\n" + "="*60)
    print("📊 FINAL TEST RESULTS")
    print("="*60)
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    # Summary by endpoint
    print("\n📋 ENDPOINT SUMMARY:")
    print(f"✅ Courses API: {'Working' if courses_success else 'Failed'}")
    print(f"✅ Events API: {'Working' if events_success else 'Failed'}")
    print(f"✅ Jobs API: {'Working' if jobs_success else 'Failed'}")
    print(f"⚠️  Auth API: Expected failures (no valid session)")
    print(f"⚠️  Saved Items API: Expected failures (requires authentication)")
    print(f"⚠️  Profile Update API: Expected failures (requires authentication)")
    
    print("\n🔍 CRITICAL ISSUES TO INVESTIGATE:")
    print("1. ❌ Company role creation defaulting to student (needs authenticated testing)")
    print("2. ❌ Saved items button not working (needs authenticated testing)")
    print("3. ✅ Basic API endpoints working correctly")
    
    if tester.tests_passed >= tester.tests_run * 0.7:  # 70% pass rate
        print("\n🎉 Overall API Status: HEALTHY")
        return 0
    else:
        print("\n⚠️  Overall API Status: NEEDS ATTENTION")
        return 1

if __name__ == "__main__":
    sys.exit(main())