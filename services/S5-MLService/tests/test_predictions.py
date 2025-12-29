"""
Tests for prediction functionality in S5-MLService.
"""
import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api import app, predict, PredictionInput, _transform_s4_features_to_model_format, _generate_explanation
from fastapi.testclient import TestClient

client = TestClient(app)


def test_predict_with_loaded_model():
    """Test predict endpoint with a loaded model."""
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([1])
    mock_model.predict_proba.return_value = np.array([[0.2, 0.8]])
    
    mock_features = ["feature1", "feature2", "feature3"]
    
    with patch('api.model', mock_model):
        with patch('api.feature_names', mock_features):
            with patch('api.shap_explainer', None):
                response = client.post(
                    "/api/v1/predict",
                    json={
                        "class_name": "TestClass",
                        "features": {
                            "feature1": 1.0,
                            "feature2": 2.0,
                            "feature3": 3.0
                        }
                    }
                )
                assert response.status_code == 200
                assert "risk_score" in response.json()
                assert "risk_level" in response.json()
                assert response.json()["class_name"] == "TestClass"


def test_predict_batch_with_loaded_model():
    """Test batch predict endpoint with loaded model."""
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([0, 1])
    mock_model.predict_proba.return_value = np.array([[0.7, 0.3], [0.2, 0.8]])
    
    mock_features = ["feature1", "feature2"]
    
    with patch('api.model', mock_model):
        with patch('api.feature_names', mock_features):
            response = client.post(
                "/api/v1/predict/batch",
                json={
                    "items": [
                        {"class_name": "Class1", "features": {"feature1": 1.0, "feature2": 2.0}},
                        {"class_name": "Class2", "features": {"feature1": 3.0, "feature2": 4.0}}
                    ]
                },
                params={"top_k": 2}
            )
            assert response.status_code == 200
            assert "predictions" in response.json()
            assert "top_k" in response.json()
            assert len(response.json()["predictions"]) == 2


def test_transform_s4_features_to_model_format():
    """Test transformation of S4 features to model format."""
    mock_features = ["feature1", "feature2", "lines_added", "avg_line_coverage"]
    
    with patch('api.feature_names', mock_features):
        s4_features = {
            "loc": 100.0,
            "line_coverage": 80.0,
            "branch_coverage": 75.0,
            "method_coverage": 70.0,
            "mutation_score": 60.0,
            "cyclomatic_complexity": 5.0,
            "num_methods": 10.0,
            "coupling_between_objects": 3.0,
            "response_for_class": 15.0,
            "lack_of_cohesion": 2.0
        }
        
        result = _transform_s4_features_to_model_format(s4_features)
        
        assert isinstance(result, dict)
        assert "lines_added" in result
        assert "avg_line_coverage" in result
        assert result["lines_added"] == 100.0
        assert result["avg_line_coverage"] == 80.0


def test_generate_explanation():
    """Test explanation generation."""
    explanation = _generate_explanation(
        risk_score=0.8,
        risk_level="high",
        features={"feature1": 1.0},
        shap_values={"feature1": 0.5, "feature2": 0.3}
    )
    
    assert isinstance(explanation, str)
    assert "HIGH" in explanation.upper()


def test_generate_explanation_without_shap():
    """Test explanation generation without SHAP values."""
    explanation = _generate_explanation(
        risk_score=0.5,
        risk_level="medium",
        features={"feature1": 1.0},
        shap_values=None
    )
    
    assert isinstance(explanation, str)


def test_predict_with_missing_features():
    """Test predict with missing features (should default to 0)."""
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([0])
    mock_model.predict_proba.return_value = np.array([[0.6, 0.4]])
    
    mock_features = ["feature1", "feature2", "feature3"]
    
    with patch('api.model', mock_model):
        with patch('api.feature_names', mock_features):
            response = client.post(
                "/api/v1/predict",
                json={
                    "class_name": "TestClass",
                    "features": {
                        "feature1": 1.0
                        # feature2 and feature3 missing
                    }
                }
            )
            assert response.status_code == 200
            assert "risk_score" in response.json()


def test_get_predictions_by_repository_with_features():
    """Test get predictions by repository when features are available."""
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([0])
    mock_model.predict_proba.return_value = np.array([[0.6, 0.4]])
    
    mock_features = ["feature1", "feature2"]
    
    mock_s4_features = [
        {
            "class_name": "TestClass1",
            "features": {
                "loc": 100,
                "line_coverage": 80.0,
                "cyclomatic_complexity": 5.0,
                "num_methods": 10.0,
                "num_dependencies": 3.0
            }
        }
    ]
    
    with patch('api.model', mock_model):
        with patch('api.feature_names', mock_features):
            with patch('api._fetch_features_from_s4', return_value=mock_s4_features):
                response = client.get("/api/v1/predictions?repository_id=repo1")
                assert response.status_code == 200
                assert "predictions" in response.json()
                assert len(response.json()["predictions"]) > 0

