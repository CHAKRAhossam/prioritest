"""
Service de stratégies de priorisation

US-S6-04: Stratégies de priorisation
- Top-K coverage : Sélectionne les K meilleures classes
- Maximize Popt@20 : Maximise le Popt@20 (effort-aware)
- Budget optimization : Sélectionne les classes dans le budget
"""

from typing import Dict, List, Optional
from src.services.optimization_service import OptimizationService


class PrioritizationStrategies:
    """
    Implémente différentes stratégies de priorisation.
    
    Les stratégies utilisent les scores effort-aware (avec criticité)
    pour ordonner et sélectionner les classes à tester.
    """
    
    def __init__(self):
        """Initialise le service de stratégies"""
        self.optimization_service = OptimizationService()
    
    def top_k_coverage(
        self, 
        classes: List[Dict], 
        k: int = 20
    ) -> List[Dict]:
        """
        Stratégie Top-K : Sélectionne les K meilleures classes.
        
        Trie les classes par score effort-aware décroissant et
        sélectionne les K premières.
        
        Args:
            classes: Liste de classes avec effort_aware_score
            k: Nombre de classes à sélectionner (défaut: 20)
        
        Returns:
            Top K classes triées par effort_aware_score décroissant
        """
        if not classes:
            return []
        
        # Trier par score effort-aware décroissant
        sorted_classes = sorted(
            classes,
            key=lambda x: x.get('effort_aware_score', 0.0),
            reverse=True
        )
        
        return sorted_classes[:k]
    
    def maximize_popt20(
        self, 
        classes: List[Dict]
    ) -> List[Dict]:
        """
        Stratégie Popt@20 : Maximise le Popt@20 (effort-aware).
        
        Popt@20 est une métrique qui mesure la performance d'un classement
        en tenant compte de l'effort. Cette stratégie trie simplement
        par score effort-aware décroissant pour maximiser cette métrique.
        
        Args:
            classes: Liste de classes avec effort_aware_score
        
        Returns:
            Classes triées pour maximiser Popt@20
        """
        if not classes:
            return []
        
        # Trier par score effort-aware décroissant
        sorted_classes = sorted(
            classes,
            key=lambda x: x.get('effort_aware_score', 0.0),
            reverse=True
        )
        
        return sorted_classes
    
    def budget_optimization(
        self, 
        classes: List[Dict], 
        budget_hours: float
    ) -> List[Dict]:
        """
        Stratégie Budget : Sélectionne les classes dans le budget.
        
        Utilise l'optimisation avec OR-Tools pour sélectionner les classes
        qui maximisent le score effort-aware sous contrainte de budget.
        
        Args:
            classes: Liste de classes avec effort_hours et effort_aware_score
            budget_hours: Budget total en heures
        
        Returns:
            Classes sélectionnées dans le budget (optimisées)
        """
        if not classes:
            return []
        
        if budget_hours <= 0:
            return []
        
        # Utiliser le service d'optimisation
        selected = self.optimization_service.optimize_with_budget_constraint(
            classes,
            budget_hours=budget_hours,
            maximize_score='effort_aware_score'
        )
        
        # Trier par score décroissant pour l'ordre de priorité
        sorted_selected = sorted(
            selected,
            key=lambda x: x.get('effort_aware_score', 0.0),
            reverse=True
        )
        
        return sorted_selected
    
    def coverage_optimization(
        self,
        classes: List[Dict],
        target_coverage: float
    ) -> List[Dict]:
        """
        Stratégie Coverage : Sélectionne les classes pour atteindre une couverture.
        
        Utilise l'optimisation pour sélectionner les classes qui maximisent
        le score tout en atteignant la couverture cible.
        
        Args:
            classes: Liste de classes avec risk_score et effort_aware_score
            target_coverage: Couverture cible (0.0 - 1.0)
        
        Returns:
            Classes sélectionnées pour atteindre la couverture
        """
        if not classes:
            return []
        
        if target_coverage <= 0 or target_coverage > 1.0:
            return []
        
        # Utiliser le service d'optimisation
        selected = self.optimization_service.optimize_with_coverage_constraint(
            classes,
            target_coverage=target_coverage,
            maximize_score='effort_aware_score'
        )
        
        # Trier par score décroissant
        sorted_selected = sorted(
            selected,
            key=lambda x: x.get('effort_aware_score', 0.0),
            reverse=True
        )
        
        return sorted_selected
    
    def multi_objective_optimization(
        self,
        classes: List[Dict],
        budget_hours: Optional[float] = None,
        target_coverage: Optional[float] = None,
        max_classes: Optional[int] = None
    ) -> List[Dict]:
        """
        Stratégie Multi-objectif : Optimise avec plusieurs contraintes.
        
        Combine plusieurs contraintes (budget, couverture, nombre max)
        pour sélectionner les classes optimales.
        
        Args:
            classes: Liste de classes
            budget_hours: Budget maximum (optionnel)
            target_coverage: Couverture cible (optionnel)
            max_classes: Nombre maximum de classes (optionnel)
        
        Returns:
            Classes sélectionnées sous toutes les contraintes
        """
        if not classes:
            return []
        
        # Utiliser le service d'optimisation multi-contraintes
        selected = self.optimization_service.optimize_multi_constraint(
            classes,
            budget_hours=budget_hours,
            target_coverage=target_coverage,
            max_classes=max_classes,
            maximize_score='effort_aware_score'
        )
        
        # Trier par score décroissant
        sorted_selected = sorted(
            selected,
            key=lambda x: x.get('effort_aware_score', 0.0),
            reverse=True
        )
        
        return sorted_selected
    
    def apply_strategy(
        self, 
        strategy: str, 
        classes: List[Dict], 
        **kwargs
    ) -> List[Dict]:
        """
        Applique une stratégie de priorisation.
        
        Args:
            strategy: Nom de la stratégie
                - 'top_k_coverage' : Top-K classes
                - 'maximize_popt20' : Maximiser Popt@20
                - 'budget_optimization' : Optimisation budget
                - 'coverage_optimization' : Optimisation couverture
                - 'multi_objective' : Multi-objectif
            classes: Liste de classes
            **kwargs: Paramètres de la stratégie
                - k: int (pour top_k_coverage)
                - budget_hours: float (pour budget_optimization)
                - target_coverage: float (pour coverage_optimization)
                - max_classes: int (pour multi_objective)
        
        Returns:
            Classes priorisées selon la stratégie
        """
        if strategy == "top_k_coverage":
            k = kwargs.get('k', 20)
            return self.top_k_coverage(classes, k)
        
        elif strategy == "maximize_popt20":
            return self.maximize_popt20(classes)
        
        elif strategy == "budget_optimization":
            budget = kwargs.get('budget_hours', 40.0)
            return self.budget_optimization(classes, budget)
        
        elif strategy == "coverage_optimization":
            coverage = kwargs.get('target_coverage', 0.8)
            return self.coverage_optimization(classes, coverage)
        
        elif strategy == "multi_objective":
            return self.multi_objective_optimization(
                classes,
                budget_hours=kwargs.get('budget_hours'),
                target_coverage=kwargs.get('target_coverage'),
                max_classes=kwargs.get('max_classes')
            )
        
        else:
            # Par défaut: maximize_popt20
            return self.maximize_popt20(classes)

