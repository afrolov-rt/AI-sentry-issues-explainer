from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth.auth_service import get_current_user, get_current_active_user
from app.models.schemas import User, Settings
from app.models.database import get_database
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class SettingsUpdate(BaseModel):
    openai_model: str = None
    auto_analyze: bool = None
    notification_email: bool = None

@router.get("/", response_model=dict)
async def get_settings(current_user: User = Depends(get_current_active_user)):
    """Get workspace settings"""
    try:
        if not current_user.workspace_id:
            raise HTTPException(status_code=400, detail="No workspace found")
        
        db = get_database()
        settings = await db.settings.find_one({"workspace_id": current_user.workspace_id})
        
        if not settings:
            return {
                "openai_model": "gpt-4",
                "auto_analyze": False,
                "notification_email": True
            }
        
        return {
            "openai_model": settings.get("openai_model", "gpt-4"),
            "auto_analyze": settings.get("auto_analyze", False),
            "notification_email": settings.get("notification_email", True)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve settings")

@router.put("/", response_model=dict)
async def update_settings(
    settings_update: SettingsUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update workspace settings"""
    try:
        if not current_user.workspace_id:
            raise HTTPException(status_code=400, detail="No workspace found")
        
        db = get_database()
        
        update_data = {}
        for field, value in settings_update.dict(exclude_unset=True).items():
            if value is not None:
                update_data[field] = value
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        update_data["updated_at"] = datetime.utcnow()
        
        result = await db.settings.update_one(
            {"workspace_id": current_user.workspace_id},
            {"$set": update_data},
            upsert=True
        )
        
        return {"message": "Settings updated successfully", "updated": bool(result.modified_count or result.upserted_id)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to update settings")
