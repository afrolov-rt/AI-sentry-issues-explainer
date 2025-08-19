from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.auth.auth_service import get_current_user, get_current_active_user
from app.models.schemas import User, SentryIssue, ProcessedIssue, IssueStatus
from app.services.sentry_service import SentryService
from app.services.openai_service import OpenAIService
from app.models.database import get_database
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=dict)
async def get_issues(
    project_id: Optional[str] = Query(None, description="Project ID to filter issues"),
    query: str = Query("is:unresolved", description="Sentry query string"),
    limit: int = Query(25, ge=1, le=100, description="Number of issues to return"),
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    current_user: User = Depends(get_current_active_user)
):
    """Get issues from Sentry"""
    try:
        if not current_user.workspace_id:
            raise HTTPException(
                status_code=400,
                detail="No workspace found. Please create a workspace first."
            )
        
        # Get workspace Sentry settings
        db = get_database()
        workspace = await db.workspaces.find_one({"_id": ObjectId(current_user.workspace_id)})
        
        if not workspace or not workspace.get("sentry_api_token"):
            raise HTTPException(
                status_code=400,
                detail="Sentry API token not configured in workspace. Please update workspace settings."
            )
        
        # Initialize Sentry service with workspace credentials
        sentry_service = SentryService(
            api_token=workspace["sentry_api_token"],
            organization=workspace.get("sentry_organization"),
            workspace_id=current_user.workspace_id
        )
        
        # Test connection
        if not await sentry_service.test_connection():
            raise HTTPException(
                status_code=400,
                detail="Failed to connect to Sentry. Please check workspace Sentry settings."
            )
        
        # Fetch issues
        result = await sentry_service.get_issues(
            project_id=project_id,
            query=query,
            limit=limit,
            cursor=cursor
        )
        
        # Check which issues are already processed in this workspace
        processed_issues = {}
        if result["issues"]:
            issue_ids = [issue.id for issue in result["issues"]]
            processed_docs = await db.processed_issues.find(
                {
                    "sentry_issue.id": {"$in": issue_ids},
                    "workspace_id": current_user.workspace_id
                },
                {"sentry_issue.id": 1, "status": 1, "ai_analysis": 1}
            ).to_list(length=None)
            
            processed_issues = {
                doc["sentry_issue"]["id"]: {
                    "status": doc["status"],
                    "has_analysis": bool(doc.get("ai_analysis"))
                }
                for doc in processed_docs
            }
        
        # Add processing status to issues
        for issue in result["issues"]:
            issue_dict = issue.dict()
            issue_dict["processing_status"] = processed_issues.get(issue.id, {
                "status": "not_processed",
                "has_analysis": False
            })
        
        return {
            "issues": [issue.dict() for issue in result["issues"]],
            "pagination": {
                "next_cursor": result["next_cursor"],
                "prev_cursor": result["prev_cursor"],
                "has_next": result["has_next"]
            },
            "processed_status": processed_issues
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch issues: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch issues from Sentry")

@router.get("/{issue_id}", response_model=dict)
async def get_issue_details(
    issue_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get detailed information about a specific issue"""
    try:
        if not current_user.workspace_id:
            raise HTTPException(status_code=400, detail="No workspace found")
        
        db = get_database()
        
        # Check if issue is already processed in this workspace
        processed_issue = await db.processed_issues.find_one({
            "sentry_issue.id": issue_id,
            "workspace_id": current_user.workspace_id
        })
        
        if processed_issue:
            # Convert ObjectId to string
            if "_id" in processed_issue:
                processed_issue["id"] = str(processed_issue["_id"])
                del processed_issue["_id"]
            return {"processed_issue": ProcessedIssue(**processed_issue)}
        
        # Get workspace Sentry settings
        workspace = await db.workspaces.find_one({"_id": ObjectId(current_user.workspace_id)})
        
        if not workspace or not workspace.get("sentry_api_token"):
            raise HTTPException(
                status_code=400,
                detail="Sentry API token not configured in workspace"
            )
        
        # Fetch from Sentry
        sentry_service = SentryService(
            api_token=workspace["sentry_api_token"],
            organization=workspace.get("sentry_organization"),
            workspace_id=current_user.workspace_id
        )
        
        issue = await sentry_service.get_issue_details(issue_id)
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")
        
        return {"sentry_issue": issue.dict()}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch issue details: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch issue details")

@router.post("/{issue_id}/analyze", response_model=dict)
async def analyze_issue(
    issue_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Analyze an issue with AI and generate technical specification"""
    try:
        if not current_user.workspace_id:
            raise HTTPException(status_code=400, detail="No workspace found")
        
        db = get_database()
        
        # Check if already being processed in this workspace
        existing = await db.processed_issues.find_one({
            "sentry_issue.id": issue_id,
            "workspace_id": current_user.workspace_id
        })
        
        if existing and existing.get("status") == IssueStatus.ANALYZING:
            raise HTTPException(
                status_code=409,
                detail="Issue is already being analyzed"
            )
        
        # Get workspace settings
        workspace = await db.workspaces.find_one({"_id": ObjectId(current_user.workspace_id)})
        if not workspace or not workspace.get("sentry_api_token"):
            raise HTTPException(
                status_code=400,
                detail="Sentry API token not configured in workspace"
            )
        
        # Initialize services
        sentry_service = SentryService(
            api_token=workspace["sentry_api_token"],
            organization=workspace.get("sentry_organization"),
            workspace_id=current_user.workspace_id
        )
        
        # Get workspace settings for OpenAI model
        workspace_settings = await db.settings.find_one({"workspace_id": current_user.workspace_id})
        openai_model = workspace_settings.get("openai_model", "gpt-4") if workspace_settings else "gpt-4"
        
        openai_service = OpenAIService(
            model=openai_model,
            workspace_id=current_user.workspace_id
        )
        
        # Fetch issue details from Sentry
        issue = await sentry_service.get_issue_details(issue_id)
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found in Sentry")
        
        # Get recent events for more context
        events = await sentry_service.get_issue_events(issue_id, limit=5)
        
        # Create or update processed issue record
        processed_issue_data = {
            "sentry_issue": issue.dict(),
            "status": IssueStatus.ANALYZING,
            "created_by": current_user.id,
            "workspace_id": current_user.workspace_id
        }
        
        if existing:
            await db.processed_issues.update_one(
                {
                    "sentry_issue.id": issue_id,
                    "workspace_id": current_user.workspace_id
                },
                {"$set": processed_issue_data}
            )
            doc_id = existing["_id"]
        else:
            result = await db.processed_issues.insert_one(processed_issue_data)
            doc_id = result.inserted_id
        
        try:
            # Perform AI analysis
            analysis = await openai_service.analyze_issue(issue, events)
            
            if analysis:
                # Update with successful analysis
                await db.processed_issues.update_one(
                    {"_id": doc_id},
                    {
                        "$set": {
                            "ai_analysis": analysis.dict(),
                            "status": IssueStatus.COMPLETED
                        }
                    }
                )
                status = IssueStatus.COMPLETED
            else:
                # Mark as failed
                await db.processed_issues.update_one(
                    {"_id": doc_id},
                    {"$set": {"status": IssueStatus.FAILED}}
                )
                status = IssueStatus.FAILED
                
        except Exception as e:
            logger.error(f"Analysis failed for issue {issue_id}: {e}")
            await db.processed_issues.update_one(
                {"_id": doc_id},
                {"$set": {"status": IssueStatus.FAILED}}
            )
            status = IssueStatus.FAILED
            analysis = None
        
        return {
            "issue_id": issue_id,
            "status": status,
            "analysis": analysis.dict() if analysis else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze issue {issue_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze issue")

@router.get("/processed/", response_model=List[dict])
async def get_processed_issues(
    status: Optional[IssueStatus] = Query(None, description="Filter by status"),
    limit: int = Query(25, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of processed issues for current workspace"""
    try:
        if not current_user.workspace_id:
            raise HTTPException(status_code=400, detail="No workspace found")
        
        db = get_database()
        
        # Build query for workspace
        query = {"workspace_id": current_user.workspace_id}
        if status:
            query["status"] = status
        
        # Fetch processed issues
        cursor = db.processed_issues.find(query).skip(skip).limit(limit).sort("created_at", -1)
        issues = await cursor.to_list(length=None)
        
        # Convert ObjectId to string
        for issue in issues:
            if "_id" in issue:
                issue["id"] = str(issue["_id"])
                del issue["_id"]
        
        return issues
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch processed issues: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch processed issues")
