#!/usr/bin/env python3
"""
Script to create default workspace for demo user
"""
import asyncio
import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from app.models.database import connect_to_mongo, get_database
from config.settings import settings
from datetime import datetime

async def create_demo_workspace():
    """Create demo workspace if it doesn't exist"""
    try:
        await connect_to_mongo()
        db = get_database()
        
        demo_user = await db.users.find_one({"username": "demo"})
        if not demo_user:
            print("❌ Demo user not found. Please create demo user first.")
            return
        
        existing_workspace = await db.workspaces.find_one({"name": "Demo Workspace"})
        if existing_workspace:
            print("✅ Demo workspace already exists")
            return
        
        workspace_data = {
            "name": "Demo Workspace",
            "description": "Default workspace for demo user",
            "owner_id": str(demo_user["_id"]),
            "settings": {
                "sentry_dsn": "",
                "sentry_org_slug": "",
                "sentry_api_token": "",
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
        
        print(f"✅ Demo workspace created successfully!")
        print(f"   Name: Demo Workspace")
        print(f"   Owner: demo")
        print(f"   Workspace ID: {workspace_id}")
        
    except Exception as e:
        print(f"❌ Error creating demo workspace: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(create_demo_workspace())
