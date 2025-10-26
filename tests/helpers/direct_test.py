#!/usr/bin/env python3
"""
Direct test with specific URL
"""

import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:8000"

async def test_specific_endpoint():
    """Test specific endpoint with different approaches"""
    
    print("🔍 Direct endpoint testing")
    print("=" * 30)
    
    # Login first
    login_data = {
        "email": "student@techhub.com", 
        "password": "student123"
    }
    
    async with aiohttp.ClientSession() as session:
        # Login
        async with session.post(f"{BASE_URL}/api/auth/login", json=login_data) as response:
            result = await response.json()
            token = result.get("access_token")
            print(f"✅ Login successful")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test the exact POST endpoint without trailing slash
        save_data = {
            "item_type": "job",
            "item_id": "job-1"
        }
        
        print(f"\n🧪 Testing POST /api/saved-items (no trailing slash)")
        async with session.post(f"{BASE_URL}/api/saved-items", json=save_data, headers=headers) as response:
            print(f"Status: {response.status}")
            text = await response.text()
            print(f"Response: {text}")
            
        print(f"\n🧪 Testing POST /api/saved-items/ (with trailing slash)")
        async with session.post(f"{BASE_URL}/api/saved-items/", json=save_data, headers=headers) as response:
            print(f"Status: {response.status}")
            text = await response.text()
            print(f"Response: {text}")

if __name__ == "__main__":
    asyncio.run(test_specific_endpoint())