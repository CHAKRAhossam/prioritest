"""
Service de gestion de la criticité des modules

US-S6-02: Intégration criticité module
- Détermine la criticité d'un module à partir du nom de classe
- Applique des poids selon la criticité (high, medium, low)
- Enrichit les classes avec la criticité et ajuste les scores
"""

from typing import Dict, List, Optional
import re


class CriticalityService:
    """
    Gère la criticité des modules et applique des poids aux scores.
    
    La criticité est déterminée à partir du nom de classe :
    - Modules critiques (auth, payment, security) : high
    - Modules importants (database, api) : medium
    - Modules utilitaires (utils, helpers) : low
    """
    
    def __init__(
        self,
        critical_modules: Optional[Dict[str, str]] = None,
        criticality_weights: Optional[Dict[str, float]] = None
    ):
        """
        Initialise le service de criticité.
        
        Args:
            critical_modules: Dictionnaire module -> criticité (ex: {'auth': 'high'})
            criticality_weights: Poids par niveau de criticité (ex: {'high': 1.5})
        """
        # Modules critiques par défaut
        self.critical_modules = critical_modules or {
            'auth': 'high',
            'authentication': 'high',
            'authorization': 'high',
            'security': 'high',
            'payment': 'high',
            'billing': 'high',
            'transaction': 'high',
            'database': 'medium',
            'db': 'medium',
            'persistence': 'medium',
            'api': 'medium',
            'controller': 'medium',
            'service': 'medium',
            'utils': 'low',
            'util': 'low',
            'helper': 'low',
            'helpers': 'low',
            'common': 'low',
            'shared': 'low'
        }
        
        # Poids par criticité
        self.criticality_weights = criticality_weights or {
            'high': 1.5,
            'medium': 1.2,
            'low': 1.0
        }
    
    def get_module_criticality(self, class_name: str) -> str:
        """
        Détermine la criticité d'un module à partir du nom de classe.
        
        Analyse le nom complet de la classe (package + classe) pour identifier
        le module et retourne sa criticité.
        
        Args:
            class_name: Nom complet de la classe (ex: com.example.auth.UserService)
        
        Returns:
            Criticité: 'high', 'medium', ou 'low'
        """
        if not class_name:
            return 'low'
        
        # Normaliser le nom (minuscules)
        class_lower = class_name.lower()
        
        # Extraire les parties du package
        parts = class_lower.split('.')
        
        # Vérifier chaque partie du package
        for part in parts:
            # Vérifier les modules critiques
            for module, criticality in self.critical_modules.items():
                if module in part:
                    return criticality
        
        # Vérifier aussi le nom de la classe elle-même
        class_simple = parts[-1] if parts else class_lower
        for module, criticality in self.critical_modules.items():
            if module in class_simple:
                return criticality
        
        # Par défaut: low
        return 'low'
    
    def apply_criticality_weight(
        self, 
        effort_aware_score: float, 
        criticality: str
    ) -> float:
        """
        Applique un poids selon la criticité au score effort-aware.
        
        Formule: adjusted_score = effort_aware_score * weight
        
        Args:
            effort_aware_score: Score effort-aware de base
            criticality: Criticité du module ('high', 'medium', 'low')
        
        Returns:
            Score ajusté selon la criticité
        """
        weight = self.criticality_weights.get(criticality, 1.0)
        adjusted_score = effort_aware_score * weight
        return round(adjusted_score, 4)
    
    def enrich_with_criticality(
        self, 
        classes: List[Dict]
    ) -> List[Dict]:
        """
        Enrichit les classes avec la criticité et ajuste les scores.
        
        Pour chaque classe :
        1. Détermine la criticité du module
        2. Applique le poids de criticité au score effort-aware
        3. Ajoute les champs module_criticality et effort_aware_score ajusté
        
        Args:
            classes: Liste de classes avec effort_aware_score (du EffortCalculator)
        
        Returns:
            Liste enrichie avec :
                - module_criticality: str
                - effort_aware_score: float (ajusté)
        """
        result = []
        
        for cls in classes:
            class_name = cls.get('class_name', '')
            effort_aware_score = cls.get('effort_aware_score', 0.0)
            
            # Déterminer la criticité
            criticality = self.get_module_criticality(class_name)
            
            # Appliquer le poids
            adjusted_score = self.apply_criticality_weight(
                effort_aware_score, 
                criticality
            )
            
            # Enrichir la classe
            enriched = {
                **cls,
                'module_criticality': criticality,
                'effort_aware_score': adjusted_score
            }
            result.append(enriched)
        
        return result
    
    def update_critical_modules(
        self,
        module: str,
        criticality: str
    ):
        """
        Met à jour la criticité d'un module.
        
        Args:
            module: Nom du module (ex: 'auth')
            criticality: Criticité ('high', 'medium', 'low')
        """
        if criticality not in ['high', 'medium', 'low']:
            raise ValueError(f"Criticité invalide: {criticality}. Doit être 'high', 'medium', ou 'low'")
        
        self.critical_modules[module.lower()] = criticality
    
    def update_criticality_weight(
        self,
        criticality: str,
        weight: float
    ):
        """
        Met à jour le poids d'un niveau de criticité.
        
        Args:
            criticality: Niveau de criticité ('high', 'medium', 'low')
            weight: Nouveau poids (doit être > 0)
        """
        if criticality not in ['high', 'medium', 'low']:
            raise ValueError(f"Criticité invalide: {criticality}")
        
        if weight <= 0:
            raise ValueError(f"Le poids doit être > 0, reçu: {weight}")
        
        self.criticality_weights[criticality] = weight
    
    def get_criticality_stats(self, classes: List[Dict]) -> Dict:
        """
        Calcule des statistiques sur la criticité des classes.
        
        Args:
            classes: Liste de classes avec module_criticality
        
        Returns:
            Dictionnaire avec statistiques par niveau de criticité
        """
        stats = {
            'high': 0,
            'medium': 0,
            'low': 0,
            'total': len(classes)
        }
        
        for cls in classes:
            criticality = cls.get('module_criticality', 'low')
            if criticality in stats:
                stats[criticality] += 1
        
        # Calculer les pourcentages
        if stats['total'] > 0:
            stats['high_percent'] = round(stats['high'] / stats['total'] * 100, 2)
            stats['medium_percent'] = round(stats['medium'] / stats['total'] * 100, 2)
            stats['low_percent'] = round(stats['low'] / stats['total'] * 100, 2)
        else:
            stats['high_percent'] = 0.0
            stats['medium_percent'] = 0.0
            stats['low_percent'] = 0.0
        
        return stats

