from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from app.models.database import connect_to_mongo, close_mongo_connection
from app.api import issues, settings as settings_api, auth, workspaces, debug
from app.services.sentry_monitoring import init_sentry
from app.middleware.sentry_context import SentryContextMiddleware
import logging

# Initialize Sentry before everything else
sentry_initialized = init_sentry()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Sentry Issues Explainer",
    description="AI-powered technical specification generator from Sentry issues",
    version="1.0.0",
    debug=settings.DEBUG
)

@app.get("/")
async def welcome():
    return {
        "message": "AI Sentry Issues Explainer API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "auth": "/auth",
            "workspaces": "/workspaces", 
            "issues": "/issues",
            "settings": "/settings",
            "debug": "/debug",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Sentry context middleware
if sentry_initialized:
    app.add_middleware(SentryContextMiddleware)

# Event handlers
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting AI Sentry Issues Explainer API")
    if sentry_initialized:
        logger.info("Sentry monitoring enabled")
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Shutting down AI Sentry Issues Explainer API")
    await close_mongo_connection()

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(workspaces.router, prefix="/api/v1/workspaces", tags=["workspaces"])
app.include_router(issues.router, prefix="/api/v1/issues", tags=["issues"])
app.include_router(settings_api.router, prefix="/api/v1/settings", tags=["settings"])

# Debug routes (only in development)
if settings.DEBUG:
    app.include_router(debug.router, prefix="/api/v1/debug", tags=["debug"])

@app.get("/")
async def root():
    return {"message": "AI Sentry Issues Explainer API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
