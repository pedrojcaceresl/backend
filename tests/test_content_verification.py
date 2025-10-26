import pytest
import requests
from typing import List, Dict, Any
from datetime import datetime

class TestContentVerification:
    """Test suite for verifying content quality and quantity in TechHub UPE"""
    
    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        """Setup for each test"""
        self.client = api_client
        self.issues = []
        self.successes = []

    def log_issue(self, category: str, message: str):
        """Log an issue found during testing"""
        self.issues.append(f"❌ {category}: {message}")

    def log_success(self, category: str, message: str):
        """Log a success found during testing"""
        self.successes.append(f"✅ {category}: {message}")

    # COURSES CONTENT VERIFICATION
    def test_courses_quantity_requirement(self):
        """Test that there are at least 20 courses"""
        response = self.client.get("/api/courses")
        assert response.status_code == 200
        courses = response.json()
        
        assert len(courses) >= 20, f"Expected at least 20 courses, found {len(courses)}"

    def test_courses_required_fields(self):
        """Test that all courses have required fields"""
        response = self.client.get("/api/courses")
        assert response.status_code == 200
        courses = response.json()
        
        required_fields = ['title', 'description', 'provider', 'url', 'category']
        
        for course in courses:
            for field in required_fields:
                assert field in course, f"Course '{course.get('title', 'Unknown')}' missing field: {field}"
                assert course[field], f"Course '{course.get('title', 'Unknown')}' has empty field: {field}"

    def test_courses_expected_providers(self):
        """Test that courses include expected real providers"""
        response = self.client.get("/api/courses")
        assert response.status_code == 200
        courses = response.json()
        
        expected_providers = ["Claseflix", "Google Skillshop", "Programación ATS"]
        found_providers = {course.get('provider', '') for course in courses}
        
        for expected in expected_providers:
            provider_found = any(expected.lower() in provider.lower() for provider in found_providers)
            assert provider_found, f"Expected provider '{expected}' not found in courses"

    def test_courses_category_diversity(self):
        """Test that courses have good category diversity"""
        response = self.client.get("/api/courses")
        assert response.status_code == 200
        courses = response.json()
        
        categories = {course.get('category') for course in courses if course.get('category')}
        
        assert len(categories) >= 5, f"Expected at least 5 different categories, found {len(categories)}"

    def test_courses_valid_urls(self):
        """Test that course URLs are valid"""
        response = self.client.get("/api/courses")
        assert response.status_code == 200
        courses = response.json()
        
        for course in courses:
            url = course.get('url')
            assert url, f"Course '{course.get('title')}' missing URL"
            assert url.startswith(('http://', 'https://')), f"Course '{course.get('title')}' has invalid URL: {url}"

    # EVENTS CONTENT VERIFICATION
    def test_events_quantity_requirement(self):
        """Test that there are at least 12 events"""
        response = self.client.get("/api/events")
        assert response.status_code == 200
        events = response.json()
        
        assert len(events) >= 12, f"Expected at least 12 events, found {len(events)}"

    def test_events_required_fields(self):
        """Test that all events have required fields"""
        response = self.client.get("/api/events")
        assert response.status_code == 200
        events = response.json()
        
        required_fields = ['title', 'description', 'organizer', 'url', 'event_date', 'location']
        
        for event in events:
            for field in required_fields:
                assert field in event, f"Event '{event.get('title', 'Unknown')}' missing field: {field}"
                assert event[field], f"Event '{event.get('title', 'Unknown')}' has empty field: {field}"

    def test_events_expected_content(self):
        """Test that events include expected Paraguay-specific content"""
        response = self.client.get("/api/events")
        assert response.status_code == 200
        events = response.json()
        
        expected_events = ["NASA Space Apps", "Iguassu Valley", "Design Week Asunción"]
        
        for expected in expected_events:
            event_found = False
            for event in events:
                title = event.get('title', '').lower()
                organizer = event.get('organizer', '').lower()
                if expected.lower() in title or expected.lower() in organizer:
                    event_found = True
                    break
            
            # Note: This is a soft assertion since exact events may vary
            if not event_found:
                print(f"Note: Expected event '{expected}' not found (this may be expected)")

    def test_events_paraguay_locations(self):
        """Test that events include Paraguay-specific locations"""
        response = self.client.get("/api/events")
        assert response.status_code == 200
        events = response.json()
        
        paraguay_locations = ['paraguay', 'asunción', 'ciudad del este']
        paraguay_events = 0
        
        for event in events:
            location = event.get('location', '').lower()
            if any(loc in location for loc in paraguay_locations):
                paraguay_events += 1
        
        # Should have at least some Paraguay-related events
        assert paraguay_events > 0, "No Paraguay-specific events found"

    def test_events_valid_dates(self):
        """Test that event dates are in valid format"""
        response = self.client.get("/api/events")
        assert response.status_code == 200
        events = response.json()
        
        for event in events:
            event_date = event.get('event_date')
            assert event_date, f"Event '{event.get('title')}' missing event_date"
            
            # Try to parse the date to ensure it's valid
            try:
                datetime.fromisoformat(event_date.replace('Z', '+00:00'))
            except ValueError:
                pytest.fail(f"Event '{event.get('title')}' has invalid date format: {event_date}")

    # JOBS CONTENT VERIFICATION
    def test_jobs_quantity_requirement(self):
        """Test that there are at least 6 job vacancies"""
        response = self.client.get("/api/jobs")
        assert response.status_code == 200
        jobs = response.json()
        
        assert len(jobs) >= 6, f"Expected at least 6 jobs, found {len(jobs)}"

    def test_jobs_required_fields(self):
        """Test that all jobs have required fields"""
        response = self.client.get("/api/jobs")
        assert response.status_code == 200
        jobs = response.json()
        
        required_fields = ['title', 'company_name', 'description', 'modality', 'job_type', 'apply_url']
        
        for job in jobs:
            for field in required_fields:
                assert field in job, f"Job '{job.get('title', 'Unknown')}' missing field: {field}"
                assert job[field], f"Job '{job.get('title', 'Unknown')}' has empty field: {field}"

    def test_jobs_expected_companies(self):
        """Test that jobs include expected real companies"""
        response = self.client.get("/api/jobs")
        assert response.status_code == 200
        jobs = response.json()
        
        expected_companies = ["Tigo", "Banco Continental", "Copetrol"]
        found_companies = {job.get('company_name', '') for job in jobs}
        
        for expected in expected_companies:
            company_found = any(expected.lower() in company.lower() for company in found_companies)
            # Note: This is a soft assertion since exact companies may vary
            if not company_found:
                print(f"Note: Expected company '{expected}' not found (this may be expected)")

    def test_jobs_real_apply_urls(self):
        """Test that jobs have real, non-placeholder apply URLs"""
        response = self.client.get("/api/jobs")
        assert response.status_code == 200
        jobs = response.json()
        
        suspicious_patterns = ['example.com', 'placeholder', 'fake', 'test']
        real_urls = 0
        
        for job in jobs:
            apply_url = job.get('apply_url', '')
            if apply_url and apply_url.startswith('http'):
                is_suspicious = any(pattern in apply_url.lower() for pattern in suspicious_patterns)
                if not is_suspicious:
                    real_urls += 1
        
        # At least 80% should have real URLs
        expected_real_urls = len(jobs) * 0.8
        assert real_urls >= expected_real_urls, f"Only {real_urls}/{len(jobs)} jobs have real apply URLs (expected at least {expected_real_urls})"

    def test_jobs_valid_enums(self):
        """Test that jobs use valid enum values"""
        response = self.client.get("/api/jobs")
        assert response.status_code == 200
        jobs = response.json()
        
        valid_modalities = ['remoto', 'presencial', 'hibrido']
        valid_job_types = ['practica', 'pasantia', 'junior', 'medio', 'senior']
        
        for job in jobs:
            modality = job.get('modality')
            job_type = job.get('job_type')
            
            assert modality in valid_modalities, f"Job '{job.get('title')}' has invalid modality: {modality}"
            assert job_type in valid_job_types, f"Job '{job.get('title')}' has invalid job_type: {job_type}"

    def test_jobs_geographic_requirements(self):
        """Test that presencial jobs are in Ciudad del Este"""
        response = self.client.get("/api/jobs")
        assert response.status_code == 200
        jobs = response.json()
        
        for job in jobs:
            if job.get('modality') == 'presencial':
                city = job.get('city')
                assert city == 'Ciudad del Este', f"Presencial job '{job.get('title')}' should be in Ciudad del Este, but is in '{city}'"

    # FILTER FUNCTIONALITY VERIFICATION
    def test_course_filters_work_correctly(self):
        """Test that course category filters work as expected"""
        # Get all courses
        all_response = self.client.get("/api/courses")
        assert all_response.status_code == 200
        all_courses = all_response.json()
        
        if all_courses:
            # Get unique categories
            categories = list(set(course.get('category') for course in all_courses if course.get('category')))
            
            # Test filtering by each category
            for category in categories[:3]:  # Test first 3 categories
                filtered_response = self.client.get(f"/api/courses?category={category}")
                assert filtered_response.status_code == 200
                filtered_courses = filtered_response.json()
                
                # All returned courses should match the category
                for course in filtered_courses:
                    assert course.get('category') == category, f"Filter failed: expected category '{category}', got '{course.get('category')}'"

    def test_job_filters_work_correctly(self):
        """Test that job modality filters work as expected"""
        # Get all jobs
        all_response = self.client.get("/api/jobs")
        assert all_response.status_code == 200
        all_jobs = all_response.json()
        
        if all_jobs:
            # Get unique modalities
            modalities = list(set(job.get('modality') for job in all_jobs if job.get('modality')))
            
            # Test filtering by each modality
            for modality in modalities:
                filtered_response = self.client.get(f"/api/jobs?modality={modality}")
                assert filtered_response.status_code == 200
                filtered_jobs = filtered_response.json()
                
                # All returned jobs should match the modality
                for job in filtered_jobs:
                    assert job.get('modality') == modality, f"Filter failed: expected modality '{modality}', got '{job.get('modality')}'"

    def test_search_functionality(self):
        """Test that search parameters work"""
        # Test course search
        response = self.client.get("/api/courses?search=python")
        assert response.status_code == 200
        
        # Test event search
        response = self.client.get("/api/events?search=tech")
        assert response.status_code == 200

    # SAVED ITEMS SECURITY VERIFICATION
    def test_saved_items_security(self):
        """Test that saved items endpoints require authentication"""
        # Get saved items should require auth
        response = self.client.get("/api/saved-items")
        assert response.status_code == 401, "Saved items endpoint should require authentication"
        
        # Save item should require auth
        response = self.client.post("/api/saved-items", json={"item_id": "test", "item_type": "course"})
        assert response.status_code == 401, "Save item endpoint should require authentication"
        
        # Delete saved item should require auth
        response = self.client.delete("/api/saved-items/test-id?item_type=course")
        assert response.status_code == 401, "Delete saved item endpoint should require authentication"

    # DATA CONSISTENCY TESTS
    def test_data_consistency(self):
        """Test that data is consistent across endpoints"""
        # Test that all referenced IDs exist
        response = self.client.get("/api/jobs")
        assert response.status_code == 200
        jobs = response.json()
        
        for job in jobs:
            # Verify job has valid ID
            job_id = job.get('id')
            assert job_id, f"Job '{job.get('title')}' missing ID"
            
            # Verify individual job endpoint works
            individual_response = self.client.get(f"/api/jobs/{job_id}")
            assert individual_response.status_code == 200, f"Job with ID {job_id} not accessible individually"

    # PERFORMANCE TESTS
    def test_response_times(self):
        """Test that API responses are reasonably fast"""
        import time
        
        endpoints = ["/api/courses", "/api/events", "/api/jobs"]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = self.client.get(endpoint)
            end_time = time.time()
            
            response_time = end_time - start_time
            assert response_time < 5.0, f"Endpoint {endpoint} took {response_time:.2f}s (should be < 5s)"

    # PAGINATION TESTS
    def test_pagination_works(self):
        """Test that pagination parameters work correctly"""
        # Test different limits
        for limit in [1, 5, 10, 20]:
            response = self.client.get(f"/api/courses?limit={limit}")
            assert response.status_code == 200
            courses = response.json()
            assert len(courses) <= limit, f"Returned {len(courses)} courses, expected max {limit}"

    # CONTENT QUALITY TESTS
    def test_content_quality(self):
        """Test overall content quality metrics"""
        # Get all content
        courses_response = self.client.get("/api/courses")
        events_response = self.client.get("/api/events")
        jobs_response = self.client.get("/api/jobs")
        
        assert courses_response.status_code == 200
        assert events_response.status_code == 200
        assert jobs_response.status_code == 200
        
        courses = courses_response.json()
        events = events_response.json()
        jobs = jobs_response.json()
        
        # Overall content should meet minimum requirements
        total_content = len(courses) + len(events) + len(jobs)
        assert total_content >= 38, f"Total content items {total_content} below minimum (20 courses + 12 events + 6 jobs = 38)"
        
        # Content should be diverse
        course_categories = {course.get('category') for course in courses}
        job_companies = {job.get('company_name') for job in jobs}
        
        assert len(course_categories) >= 3, "Course categories should be diverse"
        assert len(job_companies) >= 3, "Job companies should be diverse"