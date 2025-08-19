from fastapi import APIRouter, Depends
from app.auth.auth_service import get_current_active_user
from app.models.schemas import User
from app.services.sentry_monitoring import (
    capture_exception_with_context,
    capture_message_with_context,
    set_user_context,
    set_workspace_context
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/test-error")
async def test_sentry_error(current_user: User = Depends(get_current_active_user)):
    """Test endpoint to generate a Sentry error event"""
    try:
        # Set user context
        set_user_context(
            user_id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            workspace_id=current_user.workspace_id
        )
        
        # Set workspace context if available
        if current_user.workspace_id:
            set_workspace_context(workspace_id=current_user.workspace_id)
        
        # Generate a test error
        raise ValueError("This is a test error for Sentry monitoring")
        
    except Exception as e:
        # Capture exception with context
        capture_exception_with_context(e, {
            "test_type": "manual_error_test",
            "user_id": current_user.id,
            "workspace_id": current_user.workspace_id,
            "endpoint": "/debug/test-error"
        })
        
        return {"message": "Test error captured and sent to Sentry"}

@router.post("/test-message")
async def test_sentry_message(current_user: User = Depends(get_current_active_user)):
    """Test endpoint to send a message to Sentry"""
    # Set user context
    set_user_context(
        user_id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        workspace_id=current_user.workspace_id
    )
    
    # Send test message
    capture_message_with_context(
        "Test message from AI Sentry Explainer",
        level="info",
        extra_context={
            "test_type": "manual_message_test",
            "user_id": current_user.id,
            "workspace_id": current_user.workspace_id,
            "endpoint": "/debug/test-message"
        }
    )
    
    return {"message": "Test message sent to Sentry"}

@router.get("/sentry-status")
async def get_sentry_status():
    """Get Sentry monitoring status"""
    from app.services.sentry_monitoring import init_sentry
    from config.settings import settings
    
    return {
        "sentry_enabled": bool(settings.APP_SENTRY_DSN),
        "sentry_dsn_configured": "***" if settings.APP_SENTRY_DSN else None,
        "environment": settings.APP_SENTRY_ENVIRONMENT,
        "release": settings.APP_SENTRY_RELEASE,
        "traces_sample_rate": settings.APP_SENTRY_TRACES_SAMPLE_RATE,
        "profiles_sample_rate": settings.APP_SENTRY_PROFILES_SAMPLE_RATE
    }
