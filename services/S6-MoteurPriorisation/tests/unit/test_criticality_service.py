"""
Tests unitaires pour CriticalityService
"""
import pytest
from src.services.criticality_service import CriticalityService


class TestCriticalityService:
    """Tests pour CriticalityService"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.service = CriticalityService()
    
    def test_get_module_criticality_high_auth(self):
        """Test détection criticité high pour auth"""
        criticality = self.service.get_module_criticality('com.example.auth.UserService')
        assert criticality == 'high'
    
    def test_get_module_criticality_high_payment(self):
        """Test détection criticité high pour payment"""
        criticality = self.service.get_module_criticality('com.example.payment.PaymentService')
        assert criticality == 'high'
    
    def test_get_module_criticality_high_security(self):
        """Test détection criticité high pour security"""
        criticality = self.service.get_module_criticality('com.example.security.EncryptionService')
        assert criticality == 'high'
    
    def test_get_module_criticality_medium_database(self):
        """Test détection criticité medium pour database"""
        criticality = self.service.get_module_criticality('com.example.database.UserRepository')
        assert criticality == 'medium'
    
    def test_get_module_criticality_medium_api(self):
        """Test détection criticité medium pour api"""
        criticality = self.service.get_module_criticality('com.example.api.UserController')
        assert criticality == 'medium'
    
    def test_get_module_criticality_low_utils(self):
        """Test détection criticité low pour utils"""
        criticality = self.service.get_module_criticality('com.example.utils.StringHelper')
        assert criticality == 'low'
    
    def test_get_module_criticality_low_helper(self):
        """Test détection criticité low pour helper"""
        criticality = self.service.get_module_criticality('com.example.helper.DateHelper')
        assert criticality == 'low'
    
    def test_get_module_criticality_default_low(self):
        """Test criticité par défaut low"""
        criticality = self.service.get_module_criticality('com.example.unknown.UnknownClass')
        assert criticality == 'low'
    
    def test_get_module_criticality_empty_string(self):
        """Test avec chaîne vide"""
        criticality = self.service.get_module_criticality('')
        assert criticality == 'low'
    
    def test_apply_criticality_weight_high(self):
        """Test application poids high"""
        score = self.service.apply_criticality_weight(0.2, 'high')
        # 0.2 * 1.5 = 0.3
        assert score == 0.3
    
    def test_apply_criticality_weight_medium(self):
        """Test application poids medium"""
        score = self.service.apply_criticality_weight(0.2, 'medium')
        # 0.2 * 1.2 = 0.24
        assert score == 0.24
    
    def test_apply_criticality_weight_low(self):
        """Test application poids low"""
        score = self.service.apply_criticality_weight(0.2, 'low')
        # 0.2 * 1.0 = 0.2
        assert score == 0.2
    
    def test_apply_criticality_weight_unknown(self):
        """Test avec criticité inconnue (poids par défaut 1.0)"""
        score = self.service.apply_criticality_weight(0.2, 'unknown')
        assert score == 0.2
    
    def test_enrich_with_criticality(self):
        """Test enrichissement avec criticité"""
        classes = [
            {
                'class_name': 'com.example.auth.UserService',
                'risk_score': 0.75,
                'effort_hours': 4.0,
                'effort_aware_score': 0.1875
            },
            {
                'class_name': 'com.example.utils.StringHelper',
                'risk_score': 0.45,
                'effort_hours': 1.0,
                'effort_aware_score': 0.45
            }
        ]
        
        result = self.service.enrich_with_criticality(classes)
        
        assert len(result) == 2
        assert result[0]['module_criticality'] == 'high'
        assert result[0]['effort_aware_score'] == 0.2812  # 0.1875 * 1.5
        assert result[1]['module_criticality'] == 'low'
        assert result[1]['effort_aware_score'] == 0.45  # 0.45 * 1.0
    
    def test_enrich_with_criticality_preserves_original_data(self):
        """Test que l'enrichissement préserve les données originales"""
        classes = [
            {
                'class_name': 'com.example.payment.PaymentService',
                'risk_score': 0.8,
                'effort_hours': 5.0,
                'effort_aware_score': 0.16
            }
        ]
        
        result = self.service.enrich_with_criticality(classes)
        
        assert result[0]['class_name'] == 'com.example.payment.PaymentService'
        assert result[0]['risk_score'] == 0.8
        assert result[0]['effort_hours'] == 5.0
        assert 'module_criticality' in result[0]
        assert result[0]['effort_aware_score'] == 0.24  # 0.16 * 1.5
    
    def test_update_critical_modules(self):
        """Test mise à jour modules critiques"""
        self.service.update_critical_modules('custom', 'high')
        criticality = self.service.get_module_criticality('com.example.custom.CustomService')
        assert criticality == 'high'
    
    def test_update_critical_modules_invalid_criticality(self):
        """Test mise à jour avec criticité invalide"""
        with pytest.raises(ValueError, match="Criticité invalide"):
            self.service.update_critical_modules('test', 'invalid')
    
    def test_update_criticality_weight(self):
        """Test mise à jour poids de criticité"""
        self.service.update_criticality_weight('high', 2.0)
        score = self.service.apply_criticality_weight(0.2, 'high')
        assert score == 0.4  # 0.2 * 2.0
    
    def test_update_criticality_weight_invalid_criticality(self):
        """Test mise à jour avec criticité invalide"""
        with pytest.raises(ValueError, match="Criticité invalide"):
            self.service.update_criticality_weight('invalid', 1.5)
    
    def test_update_criticality_weight_negative(self):
        """Test mise à jour avec poids négatif"""
        with pytest.raises(ValueError, match="Le poids doit être > 0"):
            self.service.update_criticality_weight('high', -1.0)
    
    def test_get_criticality_stats(self):
        """Test calcul statistiques criticité"""
        classes = [
            {'module_criticality': 'high'},
            {'module_criticality': 'high'},
            {'module_criticality': 'medium'},
            {'module_criticality': 'low'},
            {'module_criticality': 'low'},
        ]
        
        stats = self.service.get_criticality_stats(classes)
        
        assert stats['total'] == 5
        assert stats['high'] == 2
        assert stats['medium'] == 1
        assert stats['low'] == 2
        assert stats['high_percent'] == 40.0
        assert stats['medium_percent'] == 20.0
        assert stats['low_percent'] == 40.0
    
    def test_get_criticality_stats_empty(self):
        """Test statistiques avec liste vide"""
        stats = self.service.get_criticality_stats([])
        
        assert stats['total'] == 0
        assert stats['high'] == 0
        assert stats['medium'] == 0
        assert stats['low'] == 0
        assert stats['high_percent'] == 0.0
    
    def test_custom_critical_modules(self):
        """Test avec modules critiques personnalisés"""
        custom_modules = {
            'custom': 'high',
            'special': 'medium'
        }
        service = CriticalityService(critical_modules=custom_modules)
        
        assert service.get_module_criticality('com.example.custom.Service') == 'high'
        assert service.get_module_criticality('com.example.special.Service') == 'medium'
    
    def test_custom_criticality_weights(self):
        """Test avec poids personnalisés"""
        custom_weights = {
            'high': 2.0,
            'medium': 1.5,
            'low': 1.0
        }
        service = CriticalityService(criticality_weights=custom_weights)
        
        score = service.apply_criticality_weight(0.2, 'high')
        assert score == 0.4  # 0.2 * 2.0

