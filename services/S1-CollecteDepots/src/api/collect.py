"""API endpoints for manual collection."""
import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query, Query
from pydantic import BaseModel, Field, HttpUrl
import requests

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
        
        # Get or create repository FIRST (before collecting commits)
        # This ensures the repository exists in the database immediately
        if source == "github":
            github = services["github"]
            repo = db.get_or_create_repository(
                repository_id=github._get_repo_id(repo_identifier),
                name=repo_identifier.split("/")[-1],
                full_name=repo_identifier,
                url=f"https://github.com/{repo_identifier}",
                source="github"
            )
        elif source == "gitlab":
            gitlab = services["gitlab"]
            try:
                project_id = int(repo_identifier)
            except ValueError:
                projects = gitlab.client.projects.list(search=repo_identifier)
                if not projects:
                    logger.error(f"GitLab project not found: {repo_identifier}")
                    return
                project_id = projects[0].id
                repo_identifier = projects[0].path_with_namespace
            
            repo = db.get_or_create_repository(
                repository_id=gitlab._get_repo_id(str(project_id)),
                name=repo_identifier.split("/")[-1],
                full_name=repo_identifier,
                url=f"https://gitlab.com/{repo_identifier}",
                source="gitlab"
            )
        
        # Collect commits
        if "commits" in collect_types:
            if source == "github":
                github = services["github"]
                commit_events = github.collect_commits(repo_identifier, since, until)
                
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
                        "files_changed": [f.model_dump() for f in event.files_changed],
                        "metadata_json": event.metadata.model_dump()
                    })
            
            elif source == "gitlab":
                gitlab = services["gitlab"]
                commit_events = gitlab.collect_commits(str(project_id) if 'project_id' in locals() else repo_identifier, since, until)
                
                for event in commit_events:
                    kafka.publish_commit(event)
                    db.store_commit({
                        "repository_id": event.repository_id,
                        "commit_sha": event.commit_sha,
                        "commit_message": event.commit_message,
                        "author_email": event.author_email,
                        "author_name": event.author_name,
                        "timestamp": event.timestamp,
                        "files_changed": [f.model_dump() for f in event.files_changed],
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
                        "linked_commits": event.linked_commits,
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
                        "linked_commits": event.linked_commits,
                        "metadata_json": event.metadata or {}
                    })
        
        # Collect CI/CD artifacts from GitHub Actions / GitLab CI
        if "ci_reports" in collect_types:
            logger.info(f"Collecting CI/CD artifacts for {source}:{repo_identifier}")
            minio = services["minio"]
            
            # Get repository_id (should be created earlier in commits collection)
            repository_id = None
            if source == "github":
                github = services["github"]
                # Get repo if not already created
                if not repo:
                    repo = db.get_or_create_repository(
                        repository_id=github._get_repo_id(repo_identifier),
                        name=repo_identifier.split("/")[-1],
                        full_name=repo_identifier,
                        url=f"https://github.com/{repo_identifier}",
                        source="github"
                    )
                repository_id = repo.id
                
                artifacts = github.collect_ci_artifacts(repo_identifier, branch="main", max_runs=10)
                
                for artifact_info in artifacts:
                    try:
                        # Download artifact from GitHub
                        headers = {"Authorization": f"token {settings.github_token}"} if settings.github_token else {}
                        artifact_response = requests.get(artifact_info['artifact_url'], headers=headers, timeout=30)
                        
                        if artifact_response.status_code == 200:
                            # Upload to MinIO
                            artifact_url = minio.upload_artifact(
                                artifact_type=artifact_info['artifact_type'],
                                repository_id=repository_id,
                                commit_sha=artifact_info['commit_sha'],
                                build_id=artifact_info['build_id'],
                                content=artifact_response.content,
                                content_type="application/xml"
                            )
                            
                            # Create and publish artifact event
                            artifact_event = CIArtifactEvent(
                                event_id=f"evt_artifact_{artifact_info['build_id']}",
                                repository_id=repository_id,
                                build_id=artifact_info['build_id'],
                                commit_sha=artifact_info['commit_sha'],
                                artifact_type=artifact_info['artifact_type'],
                                artifact_url=artifact_url,
                                timestamp=artifact_info.get('created_at', datetime.utcnow()),
                                metadata={
                                    "artifact_name": artifact_info.get('artifact_name'),
                                    "workflow_name": artifact_info.get('workflow_name'),
                                    "run_id": artifact_info.get('run_id')
                                }
                            )
                            
                            kafka.publish_artifact(artifact_event)
                            db.store_artifact({
                                "event_id": artifact_event.event_id,
                                "repository_id": artifact_event.repository_id,
                                "build_id": artifact_event.build_id,
                                "commit_sha": artifact_event.commit_sha,
                                "artifact_type": artifact_event.artifact_type,
                                "artifact_url": artifact_event.artifact_url,
                                "timestamp": artifact_event.timestamp,
                                "metadata_json": artifact_event.metadata
                            })
                            
                            logger.info(f"Processed CI artifact {artifact_info['artifact_name']} for commit {artifact_info['commit_sha'][:8]}")
                        else:
                            logger.warning(f"Failed to download artifact: HTTP {artifact_response.status_code}")
                    except Exception as e:
                        logger.error(f"Error processing artifact {artifact_info.get('artifact_name', 'unknown')}: {e}")
                        continue
            
            elif source == "gitlab":
                gitlab = services["gitlab"]
                # TODO: Implement GitLab CI artifact collection
                logger.info("GitLab CI artifact collection not yet implemented")
        
        kafka.flush()
        logger.info(f"Collection completed for {source}:{repo_identifier}")
        
    except Exception as e:
        logger.error(f"Error in background collection: {e}")


@router.get("/branches")
async def get_repository_branches(
    repository_url: str = Query(..., description="Repository URL (GitHub or GitLab)"),
    services: dict = Depends(get_services)
):
    """
    Get list of branches for a repository.
    
    Args:
        repository_url: Full repository URL (e.g., https://github.com/owner/repo)
    
    Returns:
        List of branches with name, commit_sha, and protected status
    """
    try:
        url_str = str(repository_url)
        
        # Determine source (GitHub or GitLab)
        if "github.com" in url_str:
            source = "github"
            # Extract repo full name from URL
            parts = url_str.replace("https://", "").replace("http://", "").split("/")
            if "github.com" in parts:
                idx = parts.index("github.com")
                if len(parts) > idx + 2:
                    repo_full_name = f"{parts[idx + 1]}/{parts[idx + 2]}".replace(".git", "")
                else:
                    raise HTTPException(status_code=400, detail="Invalid GitHub URL")
            else:
                raise HTTPException(status_code=400, detail="Invalid GitHub URL")
            
            github = services["github"]
            branches = github.get_branches(repo_full_name)
            
        elif "gitlab.com" in url_str or "gitlab" in url_str:
            source = "gitlab"
            # Extract project path from URL
            parts = url_str.replace("https://", "").replace("http://", "").split("/")
            if "gitlab.com" in parts or any("gitlab" in p for p in parts):
                # Find gitlab domain index
                gitlab_idx = next((i for i, p in enumerate(parts) if "gitlab" in p), None)
                if gitlab_idx is not None and len(parts) > gitlab_idx + 2:
                    project_path = "/".join(parts[gitlab_idx + 1:gitlab_idx + 3]).replace(".git", "")
                else:
                    raise HTTPException(status_code=400, detail="Invalid GitLab URL")
            else:
                raise HTTPException(status_code=400, detail="Invalid GitLab URL")
            
            gitlab = services["gitlab"]
            branches = gitlab.get_branches(project_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported repository URL. Only GitHub and GitLab are supported.")
        
        return {
            "repository_url": url_str,
            "source": source,
            "branches": branches,
            "count": len(branches)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting branches: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/repositories/{repository_id}")
async def delete_repository(
    repository_id: str,
    services: dict = Depends(get_services)
):
    """
    Delete a repository and all its associated data.
    
    Args:
        repository_id: The ID of the repository to delete
    
    Returns:
        Success message
    """
    try:
        db = services["db"]
        deleted = db.delete_repository(repository_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Repository {repository_id} not found")
        
        return {
            "message": f"Repository {repository_id} deleted successfully",
            "repository_id": repository_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting repository {repository_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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


@router.get("/repositories")
async def list_repositories(
    source: Optional[str] = Query(None, description="Filter by source (github, gitlab)"),
    services: dict = Depends(get_services)
):
    """
    List all repositories stored in the database.
    
    Args:
        source: Optional filter by source (github, gitlab)
    
    Returns:
        List of repositories with metadata
    """
    try:
        db = services["db"]
        repos = db.list_repositories(source=source)
        
        return {
            "repositories": [
                {
                    "id": repo.id,
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "url": repo.url,
                    "source": repo.source,
                    "default_branch": repo.default_branch,
                    "created_at": repo.created_at.isoformat() if repo.created_at else None,
                    "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
                    "metadata": repo.metadata_json or {}
                }
                for repo in repos
            ],
            "count": len(repos)
        }
    except Exception as e:
        logger.error(f"Error listing repositories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/repositories/{repository_id}")
async def delete_repository(
    repository_id: str,
    services: dict = Depends(get_services)
):
    """
    Delete a repository and all its associated data.
    
    Args:
        repository_id: The ID of the repository to delete
    
    Returns:
        Success message
    """
    try:
        db = services["db"]
        deleted = db.delete_repository(repository_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Repository {repository_id} not found")
        
        return {
            "message": f"Repository {repository_id} deleted successfully",
            "repository_id": repository_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting repository {repository_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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


@router.get("/branches")
async def get_repository_branches(
    repository_url: str = Query(..., description="Repository URL (GitHub or GitLab)"),
    services: dict = Depends(get_services)
):
    """
    Get list of branches for a repository.
    
    Args:
        repository_url: Full repository URL (e.g., https://github.com/owner/repo)
    
    Returns:
        List of branches with name, commit_sha, and protected status
    """
    try:
        url_str = str(repository_url)
        
        # Determine source (GitHub or GitLab)
        if "github.com" in url_str:
            source = "github"
            # Extract repo full name from URL
            parts = url_str.replace("https://", "").replace("http://", "").split("/")
            if "github.com" in parts:
                idx = parts.index("github.com")
                if len(parts) > idx + 2:
                    repo_full_name = f"{parts[idx + 1]}/{parts[idx + 2]}".replace(".git", "")
                else:
                    raise HTTPException(status_code=400, detail="Invalid GitHub URL")
            else:
                raise HTTPException(status_code=400, detail="Invalid GitHub URL")
            
            github = services["github"]
            branches = github.get_branches(repo_full_name)
            
        elif "gitlab.com" in url_str or "gitlab" in url_str:
            source = "gitlab"
            # Extract project path from URL
            parts = url_str.replace("https://", "").replace("http://", "").split("/")
            if "gitlab.com" in parts or any("gitlab" in p for p in parts):
                # Find gitlab domain index
                gitlab_idx = next((i for i, p in enumerate(parts) if "gitlab" in p), None)
                if gitlab_idx is not None and len(parts) > gitlab_idx + 2:
                    project_path = "/".join(parts[gitlab_idx + 1:gitlab_idx + 3]).replace(".git", "")
                else:
                    raise HTTPException(status_code=400, detail="Invalid GitLab URL")
            else:
                raise HTTPException(status_code=400, detail="Invalid GitLab URL")
            
            gitlab = services["gitlab"]
            branches = gitlab.get_branches(project_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported repository URL. Only GitHub and GitLab are supported.")
        
        return {
            "repository_url": url_str,
            "source": source,
            "branches": branches,
            "count": len(branches)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting branches: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/repositories/{repository_id}")
async def delete_repository(
    repository_id: str,
    services: dict = Depends(get_services)
):
    """
    Delete a repository and all its associated data.
    
    Args:
        repository_id: The ID of the repository to delete
    
    Returns:
        Success message
    """
    try:
        db = services["db"]
        deleted = db.delete_repository(repository_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Repository {repository_id} not found")
        
        return {
            "message": f"Repository {repository_id} deleted successfully",
            "repository_id": repository_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting repository {repository_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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


@router.get("/repositories")
async def list_repositories(
    source: Optional[str] = Query(None, description="Filter by source (github, gitlab)"),
    services: dict = Depends(get_services)
):
    """
    List all repositories stored in the database.
    
    Args:
        source: Optional filter by source (github, gitlab)
    
    Returns:
        List of repositories with metadata
    """
    try:
        db = services["db"]
        repos = db.list_repositories(source=source)
        
        return {
            "repositories": [
                {
                    "id": repo.id,
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "url": repo.url,
                    "source": repo.source,
                    "default_branch": repo.default_branch,
                    "created_at": repo.created_at.isoformat() if repo.created_at else None,
                    "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
                    "metadata": repo.metadata_json or {}
                }
                for repo in repos
            ],
            "count": len(repos)
        }
    except Exception as e:
        logger.error(f"Error listing repositories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/repositories/{repository_id}")
async def delete_repository(
    repository_id: str,
    services: dict = Depends(get_services)
):
    """
    Delete a repository and all its associated data.
    
    Args:
        repository_id: The ID of the repository to delete
    
    Returns:
        Success message
    """
    try:
        db = services["db"]
        deleted = db.delete_repository(repository_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Repository {repository_id} not found")
        
        return {
            "message": f"Repository {repository_id} deleted successfully",
            "repository_id": repository_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting repository {repository_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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

