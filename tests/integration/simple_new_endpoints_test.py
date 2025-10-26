#!/usr/bin/env python3
"""
Simple test to verify server functionality
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_server():
    """Test basic server functionality"""
    
    print("🔍 Testing Server and New Endpoints")
    print("=" * 50)
    
    try:
        # Test health endpoint
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is healthy")
            health_data = response.json()
            print(f"   Status: {health_data.get('status')}")
            print(f"   Database: {health_data.get('database', 'unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start with: uvicorn main:app --reload")
        return False
    
    # Test docs endpoint
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API Documentation is accessible")
        else:
            print(f"❌ Docs endpoint failed: {response.status_code}")
    except:
        print("❌ Docs endpoint not accessible")
    
    # Test new endpoints existence (without auth)
    print("\n📋 Testing New Endpoint Availability...")
    
    endpoints_to_test = [
        "/api/applications",
        "/api/saved-items/", 
        "/api/saved-items/stats",
        "/api/applications/stats"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            # 401 is expected for protected endpoints without auth
            if response.status_code in [401, 422]:  # 422 for validation errors
                print(f"✅ {endpoint} - Endpoint exists (requires auth)")
            elif response.status_code == 200:
                print(f"✅ {endpoint} - Accessible")
            else:
                print(f"❌ {endpoint} - Unexpected status: {response.status_code}")
        except:
            print(f"❌ {endpoint} - Not accessible")
    
    # Test authentication
    print("\n🔐 Testing Authentication...")
    
    login_data = {
        "email": "admin@techhub.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            token = result.get("access_token")
            print("✅ Authentication successful")
            
            # Test authenticated endpoints
            headers = {"Authorization": f"Bearer {token}"}
            
            print("\n📊 Testing Authenticated Endpoints...")
            
            # Test saved items stats
            response = requests.get(f"{BASE_URL}/api/saved-items/stats", headers=headers)
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ SavedItems Stats: {stats}")
            else:
                print(f"❌ SavedItems Stats failed: {response.status_code}")
            
            # Test application stats
            response = requests.get(f"{BASE_URL}/api/applications/stats", headers=headers)
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ Application Stats: {stats}")
            else:
                print(f"❌ Application Stats failed: {response.status_code}")
            
            # Test get saved items
            response = requests.get(f"{BASE_URL}/api/saved-items", headers=headers)
            if response.status_code == 200:
                items = response.json()
                print(f"✅ Get SavedItems: {len(items)} items")
            else:
                print(f"❌ Get SavedItems failed: {response.status_code}")
            
            # Test get applications
            response = requests.get(f"{BASE_URL}/api/applications", headers=headers)
            if response.status_code == 200:
                applications = response.json()
                print(f"✅ Get Applications: {len(applications)} applications")
            else:
                print(f"❌ Get Applications failed: {response.status_code}")
                
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            if response.status_code == 422:
                print(f"   Error: {response.json()}")
    
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
    
    print("\n🎉 Basic functionality test completed!")
    return True

if __name__ == "__main__":
    print("JobConnect Backend - New Endpoints Test")
    print("=" * 45)
    
    success = test_server()
    if success:
        print("\n✨ Basic tests completed!")
    else:
        print("\n❌ Some tests failed")