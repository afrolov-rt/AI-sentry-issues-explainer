#!/usr/bin/env python3
"""
Script to create default demo user
"""
import asyncio
import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from app.models.database import connect_to_mongo, get_database
from app.auth.auth_service import auth_service
from app.models.schemas import UserCreate, UserRole
from config.settings import settings

async def create_demo_user():
    """Create demo user if it doesn't exist"""
    try:
        await connect_to_mongo()
        db = get_database()
        
        existing_user = await db.users.find_one({"username": "demo"})
        if existing_user:
            print("✅ Demo user already exists")
            return
        
        user = await auth_service.create_user(
            username="demo",
            email="demo@example.com",
            password="demo123",
            full_name="Demo User",
            role="admin"
        )
        
        print(f"✅ Demo user created successfully!")
        print(f"   Username: demo")
        print(f"   Password: demo123")
        print(f"   Email: demo@example.com")
        print(f"   Role: {user.role}")
        print(f"   User ID: {user.id}")
        
    except Exception as e:
        print(f"❌ Error creating demo user: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(create_demo_user())
