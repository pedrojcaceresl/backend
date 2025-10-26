#!/usr/bin/env python3
"""
Debug script for SavedItems endpoint
"""

import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:8000"

async def debug_saved_items():
    """Debug the saved items endpoint in detail"""
    
    print("🔍 Debugging SavedItems Endpoint")
    print("=" * 40)
    
    # Login first
    login_data = {
        "email": "student@techhub.com", 
        "password": "student123"
    }
    
    async with aiohttp.ClientSession() as session:
        # Login
        async with session.post(f"{BASE_URL}/api/auth/login", json=login_data) as response:
            if response.status == 200:
                result = await response.json()
                token = result.get("access_token")
                print(f"✅ Login successful")
            else:
                print(f"❌ Login failed: {response.status}")
                return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get a job first
        async with session.get(f"{BASE_URL}/api/jobs") as response:
            if response.status == 200:
                jobs = await response.json()
                if jobs and len(jobs) > 0:
                    job = jobs[0]
                    job_id = job.get("id")
                    print(f"✅ Found job: {job_id}")
                    print(f"Job data: {json.dumps(job, indent=2)}")
                else:
                    print("❌ No jobs found")
                    return
            else:
                print(f"❌ Failed to get jobs: {response.status}")
                return
        
        # Test different save data formats
        test_formats = [
            {
                "item_type": "job",
                "item_id": job_id
            },
            {
                "item_type": "JOB",
                "item_id": job_id
            }
        ]
        
        for i, save_data in enumerate(test_formats):
            print(f"\n🧪 Testing format {i+1}: {save_data}")
            
            async with session.post(f"{BASE_URL}/api/saved-items", json=save_data, headers=headers) as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Success: {result}")
                    break
                else:
                    error_text = await response.text()
                    print(f"❌ Error: {error_text}")
                    
                    if response.status == 422:
                        try:
                            error_json = json.loads(error_text)
                            print(f"Validation details: {json.dumps(error_json, indent=2)}")
                        except:
                            pass

if __name__ == "__main__":
    asyncio.run(debug_saved_items())