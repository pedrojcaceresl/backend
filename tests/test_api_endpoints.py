import pytest
import requests
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from unittest.mock import Mock, patch

class TestAPIEndpoints:
    """Test suite for TechHub UPE API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        """Setup for each test"""
        self.client = api_client
        self.base_url = "http://localhost:8000/api"
        self.session_token = None

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

    # COURSES ENDPOINTS TESTS
    def test_get_all_courses(self):
        """Test getting all courses"""
        response = self.client.get("/api/courses")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            course = data[0]
            required_fields = ['title', 'description', 'provider', 'url', 'category']
            for field in required_fields:
                assert field in course

    def test_get_courses_with_limit(self):
        """Test getting courses with limit parameter"""
        response = self.client.get("/api/courses?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 3

    def test_get_courses_with_category_filter(self):
        """Test getting courses with category filter"""
        response = self.client.get("/api/courses?category=programacion")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # If any courses returned, they should match the category
        for course in data:
            assert course.get('category') == 'programacion'

    def test_get_courses_with_search(self):
        """Test getting courses with search parameter"""
        response = self.client.get("/api/courses?search=python")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_courses_all_categories_filter(self):
        """Test that 'todas las categorias' filter returns all courses"""
        # Get all courses without filter
        all_response = self.client.get("/api/courses")
        all_courses = all_response.json()
        
        # Get courses with "todas las categorias" filter
        filtered_response = self.client.get("/api/courses?category=todas las categorias")
        filtered_courses = filtered_response.json()
        
        assert len(all_courses) == len(filtered_courses)

    # EVENTS ENDPOINTS TESTS
    def test_get_all_events(self):
        """Test getting all events"""
        response = self.client.get("/api/events")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            event = data[0]
            required_fields = ['title', 'description', 'organizer', 'url', 'event_date', 'location']
            for field in required_fields:
                assert field in event

    def test_get_events_with_limit(self):
        """Test getting events with limit parameter"""
        response = self.client.get("/api/events?limit=4")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 4

    def test_get_events_with_category_filter(self):
        """Test getting events with category filter"""
        response = self.client.get("/api/events?category=webinar")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_events_with_search(self):
        """Test getting events with search parameter"""
        response = self.client.get("/api/events?search=tech")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    # JOBS ENDPOINTS TESTS
    def test_get_all_jobs(self):
        """Test getting all jobs"""
        response = self.client.get("/api/jobs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            job = data[0]
            required_fields = ['title', 'company_name', 'description', 'modality', 'job_type']
            for field in required_fields:
                assert field in job

    def test_get_jobs_with_modality_filter(self):
        """Test getting jobs with modality filter"""
        response = self.client.get("/api/jobs?modality=remoto")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        for job in data:
            assert job.get('modality') == 'remoto'

    def test_get_jobs_with_type_filter(self):
        """Test getting jobs with job type filter"""
        response = self.client.get("/api/jobs?job_type=junior")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        for job in data:
            assert job.get('job_type') == 'junior'

    def test_get_jobs_with_skills_filter(self):
        """Test getting jobs with skills filter"""
        response = self.client.get("/api/jobs?skills=Python,JavaScript")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_jobs_with_multiple_filters(self):
        """Test getting jobs with multiple filters"""
        response = self.client.get("/api/jobs?modality=remoto&job_type=junior&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
        
        for job in data:
            assert job.get('modality') == 'remoto'
            assert job.get('job_type') == 'junior'

    def test_get_jobs_todas_las_vacantes_filter(self):
        """Test that 'todas las vacantes' filter returns all jobs"""
        # Get all jobs without filter
        all_response = self.client.get("/api/jobs")
        all_jobs = all_response.json()
        
        # Get jobs with "todas las vacantes" filter
        filtered_response = self.client.get("/api/jobs?modality=todas las vacantes")
        filtered_jobs = filtered_response.json()
        
        assert len(all_jobs) == len(filtered_jobs)

    def test_get_individual_job(self):
        """Test getting individual job by ID"""
        # First get all jobs to get a valid ID
        response = self.client.get("/api/jobs?limit=1")
        assert response.status_code == 200
        jobs = response.json()
        
        if len(jobs) > 0:
            job_id = jobs[0]['id']
            
            # Test getting individual job
            job_response = self.client.get(f"/api/jobs/{job_id}")
            assert job_response.status_code == 200
            job_data = job_response.json()
            assert job_data['id'] == job_id

    def test_get_job_with_invalid_id(self):
        """Test getting job with invalid ID"""
        response = self.client.get("/api/jobs/invalid-id-123")
        assert response.status_code == 404

    # LOCATION TESTS
    def test_job_locations_geographic_requirements(self):
        """Test job locations meet geographic requirements"""
        response = self.client.get("/api/jobs")
        assert response.status_code == 200
        jobs = response.json()
        
        if len(jobs) > 0:
            # Check that presencial jobs are in Ciudad del Este
            presencial_jobs = [job for job in jobs if job.get('modality') == 'presencial']
            
            for job in presencial_jobs:
                city = job.get('city')
                assert city == 'Ciudad del Este', f"Presencial job '{job['title']}' should be in Ciudad del Este, but is in '{city}'"

    # AUTHENTICATION TESTS (Unauthenticated)
    def test_auth_me_unauthenticated(self):
        """Test /auth/me without authentication should fail"""
        response = self.client.get("/api/auth/me")
        assert response.status_code == 401

    def test_auth_complete_without_session_id(self):
        """Test /auth/complete without session ID should fail"""
        response = self.client.post("/api/auth/complete")
        assert response.status_code == 400

    def test_auth_logout_unauthenticated(self):
        """Test logout without authentication"""
        response = self.client.post("/api/auth/logout")
        assert response.status_code == 200

    # SAVED ITEMS TESTS (Unauthenticated - should fail)
    def test_get_saved_items_unauthenticated(self):
        """Test getting saved items without authentication should fail"""
        response = self.client.get("/api/saved-items")
        assert response.status_code == 401

    def test_save_item_unauthenticated(self):
        """Test saving item without authentication should fail"""
        response = self.client.post("/api/saved-items?item_id=test-id&item_type=course")
        assert response.status_code == 401

    def test_unsave_item_unauthenticated(self):
        """Test removing saved item without authentication should fail"""
        response = self.client.delete("/api/saved-items/test-id?item_type=course")
        assert response.status_code == 401

    # PROFILE UPDATE TESTS (Unauthenticated - should fail)
    def test_update_profile_unauthenticated(self):
        """Test updating profile without authentication should fail"""
        profile_data = {
            "role": "empresa",
            "company_name": "Test Company",
            "company_document": "12345678-9"
        }
        
        response = self.client.put("/api/users/profile", json=profile_data)
        assert response.status_code == 401

    # JOB CREATION TESTS (Unauthenticated - should fail)
    def test_create_job_unauthenticated(self):
        """Test creating job without authentication should fail"""
        job_data = {
            "title": "Test Developer Position",
            "description": "Test job description",
            "modality": "remoto",
            "job_type": "junior"
        }
        
        response = self.client.post("/api/jobs", json=job_data)
        assert response.status_code == 401

    # FILTER FUNCTIONALITY TESTS
    def test_course_filters_functionality(self):
        """Test course category filters work correctly"""
        # Get all courses first
        all_response = self.client.get("/api/courses")
        all_courses = all_response.json()
        
        if len(all_courses) > 0:
            # Get unique categories
            categories = list(set(course.get('category') for course in all_courses if course.get('category')))
            
            # Test filtering by first category
            if categories:
                test_category = categories[0]
                filtered_response = self.client.get(f"/api/courses?category={test_category}")
                filtered_courses = filtered_response.json()
                
                # All returned courses should match the category
                for course in filtered_courses:
                    assert course.get('category') == test_category

    def test_job_filters_functionality(self):
        """Test job modality filters work correctly"""
        # Get all jobs first
        all_response = self.client.get("/api/jobs")
        all_jobs = all_response.json()
        
        if len(all_jobs) > 0:
            # Get unique modalities
            modalities = list(set(job.get('modality') for job in all_jobs if job.get('modality')))
            
            # Test filtering by first modality
            if modalities:
                test_modality = modalities[0]
                filtered_response = self.client.get(f"/api/jobs?modality={test_modality}")
                filtered_jobs = filtered_response.json()
                
                # All returned jobs should match the modality
                for job in filtered_jobs:
                    assert job.get('modality') == test_modality

    # COMPANY ENDPOINTS TESTS (Unauthenticated - should fail)
    def test_get_company_applications_unauthenticated(self):
        """Test getting company applications without authentication should fail"""
        response = self.client.get("/api/company/applications")
        assert response.status_code == 401

    def test_update_application_status_unauthenticated(self):
        """Test updating application status without authentication should fail"""
        response = self.client.put("/api/company/applications/test-id/status", json={"status": "accepted"})
        assert response.status_code == 401

    # STATS ENDPOINTS TESTS
    def test_get_stats(self):
        """Test getting stats"""
        response = self.client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    # ERROR HANDLING TESTS
    def test_invalid_endpoint(self):
        """Test invalid endpoint returns 404"""
        response = self.client.get("/api/invalid-endpoint")
        assert response.status_code == 404

    def test_invalid_method(self):
        """Test invalid HTTP method returns 405"""
        response = self.client.patch("/api/courses")  # PATCH not supported
        assert response.status_code == 405

    # PAGINATION TESTS
    def test_pagination_limits(self):
        """Test pagination with various limits"""
        # Test normal limit
        response = self.client.get("/api/courses?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5
        
        # Test zero limit (should default to reasonable number)
        response = self.client.get("/api/courses?limit=0")
        assert response.status_code == 200
        
        # Test excessive limit (should be capped)
        response = self.client.get("/api/courses?limit=1000")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 100  # Should be capped at 100