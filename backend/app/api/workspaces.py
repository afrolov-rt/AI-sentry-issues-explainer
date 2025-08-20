from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.auth.auth_service import get_current_user, get_current_active_user
from app.models.schemas import User, Workspace, WorkspaceCreate, WorkspaceUpdate, UserRole
from app.models.database import get_database
from app.services.sentry_service import SentryService
from app.services.openai_service import OpenAIService
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=dict)
async def create_workspace(
    workspace_data: WorkspaceCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new workspace"""
    try:
        db = get_database()
        
        workspace_dict = {
            "name": workspace_data.name,
            "description": workspace_data.description,
            "owner_id": current_user.id,
            "sentry_api_token": None,
            "sentry_organization": None,
            "openai_api_key": None,
            "settings": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.workspaces.insert_one(workspace_dict)
        workspace_id = str(result.inserted_id)
        
        await db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {"workspace_id": workspace_id, "updated_at": datetime.utcnow()}}
        )
        
        workspace_dict["id"] = workspace_id
        if "_id" in workspace_dict:
            del workspace_dict["_id"]
        
        return {
            "message": "Workspace created successfully",
            "workspace": workspace_dict
        }
        
    except Exception as e:
        logger.error(f"Failed to create workspace: {e}")
        raise HTTPException(status_code=500, detail="Failed to create workspace")

@router.get("/", response_model=List[dict])
async def get_workspaces(current_user: User = Depends(get_current_active_user)):
    """Get user's workspaces"""
    try:
        db = get_database()
        
        if current_user.workspace_id:
            workspace = await db.workspaces.find_one({"_id": ObjectId(current_user.workspace_id)})
            if workspace:
                workspace["id"] = str(workspace["_id"])
                del workspace["_id"]
                return [workspace]
        
        return []
        
    except Exception as e:
        logger.error(f"Failed to get workspaces: {e}")
        raise HTTPException(status_code=500, detail="Failed to get workspaces")

@router.get("/current", response_model=dict)
async def get_current_workspace(current_user: User = Depends(get_current_active_user)):
    """Get current user's workspace"""
    try:
        if not current_user.workspace_id:
            raise HTTPException(status_code=404, detail="No workspace found. Please create a workspace first.")
        
        db = get_database()
        workspace = await db.workspaces.find_one({"_id": ObjectId(current_user.workspace_id)})
        
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        
        workspace["id"] = str(workspace["_id"])
        del workspace["_id"]
        
        if "sentry_api_token" in workspace and workspace["sentry_api_token"]:
            workspace["sentry_api_token"] = "***"
        if "openai_api_key" in workspace and workspace["openai_api_key"]:
            workspace["openai_api_key"] = "***"
        
        return workspace
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get current workspace: {e}")
        raise HTTPException(status_code=500, detail="Failed to get workspace")

@router.put("/current", response_model=dict)
async def update_current_workspace(
    workspace_data: WorkspaceUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update current workspace"""
    try:
        if not current_user.workspace_id:
            raise HTTPException(status_code=404, detail="No workspace found")
        
        db = get_database()
        
        workspace = await db.workspaces.find_one({"_id": ObjectId(current_user.workspace_id)})
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        
        if workspace["owner_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Only workspace owner can update settings")
        
        update_data = {}
        
        workspace_dict = workspace_data.dict(exclude_unset=True)
        for field, value in workspace_dict.items():
            if value is not None:
                update_data[field] = value
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        update_data["updated_at"] = datetime.utcnow()
        
        await db.workspaces.update_one(
            {"_id": ObjectId(current_user.workspace_id)},
            {"$set": update_data}
        )
        
        return {"message": "Workspace updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update workspace: {e}")
        raise HTTPException(status_code=500, detail="Failed to update workspace")

@router.post("/test-sentry", response_model=dict)
async def test_sentry_connection(
    test_data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """Test Sentry API connection for workspace"""
    try:
        api_token = test_data.get("sentry_api_token")
        organization = test_data.get("sentry_organization")
        
        if not api_token or not organization:
            raise HTTPException(status_code=400, detail="API token and organization are required")
        
        sentry_service = SentryService(
            api_token=api_token,
            organization=organization,
            workspace_id=current_user.workspace_id
        )
        
        result = await sentry_service.test_connection_detailed()
        
        if result["success"]:
            try:
                projects = await sentry_service.get_projects()
                result["projects_count"] = len(projects)
                result["projects"] = [{"id": p["id"], "name": p["name"]} for p in projects[:10]]
                result["message"] = f"{result['message']}. Found {len(projects)} projects."
            except Exception as e:
                logger.warning(f"Could not fetch projects: {e}")
                result["message"] = f"{result['message']} (Note: Could not fetch projects list)"
        
        return {
            "connected": result["success"],
            "message": result["message"],
            **{k: v for k, v in result.items() if k not in ["success", "message"]}
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sentry connection test failed: {e}")
        return {
            "connected": False,
            "message": f"Connection test failed: {str(e)}"
        }

@router.post("/test-openai", response_model=dict)
async def test_openai_connection(
    test_data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """Test OpenAI API connection for workspace"""
    try:
        api_key = test_data.get("openai_api_key")
        
        if not api_key:
            raise HTTPException(status_code=400, detail="OpenAI API key is required")
        
        openai_service = OpenAIService(
            api_key=api_key,
            model="gpt-3.5-turbo",
            workspace_id=current_user.workspace_id
        )
        
        import openai
        client = openai.AsyncOpenAI(api_key=api_key)
        
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Hello! Please respond with 'API key is working' if you can read this."}
            ],
            max_tokens=20,
            temperature=0
        )
        
        if response.choices and response.choices[0].message:
            return {
                "connected": True,
                "message": "OpenAI API key is valid and working",
                "model_used": "gpt-3.5-turbo",
                "tokens_used": response.usage.total_tokens if response.usage else None
            }
        else:
            return {
                "connected": False,
                "message": "OpenAI API responded but with unexpected format"
            }
            
    except openai.AuthenticationError:
        return {
            "connected": False,
            "message": "Invalid OpenAI API key. Please check your key and try again."
        }
    except openai.RateLimitError:
        return {
            "connected": False,
            "message": "OpenAI API rate limit exceeded. Your key is valid but you've reached your quota."
        }
    except openai.APIError as e:
        return {
            "connected": False,
            "message": f"OpenAI API error: {str(e)}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OpenAI connection test failed: {e}")
        return {
            "connected": False,
            "message": f"Connection test failed: {str(e)}"
        }
