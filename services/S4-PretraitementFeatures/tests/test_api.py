"""
Tests for the S4-PretraitementFeatures API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_run_pipeline_success():
    """Test pipeline execution endpoint with success."""
    with patch('api.run_pipeline') as mock_pipeline:
        mock_pipeline.return_value = None
        response = client.post("/run-pipeline")
        assert response.status_code == 200
        assert "message" in response.json()
        mock_pipeline.assert_called_once()


def test_run_pipeline_failure():
    """Test pipeline execution endpoint with failure."""
    with patch('api.run_pipeline') as mock_pipeline:
        mock_pipeline.side_effect = Exception("Pipeline failed")
        response = client.post("/run-pipeline")
        assert response.status_code == 500
        assert "error" in response.json()


def test_get_features_success():
    """Test get features endpoint with success."""
    mock_rows = [
        ("TestClass", 80.0, 75.0, 70.0, 85.0, 60.0, 100, 20)
    ]
    
    with patch('sqlalchemy.create_engine') as mock_engine:
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = mock_rows
        mock_conn.execute.return_value = mock_result
        mock_engine.return_value.connect.return_value.__enter__.return_value = mock_conn
        
        response = client.get("/api/v1/features?repository_id=repo1")
        assert response.status_code == 200
        assert "features" in response.json()
        assert response.json()["count"] > 0


def test_get_features_not_found():
    """Test get features endpoint when no data found."""
    with patch('sqlalchemy.create_engine') as mock_engine:
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_conn.execute.return_value = mock_result
        mock_engine.return_value.connect.return_value.__enter__.return_value = mock_conn
        
        # Try commits query
        mock_commit_result = MagicMock()
        mock_commit_result.fetchone.return_value = None
        mock_conn.execute.return_value = mock_commit_result
        
        response = client.get("/api/v1/features?repository_id=nonexistent")
        assert response.status_code == 404


def test_get_features_with_branch():
    """Test get features endpoint with branch parameter."""
    mock_rows = [
        ("TestClass", 80.0, 75.0, 70.0, 85.0, 60.0, 100, 20)
    ]
    
    with patch('sqlalchemy.create_engine') as mock_engine:
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = mock_rows
        mock_conn.execute.return_value = mock_result
        mock_engine.return_value.connect.return_value.__enter__.return_value = mock_conn
        
        response = client.get("/api/v1/features?repository_id=repo1&branch=main")
        assert response.status_code == 200
        assert "features" in response.json()

