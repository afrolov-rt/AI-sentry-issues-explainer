import random
import traceback
import asyncio
from typing import List, Dict, Any, Optional
import sentry_sdk
from sentry_sdk import capture_exception, capture_message, set_tag, set_extra
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class SentryEventGenerator:
    """Service for generating random events in Sentry for testing purposes"""
    
    def __init__(self):
        self.current_dsn = None
        self.error_templates = [
            {
                "type": "ValueError",
                "message": "Invalid user input: expected integer, got string",
                "context": {"user_id": "user_123", "input_value": "abc", "expected_type": "int"}
            },
            {
                "type": "KeyError", 
                "message": "Missing required configuration key",
                "context": {"missing_key": "database_url", "config_section": "database"}
            },
            {
                "type": "ConnectionError",
                "message": "Failed to connect to external service",
                "context": {"service": "payment_api", "timeout": 30, "retry_count": 3}
            },
            {
                "type": "IndexError",
                "message": "List index out of range",
                "context": {"list_length": 5, "requested_index": 8, "operation": "data_processing"}
            },
            {
                "type": "FileNotFoundError",
                "message": "Required configuration file not found",
                "context": {"file_path": "/etc/app/config.json", "operation": "startup"}
            },
            {
                "type": "PermissionError",
                "message": "Insufficient permissions to access resource",
                "context": {"resource": "/var/log/app.log", "user": "www-data", "required_permission": "write"}
            },
            {
                "type": "TimeoutError",
                "message": "Database query timeout exceeded",
                "context": {"query": "SELECT * FROM large_table", "timeout": 60, "table_size": "1M rows"}
            },
            {
                "type": "ValidationError",
                "message": "Data validation failed",
                "context": {"field": "email", "value": "invalid-email", "rule": "email_format"}
            },
            {
                "type": "AuthenticationError",
                "message": "Invalid API credentials",
                "context": {"api": "third_party_service", "credential_type": "bearer_token"}
            },
            {
                "type": "RateLimitError",
                "message": "API rate limit exceeded",
                "context": {"api": "external_service", "limit": "100/hour", "current_usage": 105}
            }
        ]
        
        self.warning_templates = [
            {
                "message": "High memory usage detected",
                "level": "warning",
                "context": {"memory_usage": "85%", "threshold": "80%", "process": "data_processor"}
            },
            {
                "message": "Slow database query detected",
                "level": "warning", 
                "context": {"query_time": "2.5s", "threshold": "1s", "query": "user_analytics"}
            },
            {
                "message": "Cache miss rate is high",
                "level": "warning",
                "context": {"cache_hit_rate": "65%", "expected_rate": "90%", "cache_type": "redis"}
            },
            {
                "message": "Deprecated API endpoint used",
                "level": "warning",
                "context": {"endpoint": "/api/v1/users", "deprecated_since": "2024-01-01", "replacement": "/api/v2/users"}
            },
            {
                "message": "Low disk space warning",
                "level": "warning",
                "context": {"available_space": "2GB", "threshold": "5GB", "partition": "/var/log"}
            }
        ]
        
        self.info_templates = [
            {
                "message": "User authentication successful",
                "level": "info",
                "context": {"user_id": "user_456", "ip_address": "192.168.1.100", "user_agent": "Chrome/120.0"}
            },
            {
                "message": "Scheduled task completed successfully",
                "level": "info", 
                "context": {"task": "daily_report", "duration": "45s", "records_processed": 1250}
            },
            {
                "message": "Cache refreshed",
                "level": "info",
                "context": {"cache_type": "user_preferences", "refresh_time": "10ms", "entries": 500}
            },
            {
                "message": "API request processed",
                "level": "info",
                "context": {"endpoint": "/api/v1/data", "response_time": "150ms", "status": 200}
            }
        ]

    def _generate_random_context(self) -> Dict[str, Any]:
        """Generate additional random context for events"""
        return {
            "request_id": f"req_{random.randint(10000, 99999)}",
            "session_id": f"sess_{random.randint(1000, 9999)}",
            "server_id": f"server_{random.randint(1, 10)}",
            "timestamp": "2024-08-20T10:30:00Z",
            "version": "1.0.0"
        }

    def _setup_sentry_dsn(self, custom_dsn: Optional[str] = None) -> str:
        """Setup Sentry DSN for event generation"""
        dsn = custom_dsn or settings.APP_SENTRY_DSN
        
        if not dsn:
            raise ValueError("No Sentry DSN configured. Please set APP_SENTRY_DSN or provide custom DSN.")
        
        if self.current_dsn != dsn:
            sentry_sdk.init(
                dsn=dsn,
                environment="test_events",
                traces_sample_rate=0.1,
                send_default_pii=False,
            )
            self.current_dsn = dsn
            logger.info(f"Sentry initialized with DSN: {dsn[:50]}...")
        
        return dsn

    def is_sentry_configured(self, custom_dsn: Optional[str] = None) -> bool:
        """Check if Sentry is configured"""
        dsn = custom_dsn or settings.APP_SENTRY_DSN
        return bool(dsn)

    def _create_fake_exception(self, error_template: Dict[str, Any]) -> Exception:
        """Create a fake exception based on template"""
        error_type = error_template["type"]
        message = error_template["message"]
        
        exception_map = {
            "ValueError": ValueError,
            "KeyError": KeyError,
            "ConnectionError": ConnectionError,
            "IndexError": IndexError,
            "FileNotFoundError": FileNotFoundError,
            "PermissionError": PermissionError,
            "TimeoutError": TimeoutError,
            "ValidationError": ValueError,
            "AuthenticationError": ValueError,
            "RateLimitError": ValueError,
        }
        
        exception_class = exception_map.get(error_type, Exception)
        return exception_class(message)

    async def generate_random_error(self, custom_dsn: Optional[str] = None) -> Dict[str, Any]:
        """Generate a random error event in Sentry"""
        dsn = self._setup_sentry_dsn(custom_dsn)
        
        error_template = random.choice(self.error_templates)
        
        set_tag("event_type", "generated_error")
        set_tag("error_category", error_template["type"])
        set_tag("environment", "testing")
        
        context = {**error_template["context"], **self._generate_random_context()}
        for key, value in context.items():
            set_extra(key, value)
        
        try:
            self._simulate_stack_trace(error_template)
        except Exception as e:
            event_id = capture_exception(e)
            
            return {
                "event_id": event_id,
                "type": "error",
                "error_type": error_template["type"],
                "message": error_template["message"],
                "context": context
            }

    def _simulate_stack_trace(self, error_template: Dict[str, Any]):
        """Simulate a realistic stack trace"""
        def level_3():
            raise self._create_fake_exception(error_template)
        
        def level_2():
            level_3()
        
        def level_1():
            level_2()
        
        level_1()

    async def generate_random_warning(self, custom_dsn: Optional[str] = None) -> Dict[str, Any]:
        """Generate a random warning event in Sentry"""
        dsn = self._setup_sentry_dsn(custom_dsn)
        
        warning_template = random.choice(self.warning_templates)
        
        set_tag("event_type", "generated_warning")
        set_tag("level", "warning")
        set_tag("environment", "testing")
        
        context = {**warning_template["context"], **self._generate_random_context()}
        for key, value in context.items():
            set_extra(key, value)
        
        event_id = capture_message(warning_template["message"], level="warning")
        
        return {
            "event_id": event_id,
            "type": "warning", 
            "message": warning_template["message"],
            "context": context
        }

    async def generate_random_info(self, custom_dsn: Optional[str] = None) -> Dict[str, Any]:
        """Generate a random info event in Sentry"""
        dsn = self._setup_sentry_dsn(custom_dsn)
        
        info_template = random.choice(self.info_templates)
        
        set_tag("event_type", "generated_info")
        set_tag("level", "info")
        set_tag("environment", "testing")
        
        context = {**info_template["context"], **self._generate_random_context()}
        for key, value in context.items():
            set_extra(key, value)
        
        event_id = capture_message(info_template["message"], level="info")
        
        return {
            "event_id": event_id,
            "type": "info",
            "message": info_template["message"],
            "context": context
        }

    async def generate_random_event(self, event_type: str = None, custom_dsn: Optional[str] = None) -> Dict[str, Any]:
        """Generate a random event of specified type or random type"""
        if event_type is None:
            event_type = random.choice(["error", "warning", "info"])
        
        if event_type == "error":
            return await self.generate_random_error(custom_dsn)
        elif event_type == "warning":
            return await self.generate_random_warning(custom_dsn)
        elif event_type == "info":
            return await self.generate_random_info(custom_dsn)
        else:
            raise ValueError(f"Unknown event type: {event_type}")

    async def generate_multiple_events(self, count: int = 5, custom_dsn: Optional[str] = None) -> List[Dict[str, Any]]:
        """Generate multiple random events"""
        events = []
        for _ in range(count):
            try:
                event = await self.generate_random_event(None, custom_dsn)
                events.append(event)
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Failed to generate event: {e}")
                events.append({
                    "error": str(e),
                    "type": "generation_failed"
                })
        
        return events

sentry_event_generator = SentryEventGenerator()
