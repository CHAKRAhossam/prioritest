"""GitHub API integration service."""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from github import Github
from github.GithubException import GithubException
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import settings
from src.models.events import CommitEvent, IssueEvent, FileChange, Metadata

logger = logging.getLogger(__name__)


class GitHubService:
    """Service for GitHub API operations."""
    
    def __init__(self):
        """Initialize GitHub client."""
        if not settings.github_token:
            logger.warning("GitHub token not configured")
            self.client = None
        else:
            self.client = Github(settings.github_token)
    
    def _get_repo_id(self, repo_full_name: str) -> str:
        """Generate repository ID from full name."""
        return f"github_{repo_full_name.replace('/', '_')}"
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def collect_commits(
        self,
        repo_full_name: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        branch: str = "main"
    ) -> List[CommitEvent]:
        """
        Collect commits from a GitHub repository.
        
        Args:
            repo_full_name: Repository full name (owner/repo)
            since: Start date for commit collection
            until: End date for commit collection
            branch: Branch to collect commits from
            
        Returns:
            List of CommitEvent objects
        """
        if not self.client:
            logger.error("GitHub client not initialized")
            return []
        
        events = []
        try:
            repo = self.client.get_repo(repo_full_name)
            repository_id = self._get_repo_id(repo_full_name)
            
            # Get commits
            commits = repo.get_commits(sha=branch, since=since, until=until)
            
            for commit in commits:
                try:
                    # Get commit details
                    commit_obj = commit.commit
                    files_changed = []
                    
                    # Get file changes
                    try:
                        for file in commit.files:
                            files_changed.append(FileChange(
                                path=file.filename,
                                status=file.status,
                                additions=file.additions,
                                deletions=file.deletions
                            ))
                    except Exception as e:
                        logger.warning(f"Could not get file changes for commit {commit.sha}: {e}")
                    
                    event = CommitEvent(
                        event_id=f"evt_github_{commit.sha}",
                        repository_id=repository_id,
                        commit_sha=commit.sha,
                        commit_message=commit_obj.message,
                        author_email=commit_obj.author.email if commit_obj.author else "unknown",
                        author_name=commit_obj.author.name if commit_obj.author else "unknown",
                        timestamp=commit_obj.author.date if commit_obj.author else datetime.utcnow(),
                        files_changed=files_changed,
                        metadata=Metadata(
                            source="github",
                            branch=branch,
                            extra={
                                "url": commit.html_url,
                                "api_url": commit.url
                            }
                        )
                    )
                    events.append(event)
                    
                except Exception as e:
                    logger.error(f"Error processing commit {commit.sha}: {e}")
                    continue
            
            logger.info(f"Collected {len(events)} commits from {repo_full_name}")
            return events
            
        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error collecting commits: {e}")
            return []
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def collect_issues(
        self,
        repo_full_name: str,
        state: str = "all"
    ) -> List[IssueEvent]:
        """
        Collect issues from a GitHub repository.
        
        Args:
            repo_full_name: Repository full name (owner/repo)
            state: Issue state (all, open, closed)
            
        Returns:
            List of IssueEvent objects
        """
        if not self.client:
            logger.error("GitHub client not initialized")
            return []
        
        events = []
        try:
            repo = self.client.get_repo(repo_full_name)
            repository_id = self._get_repo_id(repo_full_name)
            
            issues = repo.get_issues(state=state)
            
            for issue in issues:
                try:
                    # Get linked commits from issue body/comments
                    linked_commits = []
                    if issue.body:
                        # Simple regex to find commit SHAs (7+ hex chars)
                        import re
                        commits = re.findall(r'\b[0-9a-f]{7,40}\b', issue.body)
                        linked_commits.extend(commits)
                    
                    event = IssueEvent(
                        event_id=f"evt_github_issue_{issue.number}",
                        repository_id=repository_id,
                        issue_key=f"GH-{issue.number}",
                        issue_type="Bug" if "bug" in issue.labels or any("bug" in str(l).lower() for l in issue.labels) else "Feature",
                        summary=issue.title,
                        status="Open" if issue.state == "open" else "Closed",
                        created_at=issue.created_at,
                        linked_commits=linked_commits,
                        metadata={
                            "url": issue.html_url,
                            "labels": [label.name for label in issue.labels],
                            "assignees": [assignee.login for assignee in issue.assignees]
                        }
                    )
                    events.append(event)
                    
                except Exception as e:
                    logger.error(f"Error processing issue {issue.number}: {e}")
                    continue
            
            logger.info(f"Collected {len(events)} issues from {repo_full_name}")
            return events
            
        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error collecting issues: {e}")
            return []
    
    def parse_webhook(self, payload: Dict[str, Any], event_type: str) -> Optional[CommitEvent]:
        """
        Parse GitHub webhook payload.
        
        Args:
            payload: Webhook JSON payload
            event_type: Webhook event type (push, pull_request, issues)
            
        Returns:
            CommitEvent or None
        """
        try:
            if event_type == "push":
                repo = payload.get("repository", {})
                commits = payload.get("commits", [])
                
                if not commits:
                    return None
                
                # Process the head commit
                commit = commits[-1] if commits else payload.get("head_commit", {})
                
                repository_id = self._get_repo_id(repo.get("full_name", ""))
                
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
                    timestamp=datetime.fromisoformat(commit.get("timestamp", datetime.utcnow().isoformat()).replace("Z", "+00:00")),
                    files_changed=files_changed,
                    metadata=Metadata(
                        source="github",
                        branch=payload.get("ref", "").replace("refs/heads/", ""),
                        extra={
                            "pusher": payload.get("pusher", {}).get("name", ""),
                            "compare": payload.get("compare", "")
                        }
                    )
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing GitHub webhook: {e}")
            return None

