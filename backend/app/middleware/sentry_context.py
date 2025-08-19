from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.sentry_monitoring import set_user_context, set_workspace_context
from app.auth.auth_service import auth_service
import logging

logger = logging.getLogger(__name__)

class SentryContextMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically set Sentry context for authenticated requests"""
    
    async def dispatch(self, request: Request, call_next):
        # Try to extract user context from Authorization header
        authorization = request.headers.get("Authorization")
        
        if authorization and authorization.startswith("Bearer "):
            try:
                token = authorization.split(" ")[1]
                user = await auth_service.verify_token(token)
                
                if user and user.is_active:
                    # Set user context for Sentry
                    set_user_context(
                        user_id=user.id,
                        username=user.username,
                        email=user.email,
                        workspace_id=user.workspace_id
                    )
                    
                    # If user has workspace, set workspace context
                    if user.workspace_id:
                        # We could fetch workspace details here if needed
                        set_workspace_context(workspace_id=user.workspace_id)
                    
                    # Add user info to request state for later use
                    request.state.user = user
                    
            except Exception as e:
                # Don't fail the request if context setting fails
                logger.warning(f"Failed to set Sentry context: {e}")
        
        response = await call_next(request)
        return response
