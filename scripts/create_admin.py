#!/usr/bin/env python3
"""
Script to create the first admin user for TechHub UPE platform
This should be run once to bootstrap the admin system
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to sys.path to import app modules
sys.path.append(str(Path(__file__).parent))

from app.core.database import connect_to_mongo, close_mongo_connection
from app.services.user_service import UserService
from app.models.user import User
from app.models.enums import UserRole
from app.core.database import database
from datetime import datetime, timezone

async def create_first_admin():
    """Create the first admin user"""
    try:
        # Connect to database
        await connect_to_mongo()
        
        # Get user service
        user_service = UserService(database.db)
        
        # Check if any admin already exists
        existing_admins = await user_service.get_users_by_role(UserRole.ADMIN)
        if existing_admins:
            print("❌ Admin user already exists!")
            print(f"Existing admins: {[admin.email for admin in existing_admins]}")
            return
        
        # Admin user details - CHANGE THESE BEFORE RUNNING
        admin_email = "admin@techhub.edu.py"  # CHANGE THIS
        admin_name = "TechHub Administrator"   # CHANGE THIS
        
        print(f"Creating admin user: {admin_email}")
        
        # Check if user already exists with different role
        existing_user = await user_service.get_user_by_email(admin_email)
        if existing_user:
            # Update existing user to admin
            update_data = {
                "role": UserRole.ADMIN,
                "is_verified": True,
                "is_active": True,
                "updated_at": datetime.now(timezone.utc)
            }
            updated_user = await user_service.update_user(existing_user.id, update_data)
            if updated_user:
                print(f"✅ Successfully promoted existing user {admin_email} to admin!")
            else:
                print(f"❌ Failed to promote user {admin_email} to admin")
        else:
            # Create new admin user
            admin_user = User(
                email=admin_email,
                name=admin_name,
                role=UserRole.ADMIN,
                is_verified=True,
                is_active=True
            )
            
            created_user = await user_service.create_user(admin_user)
            if created_user:
                print(f"✅ Successfully created admin user: {admin_email}")
                print(f"Admin ID: {created_user.id}")
                print(f"Admin Name: {created_user.name}")
                print(f"Admin Role: {created_user.role}")
            else:
                print(f"❌ Failed to create admin user: {admin_email}")
        
        print("\n📝 IMPORTANT NOTES:")
        print("1. The admin user must authenticate via Google OAuth first")
        print("2. Once authenticated, they will have admin privileges")
        print("3. Admin can create other admins via /api/admin/create-admin endpoint")
        print("4. Admin can change user roles via /api/admin/users/{user_id}/role endpoint")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")
    finally:
        # Close database connection
        await close_mongo_connection()

if __name__ == "__main__":
    print("🔧 TechHub UPE - Admin User Creator")
    print("=" * 40)
    
    # Confirm before creating
    confirm = input("⚠️  This will create the first admin user. Continue? (y/N): ")
    if confirm.lower() != 'y':
        print("Cancelled.")
        sys.exit(0)
    
    asyncio.run(create_first_admin())