from datetime import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException

from app.auth.auth_service import get_current_active_user
from app.models.database import as_dict, create_workspace as create_workspace_record, get_workspace, update_user_workspace, update_workspace
from app.models.schemas import User, WorkspaceCreate, WorkspaceUpdate
from app.services.openai_service import OpenAIService
from app.services.sentry_service import SentryService

logger = logging.getLogger(__name__)
router = APIRouter()


def public_workspace(workspace: dict) -> dict:
    for field in ("sentry_api_token", "openai_api_key", "sentry_test_dsn"):
        if workspace.get(field):
            workspace[field] = "***"
    return workspace


@router.post("/", response_model=dict)
async def create_workspace(workspace_data: WorkspaceCreate, current_user: User = Depends(get_current_active_user)):
    try:
        workspace = await create_workspace_record(
            name=workspace_data.name,
            description=workspace_data.description,
            owner_id=current_user.id,
            sentry_api_token=None,
            sentry_organization=None,
            sentry_test_dsn=None,
            openai_api_key=None,
            workspace_settings={},
        )
        workspace_dict = as_dict(workspace)
        await update_user_workspace(current_user.id, workspace_dict["id"])
        return {"message": "Workspace created successfully", "workspace": public_workspace(workspace_dict)}
    except Exception as error:
        logger.exception("Failed to create workspace")
        raise HTTPException(status_code=500, detail="Failed to create workspace") from error


@router.get("/", response_model=list[dict])
async def get_workspaces(current_user: User = Depends(get_current_active_user)):
    if not current_user.workspace_id:
        return []
    workspace = await get_workspace(current_user.workspace_id)
    return [public_workspace(as_dict(workspace))] if workspace else []


@router.get("/current", response_model=dict)
async def get_current_workspace(current_user: User = Depends(get_current_active_user)):
    if not current_user.workspace_id:
        raise HTTPException(status_code=404, detail="No workspace found. Please create a workspace first.")
    workspace = await get_workspace(current_user.workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return public_workspace(as_dict(workspace))


@router.put("/current", response_model=dict)
async def update_current_workspace(workspace_data: WorkspaceUpdate, current_user: User = Depends(get_current_active_user)):
    if not current_user.workspace_id:
        raise HTTPException(status_code=404, detail="No workspace found")
    workspace = await get_workspace(current_user.workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    if str(workspace.owner_id) != current_user.id:
        raise HTTPException(status_code=403, detail="Only workspace owner can update settings")
    updates = workspace_data.model_dump(exclude_unset=True, exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    await update_workspace(current_user.workspace_id, **updates)
    return {"message": "Workspace updated successfully"}


@router.post("/test-sentry", response_model=dict)
async def test_sentry_connection(test_data: dict, current_user: User = Depends(get_current_active_user)):
    api_token, organization = test_data.get("sentry_api_token"), test_data.get("sentry_organization")
    if not api_token or not organization:
        raise HTTPException(status_code=400, detail="API token and organization are required")
    service = SentryService(api_token=api_token, organization=organization, workspace_id=current_user.workspace_id)
    result = await service.test_connection_detailed()
    if result["success"]:
        try:
            projects = await service.get_projects()
            result.update(projects_count=len(projects), projects=[{"id": project["id"], "name": project["name"]} for project in projects[:10]])
        except Exception:
            logger.warning("Could not fetch Sentry projects", exc_info=True)
    return {"connected": result.pop("success"), "message": result.pop("message"), **result}


@router.post("/test-openai", response_model=dict)
async def test_openai_connection(test_data: dict, current_user: User = Depends(get_current_active_user)):
    api_key = test_data.get("openai_api_key")
    if not api_key:
        raise HTTPException(status_code=400, detail="OpenAI API key is required")
    try:
        import openai
        client = openai.AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Reply with OK."}],
            max_tokens=5,
            temperature=0,
        )
        return {"connected": bool(response.choices), "message": "OpenAI API key is valid and working", "model_used": "gpt-4o-mini"}
    except openai.AuthenticationError:
        return {"connected": False, "message": "Invalid OpenAI API key. Please check your key and try again."}
    except Exception as error:
        logger.warning("OpenAI connection test failed: %s", error)
        return {"connected": False, "message": "Connection test failed"}
