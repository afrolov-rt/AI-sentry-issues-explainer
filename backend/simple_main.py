
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Sentry Issues Explainer API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/api/v1/auth/me")
async def get_current_user():
    return {
        "id": "1",
        "username": "test-user",
        "email": "test@example.com"
    }

@app.get("/api/v1/workspaces/current")
async def get_current_workspace():
    return {
        "name": "test-workspace",
        "sentry_organization": "ai-test-poject",
        "sentry_api_token": "test-token"
    }

@app.get("/api/v1/issues/processed/")
async def get_processed_issues():
    return []

@app.get("/api/v1/issues/")
async def get_sentry_issues():
    return [
        {
            "id": "1",
            "title": "Test Error 1",
            "level": "error",
            "status": "unresolved",
            "count": 10,
            "lastSeen": "2024-01-15T10:00:00Z",
            "project": {"name": "test-project"}
        },
        {
            "id": "2", 
            "title": "Test Error 2",
            "level": "warning",
            "status": "resolved",
            "count": 5,
            "lastSeen": "2024-01-15T09:00:00Z",
            "project": {"name": "test-project"}
        }
    ]

@app.get("/api/v1/issues/projects")
async def get_sentry_projects():
    return [
        {"id": "1", "name": "test-project", "slug": "test-project"}
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
