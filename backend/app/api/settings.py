import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth.auth_service import get_current_active_user
from app.models.database import get_workspace_settings, upsert_workspace_settings
from app.models.schemas import User

router = APIRouter()
logger = logging.getLogger(__name__)


class SettingsUpdate(BaseModel):
    openai_model: str | None = None
    auto_analyze: bool | None = None
    notification_email: bool | None = None


@router.get("/", response_model=dict)
async def get_settings(current_user: User = Depends(get_current_active_user)):
    if not current_user.workspace_id:
        raise HTTPException(status_code=400, detail="No workspace found")
    settings = await get_workspace_settings(current_user.workspace_id)
    if settings is None:
        return {"openai_model": "gpt-4", "auto_analyze": False, "notification_email": True}
    return {
        "openai_model": settings.openai_model,
        "auto_analyze": settings.auto_analyze,
        "notification_email": settings.notification_email,
    }


@router.put("/", response_model=dict)
async def update_settings(settings_update: SettingsUpdate, current_user: User = Depends(get_current_active_user)):
    if not current_user.workspace_id:
        raise HTTPException(status_code=400, detail="No workspace found")
    updates = settings_update.model_dump(exclude_unset=True, exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    await upsert_workspace_settings(current_user.workspace_id, **updates)
    return {"message": "Settings updated successfully", "updated": True}
