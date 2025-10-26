#!/usr/bin/env python3
"""
Integration tests for Applications API endpoints
"""

import asyncio
import sys
import os

# Add parent directory to path to import helpers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.test_client import TestClient, check_server_health, get_sample_job, print_test_header, print_test_section, print_success, print_error

async def test_applications_api():
    """Test Applications API endpoints"""
    
    print_test_header("Applications API Testing")
    
    # Check server health
    if not await check_server_health():
        print_error("Server is not running. Please start with: uvicorn main:app --reload")
        return False
    
    print_success("Server is running")
    
    async with TestClient() as client:
        # Authentication
        print_test_section("Authentication")
        if not await client.login():
            print_error("Login failed")
            return False
        print_success("Login successful")
        
        # Get sample job
        job = await get_sample_job()
        if not job:
            print_error("No jobs found for testing")
            return False
        
        job_id = job.get("id")
        print_success(f"Found job for testing: {job_id}")
        
        # Test Application Stats (initial)
        print_test_section("Application Statistics")
        async with await client.get("/api/applications/stats") as response:
            if response.status == 200:
                stats = await response.json()
                print_success(f"Initial stats: {stats}")
            else:
                print_error(f"Stats failed: {response.status}")
        
        # Test Get My Applications (initial)
        print_test_section("Get My Applications")
        async with await client.get("/api/applications/") as response:
            if response.status == 200:
                applications = await response.json()
                initial_count = len(applications)
                print_success(f"Initial applications: {initial_count}")
            else:
                print_error(f"Get applications failed: {response.status}")
                return False
        
        # Test Apply to Job
        print_test_section("Apply to Job")
        application_data = {
            "job_id": job_id,
            "cover_letter": "I am very interested in this position and believe my skills would be a great fit for this role.",
            "resume_url": "https://example.com/my-resume.pdf"
        }
        
        async with await client.post("/api/applications/", application_data) as response:
            if response.status == 200:
                application = await response.json()
                application_id = application.get("id")
                print_success(f"Applied successfully: {application_id}")
                
                # Test Get Application Detail
                print_test_section("Get Application Detail")
                async with await client.get(f"/api/applications/{application_id}") as response:
                    if response.status == 200:
                        detail = await response.json()
                        print_success(f"Application detail - Status: {detail.get('status')}")
                    else:
                        print_error(f"Get detail failed: {response.status}")
                
                # Test Withdraw Application
                print_test_section("Withdraw Application")
                async with await client.put(f"/api/applications/{application_id}/withdraw") as response:
                    if response.status == 200:
                        result = await response.json()
                        print_success(f"Withdrawn: {result.get('message', 'Success')}")
                    else:
                        print_error(f"Withdraw failed: {response.status}")
                
            elif response.status == 400:
                error = await response.json()
                if "ya has postulado" in error.get("detail", "").lower():
                    print_success("Already applied (expected behavior)")
                else:
                    print_error(f"Apply failed: {error}")
            else:
                print_error(f"Apply failed: {response.status}")
        
        # Test Final Stats
        print_test_section("Final Statistics")
        async with await client.get("/api/applications/stats") as response:
            if response.status == 200:
                final_stats = await response.json()
                print_success(f"Final stats: {final_stats}")
            else:
                print_error(f"Final stats failed: {response.status}")
    
    print_test_header("Applications Testing Complete")
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(test_applications_api())
        if success:
            print_success("All application tests completed!")
        else:
            print_error("Some tests failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print_error("Testing interrupted by user")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)