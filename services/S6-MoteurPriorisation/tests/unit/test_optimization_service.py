"""
Tests unitaires pour OptimizationService
"""
import pytest
from src.services.optimization_service import OptimizationService


class TestOptimizationService:
    """Tests pour OptimizationService"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.service = OptimizationService()
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
    
    def test_optimize_with_budget_constraint_empty(self):
        """Test avec liste vide"""
        result = self.service.optimize_with_budget_constraint([], 10.0)
        assert result == []
    
    def test_optimize_with_budget_constraint_sufficient_budget(self):
        """Test avec budget suffisant pour toutes les classes"""
        result = self.service.optimize_with_budget_constraint(
            self.sample_classes,
            budget_hours=20.0
        )
        # Devrait sélectionner toutes les classes
        assert len(result) == 4
    
    def test_optimize_with_budget_constraint_limited_budget(self):
        """Test avec budget limité"""
        result = self.service.optimize_with_budget_constraint(
            self.sample_classes,
            budget_hours=5.0
        )
        # Devrait sélectionner les classes avec meilleur ratio
        assert len(result) <= 4
        total_effort = sum(cls['effort_hours'] for cls in result)
        assert total_effort <= 5.0
    
    def test_optimize_with_budget_constraint_zero_budget(self):
        """Test avec budget zéro"""
        result = self.service.optimize_with_budget_constraint(
            self.sample_classes,
            budget_hours=0.0
        )
        assert result == []
    
    def test_optimize_with_coverage_constraint_empty(self):
        """Test couverture avec liste vide"""
        result = self.service.optimize_with_coverage_constraint([], 0.8)
        assert result == []
    
    def test_optimize_with_coverage_constraint_full_coverage(self):
        """Test avec couverture complète"""
        result = self.service.optimize_with_coverage_constraint(
            self.sample_classes,
            target_coverage=1.0
        )
        # Devrait sélectionner toutes les classes
        assert len(result) == 4
    
    def test_optimize_with_coverage_constraint_partial(self):
        """Test avec couverture partielle"""
        result = self.service.optimize_with_coverage_constraint(
            self.sample_classes,
            target_coverage=0.5
        )
        # Devrait sélectionner au moins une classe
        assert len(result) > 0
        assert len(result) <= 4
    
    def test_optimize_with_risk_constraint(self):
        """Test avec contrainte de risque"""
        total_risk = sum(cls['risk_score'] for cls in self.sample_classes)
        target_risk = total_risk * 0.6
        
        result = self.service.optimize_with_risk_constraint(
            self.sample_classes,
            target_risk=target_risk
        )
        
        assert len(result) > 0
        total_risk_selected = sum(cls['risk_score'] for cls in result)
        assert total_risk_selected >= target_risk * 0.9  # Tolérance
    
    def test_optimize_multi_constraint_budget_only(self):
        """Test multi-contraintes avec budget seulement"""
        result = self.service.optimize_multi_constraint(
            self.sample_classes,
            budget_hours=6.0
        )
        
        assert len(result) > 0
        total_effort = sum(cls['effort_hours'] for cls in result)
        assert total_effort <= 6.0
    
    def test_optimize_multi_constraint_coverage_only(self):
        """Test multi-contraintes avec couverture seulement"""
        result = self.service.optimize_multi_constraint(
            self.sample_classes,
            target_coverage=0.7
        )
        
        assert len(result) > 0
    
    def test_optimize_multi_constraint_max_classes(self):
        """Test multi-contraintes avec max classes"""
        result = self.service.optimize_multi_constraint(
            self.sample_classes,
            max_classes=2
        )
        
        assert len(result) <= 2
    
    def test_optimize_multi_constraint_all(self):
        """Test multi-contraintes avec toutes les contraintes"""
        result = self.service.optimize_multi_constraint(
            self.sample_classes,
            budget_hours=6.0,
            target_coverage=0.5,
            max_classes=3
        )
        
        assert len(result) <= 3
        total_effort = sum(cls['effort_hours'] for cls in result)
        assert total_effort <= 6.0
    
    def test_optimize_multi_constraint_no_constraints(self):
        """Test multi-contraintes sans contraintes"""
        result = self.service.optimize_multi_constraint(
            self.sample_classes
        )
        # Devrait sélectionner toutes les classes
        assert len(result) == 4
    
    def test_custom_maximize_score(self):
        """Test avec champ de score personnalisé"""
        classes_with_custom = [
            {**cls, 'custom_score': cls['effort_aware_score'] * 2}
            for cls in self.sample_classes
        ]
        
        result = self.service.optimize_with_budget_constraint(
            classes_with_custom,
            budget_hours=6.0,
            maximize_score='custom_score'
        )
        
        assert len(result) > 0
    
    def test_greedy_fallback_budget(self):
        """Test que l'algorithme glouton fonctionne en fallback"""
        # Tester directement la méthode glouton
        result = self.service._greedy_budget_selection(
            self.sample_classes,
            budget_hours=6.0,
            maximize_score='effort_aware_score'
        )
        
        assert len(result) > 0
        total_effort = sum(cls['effort_hours'] for cls in result)
        assert total_effort <= 6.0
    
    def test_greedy_fallback_risk(self):
        """Test algorithme glouton pour risque"""
        total_risk = sum(cls['risk_score'] for cls in self.sample_classes)
        target_risk = total_risk * 0.5
        
        result = self.service._greedy_risk_selection(
            self.sample_classes,
            target_risk=target_risk,
            maximize_score='effort_aware_score'
        )
        
        assert len(result) > 0

