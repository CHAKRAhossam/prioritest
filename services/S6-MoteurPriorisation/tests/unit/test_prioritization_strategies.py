"""
Tests unitaires pour PrioritizationStrategies
"""
import pytest
from src.services.prioritization_strategies import PrioritizationStrategies


class TestPrioritizationStrategies:
    """Tests pour PrioritizationStrategies"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.strategies = PrioritizationStrategies()
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
    
    def test_top_k_coverage_empty(self):
        """Test Top-K avec liste vide"""
        result = self.strategies.top_k_coverage([], k=10)
        assert result == []
    
    def test_top_k_coverage_k_smaller_than_total(self):
        """Test Top-K avec k < nombre total"""
        result = self.strategies.top_k_coverage(self.sample_classes, k=2)
        
        assert len(result) == 2
        # Devrait être trié par score décroissant
        assert result[0]['effort_aware_score'] >= result[1]['effort_aware_score']
        # StringHelper devrait être en premier (score 0.45)
        assert result[0]['class_name'] == 'com.example.utils.StringHelper'
    
    def test_top_k_coverage_k_larger_than_total(self):
        """Test Top-K avec k > nombre total"""
        result = self.strategies.top_k_coverage(self.sample_classes, k=10)
        assert len(result) == 4
    
    def test_top_k_coverage_default_k(self):
        """Test Top-K avec k par défaut"""
        result = self.strategies.top_k_coverage(self.sample_classes)
        assert len(result) == 4  # Toutes les classes (4 < 20)
    
    def test_maximize_popt20_empty(self):
        """Test Popt@20 avec liste vide"""
        result = self.strategies.maximize_popt20([])
        assert result == []
    
    def test_maximize_popt20_sorted(self):
        """Test Popt@20 trie correctement"""
        result = self.strategies.maximize_popt20(self.sample_classes)
        
        assert len(result) == 4
        # Vérifier que c'est trié par score décroissant
        for i in range(len(result) - 1):
            assert result[i]['effort_aware_score'] >= result[i+1]['effort_aware_score']
        
        # StringHelper devrait être en premier
        assert result[0]['class_name'] == 'com.example.utils.StringHelper'
    
    def test_budget_optimization_empty(self):
        """Test budget optimization avec liste vide"""
        result = self.strategies.budget_optimization([], budget_hours=10.0)
        assert result == []
    
    def test_budget_optimization_sufficient_budget(self):
        """Test budget optimization avec budget suffisant"""
        result = self.strategies.budget_optimization(
            self.sample_classes,
            budget_hours=20.0
        )
        
        # Devrait sélectionner toutes les classes
        assert len(result) == 4
        total_effort = sum(cls['effort_hours'] for cls in result)
        assert total_effort <= 20.0
    
    def test_budget_optimization_limited_budget(self):
        """Test budget optimization avec budget limité"""
        result = self.strategies.budget_optimization(
            self.sample_classes,
            budget_hours=5.0
        )
        
        assert len(result) > 0
        total_effort = sum(cls['effort_hours'] for cls in result)
        assert total_effort <= 5.0
    
    def test_budget_optimization_zero_budget(self):
        """Test budget optimization avec budget zéro"""
        result = self.strategies.budget_optimization(
            self.sample_classes,
            budget_hours=0.0
        )
        assert result == []
    
    def test_budget_optimization_sorted(self):
        """Test que budget optimization trie les résultats"""
        result = self.strategies.budget_optimization(
            self.sample_classes,
            budget_hours=10.0
        )
        
        # Vérifier que c'est trié
        for i in range(len(result) - 1):
            assert result[i]['effort_aware_score'] >= result[i+1]['effort_aware_score']
    
    def test_coverage_optimization_empty(self):
        """Test coverage optimization avec liste vide"""
        result = self.strategies.coverage_optimization([], target_coverage=0.8)
        assert result == []
    
    def test_coverage_optimization_full_coverage(self):
        """Test coverage optimization avec couverture complète"""
        result = self.strategies.coverage_optimization(
            self.sample_classes,
            target_coverage=1.0
        )
        
        assert len(result) > 0
    
    def test_coverage_optimization_invalid_coverage(self):
        """Test coverage optimization avec couverture invalide"""
        result = self.strategies.coverage_optimization(
            self.sample_classes,
            target_coverage=1.5  # > 1.0
        )
        assert result == []
    
    def test_multi_objective_optimization_budget_only(self):
        """Test multi-objectif avec budget seulement"""
        result = self.strategies.multi_objective_optimization(
            self.sample_classes,
            budget_hours=6.0
        )
        
        assert len(result) > 0
        total_effort = sum(cls['effort_hours'] for cls in result)
        assert total_effort <= 6.0
    
    def test_multi_objective_optimization_all_constraints(self):
        """Test multi-objectif avec toutes les contraintes"""
        result = self.strategies.multi_objective_optimization(
            self.sample_classes,
            budget_hours=6.0,
            target_coverage=0.5,
            max_classes=3
        )
        
        assert len(result) <= 3
        total_effort = sum(cls['effort_hours'] for cls in result)
        assert total_effort <= 6.0
    
    def test_apply_strategy_top_k(self):
        """Test apply_strategy avec top_k_coverage"""
        result = self.strategies.apply_strategy(
            'top_k_coverage',
            self.sample_classes,
            k=2
        )
        
        assert len(result) == 2
    
    def test_apply_strategy_maximize_popt20(self):
        """Test apply_strategy avec maximize_popt20"""
        result = self.strategies.apply_strategy(
            'maximize_popt20',
            self.sample_classes
        )
        
        assert len(result) == 4
        assert result[0]['effort_aware_score'] >= result[1]['effort_aware_score']
    
    def test_apply_strategy_budget_optimization(self):
        """Test apply_strategy avec budget_optimization"""
        result = self.strategies.apply_strategy(
            'budget_optimization',
            self.sample_classes,
            budget_hours=6.0
        )
        
        assert len(result) > 0
        total_effort = sum(cls['effort_hours'] for cls in result)
        assert total_effort <= 6.0
    
    def test_apply_strategy_coverage_optimization(self):
        """Test apply_strategy avec coverage_optimization"""
        result = self.strategies.apply_strategy(
            'coverage_optimization',
            self.sample_classes,
            target_coverage=0.7
        )
        
        assert len(result) > 0
    
    def test_apply_strategy_multi_objective(self):
        """Test apply_strategy avec multi_objective"""
        result = self.strategies.apply_strategy(
            'multi_objective',
            self.sample_classes,
            budget_hours=6.0,
            max_classes=2
        )
        
        assert len(result) <= 2
    
    def test_apply_strategy_unknown_defaults_to_popt20(self):
        """Test apply_strategy avec stratégie inconnue (défaut)"""
        result = self.strategies.apply_strategy(
            'unknown_strategy',
            self.sample_classes
        )
        
        # Devrait utiliser maximize_popt20 par défaut
        assert len(result) == 4
        assert result[0]['effort_aware_score'] >= result[1]['effort_aware_score']

