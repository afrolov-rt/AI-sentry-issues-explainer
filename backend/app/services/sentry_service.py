import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime
from config.settings import settings
from app.models.schemas import SentryIssue
from app.services.sentry_monitoring import track_sentry_api_call
import logging
import time

logger = logging.getLogger(__name__)

class SentryService:
    def __init__(self, api_token: str = None, organization: str = None, workspace_id: str = None):
        self.api_token = api_token or settings.SENTRY_API_TOKEN
        self.organization = organization or settings.SENTRY_ORG_SLUG
        self.workspace_id = workspace_id
        self.base_url = settings.SENTRY_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    async def test_connection(self) -> bool:
        """Test Sentry API connection"""
        start_time = time.time()
        success = False
        error = None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/organizations/{self.organization}/",
                    headers=self.headers,
                    timeout=10.0
                )
                success = response.status_code == 200
                
                # Track API call
                response_time = time.time() - start_time
                track_sentry_api_call(
                    endpoint=f"organizations/{self.organization}",
                    workspace_id=self.workspace_id,
                    success=success,
                    response_time=response_time
                )
                
                return success
                
        except Exception as e:
            error = e
            logger.error(f"Failed to test Sentry connection: {e}")
            
            # Track failed API call
            response_time = time.time() - start_time
            track_sentry_api_call(
                endpoint=f"organizations/{self.organization}",
                workspace_id=self.workspace_id,
                success=False,
                response_time=response_time,
                error=error
            )
            
            return False
    
    async def get_projects(self) -> List[Dict[str, Any]]:
        """Get list of projects from Sentry"""
        start_time = time.time()
        error = None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/organizations/{self.organization}/projects/",
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                
                # Track successful API call
                response_time = time.time() - start_time
                track_sentry_api_call(
                    endpoint=f"organizations/{self.organization}/projects",
                    workspace_id=self.workspace_id,
                    success=True,
                    response_time=response_time
                )
                
                return response.json()
                
        except Exception as e:
            error = e
            logger.error(f"Failed to fetch projects: {e}")
            
            # Track failed API call
            response_time = time.time() - start_time
            track_sentry_api_call(
                endpoint=f"organizations/{self.organization}/projects",
                workspace_id=self.workspace_id,
                success=False,
                response_time=response_time,
                error=error
            )
            
            raise
    
    async def get_issues(
        self, 
        project_id: str = None,
        query: str = "is:unresolved",
        limit: int = 25,
        cursor: str = None
    ) -> Dict[str, Any]:
        """Get issues from Sentry"""
        try:
            url = f"{self.base_url}/organizations/{self.organization}/issues/"
            if project_id:
                url = f"{self.base_url}/projects/{self.organization}/{project_id}/issues/"
            
            params = {
                "query": query,
                "limit": limit,
                "shortIdLookup": 1
            }
            
            if cursor:
                params["cursor"] = cursor
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                
                issues_data = response.json()
                
                # Parse issues into our schema
                issues = []
                for issue_data in issues_data:
                    try:
                        issue = self._parse_issue(issue_data)
                        issues.append(issue)
                    except Exception as e:
                        logger.warning(f"Failed to parse issue {issue_data.get('id')}: {e}")
                        continue
                
                # Get pagination info from headers
                links = self._parse_link_header(response.headers.get("Link", ""))
                
                return {
                    "issues": issues,
                    "next_cursor": links.get("next", {}).get("cursor"),
                    "prev_cursor": links.get("previous", {}).get("cursor"),
                    "has_next": "next" in links
                }
                
        except Exception as e:
            logger.error(f"Failed to fetch issues: {e}")
            raise
    
    async def get_issue_details(self, issue_id: str) -> Optional[SentryIssue]:
        """Get detailed information about a specific issue"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/issues/{issue_id}/",
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                
                issue_data = response.json()
                return self._parse_issue(issue_data)
                
        except Exception as e:
            logger.error(f"Failed to fetch issue details for {issue_id}: {e}")
            return None
    
    async def get_issue_events(self, issue_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get events for a specific issue"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/issues/{issue_id}/events/",
                    headers=self.headers,
                    params={"limit": limit},
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to fetch events for issue {issue_id}: {e}")
            return []
    
    def _parse_issue(self, issue_data: Dict[str, Any]) -> SentryIssue:
        """Parse Sentry issue data into our schema"""
        project = issue_data.get("project", {})
        
        return SentryIssue(
            id=issue_data["id"],
            title=issue_data.get("title", ""),
            culprit=issue_data.get("culprit"),
            message=issue_data.get("metadata", {}).get("value", issue_data.get("title", "")),
            level=issue_data.get("level", "error"),
            platform=issue_data.get("platform", "unknown"),
            project_id=project.get("id", ""),
            project_name=project.get("name", ""),
            first_seen=datetime.fromisoformat(issue_data["firstSeen"].replace("Z", "+00:00")),
            last_seen=datetime.fromisoformat(issue_data["lastSeen"].replace("Z", "+00:00")),
            count=issue_data.get("count", 0),
            user_count=issue_data.get("userCount", 0),
            permalink=issue_data.get("permalink", ""),
            tags={tag["key"]: tag["value"] for tag in issue_data.get("tags", [])},
            metadata=issue_data.get("metadata", {})
        )
    
    def _parse_link_header(self, link_header: str) -> Dict[str, Dict[str, str]]:
        """Parse Link header for pagination"""
        links = {}
        if not link_header:
            return links
        
        for link in link_header.split(","):
            parts = link.strip().split(";")
            if len(parts) != 2:
                continue
            
            url = parts[0].strip()[1:-1]  # Remove < >
            rel = parts[1].strip().split("=")[1][1:-1]  # Remove quotes
            
            # Extract cursor from URL
            if "cursor=" in url:
                cursor = url.split("cursor=")[1].split("&")[0]
                links[rel] = {"url": url, "cursor": cursor}
        
        return links
