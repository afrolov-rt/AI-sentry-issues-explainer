from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.sentry_monitoring import set_user_context, set_workspace_context
from app.auth.auth_service import auth_service
import logging

logger = logging.getLogger(__name__)

class SentryContextMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically set Sentry context for authenticated requests"""
    
    async def dispatch(self, request: Request, call_next):
        authorization = request.headers.get("Authorization")
        
        if authorization and authorization.startswith("Bearer "):
            try:
                token = authorization.split(" ")[1]
                user = await auth_service.verify_token(token)
                
                if user and user.is_active:
                    set_user_context(
                        user_id=user.id,
                        username=user.username,
                        email=user.email,
                        workspace_id=user.workspace_id
                    )
                    
                    if user.workspace_id:
                        set_workspace_context(workspace_id=user.workspace_id)
                    
                    request.state.user = user
                    
            except Exception as e:
                logger.warning(f"Failed to set Sentry context: {e}")
        
        response = await call_next(request)
        return response
