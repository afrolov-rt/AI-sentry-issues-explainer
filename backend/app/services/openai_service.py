import openai
from typing import Optional
from config.settings import settings
from app.models.schemas import SentryIssue, AIAnalysis, IssuePriority
from app.services.sentry_monitoring import track_openai_api_call, track_issue_analysis
import json
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self, api_key: str = None, model: str = None, workspace_id: str = None):
        self.client = openai.AsyncOpenAI(
            api_key=api_key or settings.OPENAI_API_KEY
        )
        self.model = model or settings.OPENAI_MODEL
        self.workspace_id = workspace_id
    
    async def analyze_issue(self, sentry_issue: SentryIssue, events_data: list = None) -> Optional[AIAnalysis]:
        """Analyze Sentry issue and generate technical specification"""
        start_time = time.time()
        analysis_status = "failed"
        error = None
        tokens_used = None
        
        try:
            context = self._prepare_issue_context(sentry_issue, events_data)
            
            prompt = self._create_analysis_prompt(context)
            
            api_start_time = time.time()
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior software engineer and technical writer. Your task is to analyze software errors and create detailed technical specifications for developers."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            api_response_time = time.time() - api_start_time
            tokens_used = response.usage.total_tokens if response.usage else None
            
            track_openai_api_call(
                model=self.model,
                tokens_used=tokens_used,
                success=True,
                response_time=api_response_time
            )
            
            analysis_text = response.choices[0].message.content
            analysis = self._parse_analysis_response(analysis_text, sentry_issue.id)
            
            analysis_status = "completed"
            
            analysis_time = time.time() - start_time
            track_issue_analysis(
                issue_id=sentry_issue.id,
                workspace_id=self.workspace_id,
                status=analysis_status,
                analysis_time=analysis_time
            )
            
            return analysis
            
        except Exception as e:
            error = e
            logger.error(f"Failed to analyze issue {sentry_issue.id}: {e}")
            
            if 'api_start_time' in locals():
                api_response_time = time.time() - api_start_time
                track_openai_api_call(
                    model=self.model,
                    tokens_used=tokens_used,
                    success=False,
                    response_time=api_response_time,
                    error=error
                )
            
            analysis_time = time.time() - start_time
            track_issue_analysis(
                issue_id=sentry_issue.id,
                workspace_id=self.workspace_id,
                status=analysis_status,
                analysis_time=analysis_time,
                error=error
            )
            
            return None
    
    def _prepare_issue_context(self, issue: SentryIssue, events_data: list = None) -> dict:
        """Prepare issue context for AI analysis"""
        context = {
            "title": issue.title,
            "message": issue.message,
            "level": issue.level,
            "platform": issue.platform,
            "project": issue.project_name,
            "culprit": issue.culprit,
            "count": issue.count,
            "user_count": issue.userCount,
            "first_seen": issue.first_seen.isoformat(),
            "last_seen": issue.last_seen.isoformat(),
            "tags": issue.tags,
            "metadata": issue.metadata
        }
        
        if issue.stack_trace:
            context["stack_trace"] = issue.stack_trace
        
        if events_data:
            context["recent_events"] = events_data[:3]
        
        return context
    
    def _create_analysis_prompt(self, context: dict) -> str:
        """Create prompt for AI analysis"""
        return f"""
Please analyze the following software error and provide a comprehensive technical specification:

**Error Details:**
- Title: {context['title']}
- Message: {context['message']}
- Level: {context['level']}
- Platform: {context['platform']}
- Project: {context['project']}
- Occurrences: {context['count']} times
- Affected Users: {context['user_count']}
- First Seen: {context['first_seen']}
- Last Seen: {context['last_seen']}

**Tags:** {json.dumps(context.get('tags', {}), indent=2)}

**Additional Context:** {json.dumps(context.get('metadata', {}), indent=2)}

Please provide your analysis in the following JSON format:

{{
    "summary": "Brief 1-2 sentence summary of the issue",
    "root_cause": "Detailed explanation of what is causing this error",
    "technical_description": "Technical details about the error for developers",
    "steps_to_reproduce": ["Step 1", "Step 2", "Step 3"],
    "suggested_fix": "Detailed explanation of how to fix this issue",
    "code_examples": "Code examples or configuration changes needed (if applicable)",
    "priority": "low|medium|high|critical",
    "estimated_effort": "Time estimate (e.g., '2-4 hours', '1-2 days')",
    "affected_components": ["component1", "component2"],
    "related_issues": []
}}

Focus on:
1. Identifying the root cause from the error message and context
2. Providing actionable steps for developers
3. Estimating the impact and effort required
4. Suggesting preventive measures if applicable
"""
    
    def _parse_analysis_response(self, response_text: str, issue_id: str) -> AIAnalysis:
        """Parse AI response into AIAnalysis object"""
        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
            
            json_text = response_text[start_idx:end_idx]
            analysis_data = json.loads(json_text)
            
            priority_mapping = {
                "low": IssuePriority.LOW,
                "medium": IssuePriority.MEDIUM,
                "high": IssuePriority.HIGH,
                "critical": IssuePriority.CRITICAL
            }
            
            priority = priority_mapping.get(
                analysis_data.get("priority", "medium").lower(),
                IssuePriority.MEDIUM
            )
            
            return AIAnalysis(
                issue_id=issue_id,
                summary=analysis_data.get("summary", ""),
                root_cause=analysis_data.get("root_cause", ""),
                technical_description=analysis_data.get("technical_description", ""),
                steps_to_reproduce=analysis_data.get("steps_to_reproduce", []),
                suggested_fix=analysis_data.get("suggested_fix", ""),
                code_examples=analysis_data.get("code_examples"),
                priority=priority,
                estimated_effort=analysis_data.get("estimated_effort", "Unknown"),
                affected_components=analysis_data.get("affected_components", []),
                related_issues=analysis_data.get("related_issues", [])
            )
            
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            
            return AIAnalysis(
                issue_id=issue_id,
                summary="AI analysis parsing failed",
                root_cause="Unable to analyze due to parsing error",
                technical_description="Manual review required",
                suggested_fix="Please review this issue manually",
                priority=IssuePriority.MEDIUM,
                estimated_effort="Unknown"
            )
