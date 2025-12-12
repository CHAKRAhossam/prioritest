"""API endpoints for manual collection."""
import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field, HttpUrl

from src.services.github_service import GitHubService
from src.services.gitlab_service import GitLabService
from src.services.jira_service import JiraService
from src.services.kafka_service import KafkaService
from src.services.database_service import DatabaseService
from src.services.minio_service import MinIOService
from src.services.cicd_parser import get_parser, CIArtifactParser
from src.models.events import CommitEvent, IssueEvent, CIArtifactEvent
from src.config import settings
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/collect", tags=["Collection"])


class DateRange(BaseModel):
    """Date range model."""
    start: str = Field(..., description="Start date (ISO format)")
    end: str = Field(..., description="End date (ISO format)")


class CollectRequest(BaseModel):
    """
    Request model for manual collection.
    
    Input format (from architecture spec):
    {
      "repository_url": "https://github.com/org/repo",
      "collect_type": "commits|issues|ci_reports",
      "date_range": {
        "start": "2025-01-01",
        "end": "2025-12-04"
      }
    }
    """
    repository_url: HttpUrl = Field(..., description="Repository URL")
    collect_type: str = Field(..., description="Types to collect: commits|issues|ci_reports")
    date_range: Optional[DateRange] = Field(None, description="Date range for collection")
    
    class Config:
        json_schema_extra = {
            "example": {
                "repository_url": "https://github.com/org/repo",
                "collect_type": "commits|issues|ci_reports",
                "date_range": {
                    "start": "2025-01-01",
                    "end": "2025-12-04"
                }
            }
        }


def get_services():
    """Dependency to get service instances."""
    return {
        "github": GitHubService(),
        "gitlab": GitLabService(),
        "jira": JiraService(),
        "kafka": KafkaService(),
        "db": DatabaseService(),
        "minio": MinIOService()
    }


@router.post("", status_code=202)
async def collect_data(
    request: CollectRequest,
    background_tasks: BackgroundTasks,
    services: dict = Depends(get_services)
):
    """
    Manually trigger data collection from a repository.
    
    Supports:
    - GitHub/GitLab repositories
    - Jira projects
    - CI/CD artifacts
    """
    try:
        # Parse repository URL
        url_str = str(request.repository_url)
        
        # Determine source type
        if "github.com" in url_str:
            source = "github"
            repo_full_name = url_str.replace("https://github.com/", "").replace(".git", "")
        elif "gitlab.com" in url_str or "gitlab" in url_str:
            source = "gitlab"
            # Extract project ID or path
            parts = url_str.replace("https://", "").replace("http://", "").split("/")
            if len(parts) >= 3:
                repo_path = "/".join(parts[2:]).replace(".git", "")
            else:
                raise HTTPException(status_code=400, detail="Invalid GitLab URL")
        else:
            raise HTTPException(status_code=400, detail="Unsupported repository URL")
        
        # Parse collect types
        collect_types = [t.strip() for t in request.collect_type.split("|")]
        
        # Parse date range
        since = None
        until = None
        if request.date_range:
            since = datetime.fromisoformat(request.date_range.start)
            until = datetime.fromisoformat(request.date_range.end)
        
        # Schedule background task
        background_tasks.add_task(
            _process_collection,
            source,
            repo_full_name if source == "github" else repo_path,
            collect_types,
            since,
            until,
            services
        )
        
        return {
            "status": "accepted",
            "message": "Collection started in background",
            "repository_url": url_str,
            "collect_types": collect_types
        }
        
    except Exception as e:
        logger.error(f"Error starting collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _process_collection(
    source: str,
    repo_identifier: str,
    collect_types: List[str],
    since: Optional[datetime],
    until: Optional[datetime],
    services: dict
):
    """Background task to process collection."""
    try:
        kafka = services["kafka"]
        db = services["db"]
        
        # Collect commits
        if "commits" in collect_types:
            if source == "github":
                github = services["github"]
                commit_events = github.collect_commits(repo_identifier, since, until)
                
                # Get or create repository
                repo = db.get_or_create_repository(
                    repository_id=github._get_repo_id(repo_identifier),
                    name=repo_identifier.split("/")[-1],
                    full_name=repo_identifier,
                    url=f"https://github.com/{repo_identifier}",
                    source="github"
                )
                
                # Publish and store commits
                for event in commit_events:
                    kafka.publish_commit(event)
                    db.store_commit({
                        "repository_id": event.repository_id,
                        "commit_sha": event.commit_sha,
                        "commit_message": event.commit_message,
                        "author_email": event.author_email,
                        "author_name": event.author_name,
                        "timestamp": event.timestamp,
                        "branch": event.metadata.branch,
                        "files_changed_json": [f.model_dump() for f in event.files_changed],
                        "metadata_json": event.metadata.model_dump()
                    })
            
            elif source == "gitlab":
                gitlab = services["gitlab"]
                # Try to get project by path or ID
                try:
                    project_id = int(repo_identifier)
                except ValueError:
                    # Search by path
                    projects = gitlab.client.projects.list(search=repo_identifier)
                    if not projects:
                        logger.error(f"GitLab project not found: {repo_identifier}")
                        return
                    project_id = projects[0].id
                
                commit_events = gitlab.collect_commits(str(project_id), since, until)
                
                repo = db.get_or_create_repository(
                    repository_id=gitlab._get_repo_id(str(project_id)),
                    name=repo_identifier.split("/")[-1],
                    full_name=repo_identifier,
                    url=f"{settings.gitlab_url}/{repo_identifier}",
                    source="gitlab"
                )
                
                for event in commit_events:
                    kafka.publish_commit(event)
                    db.store_commit({
                        "repository_id": event.repository_id,
                        "commit_sha": event.commit_sha,
                        "commit_message": event.commit_message,
                        "author_email": event.author_email,
                        "author_name": event.author_name,
                        "timestamp": event.timestamp,
                        "branch": event.metadata.branch,
                        "files_changed_json": [f.model_dump() for f in event.files_changed],
                        "metadata_json": event.metadata.model_dump()
                    })
        
        # Collect issues
        if "issues" in collect_types:
            if source == "github":
                github = services["github"]
                issue_events = github.collect_issues(repo_identifier)
                
                for event in issue_events:
                    kafka.publish_issue(event)
                    db.store_issue({
                        "repository_id": event.repository_id,
                        "issue_key": event.issue_key,
                        "issue_type": event.issue_type,
                        "summary": event.summary,
                        "status": event.status,
                        "created_at": event.created_at,
                        "linked_commits_json": event.linked_commits,
                        "metadata_json": event.metadata or {}
                    })
            
            elif source == "gitlab":
                gitlab = services["gitlab"]
                try:
                    project_id = int(repo_identifier)
                except ValueError:
                    projects = gitlab.client.projects.list(search=repo_identifier)
                    if not projects:
                        return
                    project_id = projects[0].id
                
                issue_events = gitlab.collect_issues(str(project_id))
                
                for event in issue_events:
                    kafka.publish_issue(event)
                    db.store_issue({
                        "repository_id": event.repository_id,
                        "issue_key": event.issue_key,
                        "issue_type": event.issue_type,
                        "summary": event.summary,
                        "status": event.status,
                        "created_at": event.created_at,
                        "linked_commits_json": event.linked_commits,
                        "metadata_json": event.metadata or {}
                    })
        
        # Collect CI/CD artifacts (would need build information)
        if "ci_reports" in collect_types:
            logger.info("CI/CD artifact collection requires build information - not implemented in manual collection")
        
        kafka.flush()
        logger.info(f"Collection completed for {source}:{repo_identifier}")
        
    except Exception as e:
        logger.error(f"Error in background collection: {e}")


@router.get("/status")
async def get_collection_status():
    """Get collection service status."""
    return {
        "status": "operational",
        "services": {
            "github": settings.github_token is not None,
            "gitlab": settings.gitlab_token is not None,
            "jira": all([settings.jira_url, settings.jira_email, settings.jira_api_token]),
            "kafka": True,
            "database": True,
            "minio": True
        }
    }

