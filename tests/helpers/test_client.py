#!/usr/bin/env python3
"""
Common test helpers and utilities
"""

import asyncio
import aiohttp
import json
from typing import Optional, Dict, Any

BASE_URL = "http://localhost:8000"

class TestClient:
    """Async test client for API testing"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def login(self, email: str = "student@techhub.com", password: str = "student123") -> bool:
        """Login and store auth token"""
        login_data = {"email": email, "password": password}
        
        async with self.session.post(f"{self.base_url}/api/auth/login", json=login_data) as response:
            if response.status == 200:
                result = await response.json()
                self.token = result.get("access_token")
                return True
            return False
    
    async def login_admin(self) -> bool:
        """Login as admin"""
        return await self.login("admin@techhub.com", "admin123")
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get auth headers"""
        if not self.token:
            raise ValueError("Not authenticated. Call login() first.")
        return {"Authorization": f"Bearer {self.token}"}
    
    async def get(self, endpoint: str, **kwargs) -> aiohttp.ClientResponse:
        """GET request with auth"""
        url = f"{self.base_url}{endpoint}"
        return await self.session.get(url, headers=self.headers, **kwargs)
    
    async def post(self, endpoint: str, json_data: Dict[str, Any] = None, **kwargs) -> aiohttp.ClientResponse:
        """POST request with auth"""
        url = f"{self.base_url}{endpoint}"
        return await self.session.post(url, json=json_data, headers=self.headers, **kwargs)
    
    async def put(self, endpoint: str, json_data: Dict[str, Any] = None, **kwargs) -> aiohttp.ClientResponse:
        """PUT request with auth"""
        url = f"{self.base_url}{endpoint}"
        return await self.session.put(url, json=json_data, headers=self.headers, **kwargs)
    
    async def delete(self, endpoint: str, **kwargs) -> aiohttp.ClientResponse:
        """DELETE request with auth"""
        url = f"{self.base_url}{endpoint}"
        return await self.session.delete(url, headers=self.headers, **kwargs)

async def check_server_health() -> bool:
    """Check if server is running"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health") as response:
                return response.status == 200
    except:
        return False

async def get_sample_job() -> Optional[Dict[str, Any]]:
    """Get a sample job for testing"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/api/jobs") as response:
                if response.status == 200:
                    jobs = await response.json()
                    if jobs and len(jobs) > 0:
                        return jobs[0]
    except:
        pass
    return None

def print_test_header(title: str):
    """Print formatted test header"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_test_section(section: str):
    """Print formatted test section"""
    print(f"\n📋 {section}")
    print("-" * 40)

def print_success(message: str):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message: str):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message: str):
    """Print info message"""
    print(f"ℹ️  {message}")