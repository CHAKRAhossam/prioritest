"""
Pydantic models for webhook payloads from GitHub, GitLab, and Jira.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class GitHubCommit(BaseModel):
    """GitHub commit information from push webhook."""
    id: str = Field(..., description="Commit SHA")
    message: str = Field(default="", description="Commit message")
    timestamp: Optional[str] = Field(None, description="Commit timestamp")
    author: Optional[Dict[str, str]] = Field(default=None, description="Author info")
    url: Optional[str] = Field(None, description="Commit URL")
    added: Optional[List[str]] = Field(default=[], description="Added files")
    removed: Optional[List[str]] = Field(default=[], description="Removed files")
    modified: Optional[List[str]] = Field(default=[], description="Modified files")


class GitHubRepository(BaseModel):
    """GitHub repository information."""
    id: int = Field(..., description="Repository ID")
    name: str = Field(..., description="Repository name")
    full_name: str = Field(default="", description="Full repository name (owner/repo)")
    html_url: Optional[str] = Field(None, description="Repository URL")
    clone_url: Optional[str] = Field(None, description="Clone URL")
    default_branch: Optional[str] = Field(default="main", description="Default branch")


class GitHubIssue(BaseModel):
    """GitHub issue information."""
    number: int = Field(..., description="Issue number")
    title: str = Field(default="", description="Issue title")
    state: str = Field(default="open", description="Issue state")
    body: Optional[str] = Field(None, description="Issue body")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    labels: Optional[List[Dict[str, Any]]] = Field(default=[], description="Issue labels")


class GitHubPullRequest(BaseModel):
    """GitHub pull request information."""
    number: int = Field(..., description="PR number")
    title: str = Field(default="", description="PR title")
    state: str = Field(default="open", description="PR state")
    head: Optional[Dict[str, Any]] = Field(None, description="Head branch info")
    base: Optional[Dict[str, Any]] = Field(None, description="Base branch info")


class GitHubWebhookPayload(BaseModel):
    """GitHub webhook payload model."""
    ref: Optional[str] = Field(None, description="Git ref (for push events)")
    before: Optional[str] = Field(None, description="Previous commit SHA")
    after: Optional[str] = Field(None, description="Current commit SHA")
    repository: Optional[GitHubRepository] = Field(None, description="Repository info")
    commits: Optional[List[GitHubCommit]] = Field(default=[], description="Commits (for push)")
    head_commit: Optional[GitHubCommit] = Field(None, description="Head commit")
    action: Optional[str] = Field(None, description="Action type (for issues/PR)")
    issue: Optional[GitHubIssue] = Field(None, description="Issue info")
    pull_request: Optional[GitHubPullRequest] = Field(None, description="Pull request info")
    sender: Optional[Dict[str, Any]] = Field(None, description="Sender info")

    class Config:
        extra = "allow"


class GitLabProject(BaseModel):
    """GitLab project information."""
    id: int = Field(..., description="Project ID")
    name: str = Field(..., description="Project name")
    path_with_namespace: str = Field(default="", description="Full project path")
    web_url: Optional[str] = Field(None, description="Project URL")
    default_branch: Optional[str] = Field(default="main", description="Default branch")


class GitLabCommit(BaseModel):
    """GitLab commit information."""
    id: str = Field(..., description="Commit SHA")
    message: str = Field(default="", description="Commit message")
    timestamp: Optional[str] = Field(None, description="Commit timestamp")
    author: Optional[Dict[str, str]] = Field(None, description="Author info")
    url: Optional[str] = Field(None, description="Commit URL")
    added: Optional[List[str]] = Field(default=[], description="Added files")
    removed: Optional[List[str]] = Field(default=[], description="Removed files")
    modified: Optional[List[str]] = Field(default=[], description="Modified files")


class GitLabObjectAttributes(BaseModel):
    """GitLab object attributes for issues/MRs."""
    id: Optional[int] = Field(None, description="Object ID")
    iid: Optional[int] = Field(None, description="Internal ID")
    title: Optional[str] = Field(None, description="Title")
    state: Optional[str] = Field(None, description="State")
    source_branch: Optional[str] = Field(None, description="Source branch (MR)")
    target_branch: Optional[str] = Field(None, description="Target branch (MR)")
    last_commit: Optional[GitLabCommit] = Field(None, description="Last commit")
    action: Optional[str] = Field(None, description="Action type")


class GitLabWebhookPayload(BaseModel):
    """GitLab webhook payload model."""
    object_kind: Optional[str] = Field(None, description="Event type")
    event_type: Optional[str] = Field(None, description="Event type")
    ref: Optional[str] = Field(None, description="Git ref")
    before: Optional[str] = Field(None, description="Previous commit SHA")
    after: Optional[str] = Field(None, description="Current commit SHA")
    project: Optional[GitLabProject] = Field(None, description="Project info")
    commits: Optional[List[GitLabCommit]] = Field(default=[], description="Commits")
    object_attributes: Optional[GitLabObjectAttributes] = Field(None, description="Object attributes")
    user: Optional[Dict[str, Any]] = Field(None, description="User info")

    class Config:
        extra = "allow"


class JiraIssue(BaseModel):
    """Jira issue information."""
    key: str = Field(..., description="Issue key (e.g., MTP-77)")
    id: Optional[str] = Field(None, description="Issue ID")
    self: Optional[str] = Field(None, description="Issue URL")
    fields: Optional[Dict[str, Any]] = Field(None, description="Issue fields")


class JiraWebhookPayload(BaseModel):
    """Jira webhook payload model."""
    webhookEvent: Optional[str] = Field(None, alias="webhook_event", description="Webhook event type")
    issue_event_type_name: Optional[str] = Field(None, description="Issue event type")
    timestamp: Optional[int] = Field(None, description="Event timestamp")
    issue: Optional[JiraIssue] = Field(None, description="Issue info")
    user: Optional[Dict[str, Any]] = Field(None, description="User info")
    changelog: Optional[Dict[str, Any]] = Field(None, description="Change log")

    class Config:
        extra = "allow"
        populate_by_name = True