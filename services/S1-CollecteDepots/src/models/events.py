"""
Event models aligned with architecture specifications.

These models match the JSON schemas defined in ARCHITECTURE_COMPLETE.md
for Service 1 (CollecteDepots).
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class FileChange(BaseModel):
    """Model for file changes in a commit."""
    path: str = Field(..., description="File path")
    status: str = Field(..., description="File status: modified|added|deleted|renamed")
    additions: Optional[int] = Field(None, description="Number of lines added")
    deletions: Optional[int] = Field(None, description="Number of lines deleted")
    
    class Config:
        json_schema_extra = {
            "example": {
                "path": "src/UserService.java",
                "status": "modified",
                "additions": 10,
                "deletions": 5
            }
        }


class Metadata(BaseModel):
    """Metadata for events."""
    source: str = Field(..., description="Source: github|gitlab|jira")
    branch: Optional[str] = Field(None, description="Branch name")
    extra: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source": "github",
                "branch": "main"
            }
        }


class CommitEvent(BaseModel):
    """
    Commit event model matching architecture specification.
    
    Output format for Kafka topic: repository.commits
    """
    event_id: str = Field(..., description="Unique event identifier")
    repository_id: str = Field(..., description="Repository identifier")
    commit_sha: str = Field(..., description="Commit SHA")
    commit_message: str = Field(..., description="Commit message")
    author_email: str = Field(..., description="Author email")
    author_name: str = Field(..., description="Author name")
    timestamp: datetime = Field(..., description="Commit timestamp")
    files_changed: List[FileChange] = Field(default_factory=list, description="List of changed files")
    metadata: Metadata = Field(..., description="Event metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "evt_123",
                "repository_id": "repo_12345",
                "commit_sha": "abc123",
                "commit_message": "Fix bug in UserService",
                "author_email": "developer@example.com",
                "author_name": "John Doe",
                "timestamp": "2025-12-04T10:30:00Z",
                "files_changed": [
                    {
                        "path": "src/UserService.java",
                        "status": "modified",
                        "additions": 10,
                        "deletions": 5
                    }
                ],
                "metadata": {
                    "source": "github",
                    "branch": "main"
                }
            }
        }


class IssueEvent(BaseModel):
    """
    Issue event model matching architecture specification.
    
    Output format for Kafka topic: repository.issues
    """
    event_id: str = Field(..., description="Unique event identifier")
    repository_id: str = Field(..., description="Repository identifier")
    issue_key: str = Field(..., description="Issue key (e.g., MTP-77, GH-123)")
    issue_type: str = Field(..., description="Issue type: Bug|Feature|Task")
    summary: str = Field(..., description="Issue summary/title")
    status: str = Field(..., description="Issue status: Open|Closed|In Progress")
    created_at: datetime = Field(..., description="Issue creation timestamp")
    linked_commits: List[str] = Field(default_factory=list, description="List of linked commit SHAs")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "evt_124",
                "repository_id": "repo_12345",
                "issue_key": "MTP-77",
                "issue_type": "Bug",
                "summary": "Bug in authentication",
                "status": "Open",
                "created_at": "2025-12-04T10:30:00Z",
                "linked_commits": ["abc123"]
            }
        }


class CIArtifactEvent(BaseModel):
    """
    CI artifact event model matching architecture specification.
    
    Output format for Kafka topic: ci.artifacts
    """
    event_id: str = Field(..., description="Unique event identifier")
    repository_id: str = Field(..., description="Repository identifier")
    build_id: Optional[str] = Field(None, description="Build identifier")
    commit_sha: str = Field(..., description="Commit SHA")
    artifact_type: str = Field(..., description="Artifact type: jacoco|surefire|pit")
    artifact_url: str = Field(..., description="Artifact URL (S3/MinIO)")
    timestamp: datetime = Field(..., description="Event timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "evt_125",
                "repository_id": "repo_12345",
                "build_id": "build_789",
                "commit_sha": "abc123",
                "artifact_type": "jacoco",
                "artifact_url": "s3://minio/artifacts/jacoco_abc123.xml",
                "timestamp": "2025-12-04T10:35:00Z"
            }
        }


