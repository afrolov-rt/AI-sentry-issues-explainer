from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class IssueStatus(str, Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"

class IssuePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SentryIssue(BaseModel):
    id: str = Field(..., description="Sentry issue ID")
    title: str = Field(..., description="Issue title")
    culprit: Optional[str] = Field(None, description="Issue culprit")
    message: str = Field(..., description="Error message")
    level: str = Field(..., description="Error level")
    platform: str = Field(..., description="Platform")
    project_id: str = Field(..., description="Sentry project ID")
    project_name: str = Field(..., description="Sentry project name")
    first_seen: datetime = Field(..., description="First occurrence")
    last_seen: datetime = Field(..., description="Last occurrence")
    count: int = Field(..., description="Number of occurrences")
    userCount: int = Field(default=0, description="Number of affected users", alias="user_count")
    permalink: str = Field(..., description="Sentry issue URL")
    stack_trace: Optional[List[Dict[str, Any]]] = Field(None, description="Stack trace data")
    tags: Dict[str, str] = Field(default_factory=dict, description="Issue tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class AIAnalysis(BaseModel):
    issue_id: str = Field(..., description="Related Sentry issue ID")
    summary: str = Field(..., description="AI-generated summary")
    root_cause: str = Field(..., description="Identified root cause")
    technical_description: str = Field(..., description="Technical description")
    steps_to_reproduce: List[str] = Field(default_factory=list, description="Steps to reproduce")
    suggested_fix: str = Field(..., description="Suggested fix")
    code_examples: Optional[str] = Field(None, description="Code examples")
    priority: IssuePriority = Field(..., description="Suggested priority")
    estimated_effort: str = Field(..., description="Estimated effort (e.g., '2-4 hours')")
    affected_components: List[str] = Field(default_factory=list, description="Affected system components")
    related_issues: List[str] = Field(default_factory=list, description="Related issue IDs")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProcessedIssue(BaseModel):
    id: Optional[str] = Field(None, description="MongoDB document ID")
    sentry_issue: SentryIssue = Field(..., description="Original Sentry issue data")
    ai_analysis: Optional[AIAnalysis] = Field(None, description="AI analysis results")
    status: IssueStatus = Field(default=IssueStatus.PENDING, description="Processing status")
    assigned_to: Optional[str] = Field(None, description="Assigned developer ID")
    created_by: str = Field(..., description="User ID who created the analysis")
    workspace_id: str = Field(..., description="Workspace ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    DEVELOPER = "developer"

class User(BaseModel):
    id: Optional[str] = Field(None, description="MongoDB document ID")
    username: str = Field(..., description="Unique username")
    email: str = Field(..., description="User email")
    full_name: Optional[str] = Field(None, description="Full name")
    hashed_password: str = Field(..., description="Hashed password")
    role: UserRole = Field(default=UserRole.DEVELOPER, description="User role")
    is_active: bool = Field(default=True, description="Is user active")
    workspace_id: Optional[str] = Field(None, description="Associated workspace ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: str = Field(..., description="User email")
    full_name: Optional[str] = Field(None, description="Full name")
    password: str = Field(..., min_length=6, description="Password")
    role: UserRole = Field(default=UserRole.DEVELOPER, description="User role")

class UserLogin(BaseModel):
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    workspace_id: Optional[str]
    created_at: datetime

class Workspace(BaseModel):
    id: Optional[str] = Field(None, description="MongoDB document ID")
    name: str = Field(..., description="Workspace name")
    description: Optional[str] = Field(None, description="Workspace description")
    owner_id: str = Field(..., description="Workspace owner user ID")
    sentry_api_token: Optional[str] = Field(None, description="Sentry API token")
    sentry_organization: Optional[str] = Field(None, description="Sentry organization slug")
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Workspace settings")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class WorkspaceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Workspace name")
    description: Optional[str] = Field(None, description="Workspace description")

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Workspace name")
    description: Optional[str] = Field(None, description="Workspace description")
    sentry_api_token: Optional[str] = Field(None, description="Sentry API token")
    sentry_organization: Optional[str] = Field(None, description="Sentry organization slug")
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class Settings(BaseModel):
    id: Optional[str] = Field(None, description="MongoDB document ID")
    workspace_id: str = Field(..., description="Workspace ID")
    openai_model: str = Field(default="gpt-4", description="OpenAI model to use")
    auto_analyze: bool = Field(default=False, description="Auto-analyze new issues")
    notification_email: bool = Field(default=True, description="Email notifications")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
