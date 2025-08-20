import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.pymongo import PyMongoIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

def init_sentry():
    """Initialize Sentry for application monitoring"""
    if not settings.APP_SENTRY_DSN:
        logger.info("Sentry DSN not configured, skipping Sentry initialization")
        return False
    
    try:
        sentry_sdk.init(
            dsn=settings.APP_SENTRY_DSN,
            environment=settings.APP_SENTRY_ENVIRONMENT,
            release=settings.APP_SENTRY_RELEASE,
            traces_sample_rate=settings.APP_SENTRY_TRACES_SAMPLE_RATE,
            profiles_sample_rate=settings.APP_SENTRY_PROFILES_SAMPLE_RATE,
            integrations=[
                FastApiIntegration(),
                StarletteIntegration(),
                PyMongoIntegration(),
                HttpxIntegration(),
                LoggingIntegration(
                    level=logging.INFO,
                    event_level=logging.ERROR
                ),
            ],
            enable_tracing=True,
            send_default_pii=False,
            attach_stacktrace=True,
            max_breadcrumbs=50,
            default_integrations=True,
            before_send=before_send_filter,
            before_send_transaction=before_send_transaction_filter,
        )
        
        sentry_sdk.set_tag("component", "ai-sentry-explainer-backend")
        sentry_sdk.set_tag("version", settings.APP_SENTRY_RELEASE)
        
        logger.info(f"Sentry initialized successfully for environment: {settings.APP_SENTRY_ENVIRONMENT}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")
        return False

def before_send_filter(event, hint):
    """Filter events before sending to Sentry"""
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']
        
        if hasattr(exc_value, 'status_code') and exc_value.status_code == 404:
            return None
        
        if hasattr(exc_value, 'status_code') and exc_value.status_code == 400:
            return None
    
    sentry_sdk.set_context("app_info", {
        "component": "backend",
        "service": "ai-sentry-explainer"
    })
    
    return event

def before_send_transaction_filter(event, hint):
    """Filter transactions before sending to Sentry"""
    if event.get('transaction') == 'GET /health':
        return None
    
    if event.get('request', {}).get('method') == 'OPTIONS':
        return None
    
    return event

def capture_exception_with_context(exception, extra_context=None):
    """Capture exception with additional context"""
    if extra_context:
        sentry_sdk.set_context("error_context", extra_context)
    
    sentry_sdk.capture_exception(exception)

def capture_message_with_context(message, level="info", extra_context=None):
    """Capture message with additional context"""
    if extra_context:
        sentry_sdk.set_context("message_context", extra_context)
    
    sentry_sdk.capture_message(message, level=level)

def set_user_context(user_id, username=None, email=None, workspace_id=None):
    """Set user context for Sentry"""
    user_data = {"id": user_id}
    
    if username:
        user_data["username"] = username
    if email:
        user_data["email"] = email
    if workspace_id:
        user_data["workspace_id"] = workspace_id
    
    sentry_sdk.set_user(user_data)

def set_workspace_context(workspace_id, workspace_name=None, owner_id=None):
    """Set workspace context for Sentry"""
    workspace_data = {"workspace_id": workspace_id}
    
    if workspace_name:
        workspace_data["workspace_name"] = workspace_name
    if owner_id:
        workspace_data["owner_id"] = owner_id
    
    sentry_sdk.set_context("workspace", workspace_data)

def track_issue_analysis(issue_id, workspace_id, status, analysis_time=None, error=None):
    """Track issue analysis events"""
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("operation", "issue_analysis")
        scope.set_context("analysis", {
            "issue_id": issue_id,
            "workspace_id": workspace_id,
            "status": status,
            "analysis_time": analysis_time
        })
        
        if error:
            capture_exception_with_context(error, {
                "issue_id": issue_id,
                "workspace_id": workspace_id,
                "operation": "issue_analysis"
            })
        else:
            sentry_sdk.capture_message(
                f"Issue analysis completed: {status}",
                level="info"
            )

def track_sentry_api_call(endpoint, workspace_id, success=True, response_time=None, error=None):
    """Track Sentry API calls"""
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("operation", "sentry_api_call")
        scope.set_context("sentry_api", {
            "endpoint": endpoint,
            "workspace_id": workspace_id,
            "success": success,
            "response_time": response_time
        })
        
        if error:
            capture_exception_with_context(error, {
                "endpoint": endpoint,
                "workspace_id": workspace_id,
                "operation": "sentry_api_call"
            })
        else:
            sentry_sdk.add_breadcrumb(
                message=f"Sentry API call: {endpoint}",
                category="api",
                level="info",
                data={
                    "endpoint": endpoint,
                    "success": success,
                    "response_time": response_time
                }
            )

def track_openai_api_call(model, tokens_used=None, success=True, response_time=None, error=None):
    """Track OpenAI API calls"""
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("operation", "openai_api_call")
        scope.set_context("openai_api", {
            "model": model,
            "tokens_used": tokens_used,
            "success": success,
            "response_time": response_time
        })
        
        if error:
            capture_exception_with_context(error, {
                "model": model,
                "operation": "openai_api_call"
            })
        else:
            sentry_sdk.add_breadcrumb(
                message=f"OpenAI API call: {model}",
                category="ai",
                level="info",
                data={
                    "model": model,
                    "tokens_used": tokens_used,
                    "success": success,
                    "response_time": response_time
                }
            )
