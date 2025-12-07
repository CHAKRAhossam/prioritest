"""
Service de calcul d'effort et de scores effort-aware

US-S6-01: Calcul effort-aware
- Estime l'effort en heures pour tester une classe
- Calcule le score effort-aware (risk_score / effort_hours)
"""

from typing import Dict, List, Optional
import math


class EffortCalculator:
    """
    Calcule l'effort estimé et les scores effort-aware pour les classes à tester.
    
    L'effort est estimé en fonction de :
    - LOC (Lines of Code) : Plus de code = plus d'effort
    - Complexité cyclomatique : Plus de complexité = plus d'effort
    """
    
    def __init__(
        self,
        loc_per_hour: float = 50.0,
        complexity_factor: float = 1.5,
        min_effort_hours: float = 0.5,
        max_effort_hours: float = 40.0
    ):
        """
        Initialise le calculateur d'effort.
        
        Args:
            loc_per_hour: Nombre de lignes de code par heure (défaut: 50)
            complexity_factor: Multiplicateur pour complexité élevée (défaut: 1.5)
            min_effort_hours: Effort minimum en heures (défaut: 0.5)
            max_effort_hours: Effort maximum en heures (défaut: 40.0)
        """
        self.loc_per_hour = loc_per_hour
        self.complexity_factor = complexity_factor
        self.min_effort_hours = min_effort_hours
        self.max_effort_hours = max_effort_hours
    
    def estimate_effort_hours(
        self, 
        loc: int, 
        complexity: float,
        additional_factors: Optional[Dict] = None
    ) -> float:
        """
        Estime l'effort en heures pour tester une classe.
        
        Formule de base :
        effort = (LOC / loc_per_hour) * complexity_multiplier
        
        Args:
            loc: Lines of Code de la classe
            complexity: Complexité cyclomatique
            additional_factors: Facteurs additionnels (ex: nombre de méthodes, dépendances)
        
        Returns:
            Effort estimé en heures (arrondi à 2 décimales)
        """
        if loc <= 0:
            return self.min_effort_hours
        
        # Effort de base basé sur LOC
        base_effort = loc / self.loc_per_hour
        
        # Ajustement selon la complexité
        # Complexité élevée (> 10) augmente l'effort
        if complexity > 10:
            complexity_multiplier = 1.0 + (complexity - 10) / 20.0
            complexity_multiplier = min(complexity_multiplier, self.complexity_factor)
        else:
            complexity_multiplier = 1.0
        
        effort = base_effort * complexity_multiplier
        
        # Facteurs additionnels (ex: nombre de méthodes, dépendances)
        if additional_factors:
            if 'num_methods' in additional_factors:
                # Chaque méthode supplémentaire ajoute 0.1h
                effort += additional_factors['num_methods'] * 0.1
            
            if 'num_dependencies' in additional_factors:
                # Chaque dépendance ajoute 0.05h (pour mocks)
                effort += additional_factors['num_dependencies'] * 0.05
        
        # Appliquer min/max
        effort = max(self.min_effort_hours, min(effort, self.max_effort_hours))
        
        return round(effort, 2)
    
    def calculate_effort_aware_score(
        self, 
        risk_score: float, 
        effort_hours: float
    ) -> float:
        """
        Calcule le score effort-aware.
        
        Formule: risk_score / effort_hours
        
        Ce score favorise les classes avec :
        - Score de risque élevé
        - Effort faible
        
        Args:
            risk_score: Score de risque [0-1] (du service ML)
            effort_hours: Effort estimé en heures
        
        Returns:
            Score effort-aware (arrondi à 4 décimales)
        """
        if effort_hours <= 0:
            return 0.0
        
        # Éviter la division par zéro
        if effort_hours < 0.1:
            effort_hours = 0.1
        
        score = risk_score / effort_hours
        
        return round(score, 4)
    
    def calculate_for_classes(
        self, 
        predictions: List[Dict]
    ) -> List[Dict]:
        """
        Calcule l'effort et les scores effort-aware pour une liste de classes.
        
        Args:
            predictions: Liste de prédictions du service ML avec :
                - class_name: str
                - risk_score: float [0-1]
                - loc: int
                - cyclomatic_complexity: float
                - (optionnel) num_methods: int
                - (optionnel) num_dependencies: int
        
        Returns:
            Liste enrichie avec :
                - effort_hours: float
                - effort_aware_score: float
        """
        result = []
        
        for pred in predictions:
            # Extraire les données
            class_name = pred.get('class_name', '')
            risk_score = pred.get('risk_score', 0.0)
            loc = pred.get('loc', 0)
            complexity = pred.get('cyclomatic_complexity', 1.0)
            
            # Facteurs additionnels
            additional_factors = {}
            if 'num_methods' in pred:
                additional_factors['num_methods'] = pred['num_methods']
            if 'num_dependencies' in pred:
                additional_factors['num_dependencies'] = pred['num_dependencies']
            
            # Calculer l'effort
            effort_hours = self.estimate_effort_hours(
                loc=loc,
                complexity=complexity,
                additional_factors=additional_factors if additional_factors else None
            )
            
            # Calculer le score effort-aware
            effort_aware_score = self.calculate_effort_aware_score(
                risk_score=risk_score,
                effort_hours=effort_hours
            )
            
            # Enrichir la prédiction
            enriched = {
                **pred,
                'effort_hours': effort_hours,
                'effort_aware_score': effort_aware_score
            }
            result.append(enriched)
        
        return result
    
    def update_config(
        self,
        loc_per_hour: Optional[float] = None,
        complexity_factor: Optional[float] = None,
        min_effort_hours: Optional[float] = None,
        max_effort_hours: Optional[float] = None
    ):
        """
        Met à jour la configuration du calculateur.
        
        Args:
            loc_per_hour: Nouveau nombre de LOC par heure
            complexity_factor: Nouveau facteur de complexité
            min_effort_hours: Nouvel effort minimum
            max_effort_hours: Nouvel effort maximum
        """
        if loc_per_hour is not None:
            self.loc_per_hour = loc_per_hour
        if complexity_factor is not None:
            self.complexity_factor = complexity_factor
        if min_effort_hours is not None:
            self.min_effort_hours = min_effort_hours
        if max_effort_hours is not None:
            self.max_effort_hours = max_effort_hours


