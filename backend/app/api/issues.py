import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth.auth_service import get_current_active_user
from app.models.database import (
    as_dict,
    get_processed_issue,
    get_processed_statuses,
    get_workspace,
    get_workspace_settings,
    list_processed_issues,
    save_processed_issue,
)
from app.models.schemas import IssueStatus, ProcessedIssue, User
from app.services.openai_service import OpenAIService
from app.services.sentry_service import SentryService

logger = logging.getLogger(__name__)
router = APIRouter()


def json_data(model):
    return model.model_dump(mode="json", by_alias=True)


async def workspace_for_user(user: User):
    if not user.workspace_id:
        raise HTTPException(status_code=400, detail="No workspace found. Please create a workspace first.")
    workspace = await get_workspace(user.workspace_id)
    if workspace is None or not workspace.sentry_api_token:
        raise HTTPException(status_code=400, detail="Sentry API token not configured in workspace. Please update workspace settings.")
    return workspace


def sentry_service(workspace, workspace_id: str) -> SentryService:
    return SentryService(api_token=workspace.sentry_api_token, organization=workspace.sentry_organization, workspace_id=workspace_id)


@router.get("/", response_model=dict)
async def get_issues(
    project_id: Optional[str] = Query(None),
    query: str = Query("is:unresolved"),
    limit: int = Query(25, ge=1, le=100),
    cursor: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
):
    workspace = await workspace_for_user(current_user)
    service = sentry_service(workspace, current_user.workspace_id)
    if not await service.test_connection():
        raise HTTPException(status_code=400, detail="Failed to connect to Sentry. Please check workspace Sentry settings.")
    result = await service.get_issues(project_id=project_id, query=query, limit=limit, cursor=cursor)
    records = await get_processed_statuses(current_user.workspace_id, [issue.id for issue in result["issues"]]) if result["issues"] else []
    processed_status = {
        record.sentry_issue_id: {"status": record.status, "has_analysis": bool(record.ai_analysis)}
        for record in records
    }
    return {
        "issues": [json_data(issue) for issue in result["issues"]],
        "pagination": {"next_cursor": result["next_cursor"], "prev_cursor": result["prev_cursor"], "has_next": result["has_next"]},
        "processed_status": processed_status,
    }


@router.get("/projects", response_model=list[dict])
async def get_sentry_projects(current_user: User = Depends(get_current_active_user)):
    workspace = await workspace_for_user(current_user)
    service = sentry_service(workspace, current_user.workspace_id)
    if not await service.test_connection():
        raise HTTPException(status_code=400, detail="Failed to connect to Sentry. Please check your API token and organization settings.")
    return await service.get_projects()


@router.get("/processed/", response_model=list[dict])
async def get_processed_issues(
    status: Optional[IssueStatus] = Query(None),
    limit: int = Query(25, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
):
    if not current_user.workspace_id:
        raise HTTPException(status_code=400, detail="No workspace found")
    records = await list_processed_issues(current_user.workspace_id, status.value if status else None, limit, skip)
    return [
        {
            "id": str(record.id), "sentry_issue": record.sentry_issue, "sentry_issue_data": record.sentry_issue,
            "ai_analysis": record.ai_analysis, "status": record.status, "assigned_to": str(record.assigned_to) if record.assigned_to else None,
            "created_by": str(record.created_by), "workspace_id": str(record.workspace_id),
            "created_at": record.created_at, "updated_at": record.updated_at,
        }
        for record in records
    ]


@router.get("/{issue_id}", response_model=dict)
async def get_issue_details(issue_id: str, current_user: User = Depends(get_current_active_user)):
    if not current_user.workspace_id:
        raise HTTPException(status_code=400, detail="No workspace found")
    processed = await get_processed_issue(current_user.workspace_id, issue_id)
    if processed:
        payload = {
            "id": str(processed.id), "sentry_issue": processed.sentry_issue, "ai_analysis": processed.ai_analysis,
            "status": processed.status, "created_by": str(processed.created_by), "workspace_id": str(processed.workspace_id),
            "created_at": processed.created_at, "updated_at": processed.updated_at,
        }
        return {"processed_issue": ProcessedIssue(**payload)}
    workspace = await workspace_for_user(current_user)
    issue = await sentry_service(workspace, current_user.workspace_id).get_issue_details(issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")
    return {"sentry_issue": json_data(issue)}


@router.post("/{issue_id}/analyze", response_model=dict)
async def analyze_issue(issue_id: str, current_user: User = Depends(get_current_active_user)):
    if not current_user.workspace_id:
        raise HTTPException(status_code=400, detail="No workspace found")
    existing = await get_processed_issue(current_user.workspace_id, issue_id)
    if existing and existing.status == IssueStatus.ANALYZING.value:
        raise HTTPException(status_code=409, detail="Issue is already being analyzed")
    workspace = await workspace_for_user(current_user)
    service = sentry_service(workspace, current_user.workspace_id)
    issue = await service.get_issue_details(issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found in Sentry")
    issue_data = json_data(issue)
    await save_processed_issue(
        current_user.workspace_id, issue_id,
        sentry_issue=issue_data, status=IssueStatus.ANALYZING.value,
        created_by=current_user.id,
    )
    settings = await get_workspace_settings(current_user.workspace_id)
    analyzer = OpenAIService(api_key=workspace.openai_api_key, model=settings.openai_model if settings else "gpt-4", workspace_id=current_user.workspace_id)
    try:
        analysis = await analyzer.analyze_issue(issue, await service.get_issue_events(issue_id, limit=5))
        status = IssueStatus.COMPLETED.value if analysis else IssueStatus.FAILED.value
        await save_processed_issue(
            current_user.workspace_id, issue_id, sentry_issue=issue_data, status=status,
            created_by=current_user.id, ai_analysis=json_data(analysis) if analysis else None,
        )
        return {"issue_id": issue_id, "status": status, "analysis": json_data(analysis) if analysis else None}
    except Exception:
        logger.exception("Analysis failed for issue %s", issue_id)
        await save_processed_issue(
            current_user.workspace_id, issue_id, sentry_issue=issue_data, status=IssueStatus.FAILED.value,
            created_by=current_user.id, ai_analysis=None,
        )
        return {"issue_id": issue_id, "status": IssueStatus.FAILED.value, "analysis": None}
