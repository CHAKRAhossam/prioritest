"""GitLab API integration service."""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import gitlab
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import settings
from src.models.events import CommitEvent, IssueEvent, FileChange, Metadata

logger = logging.getLogger(__name__)


class GitLabService:
    """Service for GitLab API operations."""
    
    def __init__(self):
        """Initialize GitLab client."""
        if not settings.gitlab_token:
            logger.warning("GitLab token not configured")
            self.client = None
        else:
            self.client = gitlab.Gitlab(settings.gitlab_url, private_token=settings.gitlab_token)
            try:
                self.client.auth()
            except Exception as e:
                logger.error(f"GitLab authentication failed: {e}")
                self.client = None
    
    def _get_repo_id(self, project_id: str) -> str:
        """Generate repository ID from project ID."""
        return f"gitlab_{project_id}"
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def collect_commits(
        self,
        project_id: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        branch: str = "main"
    ) -> List[CommitEvent]:
        """
        Collect commits from a GitLab repository.
        
        Args:
            project_id: GitLab project ID
            since: Start date for commit collection
            until: End date for commit collection
            branch: Branch to collect commits from
            
        Returns:
            List of CommitEvent objects
        """
        if not self.client:
            logger.error("GitLab client not initialized")
            return []
        
        events = []
        try:
            project = self.client.projects.get(project_id)
            repository_id = self._get_repo_id(str(project_id))
            
            # Get commits
            commits = project.commits.list(
                ref_name=branch,
                since=since.isoformat() if since else None,
                until=until.isoformat() if until else None,
                all=True
            )
            
            for commit in commits:
                try:
                    # Get commit details
                    commit_detail = project.commits.get(commit.id)
                    
                    files_changed = []
                    # Get file changes from diff
                    try:
                        for change in commit_detail.diff():
                            files_changed.append(FileChange(
                                path=change.get("new_path") or change.get("old_path", ""),
                                status=change.get("new_file") and "added" or (change.get("deleted_file") and "deleted" or "modified"),
                                additions=change.get("diff", "").count("\n+") - 1,  # Approximate
                                deletions=change.get("diff", "").count("\n-") - 1
                            ))
                    except Exception as e:
                        logger.warning(f"Could not get file changes for commit {commit.id}: {e}")
                    
                    event = CommitEvent(
                        event_id=f"evt_gitlab_{commit.id}",
                        repository_id=repository_id,
                        commit_sha=commit.id,
                        commit_message=commit.message,
                        author_email=commit.author_email,
                        author_name=commit.author_name,
                        timestamp=commit.created_at,
                        files_changed=files_changed,
                        metadata=Metadata(
                            source="gitlab",
                            branch=branch,
                            extra={
                                "web_url": commit.web_url
                            }
                        )
                    )
                    events.append(event)
                    
                except Exception as e:
                    logger.error(f"Error processing commit {commit.id}: {e}")
                    continue
            
            logger.info(f"Collected {len(events)} commits from project {project_id}")
            return events
            
        except Exception as e:
            logger.error(f"Error collecting commits: {e}")
            return []
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def collect_issues(
        self,
        project_id: str,
        state: str = "all"
    ) -> List[IssueEvent]:
        """
        Collect issues from a GitLab repository.
        
        Args:
            project_id: GitLab project ID
            state: Issue state (all, opened, closed)
            
        Returns:
            List of IssueEvent objects
        """
        if not self.client:
            logger.error("GitLab client not initialized")
            return []
        
        events = []
        try:
            project = self.client.projects.get(project_id)
            repository_id = self._get_repo_id(str(project_id))
            
            issues = project.issues.list(state=state, all=True)
            
            for issue in issues:
                try:
                    # Get linked commits from issue description
                    linked_commits = []
                    if issue.description:
                        import re
                        commits = re.findall(r'\b[0-9a-f]{7,40}\b', issue.description)
                        linked_commits.extend(commits)
                    
                    event = IssueEvent(
                        event_id=f"evt_gitlab_issue_{issue.iid}",
                        repository_id=repository_id,
                        issue_key=f"GL-{issue.iid}",
                        issue_type=issue.labels[0] if issue.labels else "Task",
                        summary=issue.title,
                        status=issue.state.capitalize(),
                        created_at=issue.created_at,
                        linked_commits=linked_commits,
                        metadata={
                            "web_url": issue.web_url,
                            "labels": issue.labels,
                            "assignees": [assignee["username"] for assignee in issue.assignees] if issue.assignees else []
                        }
                    )
                    events.append(event)
                    
                except Exception as e:
                    logger.error(f"Error processing issue {issue.iid}: {e}")
                    continue
            
            logger.info(f"Collected {len(events)} issues from project {project_id}")
            return events
            
        except Exception as e:
            logger.error(f"Error collecting issues: {e}")
            return []
    
    def parse_webhook(self, payload: Dict[str, Any], event_type: str) -> Optional[CommitEvent]:
        """
        Parse GitLab webhook payload.
        
        Args:
            payload: Webhook JSON payload
            event_type: Webhook event type (push, merge_request, issue)
            
        Returns:
            CommitEvent or None
        """
        try:
            if event_type == "push":
                project = payload.get("project", {})
                commits = payload.get("commits", [])
                
                if not commits:
                    return None
                
                # Process the head commit
                commit = commits[-1] if commits else {}
                
                repository_id = self._get_repo_id(str(project.get("id", "")))
                
                files_changed = []
                for file in commit.get("added", []):
                    files_changed.append(FileChange(path=file, status="added"))
                for file in commit.get("modified", []):
                    files_changed.append(FileChange(path=file, status="modified"))
                for file in commit.get("removed", []):
                    files_changed.append(FileChange(path=file, status="deleted"))
                
                return CommitEvent(
                    event_id=f"evt_webhook_{commit.get('id', '')}",
                    repository_id=repository_id,
                    commit_sha=commit.get("id", ""),
                    commit_message=commit.get("message", ""),
                    author_email=commit.get("author", {}).get("email", ""),
                    author_name=commit.get("author", {}).get("name", ""),
                    timestamp=datetime.fromisoformat(commit.get("timestamp", "").replace("Z", "+00:00")),
                    files_changed=files_changed,
                    metadata=Metadata(
                        source="gitlab",
                        branch=payload.get("ref", "").replace("refs/heads/", ""),
                        extra={
                            "user_name": payload.get("user_name", ""),
                            "project": project.get("name", "")
                        }
                    )
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing GitLab webhook: {e}")
            return None

