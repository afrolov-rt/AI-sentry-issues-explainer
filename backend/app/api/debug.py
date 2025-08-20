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
        set_user_context(
            user_id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            workspace_id=current_user.workspace_id
        )
        
        if current_user.workspace_id:
            set_workspace_context(workspace_id=current_user.workspace_id)
        
        raise ValueError("This is a test error for Sentry monitoring")
        
    except Exception as e:
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
    set_user_context(
        user_id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        workspace_id=current_user.workspace_id
    )
    
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

@router.post("/simple-test-error")
async def simple_test_error():
    """Simple test endpoint to generate a Sentry error without authentication"""
    try:
        raise ValueError("This is a simple test error for Sentry monitoring")
        
    except Exception as e:
        capture_exception_with_context(e, {
            "test_type": "simple_error_test",
            "endpoint": "/debug/simple-test-error"
        })
        
        return {"message": "Simple test error captured and sent to Sentry"}

@router.post("/simple-test-message")
async def simple_test_message():
    """Simple test endpoint to send a message to Sentry without authentication"""
    capture_message_with_context(
        "Simple test message from AI Sentry Explainer",
        level="info",
        extra_context={
            "test_type": "simple_message_test",
            "endpoint": "/debug/simple-test-message"
        }
    )
    
    return {"message": "Simple test message sent to Sentry"}

@router.post("/test-real-error")
async def test_real_error():
    """Test real application error with full context"""
    try:
        fake_data = {"issues": [{"id": "test"}]}
        
        issue_id = fake_data["issues"][0]["non_existent_field"]
        
    except Exception as e:
        capture_exception_with_context(e, {
            "test_type": "real_application_error",
            "endpoint": "/debug/test-real-error", 
            "user_data": fake_data,
            "operation": "accessing_issue_field",
            "severity": "high"
        })
        
        return {
            "message": "Real application error captured and sent to Sentry",
            "error_type": type(e).__name__,
            "error_message": str(e)
        }

@router.post("/test-sentry-api")
async def test_sentry_api_connection():
    """Test Sentry API connection with detailed debugging"""
    try:
        import httpx
        from config.settings import settings
        
        default_token = settings.SENTRY_API_TOKEN
        default_org = settings.SENTRY_ORG_SLUG
        base_url = settings.SENTRY_BASE_URL
        
        debug_info = {
            "base_url": base_url,
            "has_default_token": bool(default_token),
            "has_default_org": bool(default_org),
            "default_org": default_org if default_org else "Not set"
        }
        
        if not default_token:
            return {
                "success": False,
                "message": "No default SENTRY_API_TOKEN in environment",
                "debug_info": debug_info
            }
        
        if not default_org:
            return {
                "success": False,
                "message": "No default SENTRY_ORG_SLUG in environment", 
                "debug_info": debug_info
            }
        
        headers = {
            "Authorization": f"Bearer {default_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{base_url}/organizations/{default_org}/",
                    headers=headers,
                    timeout=10.0
                )
                
                debug_info["response_status"] = response.status_code
                debug_info["response_headers"] = dict(response.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "message": "Successfully connected to Sentry API",
                        "debug_info": debug_info,
                        "organization_data": {
                            "id": data.get("id"),
                            "name": data.get("name"),
                            "slug": data.get("slug")
                        }
                    }
                else:
                    debug_info["response_text"] = response.text[:500]
                    return {
                        "success": False,
                        "message": f"Sentry API returned status {response.status_code}",
                        "debug_info": debug_info
                    }
                    
            except httpx.TimeoutException:
                return {
                    "success": False,
                    "message": "Connection timeout to Sentry API",
                    "debug_info": debug_info
                }
            except Exception as api_error:
                return {
                    "success": False,
                    "message": f"API request failed: {str(api_error)}",
                    "debug_info": debug_info
                }
                
    except Exception as e:
        return {
            "success": False,
            "message": f"Test failed: {str(e)}",
            "debug_info": {"error": str(e)}
        }

@router.post("/test-sentry-with-params")
async def test_sentry_with_params(test_data: dict):
    """Test Sentry API connection with provided parameters (no auth required)"""
    try:
        import httpx
        from config.settings import settings
        
        api_token = test_data.get("sentry_api_token")
        organization = test_data.get("sentry_organization")
        base_url = settings.SENTRY_BASE_URL
        
        debug_info = {
            "base_url": base_url,
            "has_token": bool(api_token),
            "has_org": bool(organization),
            "organization": organization if organization else "Not provided"
        }
        
        if not api_token:
            return {
                "success": False,
                "message": "No sentry_api_token provided",
                "debug_info": debug_info
            }
        
        if not organization:
            return {
                "success": False,
                "message": "No sentry_organization provided", 
                "debug_info": debug_info
            }
        
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{base_url}/organizations/{organization}/",
                    headers=headers,
                    timeout=10.0
                )
                
                debug_info["response_status"] = response.status_code
                debug_info["response_headers"] = dict(response.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "message": "Successfully connected to Sentry API",
                        "debug_info": debug_info,
                        "organization_data": {
                            "id": data.get("id"),
                            "name": data.get("name"),
                            "slug": data.get("slug")
                        }
                    }
                elif response.status_code == 401:
                    return {
                        "success": False,
                        "message": "Invalid API token - unauthorized",
                        "debug_info": debug_info
                    }
                elif response.status_code == 404:
                    return {
                        "success": False,
                        "message": f"Organization '{organization}' not found",
                        "debug_info": debug_info
                    }
                else:
                    debug_info["response_text"] = response.text[:500]
                    return {
                        "success": False,
                        "message": f"Sentry API returned status {response.status_code}",
                        "debug_info": debug_info
                    }
                    
            except httpx.TimeoutException:
                return {
                    "success": False,
                    "message": "Connection timeout to Sentry API",
                    "debug_info": debug_info
                }
            except Exception as api_error:
                return {
                    "success": False,
                    "message": f"API request failed: {str(api_error)}",
                    "debug_info": debug_info
                }
                
    except Exception as e:
        return {
            "success": False,
            "message": f"Test failed: {str(e)}",
            "debug_info": {"error": str(e)}
        }
