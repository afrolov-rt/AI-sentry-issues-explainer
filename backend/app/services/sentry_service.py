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
            
            response_time = time.time() - start_time
            track_sentry_api_call(
                endpoint=f"organizations/{self.organization}",
                workspace_id=self.workspace_id,
                success=False,
                response_time=response_time,
                error=error
            )
            
            return False

    async def test_connection_detailed(self) -> dict:
        """Test Sentry API connection with detailed response"""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/organizations/{self.organization}/",
                    headers=self.headers,
                    timeout=10.0
                )
                
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    track_sentry_api_call(
                        endpoint=f"organizations/{self.organization}",
                        workspace_id=self.workspace_id,
                        success=True,
                        response_time=response_time
                    )
                    return {
                        "success": True,
                        "message": "Successfully connected to Sentry",
                        "organization": {
                            "id": data.get("id"),
                            "name": data.get("name"),
                            "slug": data.get("slug")
                        }
                    }
                elif response.status_code == 401:
                    track_sentry_api_call(
                        endpoint=f"organizations/{self.organization}",
                        workspace_id=self.workspace_id,
                        success=False,
                        response_time=response_time
                    )
                    return {
                        "success": False,
                        "message": "Invalid API token. Please check your Sentry API token and make sure it has the necessary permissions.",
                        "error_code": "unauthorized"
                    }
                elif response.status_code == 404:
                    track_sentry_api_call(
                        endpoint=f"organizations/{self.organization}",
                        workspace_id=self.workspace_id,
                        success=False,
                        response_time=response_time
                    )
                    return {
                        "success": False,
                        "message": f"Organization '{self.organization}' not found. Please check the organization slug.",
                        "error_code": "not_found"
                    }
                else:
                    track_sentry_api_call(
                        endpoint=f"organizations/{self.organization}",
                        workspace_id=self.workspace_id,
                        success=False,
                        response_time=response_time
                    )
                    return {
                        "success": False,
                        "message": f"Sentry API returned status {response.status_code}. Please try again later.",
                        "error_code": "api_error"
                    }
                
        except httpx.TimeoutException:
            response_time = time.time() - start_time
            track_sentry_api_call(
                endpoint=f"organizations/{self.organization}",
                workspace_id=self.workspace_id,
                success=False,
                response_time=response_time,
                error="timeout"
            )
            return {
                "success": False,
                "message": "Connection timeout. Please check your internet connection and try again.",
                "error_code": "timeout"
            }
        except Exception as e:
            response_time = time.time() - start_time
            track_sentry_api_call(
                endpoint=f"organizations/{self.organization}",
                workspace_id=self.workspace_id,
                success=False,
                response_time=response_time,
                error=e
            )
            logger.error(f"Failed to test Sentry connection: {e}")
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}",
                "error_code": "connection_error"
            }
    
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
            
            logger.info(f"Fetching issues from Sentry URL: {url}")
            logger.info(f"Query parameters: query={query}, limit={limit}")
            
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
                
                logger.info(f"Sentry API response status: {response.status_code}")
                
                if response.status_code != 200:
                    logger.error(f"Sentry API error: {response.status_code} - {response.text}")
                    response.raise_for_status()
                
                issues_data = response.json()
                logger.info(f"Received {len(issues_data)} issues from Sentry")
                
                issues = []
                for i, issue_data in enumerate(issues_data):
                    try:
                        logger.debug(f"Parsing issue {i+1}: ID={issue_data.get('id')}, Title={issue_data.get('title', 'No title')[:50]}...")
                        issue = self._parse_issue(issue_data)
                        issues.append(issue)
                    except Exception as e:
                        logger.warning(f"Failed to parse issue {issue_data.get('id')}: {e}")
                        continue
                
                logger.info(f"Successfully parsed {len(issues)} issues")
                
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
        start_time = time.time()
        success = False
        error = None
        
        try:
            logger.info(f"Fetching issue details for ID: {issue_id}")
            logger.info(f"Using organization: {self.organization}")
            logger.info(f"Using base URL: {self.base_url}")
            
            async with httpx.AsyncClient() as client:
                org_url = f"{self.base_url}/organizations/{self.organization}/issues/{issue_id}/"
                logger.info(f"Trying organization endpoint: {org_url}")
                
                response = await client.get(
                    org_url,
                    headers=self.headers,
                    timeout=30.0
                )
                
                logger.info(f"Organization endpoint response status: {response.status_code}")
                
                if response.status_code == 404:
                    global_url = f"{self.base_url}/issues/{issue_id}/"
                    logger.info(f"Trying global endpoint: {global_url}")
                    
                    response = await client.get(
                        global_url,
                        headers=self.headers,
                        timeout=30.0
                    )
                    logger.info(f"Global endpoint response status: {response.status_code}")
                
                if response.status_code != 200:
                    logger.error(f"Sentry API error: {response.status_code} - {response.text}")
                    return None
                
                response.raise_for_status()
                success = True
                
                issue_data = response.json()
                logger.info(f"Successfully fetched issue data: {issue_data.get('id')} - {issue_data.get('title', 'No title')}")
                result = self._parse_issue(issue_data)
                
                response_time = time.time() - start_time
                track_sentry_api_call(
                    endpoint=f"issues/{issue_id}",
                    workspace_id=self.workspace_id,
                    success=success,
                    response_time=response_time
                )
                
                return result
                
        except Exception as e:
            error = e
            logger.error(f"Failed to fetch issue details for {issue_id}: {e}")
            
            response_time = time.time() - start_time
            track_sentry_api_call(
                endpoint=f"issues/{issue_id}",
                workspace_id=self.workspace_id,
                success=success,
                response_time=response_time,
                error=error
            )
            
            return None
    
    async def get_issue_events(self, issue_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get events for a specific issue"""
        start_time = time.time()
        success = False
        error = None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/organizations/{self.organization}/issues/{issue_id}/events/",
                    headers=self.headers,
                    params={"limit": limit},
                    timeout=30.0
                )
                
                if response.status_code == 404:
                    response = await client.get(
                        f"{self.base_url}/issues/{issue_id}/events/",
                        headers=self.headers,
                        params={"limit": limit},
                        timeout=30.0
                    )
                
                response.raise_for_status()
                success = True
                result = response.json()
                
                response_time = time.time() - start_time
                track_sentry_api_call(
                    endpoint=f"issues/{issue_id}/events",
                    workspace_id=self.workspace_id,
                    success=success,
                    response_time=response_time
                )
                
                return result
                
        except Exception as e:
            error = e
            logger.error(f"Failed to fetch events for issue {issue_id}: {e}")
            
            response_time = time.time() - start_time
            track_sentry_api_call(
                endpoint=f"issues/{issue_id}/events",
                workspace_id=self.workspace_id,
                success=success,
                response_time=response_time,
                error=error
            )
            
            return []
    
    def _parse_issue(self, issue_data: Dict[str, Any]) -> SentryIssue:
        """Parse Sentry issue data into our schema"""
        try:
            logger.info(f"Parsing issue {issue_data.get('id')}")
            
            project = issue_data.get("project", {})
            logger.debug(f"Project data: {project}")
            
            metadata = issue_data.get("metadata", {})
            logger.debug(f"Metadata: {metadata}")
            
            message = ""
            if isinstance(metadata, dict):
                message = metadata.get("value", "") or metadata.get("title", "") or issue_data.get("title", "")
            else:
                message = issue_data.get("title", "")
            logger.debug(f"Extracted message: {message}")
            
            try:
                first_seen = datetime.fromisoformat(issue_data["firstSeen"].replace("Z", "+00:00"))
                logger.debug(f"Parsed firstSeen: {first_seen}")
            except (KeyError, ValueError, AttributeError) as e:
                logger.warning(f"Failed to parse firstSeen for issue {issue_data.get('id')}: {e}")
                first_seen = datetime.now()
            
            try:
                last_seen = datetime.fromisoformat(issue_data["lastSeen"].replace("Z", "+00:00"))
                logger.debug(f"Parsed lastSeen: {last_seen}")
            except (KeyError, ValueError, AttributeError) as e:
                logger.warning(f"Failed to parse lastSeen for issue {issue_data.get('id')}: {e}")
                last_seen = datetime.now()
            
            tags = {}
            try:
                raw_tags = issue_data.get("tags", [])
                logger.debug(f"Raw tags: {raw_tags}")
                if isinstance(raw_tags, list):
                    tags = {tag["key"]: tag.get("value", "") for tag in raw_tags if isinstance(tag, dict) and "key" in tag}
                logger.debug(f"Parsed tags: {tags}")
            except Exception as e:
                logger.warning(f"Failed to parse tags for issue {issue_data.get('id')}: {e}")
                tags = {}
            
            try:
                count = issue_data.get("count", 0)
                if isinstance(count, str):
                    count = int(count)
                elif not isinstance(count, int):
                    count = 0
            except (ValueError, TypeError):
                count = 0
                
            try:
                user_count = issue_data.get("userCount", 0)
                if isinstance(user_count, str):
                    user_count = int(user_count)
                elif not isinstance(user_count, int):
                    user_count = 0
            except (ValueError, TypeError):
                user_count = 0
            
            logger.info(f"Creating SentryIssue object for {issue_data.get('id')}")
            result = SentryIssue(
                id=issue_data["id"],
                title=issue_data.get("title", ""),
                culprit=issue_data.get("culprit"),
                message=message,
                level=issue_data.get("level", "error"),
                platform=issue_data.get("platform", "unknown"),
                project_id=project.get("id", ""),
                project_name=project.get("name", ""),
                first_seen=first_seen,
                last_seen=last_seen,
                count=count,
                userCount=user_count,
                permalink=issue_data.get("permalink", ""),
                tags=tags,
                metadata=metadata if isinstance(metadata, dict) else {}
            )
            logger.info(f"Successfully created SentryIssue for {issue_data.get('id')}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse issue data for {issue_data.get('id', 'unknown')}: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception args: {e.args}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def _parse_link_header(self, link_header: str) -> Dict[str, Dict[str, str]]:
        """Parse Link header for pagination"""
        links = {}
        if not link_header:
            return links
        
        for link in link_header.split(","):
            parts = link.strip().split(";")
            if len(parts) != 2:
                continue
            
            url = parts[0].strip()[1:-1]
            rel = parts[1].strip().split("=")[1][1:-1]
            
            if "cursor=" in url:
                cursor = url.split("cursor=")[1].split("&")[0]
                links[rel] = {"url": url, "cursor": cursor}
        
        return links
