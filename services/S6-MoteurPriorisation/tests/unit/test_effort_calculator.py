"""
Tests unitaires pour EffortCalculator
"""
import pytest
from src.services.effort_calculator import EffortCalculator


class TestEffortCalculator:
    """Tests pour EffortCalculator"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.calculator = EffortCalculator()
    
    def test_estimate_effort_hours_simple(self):
        """Test estimation effort pour classe simple"""
        effort = self.calculator.estimate_effort_hours(loc=100, complexity=5)
        # 100 LOC / 50 LOC/h = 2h, complexité faible donc pas de multiplicateur
        assert effort == 2.0
    
    def test_estimate_effort_hours_complex(self):
        """Test estimation effort pour classe complexe"""
        effort = self.calculator.estimate_effort_hours(loc=200, complexity=15)
        # 200 LOC / 50 = 4h, complexité élevée donc multiplicateur
        assert effort > 4.0
        assert effort <= 8.0  # Avec multiplicateur max 1.5
    
    def test_estimate_effort_hours_minimum(self):
        """Test effort minimum"""
        effort = self.calculator.estimate_effort_hours(loc=10, complexity=1)
        assert effort >= self.calculator.min_effort_hours
    
    def test_estimate_effort_hours_maximum(self):
        """Test effort maximum"""
        effort = self.calculator.estimate_effort_hours(loc=5000, complexity=50)
        assert effort <= self.calculator.max_effort_hours
    
    def test_estimate_effort_hours_zero_loc(self):
        """Test avec LOC = 0"""
        effort = self.calculator.estimate_effort_hours(loc=0, complexity=1)
        assert effort == self.calculator.min_effort_hours
    
    def test_estimate_effort_hours_with_additional_factors(self):
        """Test avec facteurs additionnels"""
        additional = {
            'num_methods': 5,
            'num_dependencies': 3
        }
        effort = self.calculator.estimate_effort_hours(
            loc=100, 
            complexity=5,
            additional_factors=additional
        )
        # 2h base + 5*0.1 + 3*0.05 = 2 + 0.5 + 0.15 = 2.65h
        assert effort >= 2.65
    
    def test_calculate_effort_aware_score(self):
        """Test calcul score effort-aware"""
        score = self.calculator.calculate_effort_aware_score(
            risk_score=0.75,
            effort_hours=4.0
        )
        # 0.75 / 4.0 = 0.1875
        assert score == 0.1875
    
    def test_calculate_effort_aware_score_high_risk_low_effort(self):
        """Test score élevé pour risque élevé et effort faible"""
        score = self.calculator.calculate_effort_aware_score(
            risk_score=0.9,
            effort_hours=2.0
        )
        # 0.9 / 2.0 = 0.45
        assert score == 0.45
    
    def test_calculate_effort_aware_score_low_risk_high_effort(self):
        """Test score faible pour risque faible et effort élevé"""
        score = self.calculator.calculate_effort_aware_score(
            risk_score=0.3,
            effort_hours=10.0
        )
        # 0.3 / 10.0 = 0.03
        assert score == 0.03
    
    def test_calculate_effort_aware_score_zero_effort(self):
        """Test avec effort = 0"""
        score = self.calculator.calculate_effort_aware_score(
            risk_score=0.75,
            effort_hours=0.0
        )
        assert score == 0.0
    
    def test_calculate_effort_aware_score_very_small_effort(self):
        """Test avec effort très petit"""
        score = self.calculator.calculate_effort_aware_score(
            risk_score=0.5,
            effort_hours=0.05
        )
        # Devrait utiliser 0.1 comme minimum
        assert score == 5.0  # 0.5 / 0.1
    
    def test_calculate_for_classes(self):
        """Test calcul pour liste de classes"""
        predictions = [
            {
                'class_name': 'com.example.UserService',
                'risk_score': 0.75,
                'loc': 150,
                'cyclomatic_complexity': 12
            },
            {
                'class_name': 'com.example.StringHelper',
                'risk_score': 0.45,
                'loc': 50,
                'cyclomatic_complexity': 3
            }
        ]
        
        result = self.calculator.calculate_for_classes(predictions)
        
        assert len(result) == 2
        assert 'effort_hours' in result[0]
        assert 'effort_aware_score' in result[0]
        assert result[0]['class_name'] == 'com.example.UserService'
        assert result[0]['effort_hours'] > 0
        assert result[0]['effort_aware_score'] > 0
    
    def test_calculate_for_classes_with_additional_factors(self):
        """Test avec facteurs additionnels"""
        predictions = [
            {
                'class_name': 'com.example.Service',
                'risk_score': 0.8,
                'loc': 200,
                'cyclomatic_complexity': 10,
                'num_methods': 8,
                'num_dependencies': 5
            }
        ]
        
        result = self.calculator.calculate_for_classes(predictions)
        
        assert len(result) == 1
        assert result[0]['effort_hours'] > 4.0  # 200/50 = 4h + méthodes + dépendances
    
    def test_update_config(self):
        """Test mise à jour configuration"""
        self.calculator.update_config(
            loc_per_hour=100.0,
            complexity_factor=2.0
        )
        
        assert self.calculator.loc_per_hour == 100.0
        assert self.calculator.complexity_factor == 2.0
        
        # Tester avec nouvelle config
        effort = self.calculator.estimate_effort_hours(loc=200, complexity=15)
        # 200 / 100 = 2h, avec multiplicateur complexité
        assert effort > 2.0

