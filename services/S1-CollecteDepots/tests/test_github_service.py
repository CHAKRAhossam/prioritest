"""Tests for GitHub service."""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.services.github_service import GitHubService
from src.models.events import CommitEvent


@pytest.fixture
def github_service():
    """Create GitHub service instance."""
    with patch('src.services.github_service.settings') as mock_settings:
        mock_settings.github_token = "test_token"
        service = GitHubService()
        service.client = Mock()
        return service


def test_parse_webhook_push(github_service):
    """Test parsing GitHub push webhook."""
    payload = {
        "repository": {
            "full_name": "org/repo"
        },
        "commits": [
            {
                "id": "abc123",
                "message": "Test commit",
                "author": {
                    "email": "test@example.com",
                    "name": "Test User"
                },
                "timestamp": "2025-12-04T10:30:00Z",
                "added": ["file1.java"],
                "modified": ["file2.java"],
                "removed": []
            }
        ],
        "ref": "refs/heads/main"
    }
    
    event = github_service.parse_webhook(payload, "push")
    
    assert event is not None
    assert event.commit_sha == "abc123"
    assert event.commit_message == "Test commit"
    assert event.author_email == "test@example.com"
    assert len(event.files_changed) == 2
    assert event.metadata.source == "github"


def test_get_repo_id(github_service):
    """Test repository ID generation."""
    repo_id = github_service._get_repo_id("org/repo")
    assert repo_id == "github_org_repo"


def test_collect_commits_empty(github_service):
    """Test collecting commits when client is None."""
    github_service.client = None
    result = github_service.collect_commits("org/repo")
    assert result == []

