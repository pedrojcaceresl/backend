#!/usr/bin/env python3
"""
Simple script to create test users and populate data
"""

import asyncio
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import bcrypt
import uuid

# Load environment variables
load_dotenv()

async def create_test_data():
    """Create test users and populate database"""
    
    try:
        # MongoDB connection
        mongo_url = os.environ.get('MONGO_URL')
        db_name = os.environ.get('DB_NAME', 'tech_hub')
        
        if not mongo_url:
            print("❌ MONGO_URL not found in environment variables")
            return False
            
        print(f"🔗 Connecting to MongoDB: {db_name}")
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB successfully!")
        
        # Create test users with hashed passwords
        print("\n👥 Creating test users...")
        
        test_users = [
            {
                "id": str(uuid.uuid4()),
                "email": "admin@techhub.com",
                "name": "Admin User",
                "password_hash": bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                "role": "ADMIN",
                "is_verified": True,
                "is_active": True,
                "created_at": datetime.now(timezone.utc)
            },
            {
                "id": str(uuid.uuid4()),
                "email": "student@techhub.com", 
                "name": "Test Student",
                "password_hash": bcrypt.hashpw("student123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                "role": "STUDENT",
                "is_verified": True,
                "is_active": True,
                "created_at": datetime.now(timezone.utc)
            },
            {
                "id": str(uuid.uuid4()),
                "email": "company@techhub.com",
                "name": "Test Company", 
                "password_hash": bcrypt.hashpw("company123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                "role": "COMPANY",
                "is_verified": True,
                "is_active": True,
                "created_at": datetime.now(timezone.utc)
            }
        ]
        
        # Clear existing users
        await db.users.delete_many({})
        
        # Insert test users
        result = await db.users.insert_many(test_users)
        print(f"✅ Created {len(result.inserted_ids)} test users")
        
        # Create some sample courses
        print("\n📚 Creating sample courses...")
        
        sample_courses = [
            {
                "id": str(uuid.uuid4()),
                "title": "Desarrollo Web Full Stack",
                "description": "Aprende desarrollo web completo con React y Node.js",
                "provider": "TechHub UPE",
                "url": "https://example.com/curso-fullstack",
                "language": "es",
                "has_spanish_subtitles": True,
                "category": "Tecnología",
                "is_free": True,
                "created_at": datetime.now(timezone.utc)
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Marketing Digital",
                "description": "Estrategias de marketing digital para empresas",
                "provider": "TechHub UPE",
                "url": "https://example.com/marketing-digital",
                "language": "es", 
                "has_spanish_subtitles": True,
                "category": "Marketing",
                "is_free": True,
                "created_at": datetime.now(timezone.utc)
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Gestión de Proyectos",
                "description": "Metodologías ágiles y gestión efectiva de proyectos",
                "provider": "TechHub UPE",
                "url": "https://example.com/gestion-proyectos", 
                "language": "es",
                "has_spanish_subtitles": True,
                "category": "Gestión",
                "is_free": True,
                "created_at": datetime.now(timezone.utc)
            }
        ]
        
        # Clear existing courses
        await db.courses.delete_many({})
        
        # Insert sample courses
        result = await db.courses.insert_many(sample_courses)
        print(f"✅ Created {len(result.inserted_ids)} sample courses")
        
        # Create sample events
        print("\n📅 Creating sample events...")
        
        sample_events = [
            {
                "id": str(uuid.uuid4()),
                "title": "Workshop: Introducción a React",
                "description": "Taller práctico para aprender los fundamentos de React",
                "date": datetime.now(timezone.utc) + timedelta(days=7),
                "location": "Aula Virtual TechHub",
                "organizer": "TechHub UPE",
                "category": "Workshop",
                "is_free": True,
                "max_attendees": 50,
                "created_at": datetime.now(timezone.utc)
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Conferencia: El Futuro del Trabajo Remoto",
                "description": "Charla sobre tendencias en trabajo remoto y tecnologías emergentes",
                "date": datetime.now(timezone.utc) + timedelta(days=14),
                "location": "Auditorio Principal",
                "organizer": "TechHub UPE",
                "category": "Conferencia", 
                "is_free": True,
                "max_attendees": 200,
                "created_at": datetime.now(timezone.utc)
            }
        ]
        
        # Clear existing events
        await db.events.delete_many({})
        
        # Insert sample events  
        result = await db.events.insert_many(sample_events)
        print(f"✅ Created {len(result.inserted_ids)} sample events")
        
        # Create sample jobs
        print("\n💼 Creating sample jobs...")
        
        sample_jobs = [
            {
                "id": str(uuid.uuid4()),
                "title": "Desarrollador Frontend React",
                "company": "TechCorp",
                "description": "Buscamos desarrollador frontend con experiencia en React y TypeScript",
                "requirements": ["React", "TypeScript", "CSS", "Git"],
                "location": "Remoto",
                "salary_range": "USD 2000-3000",
                "job_type": "Tiempo completo",
                "category": "Tecnología",
                "posted_date": datetime.now(timezone.utc),
                "application_deadline": datetime.now(timezone.utc) + timedelta(days=30),
                "is_active": True,
                "created_at": datetime.now(timezone.utc)
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Especialista en Marketing Digital",
                "company": "MarketingPro",
                "description": "Especialista en marketing digital para gestionar campañas y estrategias",
                "requirements": ["Google Ads", "Facebook Ads", "Analytics", "SEO"],
                "location": "Lima, Perú",
                "salary_range": "S/ 3000-4500",
                "job_type": "Tiempo completo",
                "category": "Marketing",
                "posted_date": datetime.now(timezone.utc),
                "application_deadline": datetime.now(timezone.utc) + timedelta(days=25),
                "is_active": True,
                "created_at": datetime.now(timezone.utc)
            }
        ]
        
        # Clear existing jobs
        await db.jobs.delete_many({})
        
        # Insert sample jobs
        result = await db.jobs.insert_many(sample_jobs)
        print(f"✅ Created {len(result.inserted_ids)} sample jobs")
        
        print("\n🎉 Database populated successfully!")
        print("\n📋 Test Credentials:")
        print("Admin:   admin@techhub.com / admin123")
        print("Student: student@techhub.com / student123")
        print("Company: company@techhub.com / company123")
        
        # Close connection
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error populating database: {str(e)}")
        return False

if __name__ == "__main__":
    print("TechHub UPE - Database Setup")
    print("=" * 40)
    
    success = asyncio.run(create_test_data())
    
    if not success:
        sys.exit(1)
    
    print("\n✨ Ready to test your application!")
    print("🚀 Start the server with: uvicorn main:app --reload")
    print("🌐 Visit: http://localhost:8000/docs")