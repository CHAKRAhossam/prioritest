"""
Tests for the S5-MLService API endpoints.
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


def test_root():
    """Test root endpoint."""
    with patch('api.model', None):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["service"] == "ML Service"
        assert response.json()["model_loaded"] is False


def test_health_check():
    """Test health check endpoint."""
    with patch('api.model', None):
        with patch('api.feature_names', None):
            response = client.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "ok"
            assert response.json()["model_loaded"] is False


def test_get_features_not_loaded():
    """Test get features endpoint when features not loaded."""
    with patch('api.feature_names', None):
        response = client.get("/api/v1/features")
        assert response.status_code == 503
        assert "not loaded" in response.json()["detail"].lower()


def test_get_features_loaded():
    """Test get features endpoint when features are loaded."""
    mock_features = ["feature1", "feature2", "feature3"]
    with patch('api.feature_names', mock_features):
        response = client.get("/api/v1/features")
        assert response.status_code == 200
        assert response.json()["count"] == 3
        assert len(response.json()["features"]) == 3


def test_train_model():
    """Test train model endpoint."""
    response = client.post("/api/v1/train")
    assert response.status_code == 200
    assert response.json()["status"] in ["success", "error"]


def test_predict_model_not_loaded():
    """Test predict endpoint when model not loaded."""
    with patch('api.model', None):
        response = client.post(
            "/api/v1/predict",
            json={
                "class_name": "TestClass",
                "features": {"feature1": 1.0, "feature2": 2.0}
            }
        )
        assert response.status_code == 503
        assert "not loaded" in response.json()["detail"].lower()


def test_predict_batch_model_not_loaded():
    """Test batch predict endpoint when model not loaded."""
    with patch('api.model', None):
        response = client.post(
            "/api/v1/predict/batch",
            json={
                "items": [
                    {"class_name": "TestClass1", "features": {"feature1": 1.0}},
                    {"class_name": "TestClass2", "features": {"feature1": 2.0}}
                ]
            }
        )
        assert response.status_code == 503


def test_get_predictions_by_repository_model_not_loaded():
    """Test get predictions by repository when model not loaded."""
    with patch('api.model', None):
        response = client.get("/api/v1/predictions?repository_id=repo1")
        assert response.status_code == 503


def test_get_predictions_by_repository_no_features():
    """Test get predictions by repository when no features found."""
    mock_model = MagicMock()
    mock_model.predict.return_value = [0]
    mock_model.predict_proba.return_value = [[0.7, 0.3]]
    
    with patch('api.model', mock_model):
        with patch('api.feature_names', ["feature1", "feature2"]):
            with patch('api._fetch_features_from_s4', return_value=[]):
                with patch('api._fetch_classes_from_s2', return_value=[]):
                    response = client.get("/api/v1/predictions?repository_id=repo1")
                    assert response.status_code == 404

