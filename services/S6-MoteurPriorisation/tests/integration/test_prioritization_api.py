"""
Tests d'intégration pour l'API de priorisation
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestPrioritizationAPI:
    """Tests d'intégration pour l'API de priorisation"""
    
    def test_prioritize_maximize_popt20(self):
        """Test priorisation avec stratégie maximize_popt20"""
        request = {
            "repository_id": "repo_12345",
            "sprint_id": "sprint_1"
        }
        
        response = client.post(
            "/api/v1/prioritize?strategy=maximize_popt20",
            json=request
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'prioritized_plan' in data
        assert 'metrics' in data
        assert len(data['prioritized_plan']) > 0
        
        # Vérifier que les classes sont triées par priorité
        priorities = [c['priority'] for c in data['prioritized_plan']]
        assert priorities == sorted(priorities)
    
    def test_prioritize_top_k_coverage(self):
        """Test priorisation avec stratégie top_k_coverage"""
        request = {
            "repository_id": "repo_12345",
            "constraints": {
                "k": 2
            }
        }
        
        response = client.post(
            "/api/v1/prioritize?strategy=top_k_coverage",
            json=request
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data['prioritized_plan']) == 2
    
    def test_prioritize_budget_optimization(self):
        """Test priorisation avec stratégie budget_optimization"""
        request = {
            "repository_id": "repo_12345",
            "constraints": {
                "budget_hours": 5.0
            }
        }
        
        response = client.post(
            "/api/v1/prioritize?strategy=budget_optimization",
            json=request
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier que l'effort total est dans le budget
        total_effort = data['metrics']['total_effort_hours']
        assert total_effort <= 5.0
    
    def test_prioritize_coverage_optimization(self):
        """Test priorisation avec stratégie coverage_optimization"""
        request = {
            "repository_id": "repo_12345",
            "constraints": {
                "target_coverage": 0.7
            }
        }
        
        response = client.post(
            "/api/v1/prioritize?strategy=coverage_optimization",
            json=request
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data['prioritized_plan']) > 0
    
    def test_prioritize_multi_objective(self):
        """Test priorisation avec stratégie multi_objective"""
        request = {
            "repository_id": "repo_12345",
            "constraints": {
                "budget_hours": 6.0,
                "max_classes": 3
            }
        }
        
        response = client.post(
            "/api/v1/prioritize?strategy=multi_objective",
            json=request
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data['prioritized_plan']) <= 3
        total_effort = data['metrics']['total_effort_hours']
        assert total_effort <= 6.0
    
    def test_prioritize_invalid_repository(self):
        """Test avec repository invalide (devrait utiliser mock)"""
        request = {
            "repository_id": "invalid_repo"
        }
        
        response = client.post(
            "/api/v1/prioritize",
            json=request
        )
        
        # Devrait fonctionner avec les données mockées
        assert response.status_code in [200, 404]
    
    def test_get_prioritization(self):
        """Test récupération plan priorisé"""
        response = client.get(
            "/api/v1/prioritize/repo_12345?strategy=maximize_popt20"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'prioritized_plan' in data
        assert 'metrics' in data
    
    def test_prioritize_response_structure(self):
        """Test structure de la réponse"""
        request = {
            "repository_id": "repo_12345"
        }
        
        response = client.post(
            "/api/v1/prioritize",
            json=request
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier la structure
        assert 'prioritized_plan' in data
        assert 'metrics' in data
        
        # Vérifier structure d'une classe priorisée
        if data['prioritized_plan']:
            cls = data['prioritized_plan'][0]
            assert 'class_name' in cls
            assert 'priority' in cls
            assert 'risk_score' in cls
            assert 'effort_hours' in cls
            assert 'effort_aware_score' in cls
            assert 'module_criticality' in cls
            assert 'strategy' in cls
            assert 'reason' in cls
        
        # Vérifier structure des métriques
        metrics = data['metrics']
        assert 'total_effort_hours' in metrics
        assert 'estimated_coverage_gain' in metrics

