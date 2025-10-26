#!/usr/bin/env python3
"""
Create test users for development
This script creates sample users for testing the authentication system
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend root to the Python path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

from app.core.database import get_database
from app.services.user_service import UserService
from app.models.user import User
from app.models.enums import UserRole
from app.utils.auth import auth_utils

async def create_test_users():
    """Create test users for development"""
    
    try:
        # Get database connection
        db = await get_database()
        user_service = UserService(db)
        
        # Test users data
        test_users = [
            {
                "email": "admin@techhub.com",
                "password": "admin123",
                "name": "Admin User",
                "role": UserRole.ADMIN
            },
            {
                "email": "student@techhub.com",
                "password": "student123",
                "name": "Test Student",
                "role": UserRole.STUDENT
            },
            {
                "email": "company@techhub.com",
                "password": "company123",
                "name": "Test Company",
                "role": UserRole.COMPANY
            }
        ]
        
        print("🚀 Creating test users...")
        print("=" * 50)
        
        for user_data in test_users:
            # Check if user already exists
            existing_user = await user_service.get_user_by_email(user_data["email"])
            
            if existing_user:
                print(f"⚠️  User {user_data['email']} already exists - skipping")
                continue
            
            # Hash password
            password_hash = auth_utils.hash_password(user_data["password"])
            
            # Create user
            user = User(
                email=user_data["email"],
                name=user_data["name"],
                password_hash=password_hash,
                role=user_data["role"],
                is_verified=True,
                is_active=True
            )
            
            created_user = await user_service.create_user(user)
            
            if created_user:
                print(f"✅ Created user: {user_data['email']} ({user_data['role'].value})")
                print(f"   Password: {user_data['password']}")
            else:
                print(f"❌ Failed to create user: {user_data['email']}")
        
        print("=" * 50)
        print("🎉 Test users creation completed!")
        print()
        print("📋 Test Credentials:")
        print("Admin:   admin@techhub.com / admin123")
        print("Student: student@techhub.com / student123") 
        print("Company: company@techhub.com / company123")
        print()
        print("🔗 You can now test the API endpoints:")
        print("POST /auth/login - Login with email/password")
        print("POST /auth/register - Register new user")
        print("GET /auth/me - Get current user info")
        print("POST /auth/logout - Logout")
        
    except Exception as e:
        print(f"❌ Error creating test users: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("TechHub UPE - Test Users Creator")
    print("=" * 40)
    
    success = asyncio.run(create_test_users())
    
    if not success:
        sys.exit(1)
    
    print("\n✨ Ready to test your authentication system!")