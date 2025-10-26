#!/usr/bin/env python3
"""
Integration tests for SavedItems API endpoints
"""

import asyncio
import sys
import os

# Add parent directory to path to import helpers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.test_client import TestClient, check_server_health, get_sample_job, print_test_header, print_test_section, print_success, print_error

async def test_saved_items_api():
    """Test SavedItems API endpoints"""
    
    print_test_header("SavedItems API Testing")
    
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
        
        # Test Get Saved Items (initial)
        print_test_section("Get Saved Items (Initial)")
        async with await client.get("/api/saved-items/") as response:
            if response.status == 200:
                items = await response.json()
                initial_count = len(items)
                print_success(f"Initial saved items: {initial_count}")
            else:
                print_error(f"Get saved items failed: {response.status}")
        
        # Test Legacy Format
        print_test_section("Legacy Format")
        async with await client.get("/api/saved-items/legacy") as response:
            if response.status == 200:
                legacy_items = await response.json()
                print_success(f"Legacy format: {len(legacy_items.get('jobs', []))} jobs, {len(legacy_items.get('courses', []))} courses")
            else:
                print_error(f"Legacy format failed: {response.status}")
        
        # Get sample job for testing
        job = await get_sample_job()
        if not job:
            print_error("No jobs found for testing")
            return False
        
        job_id = job.get("id")
        print_success(f"Found job for testing: {job_id}")
        
        # Test Save Item
        print_test_section("Save Item")
        save_data = {
            "item_type": "job",
            "item_id": job_id
        }
        
        async with await client.post("/api/saved-items/", save_data) as response:
            if response.status == 200:
                saved_item = await response.json()
                saved_item_id = saved_item.get("id")
                print_success(f"Saved item: {saved_item_id}")
                
                # Test Check If Saved
                print_test_section("Check If Saved")
                async with await client.get(f"/api/saved-items/check/job/{job_id}") as response:
                    if response.status == 200:
                        check_result = await response.json()
                        print_success(f"Check result: {check_result}")
                    else:
                        print_error(f"Check failed: {response.status}")
                
                # Test Toggle (should unsave)
                print_test_section("Toggle Save Status")
                async with await client.post(f"/api/saved-items/toggle/job/{job_id}") as response:
                    if response.status == 200:
                        toggle_result = await response.json()
                        print_success(f"Toggle result: {toggle_result}")
                    else:
                        print_error(f"Toggle failed: {response.status}")
                
                # Test Remove by ID
                print_test_section("Remove Saved Item")
                async with await client.delete(f"/api/saved-items/{saved_item_id}") as response:
                    if response.status == 200:
                        print_success("Item removed successfully")
                    else:
                        print_error(f"Remove failed: {response.status}")
                
            elif response.status == 400:
                error = await response.json()
                if "ya está guardado" in error.get("detail", "").lower():
                    print_success("Already saved (expected behavior)")
                else:
                    print_error(f"Save failed: {error}")
            else:
                print_error(f"Save failed: {response.status}")
        
        # Test Bulk Save
        print_test_section("Bulk Save")
        bulk_data = {
            "items": [
                {"item_type": "job", "item_id": job_id}
            ]
        }
        
        async with await client.post("/api/saved-items/bulk", bulk_data) as response:
            if response.status == 200:
                bulk_result = await response.json()
                print_success(f"Bulk save: {bulk_result.get('saved_count', 0)} items saved")
            else:
                print_error(f"Bulk save failed: {response.status}")
        
        # Test Final Stats
        print_test_section("Final Statistics")
        async with await client.get("/api/saved-items/stats") as response:
            if response.status == 200:
                final_stats = await response.json()
                print_success(f"Final stats: {final_stats}")
            else:
                print_error(f"Stats failed: {response.status}")
    
    print_test_header("SavedItems Testing Complete")
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(test_saved_items_api())
        if success:
            print_success("All saved items tests completed!")
        else:
            print_error("Some tests failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print_error("Testing interrupted by user")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)