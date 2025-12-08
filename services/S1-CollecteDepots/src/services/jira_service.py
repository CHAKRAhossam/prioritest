"""Jira API integration service."""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from jira import JIRA
from jira.exceptions import JIRAError
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import settings
from src.models.events import IssueEvent

logger = logging.getLogger(__name__)


class JiraService:
    """Service for Jira API operations."""
    
    def __init__(self):
        """Initialize Jira client."""
        if not all([settings.jira_url, settings.jira_email, settings.jira_api_token]):
            logger.warning("Jira credentials not fully configured")
            self.client = None
        else:
            try:
                self.client = JIRA(
                    server=settings.jira_url,
                    basic_auth=(settings.jira_email, settings.jira_api_token)
                )
                logger.info("Jira client initialized successfully")
            except Exception as e:
                logger.error(f"Jira initialization failed: {e}")
                self.client = None
    
    def _get_repo_id(self, project_key: str) -> str:
        """Generate repository ID from Jira project key."""
        return f"jira_{project_key}"
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def collect_issues(
        self,
        project_key: str,
        jql: Optional[str] = None
    ) -> List[IssueEvent]:
        """
        Collect issues from a Jira project.
        
        Args:
            project_key: Jira project key (e.g., "MTP")
            jql: Optional JQL query to filter issues
            
        Returns:
            List of IssueEvent objects
        """
        if not self.client:
            logger.error("Jira client not initialized")
            return []
        
        events = []
        try:
            # Build JQL query
            if not jql:
                jql = f"project = {project_key} ORDER BY created DESC"
            
            issues = self.client.search_issues(jql, maxResults=1000)
            repository_id = self._get_repo_id(project_key)
            
            for issue in issues:
                try:
                    # Get linked commits from issue description/comments
                    linked_commits = []
                    
                    # Check description
                    if issue.fields.description:
                        import re
                        commits = re.findall(r'\b[0-9a-f]{7,40}\b', issue.fields.description)
                        linked_commits.extend(commits)
                    
                    # Check comments
                    comments = self.client.comments(issue)
                    for comment in comments:
                        if comment.body:
                            import re
                            commits = re.findall(r'\b[0-9a-f]{7,40}\b', comment.body)
                            linked_commits.extend(commits)
                    
                    # Remove duplicates
                    linked_commits = list(set(linked_commits))
                    
                    event = IssueEvent(
                        event_id=f"evt_jira_{issue.key}",
                        repository_id=repository_id,
                        issue_key=issue.key,
                        issue_type=issue.fields.issuetype.name,
                        summary=issue.fields.summary,
                        status=issue.fields.status.name,
                        created_at=datetime.strptime(issue.fields.created, "%Y-%m-%dT%H:%M:%S.%f%z"),
                        linked_commits=linked_commits,
                        metadata={
                            "url": f"{settings.jira_url}/browse/{issue.key}",
                            "assignee": issue.fields.assignee.key if issue.fields.assignee else None,
                            "priority": issue.fields.priority.name if issue.fields.priority else None,
                            "labels": issue.fields.labels
                        }
                    )
                    events.append(event)
                    
                except Exception as e:
                    logger.error(f"Error processing issue {issue.key}: {e}")
                    continue
            
            logger.info(f"Collected {len(events)} issues from project {project_key}")
            return events
            
        except JIRAError as e:
            logger.error(f"Jira API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error collecting issues: {e}")
            return []
    
    def parse_webhook(self, payload: Dict[str, Any], event_type: str) -> Optional[IssueEvent]:
        """
        Parse Jira webhook payload.
        
        Args:
            payload: Webhook JSON payload
            event_type: Webhook event type (jira:issue_created, jira:issue_updated)
            
        Returns:
            IssueEvent or None
        """
        try:
            if "issue" in payload:
                issue = payload["issue"]
                fields = issue.get("fields", {})
                
                repository_id = self._get_repo_id(fields.get("project", {}).get("key", ""))
                
                # Extract linked commits from description
                linked_commits = []
                description = fields.get("description", "")
                if description:
                    import re
                    commits = re.findall(r'\b[0-9a-f]{7,40}\b', description)
                    linked_commits.extend(commits)
                
                return IssueEvent(
                    event_id=f"evt_webhook_{issue.get('key', '')}",
                    repository_id=repository_id,
                    issue_key=issue.get("key", ""),
                    issue_type=fields.get("issuetype", {}).get("name", "Task"),
                    summary=fields.get("summary", ""),
                    status=fields.get("status", {}).get("name", "Open"),
                    created_at=datetime.fromisoformat(issue.get("fields", {}).get("created", "").replace("Z", "+00:00")),
                    linked_commits=linked_commits,
                    metadata={
                        "webhook_event": event_type,
                        "changelog": payload.get("changelog", {})
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing Jira webhook: {e}")
            return None

