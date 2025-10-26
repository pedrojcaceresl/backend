#!/usr/bin/env python3
"""
Simple endpoint testing without complex dependencies
"""

import requests
import json

def test_basic_connectivity():
    """Test basic server connectivity"""
    base_url = "http://localhost:8000"
    
    print("🚀 Testing Basic API Connectivity")
    print("=" * 50)
    
    tests = [
        {"name": "Root endpoint", "url": f"{base_url}/", "method": "GET"},
        {"name": "API docs", "url": f"{base_url}/docs", "method": "GET"},
        {"name": "OpenAPI spec", "url": f"{base_url}/openapi.json", "method": "GET"},
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test["method"] == "GET":
                response = requests.get(test["url"], timeout=5)
            
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {test['name']}: {response.status_code}")
            
            if response.status_code == 200:
                passed += 1
                
        except Exception as e:
            print(f"❌ {test['name']}: Error - {str(e)}")
    
    print(f"\n📊 Basic Connectivity: {passed}/{total} tests passed")
    return passed == total

def test_endpoints_with_error_handling():
    """Test endpoints with proper error handling"""
    base_url = "http://localhost:8000"
    
    print("\n🔍 Testing API Endpoints (with error tolerance)")
    print("=" * 50)
    
    endpoints = [
        "/api/courses",
        "/api/events", 
        "/api/jobs",
        "/api/auth/me",
        "/api/users",
        "/api/stats/overview"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status_code = response.status_code
            
            if status_code == 200:
                status = "✅ Working"
                try:
                    data = response.json()
                    if isinstance(data, list):
                        status += f" (found {len(data)} items)"
                    elif isinstance(data, dict):
                        status += f" (keys: {list(data.keys())[:3]})"
                except:
                    status += " (response not JSON)"
            elif status_code == 401:
                status = "🔒 Requires auth"
            elif status_code == 404:
                status = "🚫 Not found"
            elif status_code == 500:
                status = "⚠️ Server error"
                try:
                    error_detail = response.json().get("detail", "Unknown error")
                    status += f" ({error_detail[:50]}...)"
                except:
                    pass
            else:
                status = f"❓ Status {status_code}"
            
            results[endpoint] = {"status_code": status_code, "status": status}
            print(f"{endpoint:<25} {status}")
            
        except Exception as e:
            results[endpoint] = {"error": str(e)}
            print(f"{endpoint:<25} ❌ Error: {str(e)}")
    
    return results

def test_auth_endpoints():
    """Test authentication endpoints"""
    base_url = "http://localhost:8000"
    
    print("\n🔐 Testing Authentication Endpoints")
    print("=" * 50)
    
    # Test login with known credentials
    login_data = {
        "email": "student@techhub.com",
        "password": "student123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=5)
        
        if response.status_code == 200:
            print("✅ Login endpoint working")
            data = response.json()
            if "access_token" in data:
                print("✅ JWT token generated")
            if "user" in data:
                print(f"✅ User data returned: {data['user'].get('name', 'Unknown')}")
        elif response.status_code == 500:
            error_detail = response.json().get("detail", "Unknown error")
            print(f"⚠️ Login endpoint has server error: {error_detail[:100]}")
        else:
            print(f"❌ Login failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Login test failed: {str(e)}")
    
    # Test unauthorized access
    try:
        response = requests.get(f"{base_url}/api/auth/me", timeout=5)
        if response.status_code == 401:
            print("✅ Unauthorized access properly blocked")
        else:
            print(f"⚠️ Expected 401, got {response.status_code}")
    except Exception as e:
        print(f"❌ Auth test failed: {str(e)}")

def main():
    print("TechHub UPE - Simple API Testing")
    print("=" * 40)
    
    # Test 1: Basic connectivity
    if not test_basic_connectivity():
        print("❌ Basic connectivity failed - check if server is running")
        return
    
    # Test 2: Endpoint availability
    results = test_endpoints_with_error_handling()
    
    # Test 3: Authentication
    test_auth_endpoints()
    
    # Summary
    print("\n📋 Summary")
    print("=" * 20)
    
    working_endpoints = sum(1 for r in results.values() if r.get("status_code") == 200)
    total_endpoints = len(results)
    
    print(f"✅ Working endpoints: {working_endpoints}/{total_endpoints}")
    
    if working_endpoints > 0:
        print("🎉 Your API is partially working!")
        print("🌐 Visit http://localhost:8000/docs for interactive testing")
    else:
        print("⚠️ API has issues - check server logs for details")
    
    # Show specific issues
    server_errors = [ep for ep, r in results.items() if r.get("status_code") == 500]
    if server_errors:
        print(f"\n⚠️ Endpoints with server errors:")
        for ep in server_errors:
            print(f"   • {ep}")

if __name__ == "__main__":
    main()