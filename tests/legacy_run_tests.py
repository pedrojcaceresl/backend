#!/usr/bin/env python3
"""
Test runner for TechHub UPE backend tests
Run this script to execute all tests with proper configuration
"""

import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """Run all tests with proper configuration"""
    
    # Add project root to Python path
    project_root = Path(__file__).parent
    os.environ["PYTHONPATH"] = str(project_root)
    
    # Test commands to run
    test_commands = [
        # Run all tests with coverage
        [
            "python", "-m", "pytest", 
            "tests/", 
            "-v", 
            "--tb=short",
            "--durations=10",
            "-x"  # Stop on first failure
        ],
        
        # Run only unit tests
        [
            "python", "-m", "pytest", 
            "tests/", 
            "-v", 
            "-m", "unit",
            "--tb=short"
        ],
        
        # Run only integration tests
        [
            "python", "-m", "pytest", 
            "tests/", 
            "-v", 
            "-m", "integration",
            "--tb=short"
        ],
        
        # Run content verification tests
        [
            "python", "-m", "pytest", 
            "tests/test_content_verification.py", 
            "-v", 
            "--tb=short"
        ],
        
        # Run API endpoint tests
        [
            "python", "-m", "pytest", 
            "tests/test_api_endpoints.py", 
            "-v", 
            "--tb=short"
        ]
    ]
    
    print("🚀 Starting TechHub UPE Backend Tests")
    print("=" * 60)
    
    for i, cmd in enumerate(test_commands, 1):
        test_name = " ".join(cmd[-3:]) if "-m" in cmd else cmd[-1]
        print(f"\n📋 Running Test Suite {i}/{len(test_commands)}: {test_name}")
        print("-" * 40)
        
        try:
            result = subprocess.run(cmd, cwd=project_root, check=False)
            if result.returncode != 0:
                print(f"❌ Test suite failed with return code {result.returncode}")
                if "--tb=short" in cmd:
                    print("💡 Tip: Run with --tb=long for more detailed error info")
            else:
                print(f"✅ Test suite passed!")
                
        except FileNotFoundError:
            print(f"❌ Could not run pytest. Make sure pytest is installed:")
            print("   pip install pytest pytest-asyncio")
            return 1
        except KeyboardInterrupt:
            print(f"\n⚠️ Tests interrupted by user")
            return 1
    
    print(f"\n🏁 All test suites completed!")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)