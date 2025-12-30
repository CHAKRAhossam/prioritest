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
    def get_branches(self, repo_full_name: str) -> List[Dict[str, Any]]:
        """
        Get list of branches for a repository.
        
        Args:
            repo_full_name: Repository full name (owner/repo)
        
        Returns:
            List of branch information with name, commit_sha, and protected status
        """
        if not self.client:
            logger.error("GitHub client not initialized")
            return []
        
        try:
            repo = self.client.get_repo(repo_full_name)
            branches = repo.get_branches()
            
            branch_list = []
            for branch in branches:
                branch_list.append({
                    'name': branch.name,
                    'commit_sha': branch.commit.sha,
                    'protected': branch.protected if hasattr(branch, 'protected') else False
                })
            
            # Sort: main/master first, then alphabetically
            def sort_key(b):
                name = b['name'].lower()
                if name == 'main' or name == 'master':
                    return (0, name)
                return (1, name)
            
            branch_list.sort(key=sort_key)
            logger.info(f"Retrieved {len(branch_list)} branches for {repo_full_name}")
            return branch_list
            
        except GithubException as e:
            logger.error(f"GitHub API error getting branches: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting branches: {e}")
            return []
    
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
            logger.info(f"Fetching commits from {repo_full_name} on branch {branch}")
            
            # Get commits - PyGithub doesn't accept None for since/until, must omit or use undefined
            from github.GithubObject import NotSet
            commit_params = {"sha": branch}
            if since is not None:
                commit_params["since"] = since
            if until is not None:
                commit_params["until"] = until
            
            try:
                commits = repo.get_commits(**commit_params)
                logger.info(f"Successfully retrieved commits iterator for {repo_full_name} on branch {branch}")
            except GithubException as commit_error:
                logger.error(f"GitHub API error getting commits from {repo_full_name} (branch: {branch}): Status={commit_error.status}, Data={commit_error.data}")
                # Try without branch specification
                try:
                    logger.info(f"Retrying without branch specification for {repo_full_name}")
                    retry_params = {}
                    if since is not None:
                        retry_params["since"] = since
                    if until is not None:
                        retry_params["until"] = until
                    commits = repo.get_commits(**retry_params)
                    logger.info(f"Successfully retrieved commits iterator without branch for {repo_full_name}")
                except GithubException as retry_error:
                    logger.error(f"GitHub API error getting commits without branch for {repo_full_name}: Status={retry_error.status}, Data={retry_error.data}")
                    return []
                except Exception as retry_error:
                    logger.error(f"Unexpected error getting commits without branch for {repo_full_name}: {type(retry_error).__name__}: {str(retry_error)}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    return []
            except Exception as commit_error:
                logger.error(f"Unexpected error getting commits from {repo_full_name} (branch: {branch}): {type(commit_error).__name__}: {str(commit_error)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                # Try without branch specification
                try:
                    logger.info(f"Retrying without branch specification for {repo_full_name}")
                    retry_params = {}
                    if since is not None:
                        retry_params["since"] = since
                    if until is not None:
                        retry_params["until"] = until
                    commits = repo.get_commits(**retry_params)
                    logger.info(f"Successfully retrieved commits iterator without branch for {repo_full_name}")
                except Exception as retry_error:
                    logger.error(f"Error getting commits without branch for {repo_full_name}: {type(retry_error).__name__}: {str(retry_error)}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    return []
            
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
                                "api_url": commit.url,
                                "repository_url": f"https://github.com/{repo_full_name}.git"  # Add full repo URL for S2
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
            logger.error(f"GitHub API error collecting commits from {repo_full_name}: {e.status} - {e.data}")
            return []
        except Exception as e:
            import traceback
            logger.error(f"Error collecting commits from {repo_full_name}: {type(e).__name__}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
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
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def collect_ci_artifacts(
        self,
        repo_full_name: str,
        branch: str = "main",
        max_runs: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Collect CI/CD artifacts (JaCoCo, PIT reports) from GitHub Actions.
        
        Args:
            repo_full_name: Repository full name (owner/repo)
            branch: Branch to collect artifacts from
            max_runs: Maximum number of workflow runs to check
            
        Returns:
            List of artifact information dictionaries
        """
        if not self.client:
            logger.warning("GitHub client not initialized - cannot collect CI artifacts")
            return []
        
        artifacts = []
        try:
            repo = self.client.get_repo(repo_full_name)
            
            # Get workflow runs for the branch
            workflows = repo.get_workflows()
            for workflow in workflows[:5]:  # Check first 5 workflows
                try:
                    runs = workflow.get_runs(branch=branch, per_page=min(max_runs, 10))
                    
                    for run in runs:
                        if run.status != "completed" or run.conclusion != "success":
                            continue
                        
                        # Get artifacts for this run
                        try:
                            run_artifacts = run.get_artifacts()
                            
                            for artifact in run_artifacts:
                                artifact_name = artifact.name.lower()
                                
                                # Check if it's a coverage artifact
                                if any(keyword in artifact_name for keyword in ['jacoco', 'coverage', 'pit', 'mutation']):
                                    # Download artifact
                                    try:
                                        artifact_url = artifact.archive_download_url
                                        
                                        artifacts.append({
                                            'artifact_type': 'jacoco' if 'jacoco' in artifact_name else ('pit' if 'pit' in artifact_name else 'coverage'),
                                            'build_id': f"gha_{run.id}",
                                            'commit_sha': run.head_sha,
                                            'artifact_url': artifact_url,
                                            'artifact_name': artifact.name,
                                            'workflow_name': workflow.name,
                                            'run_id': run.id,
                                            'created_at': run.created_at
                                        })
                                        logger.info(f"Found CI artifact: {artifact.name} for commit {run.head_sha[:8]}")
                                    except Exception as e:
                                        logger.warning(f"Could not get artifact download URL: {e}")
                                        continue
                        except Exception as e:
                            logger.warning(f"Could not get artifacts for run {run.id}: {e}")
                            continue
                            
                except Exception as e:
                    logger.warning(f"Error processing workflow {workflow.name}: {e}")
                    continue
            
            logger.info(f"Collected {len(artifacts)} CI artifacts from {repo_full_name}")
            return artifacts
            
        except GithubException as e:
            logger.warning(f"GitHub API error collecting CI artifacts: {e}")
            return []
        except Exception as e:
            logger.warning(f"Error collecting CI artifacts: {e}")
            return []

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
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def collect_ci_artifacts(
        self,
        repo_full_name: str,
        branch: str = "main",
        max_runs: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Collect CI/CD artifacts (JaCoCo, PIT reports) from GitHub Actions.
        
        Args:
            repo_full_name: Repository full name (owner/repo)
            branch: Branch to collect artifacts from
            max_runs: Maximum number of workflow runs to check
            
        Returns:
            List of artifact information dictionaries
        """
        if not self.client:
            logger.warning("GitHub client not initialized - cannot collect CI artifacts")
            return []
        
        artifacts = []
        try:
            repo = self.client.get_repo(repo_full_name)
            
            # Get workflow runs for the branch
            workflows = repo.get_workflows()
            for workflow in workflows[:5]:  # Check first 5 workflows
                try:
                    runs = workflow.get_runs(branch=branch, per_page=min(max_runs, 10))
                    
                    for run in runs:
                        if run.status != "completed" or run.conclusion != "success":
                            continue
                        
                        # Get artifacts for this run
                        try:
                            run_artifacts = run.get_artifacts()
                            
                            for artifact in run_artifacts:
                                artifact_name = artifact.name.lower()
                                
                                # Check if it's a coverage artifact
                                if any(keyword in artifact_name for keyword in ['jacoco', 'coverage', 'pit', 'mutation']):
                                    # Download artifact
                                    try:
                                        artifact_url = artifact.archive_download_url
                                        
                                        artifacts.append({
                                            'artifact_type': 'jacoco' if 'jacoco' in artifact_name else ('pit' if 'pit' in artifact_name else 'coverage'),
                                            'build_id': f"gha_{run.id}",
                                            'commit_sha': run.head_sha,
                                            'artifact_url': artifact_url,
                                            'artifact_name': artifact.name,
                                            'workflow_name': workflow.name,
                                            'run_id': run.id,
                                            'created_at': run.created_at
                                        })
                                        logger.info(f"Found CI artifact: {artifact.name} for commit {run.head_sha[:8]}")
                                    except Exception as e:
                                        logger.warning(f"Could not get artifact download URL: {e}")
                                        continue
                        except Exception as e:
                            logger.warning(f"Could not get artifacts for run {run.id}: {e}")
                            continue
                            
                except Exception as e:
                    logger.warning(f"Error processing workflow {workflow.name}: {e}")
                    continue
            
            logger.info(f"Collected {len(artifacts)} CI artifacts from {repo_full_name}")
            return artifacts
            
        except GithubException as e:
            logger.warning(f"GitHub API error collecting CI artifacts: {e}")
            return []
        except Exception as e:
            logger.warning(f"Error collecting CI artifacts: {e}")
            return []

