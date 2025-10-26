#!/usr/bin/env python3
"""
Basic health and connectivity tests
"""

import asyncio
import sys
import os

# Add parent directory to path to import helpers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.test_client import TestClient, check_server_health, print_test_header, print_test_section, print_success, print_error
import aiohttp

BASE_URL = "http://localhost:8000"

async def test_server_health():
    """Test basic server health and endpoints"""
    
    print_test_header("Server Health Testing")
    
    # Test server connectivity
    print_test_section("Server Connectivity")
    if await check_server_health():
        print_success("Server is running and healthy")
    else:
        print_error("Server is not responding")
        return False
    
    # Test documentation endpoint
    print_test_section("API Documentation")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/docs") as response:
                if response.status == 200:
                    print_success("API documentation is accessible")
                else:
                    print_error(f"Docs endpoint failed: {response.status}")
    except Exception as e:
        print_error(f"Docs endpoint error: {e}")
    
    # Test OpenAPI schema
    print_test_section("OpenAPI Schema")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/openapi.json") as response:
                if response.status == 200:
                    schema = await response.json()
                    paths_count = len(schema.get("paths", {}))
                    print_success(f"OpenAPI schema accessible ({paths_count} endpoints)")
                else:
                    print_error(f"OpenAPI schema failed: {response.status}")
    except Exception as e:
        print_error(f"OpenAPI schema error: {e}")
    
    # Test authentication
    print_test_section("Authentication System")
    async with TestClient() as client:
        if await client.login():
            print_success("Authentication system working")
        else:
            print_error("Authentication failed")
            return False
        
        if await client.login_admin():
            print_success("Admin authentication working")
        else:
            print_error("Admin authentication failed")
    
    # Test basic endpoints availability
    print_test_section("Core Endpoints Availability")
    endpoints_to_test = [
        "/api/applications",
        "/api/applications/stats", 
        "/api/saved-items/",
        "/api/saved-items/stats",
        "/api/jobs",
        "/api/courses",
        "/api/events"
    ]
    
    async with TestClient() as client:
        await client.login()
        
        for endpoint in endpoints_to_test:
            try:
                async with await client.get(endpoint) as response:
                    if response.status in [200, 307]:  # 307 for redirects
                        print_success(f"{endpoint} - Available")
                    else:
                        print_error(f"{endpoint} - Status {response.status}")
            except Exception as e:
                print_error(f"{endpoint} - Error: {e}")
    
    print_test_header("Health Testing Complete")
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(test_server_health())
        if success:
            print_success("All health tests passed!")
        else:
            print_error("Some health tests failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print_error("Testing interrupted by user")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)