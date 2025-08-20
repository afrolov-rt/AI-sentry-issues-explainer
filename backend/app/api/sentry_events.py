from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.services.sentry_event_generator import sentry_event_generator
from app.auth.auth_service import get_current_active_user
from app.models.schemas import User, Workspace
from app.models.database import get_database
from config.settings import settings
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

async def get_current_workspace(current_user: User = Depends(get_current_active_user)) -> Optional[Workspace]:
    """Get the current user's workspace"""
    if not current_user.workspace_id:
        return None
    
    db = get_database()
    workspace_doc = await db.workspaces.find_one({"_id": ObjectId(current_user.workspace_id)})
    
    if not workspace_doc:
        return None
    
    workspace_doc["id"] = str(workspace_doc["_id"])
    return Workspace(**workspace_doc)

class GenerateEventRequest(BaseModel):
    event_type: Optional[str] = Field(None, description="Type of event: error, warning, info, or random")
    count: Optional[int] = Field(1, ge=1, le=10, description="Number of events to generate (1-10)")

class GenerateEventResponse(BaseModel):
    success: bool
    message: str
    events: List[Dict[str, Any]]
    total_generated: int

@router.post("/generate-random-event", response_model=GenerateEventResponse)
async def generate_random_sentry_event(
    request: GenerateEventRequest,
    background_tasks: BackgroundTasks,
    workspace: Optional[Workspace] = Depends(get_current_workspace)
):
    """
    Generate random Sentry events for testing purposes
    
    - **event_type**: Type of event to generate (error, warning, info, or random)
    - **count**: Number of events to generate (1-10)
    """
    try:
        custom_dsn = workspace.sentry_test_dsn if workspace else None
        
        if not sentry_event_generator.is_sentry_configured(custom_dsn):
            raise HTTPException(
                status_code=400,
                detail="Sentry DSN is not configured. Please set APP_SENTRY_DSN environment variable or configure sentry_test_dsn in workspace settings."
            )
        
        logger.info(f"Generating {request.count} random Sentry events of type: {request.event_type or 'random'}")
        if custom_dsn:
            logger.info(f"Using workspace-specific DSN: {custom_dsn[:50]}...")
        else:
            logger.info("Using global APP_SENTRY_DSN")
        
        if request.count == 1:
            event = await sentry_event_generator.generate_random_event(request.event_type, custom_dsn)
            events = [event]
        else:
            if request.event_type:
                events = []
                for _ in range(request.count):
                    event = await sentry_event_generator.generate_random_event(request.event_type, custom_dsn)
                    events.append(event)
            else:
                events = await sentry_event_generator.generate_multiple_events(request.count, custom_dsn)
        
        successful_events = [e for e in events if "error" not in e]
        
        return GenerateEventResponse(
            success=True,
            message=f"Successfully generated {len(successful_events)} Sentry events",
            events=events,
            total_generated=len(successful_events)
        )
        
    except Exception as e:
        logger.error(f"Failed to generate Sentry events: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate Sentry events: {str(e)}"
        )

@router.get("/sentry-status")
async def get_sentry_status(workspace: Optional[Workspace] = Depends(get_current_workspace)):
    """Get Sentry configuration status"""
    custom_dsn = workspace.sentry_test_dsn if workspace else None
    app_dsn_configured = bool(settings.APP_SENTRY_DSN)
    workspace_dsn_configured = bool(custom_dsn)
    
    return {
        "sentry_configured": app_dsn_configured or workspace_dsn_configured,
        "app_sentry_dsn_set": "***configured***" if app_dsn_configured else None,
        "workspace_sentry_dsn_set": "***configured***" if workspace_dsn_configured else None,
        "using_workspace_dsn": workspace_dsn_configured,
        "environment": settings.APP_SENTRY_ENVIRONMENT,
        "release": settings.APP_SENTRY_RELEASE
    }

@router.get("/sentry-status-public")
async def get_sentry_status_public():
    """Get public Sentry configuration status (no auth required)"""
    app_dsn_configured = bool(settings.APP_SENTRY_DSN)
    
    return {
        "sentry_configured": app_dsn_configured,
        "app_sentry_dsn_set": "***configured***" if app_dsn_configured else None,
        "environment": settings.APP_SENTRY_ENVIRONMENT,
        "release": settings.APP_SENTRY_RELEASE
    }

@router.get("/event-templates")
async def get_event_templates():
    """Get available event templates for preview"""
    return {
        "error_templates": sentry_event_generator.error_templates,
        "warning_templates": sentry_event_generator.warning_templates,
        "info_templates": sentry_event_generator.info_templates
    }
