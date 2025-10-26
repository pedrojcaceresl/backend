#!/usr/bin/env python3
"""
Main test runner for JobConnect Backend
"""

import asyncio
import sys
import os
import importlib.util

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from helpers.test_client import print_test_header, print_success, print_error

async def run_test_module(module_path: str, test_function: str) -> bool:
    """Run a specific test module"""
    try:
        spec = importlib.util.spec_from_file_location("test_module", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        test_func = getattr(module, test_function)
        return await test_func()
    except Exception as e:
        print_error(f"Failed to run {module_path}: {e}")
        return False

async def run_all_tests():
    """Run all integration tests"""
    
    print_test_header("JobConnect Backend - Complete Test Suite")
    
    test_modules = [
        ("integration/test_health.py", "test_server_health"),
        ("integration/test_applications.py", "test_applications_api"),
        ("integration/test_saved_items.py", "test_saved_items_api")
    ]
    
    results = []
    
    for module_file, test_function in test_modules:
        module_path = os.path.join(os.path.dirname(__file__), module_file)
        print(f"\n🚀 Running {module_file}...")
        
        try:
            success = await run_test_module(module_path, test_function)
            results.append((module_file, success))
            
            if success:
                print_success(f"{module_file} - PASSED")
            else:
                print_error(f"{module_file} - FAILED")
        except Exception as e:
            print_error(f"{module_file} - ERROR: {e}")
            results.append((module_file, False))
    
    # Summary
    print_test_header("Test Results Summary")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n📊 Results: {passed}/{total} test modules passed\n")
    
    for module_file, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {status} - {module_file}")
    
    if passed == total:
        print_success(f"\n🎉 All {total} test modules passed!")
        return True
    else:
        print_error(f"\n💥 {total - passed} test modules failed!")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print_error("\n🛑 Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n💥 Unexpected error: {e}")
        sys.exit(1)