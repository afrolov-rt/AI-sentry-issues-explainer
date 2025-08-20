#!/usr/bin/env python3
"""
Complete initialization script for demo setup
"""
import asyncio
import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from app.models.database import connect_to_mongo, get_database
from app.auth.auth_service import auth_service
from config.settings import settings
from datetime import datetime

async def init_demo_data():
    """Initialize demo user and workspace"""
    try:
        print("🚀 Initializing demo data...")
        await connect_to_mongo()
        db = get_database()
        
        demo_user = await db.users.find_one({"username": "demo"})
        if not demo_user:
            print("👤 Creating demo user...")
            user = await auth_service.create_user(
                username="demo",
                email="demo@example.com",
                password="demo123",
                full_name="Demo User",
                role="admin"
            )
            print(f"✅ Demo user created! User ID: {user.id}")
            demo_user = await db.users.find_one({"username": "demo"})
        else:
            print("✅ Demo user already exists")
        
        existing_workspace = await db.workspaces.find_one({"name": "Demo Workspace"})
        if not existing_workspace:
            print("🏢 Creating demo workspace...")
            workspace_data = {
                "name": "Demo Workspace",
                "description": "Default workspace for demo user with sample Sentry configuration",
                "owner_id": str(demo_user["_id"]),
                "settings": {
                    "sentry_dsn": "https://demo@example.sentry.io/123456",
                    "sentry_org_slug": "demo-org",
                    "sentry_api_token": "demo-token",
                    "openai_model": "gpt-4"
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await db.workspaces.insert_one(workspace_data)
            workspace_id = str(result.inserted_id)
            
            await db.users.update_one(
                {"_id": demo_user["_id"]},
                {"$set": {"workspace_id": workspace_id}}
            )
            print(f"✅ Demo workspace created! Workspace ID: {workspace_id}")
        else:
            print("✅ Demo workspace already exists")
        
        print("\n🎉 Demo initialization complete!")
        print("=" * 50)
        print("Demo Login Credentials:")
        print("  Username: demo")
        print("  Password: demo123")
        print("  Email: demo@example.com")
        print("  Role: admin")
        print("=" * 50)
        print("Access the application:")
        print("  Frontend: http://localhost:3001")
        print("  Backend API: http://localhost:8881")
        print("  API Docs: http://localhost:8881/docs")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(init_demo_data())
