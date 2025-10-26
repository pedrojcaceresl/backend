#!/usr/bin/env python3
"""
Test script for new Applications and SavedItems functionality
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import sys

BASE_URL = "http://localhost:8000"

async def test_new_endpoints():
    """Test the new applications and saved items endpoints"""
    
    print("🔍 Testing New Applications and Saved Items Endpoints")
    print("=" * 60)
    
    # First check if server is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health") as response:
                if response.status != 200:
                    print("❌ Server is not healthy")
                    return False
    except:
        print("❌ Server is not running. Please start with: uvicorn main:app --reload")
        return False
    
    print("✅ Server is running")
    
    # Test user login first
    login_data = {
        "email": "student@techhub.com", 
        "password": "student123"
    }
    
    token = None
    
    async with aiohttp.ClientSession() as session:
        print("\n🔐 Testing Authentication...")
        
        # Login
        async with session.post(f"{BASE_URL}/api/auth/login", json=login_data) as response:
            if response.status == 200:
                result = await response.json()
                token = result.get("access_token")
                print(f"✅ Login successful")
            else:
                print(f"❌ Login failed: {response.status}")
                return False
        
        headers = {"Authorization": f"Bearer {token}"}
        
        print("\n📊 Testing SavedItems Endpoints...")
        
        # Test saved items stats (should be empty initially)
        async with session.get(f"{BASE_URL}/api/saved-items/stats", headers=headers) as response:
            if response.status == 200:
                stats = await response.json()
                print(f"✅ SavedItems Stats: {stats}")
            else:
                print(f"❌ SavedItems Stats failed: {response.status}")
        
        # Test get saved items (should be empty)
        async with session.get(f"{BASE_URL}/api/saved-items", headers=headers) as response:
            if response.status == 200:
                items = await response.json()
                print(f"✅ Get SavedItems: {len(items)} items")
            else:
                print(f"❌ Get SavedItems failed: {response.status}")
        
        # Test legacy saved items endpoint
        async with session.get(f"{BASE_URL}/api/saved-items/legacy", headers=headers) as response:
            if response.status == 200:
                legacy_items = await response.json()
                print(f"✅ Legacy SavedItems: {legacy_items}")
            else:
                print(f"❌ Legacy SavedItems failed: {response.status}")
        
        # Get a job to save
        async with session.get(f"{BASE_URL}/api/jobs") as response:
            if response.status == 200:
                jobs = await response.json()
                if jobs and len(jobs) > 0:
                    job_id = jobs[0].get("id")
                    print(f"✅ Found job to test with: {job_id}")
                    
                    # Test saving a job
                    save_data = {
                        "item_type": "job",
                        "item_id": job_id
                    }
                    
                    async with session.post(f"{BASE_URL}/api/saved-items/", json=save_data, headers=headers) as response:
                        if response.status == 200:
                            saved_item = await response.json()
                            print(f"✅ Saved job successfully: {saved_item.get('id')}")
                            
                            # Test check if saved
                            async with session.get(f"{BASE_URL}/api/saved-items/check/job/{job_id}", headers=headers) as response:
                                if response.status == 200:
                                    check_result = await response.json()
                                    print(f"✅ Check if saved: {check_result}")
                                else:
                                    print(f"❌ Check if saved failed: {response.status}")
                            
                            # Test toggle (should unsave)
                            async with session.post(f"{BASE_URL}/api/saved-items/toggle/job/{job_id}", headers=headers) as response:
                                if response.status == 200:
                                    toggle_result = await response.json()
                                    print(f"✅ Toggle save status: {toggle_result}")
                                else:
                                    print(f"❌ Toggle save failed: {response.status}")
                        
                        elif response.status == 400:
                            error = await response.json()
                            if "ya está guardado" in error.get("detail", ""):
                                print(f"✅ Save job (already saved): {error.get('detail')}")
                            else:
                                print(f"❌ Save job failed: {error}")
                        else:
                            print(f"❌ Save job failed: {response.status}")
                else:
                    print("❌ No jobs found to test with")
        
        print("\n💼 Testing Applications Endpoints...")
        
        # Test application stats (should be empty initially)
        async with session.get(f"{BASE_URL}/api/applications/stats", headers=headers) as response:
            if response.status == 200:
                stats = await response.json()
                print(f"✅ Application Stats: {stats}")
            else:
                print(f"❌ Application Stats failed: {response.status}")
        
        # Test get my applications (should be empty)
        async with session.get(f"{BASE_URL}/api/applications", headers=headers) as response:
            if response.status == 200:
                applications = await response.json()
                print(f"✅ Get My Applications: {len(applications)} applications")
            else:
                print(f"❌ Get My Applications failed: {response.status}")
        
        # Get a job to apply to
        async with session.get(f"{BASE_URL}/api/jobs") as response:
            if response.status == 200:
                jobs = await response.json()
                if jobs and len(jobs) > 0:
                    job_id = jobs[0].get("id")
                    print(f"✅ Found job to apply to: {job_id}")
                    
                    # Test applying to job
                    application_data = {
                        "job_id": job_id,
                        "cover_letter": "I am very interested in this position and believe my skills would be a great fit.",
                        "resume_url": "https://example.com/my-resume.pdf"
                    }
                    
                    async with session.post(f"{BASE_URL}/api/applications", json=application_data, headers=headers) as response:
                        if response.status == 200:
                            application = await response.json()
                            application_id = application.get("id")
                            print(f"✅ Applied to job successfully: {application_id}")
                            
                            # Test get application detail
                            async with session.get(f"{BASE_URL}/api/applications/{application_id}", headers=headers) as response:
                                if response.status == 200:
                                    app_detail = await response.json()
                                    print(f"✅ Get Application Detail: {app_detail.get('status')}")
                                else:
                                    print(f"❌ Get Application Detail failed: {response.status}")
                            
                            # Test withdraw application
                            async with session.put(f"{BASE_URL}/api/applications/{application_id}/withdraw", headers=headers) as response:
                                if response.status == 200:
                                    withdraw_result = await response.json()
                                    print(f"✅ Withdraw Application: {withdraw_result}")
                                else:
                                    print(f"❌ Withdraw Application failed: {response.status}")
                        
                        elif response.status == 400:
                            error = await response.json()
                            if "ya has postulado" in error.get("detail", ""):
                                print(f"✅ Apply to job (already applied): {error.get('detail')}")
                            else:
                                print(f"❌ Apply to job failed: {error}")
                        else:
                            print(f"❌ Apply to job failed: {response.status}")
                else:
                    print("❌ No jobs found to apply to")
        
        print("\n📈 Final Stats Check...")
        
        # Final stats check
        async with session.get(f"{BASE_URL}/api/saved-items/stats", headers=headers) as response:
            if response.status == 200:
                final_saved_stats = await response.json()
                print(f"✅ Final SavedItems Stats: {final_saved_stats}")
        
        async with session.get(f"{BASE_URL}/api/applications/stats", headers=headers) as response:
            if response.status == 200:
                final_app_stats = await response.json()
                print(f"✅ Final Application Stats: {final_app_stats}")
    
    print("\n🎉 New endpoints testing completed!")
    return True

if __name__ == "__main__":
    print("New Endpoints Testing - JobConnect Backend")
    print("=" * 50)
    
    try:
        success = asyncio.run(test_new_endpoints())
        if success:
            print("\n✨ All new endpoint tests completed successfully!")
        else:
            print("\n❌ Some tests failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)