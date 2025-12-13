"""Pydantic models for webhook payloads."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ============================================================================
# GitHub Webhook Models
# ============================================================================

class GitHubUser(BaseModel):
    """GitHub user model."""
    name: str
    email: str
    username: Optional[str] = None


class GitHubCommit(BaseModel):
    """GitHub commit model."""
    id: str
    tree_id: Optional[str] = None
    message: str
    timestamp: str
    url: Optional[str] = None
    author: GitHubUser
    committer: Optional[GitHubUser] = None
    added: List[str] = []
    removed: List[str] = []
    modified: List[str] = []


class GitHubRepository(BaseModel):
    """GitHub repository model."""
    id: int
    name: str
    full_name: str
    url: Optional[str] = None
    description: Optional[str] = None


class GitHubPusher(BaseModel):
    """GitHub pusher model."""
    name: str
    email: str


class GitHubWebhookPayload(BaseModel):
    """GitHub webhook payload model."""
    ref: str = Field(..., description="Git ref that was pushed (e.g., refs/heads/main)")
    before: Optional[str] = Field(None, description="SHA before push")
    after: Optional[str] = Field(None, description="SHA after push")
    repository: GitHubRepository
    pusher: Optional[GitHubPusher] = None
    commits: List[GitHubCommit] = Field(default_factory=list, description="List of commits in the push")

    class Config:
        json_schema_extra = {
            "example": {
                "ref": "refs/heads/main",
                "before": "0000000000000000000000000000000000000000",
                "after": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
                "repository": {
                    "id": 123456789,
                    "name": "my-awesome-project",
                    "full_name": "monequipe/my-awesome-project",
                    "url": "https://github.com/monequipe/my-awesome-project",
                    "description": "Un projet incroyable"
                },
                "pusher": {
                    "name": "jean-dupont",
                    "email": "jean.dupont@example.com"
                },
                "commits": [
                    {
                        "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
                        "message": "feat: Ajout de la fonctionnalité OAuth2",
                        "timestamp": "2025-12-13T14:30:00+01:00",
                        "url": "https://github.com/monequipe/my-awesome-project/commit/a1b2c3d4",
                        "author": {
                            "name": "Jean Dupont",
                            "email": "jean.dupont@example.com",
                            "username": "jean-dupont"
                        },
                        "committer": {
                            "name": "Jean Dupont",
                            "email": "jean.dupont@example.com"
                        },
                        "added": ["src/main/java/com/example/auth/OAuth2Service.java"],
                        "removed": [],
                        "modified": ["pom.xml"]
                    }
                ]
            }
        }


# ============================================================================
# GitLab Webhook Models
# ============================================================================

class GitLabUser(BaseModel):
    """GitLab user model."""
    name: str
    email: str


class GitLabCommit(BaseModel):
    """GitLab commit model."""
    id: str
    message: str
    title: Optional[str] = None
    timestamp: str
    url: Optional[str] = None
    author: GitLabUser
    added: List[str] = []
    modified: List[str] = []
    removed: List[str] = []


class GitLabProject(BaseModel):
    """GitLab project model."""
    id: int
    name: str
    description: Optional[str] = None
    web_url: Optional[str] = None
    path_with_namespace: str


class GitLabWebhookPayload(BaseModel):
    """GitLab webhook payload model."""
    object_kind: str = Field(..., description="Type of event (push, merge_request, issue)")
    event_name: Optional[str] = None
    before: Optional[str] = None
    after: Optional[str] = None
    ref: str = Field(..., description="Git ref (e.g., refs/heads/develop)")
    checkout_sha: Optional[str] = None
    project: GitLabProject
    commits: List[GitLabCommit] = Field(default_factory=list)
    total_commits_count: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "object_kind": "push",
                "event_name": "push",
                "before": "0000000000000000000000000000000000000000",
                "after": "c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3",
                "ref": "refs/heads/develop",
                "checkout_sha": "c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3",
                "project": {
                    "id": 987654321,
                    "name": "Application Mobile",
                    "description": "Application mobile React Native",
                    "web_url": "https://gitlab.com/monentreprise/app-mobile",
                    "path_with_namespace": "monentreprise/app-mobile"
                },
                "commits": [
                    {
                        "id": "c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3",
                        "message": "refactor: Optimisation des performances",
                        "title": "refactor: Optimisation",
                        "timestamp": "2025-12-13T15:00:00+01:00",
                        "url": "https://gitlab.com/monentreprise/app-mobile/-/commit/c4d5e6f7",
                        "author": {
                            "name": "Marie Martin",
                            "email": "marie.martin@example.com"
                        },
                        "added": ["src/components/HomeScreen/OptimizedList.tsx"],
                        "modified": ["src/components/HomeScreen/index.tsx"],
                        "removed": []
                    }
                ],
                "total_commits_count": 1
            }
        }


# ============================================================================
# Jira Webhook Models
# ============================================================================

class JiraUser(BaseModel):
    """Jira user model."""
    accountId: Optional[str] = None
    emailAddress: Optional[str] = None
    displayName: str


class JiraIssueType(BaseModel):
    """Jira issue type model."""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    iconUrl: Optional[str] = None
    subtask: Optional[bool] = False


class JiraProject(BaseModel):
    """Jira project model."""
    id: Optional[str] = None
    key: str
    name: str


class JiraPriority(BaseModel):
    """Jira priority model."""
    name: str
    id: Optional[str] = None


class JiraStatus(BaseModel):
    """Jira status model."""
    name: str
    id: Optional[str] = None
    description: Optional[str] = None
    iconUrl: Optional[str] = None


class JiraIssueFields(BaseModel):
    """Jira issue fields model."""
    summary: str
    description: Optional[str] = None
    issuetype: JiraIssueType
    project: JiraProject
    priority: Optional[JiraPriority] = None
    status: JiraStatus
    created: str
    updated: Optional[str] = None
    reporter: Optional[JiraUser] = None
    assignee: Optional[JiraUser] = None
    labels: List[str] = []


class JiraIssue(BaseModel):
    """Jira issue model."""
    id: Optional[str] = None
    key: str
    fields: JiraIssueFields


class JiraWebhookPayload(BaseModel):
    """Jira webhook payload model."""
    timestamp: Optional[int] = None
    webhookEvent: str = Field(..., description="Event type (e.g., jira:issue_created)")
    issue_event_type_name: Optional[str] = None
    user: Optional[JiraUser] = None
    issue: JiraIssue

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": 1702472400000,
                "webhookEvent": "jira:issue_created",
                "issue_event_type_name": "issue_created",
                "user": {
                    "accountId": "123abc456def",
                    "emailAddress": "product.owner@example.com",
                    "displayName": "Sophie Durand"
                },
                "issue": {
                    "id": "10001",
                    "key": "MOBILE-456",
                    "fields": {
                        "summary": "Bug critique: Crash de l'application",
                        "description": "L'application crash au démarrage",
                        "issuetype": {
                            "id": "1",
                            "name": "Bug",
                            "subtask": False
                        },
                        "project": {
                            "id": "10000",
                            "key": "MOBILE",
                            "name": "Application Mobile"
                        },
                        "priority": {
                            "name": "Critical",
                            "id": "1"
                        },
                        "status": {
                            "name": "Open",
                            "id": "1"
                        },
                        "created": "2025-12-13T15:30:00.000+0100",
                        "updated": "2025-12-13T15:30:00.000+0100",
                        "reporter": {
                            "displayName": "Sophie Durand",
                            "emailAddress": "product.owner@example.com"
                        },
                        "assignee": {
                            "displayName": "Marie Martin",
                            "emailAddress": "marie.martin@example.com"
                        },
                        "labels": ["urgent", "android", "crash"]
                    }
                }
            }
        }

