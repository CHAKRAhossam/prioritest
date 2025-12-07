"""
Tests unitaires pour MetricsService
"""
import pytest
from src.services.metrics_service import MetricsService


class TestMetricsService:
    """Tests pour MetricsService"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.service = MetricsService()
        self.sample_classes = [
            {
                'class_name': 'com.example.auth.UserService',
                'risk_score': 0.75,
                'effort_hours': 4.0,
                'effort_aware_score': 0.1875
            },
            {
                'class_name': 'com.example.payment.PaymentService',
                'risk_score': 0.68,
                'effort_hours': 5.0,
                'effort_aware_score': 0.136
            },
            {
                'class_name': 'com.example.utils.StringHelper',
                'risk_score': 0.45,
                'effort_hours': 1.0,
                'effort_aware_score': 0.45
            },
            {
                'class_name': 'com.example.database.UserRepository',
                'risk_score': 0.60,
                'effort_hours': 2.0,
                'effort_aware_score': 0.30
            }
        ]
    
    def test_calculate_popt20_empty(self):
        """Test Popt@20 avec liste vide"""
        result = self.service.calculate_popt20([])
        assert result is None
    
    def test_calculate_popt20_with_risk_scores(self):
        """Test Popt@20 avec risk_scores"""
        result = self.service.calculate_popt20(self.sample_classes)
        
        assert result is not None
        assert 0.0 <= result <= 1.0
    
    def test_calculate_popt20_with_defects(self):
        """Test Popt@20 avec données de défauts"""
        actual_defects = [
            {'class_name': 'com.example.auth.UserService', 'has_defect': True},
            {'class_name': 'com.example.payment.PaymentService', 'has_defect': True},
            {'class_name': 'com.example.utils.StringHelper', 'has_defect': False},
            {'class_name': 'com.example.database.UserRepository', 'has_defect': False}
        ]
        
        result = self.service.calculate_popt20(self.sample_classes, actual_defects)
        
        assert result is not None
        assert 0.0 <= result <= 1.0
    
    def test_calculate_popt20_zero_effort(self):
        """Test Popt@20 avec effort zéro"""
        classes = [
            {'class_name': 'Test', 'risk_score': 0.5, 'effort_hours': 0.0}
        ]
        result = self.service.calculate_popt20(classes)
        assert result is None
    
    def test_calculate_recall_top20_empty(self):
        """Test Recall@Top20 avec liste vide"""
        result = self.service.calculate_recall_top20([])
        assert result is None
    
    def test_calculate_recall_top20_with_risk_scores(self):
        """Test Recall@Top20 avec risk_scores"""
        result = self.service.calculate_recall_top20(self.sample_classes)
        
        assert result is not None
        assert 0.0 <= result <= 1.0
    
    def test_calculate_recall_top20_with_defects(self):
        """Test Recall@Top20 avec données de défauts"""
        actual_defects = [
            {'class_name': 'com.example.auth.UserService', 'has_defect': True},
            {'class_name': 'com.example.payment.PaymentService', 'has_defect': True},
            {'class_name': 'com.example.utils.StringHelper', 'has_defect': False},
            {'class_name': 'com.example.database.UserRepository', 'has_defect': False}
        ]
        
        result = self.service.calculate_recall_top20(self.sample_classes, actual_defects)
        
        assert result is not None
        assert 0.0 <= result <= 1.0
    
    def test_calculate_recall_top20_no_defects(self):
        """Test Recall@Top20 sans défauts"""
        actual_defects = [
            {'class_name': 'com.example.auth.UserService', 'has_defect': False},
            {'class_name': 'com.example.payment.PaymentService', 'has_defect': False}
        ]
        
        result = self.service.calculate_recall_top20(self.sample_classes, actual_defects)
        assert result is None
    
    def test_calculate_coverage_gain_empty(self):
        """Test coverage gain avec liste vide"""
        result = self.service.calculate_coverage_gain([])
        assert result == 0.0
    
    def test_calculate_coverage_gain_basic(self):
        """Test coverage gain basique"""
        result = self.service.calculate_coverage_gain(self.sample_classes)
        
        assert result is not None
        assert 0.0 <= result <= 1.0
    
    def test_calculate_coverage_gain_with_baseline(self):
        """Test coverage gain avec baseline"""
        baseline = 0.5
        result = self.service.calculate_coverage_gain(
            self.sample_classes,
            baseline_coverage=baseline
        )
        
        assert result is not None
        # Gain peut être négatif si coverage < baseline
        assert isinstance(result, float)
    
    def test_calculate_all_metrics(self):
        """Test calcul de toutes les métriques"""
        result = self.service.calculate_all_metrics(self.sample_classes)
        
        assert 'popt20_score' in result
        assert 'recall_top20' in result
        assert 'coverage_gain' in result
        assert 'total_classes' in result
        assert 'total_effort_hours' in result
        assert 'total_risk_covered' in result
        assert 'avg_effort_aware_score' in result
        
        assert result['total_classes'] == 4
        assert result['total_effort_hours'] == 12.0  # 4 + 5 + 1 + 2
    
    def test_calculate_all_metrics_with_defects(self):
        """Test calcul avec données de défauts"""
        actual_defects = [
            {'class_name': 'com.example.auth.UserService', 'has_defect': True},
            {'class_name': 'com.example.payment.PaymentService', 'has_defect': True}
        ]
        
        result = self.service.calculate_all_metrics(
            self.sample_classes,
            actual_defects=actual_defects
        )
        
        assert result['popt20_score'] is not None
        assert result['recall_top20'] is not None
    
    def test_compare_strategies(self):
        """Test comparaison de stratégies"""
        strategies_results = {
            'maximize_popt20': self.sample_classes,
            'top_k_coverage': self.sample_classes[:2]
        }
        
        result = self.service.compare_strategies(strategies_results)
        
        assert 'maximize_popt20' in result
        assert 'top_k_coverage' in result
        
        assert result['maximize_popt20']['total_classes'] == 4
        assert result['top_k_coverage']['total_classes'] == 2
    
    def test_compare_strategies_with_defects(self):
        """Test comparaison avec données de défauts"""
        actual_defects = [
            {'class_name': 'com.example.auth.UserService', 'has_defect': True}
        ]
        
        strategies_results = {
            'strategy1': self.sample_classes,
            'strategy2': self.sample_classes[:2]
        }
        
        result = self.service.compare_strategies(
            strategies_results,
            actual_defects=actual_defects
        )
        
        assert 'strategy1' in result
        assert 'strategy2' in result

