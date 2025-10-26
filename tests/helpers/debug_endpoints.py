#!/usr/bin/env python3

import requests
import sys

BASE_URL = "http://localhost:8000"

def test_specific_endpoint():
    """Test specific failing endpoints with detailed error reporting"""
    
    # First authenticate
    auth_data = {
        "email": "admin@techhub.com",
        "password": "admin123"
    }
    
    auth_response = requests.post(f"{BASE_URL}/api/auth/login", json=auth_data)
    if auth_response.status_code != 200:
        print("❌ Authentication failed")
        return
    
    token = auth_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test SavedItems Stats multiple times
    print("🔍 Testing SavedItems Stats (Test 1)...")
    try:
        response = requests.get(f"{BASE_URL}/api/saved-items/stats", headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 500:
            print(f"Error Content: {response.text}")
        else:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Exception: {e}")
    
    print("\n🔍 Testing SavedItems Stats (Test 2)...")
    try:
        response = requests.get(f"{BASE_URL}/api/saved-items/stats", headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 500:
            print(f"Error Content: {response.text}")
        else:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Exception: {e}")
    
    print("\n🔍 Testing SavedItems Stats (Test 3)...")
    try:
        response = requests.get(f"{BASE_URL}/api/saved-items/stats", headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 500:
            print(f"Error Content: {response.text}")
        else:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Exception: {e}")
    
    print("\n🔍 Testing Applications...")
    try:
        response = requests.get(f"{BASE_URL}/api/applications/", headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 500:
            print(f"Error Content: {response.text}")
        else:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Exception: {e}")
    
    print("\n🔍 Testing Applications (without trailing slash)...")
    try:
        response = requests.get(f"{BASE_URL}/api/applications", headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 500:
            print(f"Error Content: {response.text}")
        else:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_specific_endpoint()