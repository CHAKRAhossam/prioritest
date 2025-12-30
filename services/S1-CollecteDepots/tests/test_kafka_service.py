"""Tests for Kafka service."""
import pytest
from unittest.mock import Mock, patch, MagicMock

from src.services.kafka_service import KafkaService
from src.models.events import CommitEvent, IssueEvent, CIArtifactEvent
from src.models.events import FileChange, Metadata
from datetime import datetime


@pytest.fixture
def kafka_service():
    """Create Kafka service instance."""
    with patch('src.services.kafka_service.Producer') as mock_producer, \
         patch('src.services.kafka_service.AdminClient') as mock_admin:
        
        mock_prod = Mock()
        mock_producer.return_value = mock_prod
        
        mock_admin_client = Mock()
        mock_future = Mock()
        mock_future.result.return_value = None
        mock_admin_client.create_topics.return_value = {"topic": mock_future}
        mock_admin.return_value = mock_admin_client
        
        service = KafkaService()
        return service


def test_publish_commit(kafka_service):
    """Test publishing commit event."""
    event = CommitEvent(
        event_id="evt_123",
        repository_id="repo_123",
        commit_sha="abc123",
        commit_message="Test commit",
        author_email="test@example.com",
        author_name="Test User",
        timestamp=datetime.utcnow(),
        files_changed=[],
        metadata=Metadata(source="github", branch="main")
    )
    
    result = kafka_service.publish_commit(event)
    assert result is True


def test_publish_issue(kafka_service):
    """Test publishing issue event."""
    event = IssueEvent(
        event_id="evt_124",
        repository_id="repo_123",
        issue_key="MTP-77",
        issue_type="Bug",
        summary="Test issue",
        status="Open",
        created_at=datetime.utcnow(),
        linked_commits=[]
    )
    
    result = kafka_service.publish_issue(event)
    assert result is True


def test_publish_artifact(kafka_service):
    """Test publishing artifact event."""
    event = CIArtifactEvent(
        event_id="evt_125",
        repository_id="repo_123",
        build_id="build_789",
        commit_sha="abc123",
        artifact_type="jacoco",
        artifact_url="s3://minio/artifacts/jacoco.xml",
        timestamp=datetime.utcnow()
    )
    
    result = kafka_service.publish_artifact(event)
    assert result is True

