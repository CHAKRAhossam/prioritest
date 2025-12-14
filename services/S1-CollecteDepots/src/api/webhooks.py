"""Webhook endpoints for GitHub, GitLab, and Jira."""
import logging
import hmac
import hashlib
from typing import Optional, Dict, Any
from fastapi import APIRouter, Request, HTTPException, Header, Depends, BackgroundTasks, Body
from fastapi.responses import Response
from datetime import datetime

from src.services.github_service import GitHubService
from src.services.gitlab_service import GitLabService
from src.services.jira_service import JiraService
from src.services.kafka_service import KafkaService
from src.services.database_service import DatabaseService
from src.models.events import CommitEvent, IssueEvent
from src.models.webhook_models import GitHubWebhookPayload, GitLabWebhookPayload, JiraWebhookPayload
from src.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhooks"])


def verify_github_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature."""
    if not settings.github_webhook_secret:
        return True  # Skip verification if secret not configured
    
    expected_signature = hmac.new(
        settings.github_webhook_secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected_signature}", signature)


def verify_gitlab_signature(payload: bytes, token: str) -> bool:
    """Verify GitLab webhook signature."""
    if not settings.gitlab_webhook_secret:
        return True
    
    return hmac.compare_digest(settings.gitlab_webhook_secret, token)


@router.post("/github")
async def github_webhook(
    background_tasks: BackgroundTasks,
    payload: GitHubWebhookPayload = Body(..., description="GitHub webhook payload"),
    x_github_event: str = Header(None, description="GitHub event type (push, pull_request, issues)"),
    x_hub_signature_256: str = Header(None, alias="X-Hub-Signature-256", description="GitHub signature for verification")
):
    """
    Handle GitHub webhooks.
    
    Receives push events, pull requests, and issues from GitHub.
    
    **Supported events:**
    - `push`: Commit events
    - `pull_request`: Pull request events  
    - `issues`: Issue events
    
    **Example:**
    ```json
    {
      "ref": "refs/heads/main",
      "repository": {
        "id": 123456,
        "name": "my-repo",
        "full_name": "org/my-repo"
      },
      "commits": [
        {
          "id": "abc123",
          "message": "Fix bug",
          "author": {"name": "John", "email": "john@example.com"},
          "timestamp": "2025-12-13T10:00:00Z"
        }
      ]
    }
    ```
    """
    try:
        # Convert payload to dict for processing
        import json
        data = json.loads(payload.model_dump_json())
        
        # Note: Signature verification would require raw body, skipped for now in typed version
        
        # Process based on event type
        github_service = GitHubService()
        kafka_service = KafkaService()
        db_service = DatabaseService()
        
        if x_github_event == "push":
            commit_event = github_service.parse_webhook(data, "push")
            if commit_event:
                background_tasks.add_task(
                    _process_commit_event,
                    commit_event,
                    kafka_service,
                    db_service
                )
        
        elif x_github_event == "issues":
            # Parse issue event
            issue = data.get("issue", {})
            repository = data.get("repository", {})
            
            if issue and repository:
                repository_id = github_service._get_repo_id(repository.get("full_name", ""))
                
                from src.models.events import IssueEvent
                # Parse created_at date
                created_at_str = issue.get("created_at", "")
                if created_at_str:
                    try:
                        created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                    except:
                        created_at = datetime.utcnow()
                else:
                    created_at = datetime.utcnow()
                
                issue_event = IssueEvent(
                    event_id=f"evt_webhook_gh_{issue.get('number', '')}",
                    repository_id=repository_id,
                    issue_key=f"GH-{issue.get('number', '')}",
                    issue_type="Bug" if "bug" in str(issue.get("labels", [])).lower() else "Feature",
                    summary=issue.get("title", ""),
                    status=issue.get("state", "").capitalize(),
                    created_at=created_at,
                    linked_commits=[],
                    metadata={"action": data.get("action", "")}
                )
                
                background_tasks.add_task(
                    _process_issue_event,
                    issue_event,
                    kafka_service,
                    db_service
                )
        
        return Response(status_code=200, content="OK")
        
    except Exception as e:
        logger.error(f"Error processing GitHub webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gitlab")
async def gitlab_webhook(
    background_tasks: BackgroundTasks,
    payload: GitLabWebhookPayload = Body(..., description="GitLab webhook payload"),
    x_gitlab_token: str = Header(None, alias="X-Gitlab-Token", description="GitLab token for verification"),
    x_gitlab_event: str = Header(None, alias="X-Gitlab-Event", description="GitLab event type (Push Hook, Issue Hook)")
):
    """
    Handle GitLab webhooks.
    
    Receives push events, merge requests, and issues from GitLab.
    
    **Supported events:**
    - `Push Hook`: Commit events
    - `Issue Hook`: Issue events
    - `Merge Request Hook`: Merge request events
    
    **Example:**
    ```json
    {
      "object_kind": "push",
      "ref": "refs/heads/develop",
      "project": {
        "id": 123,
        "name": "my-project",
        "path_with_namespace": "org/my-project"
      },
      "commits": [
        {
          "id": "def456",
          "message": "Add feature",
          "author": {"name": "Jane", "email": "jane@example.com"},
          "timestamp": "2025-12-13T10:00:00Z"
        }
      ]
    }
    ```
    """
    try:
        # Convert payload to dict for processing
        import json
        data = json.loads(payload.model_dump_json())
        
        gitlab_service = GitLabService()
        kafka_service = KafkaService()
        db_service = DatabaseService()
        
        if x_gitlab_event == "Push Hook":
            commit_event = gitlab_service.parse_webhook(data, "push")
            if commit_event:
                background_tasks.add_task(
                    _process_commit_event,
                    commit_event,
                    kafka_service,
                    db_service
                )
        
        elif x_gitlab_event == "Issue Hook":
            issue = data.get("object_attributes", {})
            project = data.get("project", {})
            
            if issue and project:
                repository_id = gitlab_service._get_repo_id(str(project.get("id", "")))
                
                from src.models.events import IssueEvent
                from datetime import datetime
                
                issue_event = IssueEvent(
                    event_id=f"evt_webhook_gl_{issue.get('iid', '')}",
                    repository_id=repository_id,
                    issue_key=f"GL-{issue.get('iid', '')}",
                    issue_type=issue.get("labels", [{}])[0].get("name", "Task") if issue.get("labels") else "Task",
                    summary=issue.get("title", ""),
                    status=issue.get("state", "").capitalize(),
                    created_at=datetime.fromisoformat(issue.get("created_at", "").replace("Z", "+00:00")),
                    linked_commits=[],
                    metadata={"action": data.get("object_attributes", {}).get("action", "")}
                )
                
                background_tasks.add_task(
                    _process_issue_event,
                    issue_event,
                    kafka_service,
                    db_service
                )
        
        return Response(status_code=200, content="OK")
        
    except Exception as e:
        logger.error(f"Error processing GitLab webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jira")
async def jira_webhook(
    background_tasks: BackgroundTasks,
    payload: JiraWebhookPayload = Body(..., description="Jira webhook payload")
):
    """
    Handle Jira webhooks.
    
    Receives issue events from Jira.
    
    **Supported events:**
    - `jira:issue_created`: New issue created
    - `jira:issue_updated`: Issue updated
    
    **Example:**
    ```json
    {
      "webhookEvent": "jira:issue_created",
      "issue": {
        "key": "PROJ-123",
        "fields": {
          "summary": "Bug in login",
          "issuetype": {"name": "Bug"},
          "status": {"name": "Open"},
          "created": "2025-12-13T10:00:00.000+0100"
        }
      }
    }
    ```
    """
    try:
        # Convert payload to dict for processing
        import json
        data = json.loads(payload.model_dump_json())
        
        webhook_event = data.get("webhookEvent", "")
        
        jira_service = JiraService()
        kafka_service = KafkaService()
        db_service = DatabaseService()
        
        if "issue" in webhook_event:
            issue_event = jira_service.parse_webhook(data, webhook_event)
            if issue_event:
                background_tasks.add_task(
                    _process_issue_event,
                    issue_event,
                    kafka_service,
                    db_service
                )
        
        return Response(status_code=200, content="OK")
        
    except Exception as e:
        logger.error(f"Error processing Jira webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _process_commit_event(
    event: CommitEvent,
    kafka_service: KafkaService,
    db_service: DatabaseService
):
    """Process commit event in background."""
    try:
        # Publish to Kafka
        kafka_service.publish_commit(event)
        
        # Store in database
        db_service.store_commit({
            "event_id": event.event_id,
            "repository_id": event.repository_id,
            "commit_sha": event.commit_sha,
            "commit_message": event.commit_message,
            "author_email": event.author_email,
            "author_name": event.author_name,
            "timestamp": event.timestamp,
            "files_changed": [f.model_dump() for f in event.files_changed],
            "metadata_json": event.metadata.model_dump()
        })
        
        kafka_service.flush()
        logger.info(f"Processed commit event {event.event_id}")
        
    except Exception as e:
        logger.error(f"Error processing commit event: {e}")


def _process_issue_event(
    event: IssueEvent,
    kafka_service: KafkaService,
    db_service: DatabaseService
):
    """Process issue event in background."""
    try:
        # Publish to Kafka
        kafka_service.publish_issue(event)
        
        # Get or create repository (required for foreign key constraint)
        # Extract project info from repository_id (format: jira_PROJECT_KEY)
        project_key = event.repository_id.replace("jira_", "")
        
        # Get Jira URL from settings
        from src.config import settings
        jira_url = settings.jira_url or "https://prioritest.atlassian.net"
        
        # Create repository if it doesn't exist
        db_service.get_or_create_repository(
            repository_id=event.repository_id,
            name=project_key,
            full_name=f"{project_key} (Jira)",
            url=f"{jira_url}/browse/{project_key}",
            source="jira",
            default_branch="main",
            metadata_json={"project_key": project_key}
        )
        
        # Store in database
        # Handle metadata: it can be a dict or a Pydantic model
        if event.metadata:
            if isinstance(event.metadata, dict):
                metadata_json = event.metadata
            else:
                metadata_json = event.metadata.model_dump()
        else:
            metadata_json = {}
        
        db_service.store_issue({
            "event_id": event.event_id,
            "repository_id": event.repository_id,
            "issue_key": event.issue_key,
            "issue_type": event.issue_type,
            "summary": event.summary,
            "status": event.status,
            "created_at": event.created_at,
            "linked_commits": event.linked_commits,
            "metadata_json": metadata_json
        })
        
        kafka_service.flush()
        logger.info(f"Processed issue event {event.event_id}")
        
    except Exception as e:
        logger.error(f"Error processing issue event: {e}")

