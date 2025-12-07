"""
Service de calcul des métriques de performance

US-S6-07: Métriques de performance
- Calcul Popt@20 (effort-aware)
- Calcul Recall@Top20
- Calcul gain de couverture
- Autres métriques de performance
"""

from typing import Dict, List, Optional
import math


class MetricsService:
    """
    Calcule les métriques de performance pour la priorisation.
    
    Métriques supportées :
    - Popt@20 : Performance effort-aware à 20% de l'effort
    - Recall@Top20 : Rappel sur les 20% meilleures classes
    - Coverage Gain : Gain de couverture estimé
    """
    
    def __init__(self):
        """Initialise le service de métriques"""
        pass
    
    def calculate_popt20(
        self,
        prioritized_classes: List[Dict],
        actual_defects: Optional[List[Dict]] = None
    ) -> float:
        """
        Calcule le Popt@20 (effort-aware performance).
        
        Popt@20 mesure la performance d'un classement en tenant compte
        de l'effort. Il compare la proportion de défauts trouvés dans
        les 20% de l'effort total avec un classement optimal.
        
        Args:
            prioritized_classes: Liste de classes priorisées avec effort_hours
            actual_defects: Liste des classes avec défauts réels (optionnel)
                Format: [{'class_name': '...', 'has_defect': True/False}]
        
        Returns:
            Score Popt@20 [0-1] ou None si données insuffisantes
        """
        if not prioritized_classes:
            return None
        
        # Calculer l'effort total
        total_effort = sum(cls.get('effort_hours', 0.0) for cls in prioritized_classes)
        if total_effort == 0:
            return None
        
        # Effort cible : 20% du total
        target_effort = total_effort * 0.2
        
        # Si pas de données de défauts, utiliser risk_score comme proxy
        if actual_defects is None:
            # Utiliser risk_score comme approximation
            return self._calculate_popt20_with_risk_scores(prioritized_classes, target_effort)
        
        # Calculer avec données réelles
        return self._calculate_popt20_with_defects(
            prioritized_classes,
            actual_defects,
            target_effort
        )
    
    def _calculate_popt20_with_risk_scores(
        self,
        prioritized_classes: List[Dict],
        target_effort: float
    ) -> float:
        """Calcule Popt@20 en utilisant risk_score comme proxy"""
        cumulative_effort = 0.0
        cumulative_risk = 0.0
        total_risk = sum(cls.get('risk_score', 0.0) for cls in prioritized_classes)
        
        if total_risk == 0:
            return None
        
        for cls in prioritized_classes:
            effort = cls.get('effort_hours', 0.0)
            risk = cls.get('risk_score', 0.0)
            
            if cumulative_effort + effort <= target_effort:
                cumulative_effort += effort
                cumulative_risk += risk
            else:
                # Proportion partielle
                remaining_effort = target_effort - cumulative_effort
                if remaining_effort > 0 and effort > 0:
                    proportion = remaining_effort / effort
                    cumulative_risk += risk * proportion
                break
        
        # Popt@20 = proportion de risque couverte dans 20% de l'effort
        return round(cumulative_risk / total_risk, 4) if total_risk > 0 else None
    
    def _calculate_popt20_with_defects(
        self,
        prioritized_classes: List[Dict],
        actual_defects: List[Dict],
        target_effort: float
    ) -> float:
        """Calcule Popt@20 avec données de défauts réelles"""
        # Créer un mapping classe -> défaut
        defect_map = {
            defect['class_name']: defect.get('has_defect', False)
            for defect in actual_defects
        }
        
        total_defects = sum(1 for d in actual_defects if d.get('has_defect', False))
        if total_defects == 0:
            return None
        
        cumulative_effort = 0.0
        defects_found = 0
        
        for cls in prioritized_classes:
            effort = cls.get('effort_hours', 0.0)
            class_name = cls.get('class_name', '')
            
            if cumulative_effort + effort <= target_effort:
                cumulative_effort += effort
                if defect_map.get(class_name, False):
                    defects_found += 1
            else:
                break
        
        # Popt@20 = proportion de défauts trouvés dans 20% de l'effort
        return round(defects_found / total_defects, 4) if total_defects > 0 else None
    
    def calculate_recall_top20(
        self,
        prioritized_classes: List[Dict],
        actual_defects: Optional[List[Dict]] = None
    ) -> float:
        """
        Calcule le Recall@Top20.
        
        Recall@Top20 mesure la proportion de défauts réels trouvés
        dans les 20% premières classes du classement.
        
        Args:
            prioritized_classes: Liste de classes priorisées
            actual_defects: Liste des classes avec défauts réels (optionnel)
        
        Returns:
            Recall@Top20 [0-1] ou None si données insuffisantes
        """
        if not prioritized_classes:
            return None
        
        # Top 20% des classes
        top_k = max(1, int(len(prioritized_classes) * 0.2))
        top_classes = prioritized_classes[:top_k]
        
        if actual_defects is None:
            # Utiliser risk_score comme proxy
            total_risk = sum(cls.get('risk_score', 0.0) for cls in prioritized_classes)
            top_risk = sum(cls.get('risk_score', 0.0) for cls in top_classes)
            return round(top_risk / total_risk, 4) if total_risk > 0 else None
        
        # Calculer avec données réelles
        defect_map = {
            defect['class_name']: defect.get('has_defect', False)
            for defect in actual_defects
        }
        
        total_defects = sum(1 for d in actual_defects if d.get('has_defect', False))
        if total_defects == 0:
            return None
        
        top_defects = sum(
            1 for cls in top_classes
            if defect_map.get(cls.get('class_name', ''), False)
        )
        
        return round(top_defects / total_defects, 4) if total_defects > 0 else None
    
    def calculate_coverage_gain(
        self,
        prioritized_classes: List[Dict],
        baseline_coverage: Optional[float] = None
    ) -> float:
        """
        Calcule le gain de couverture estimé.
        
        Args:
            prioritized_classes: Liste de classes priorisées
            baseline_coverage: Couverture de base (optionnel)
        
        Returns:
            Gain de couverture estimé [0-1]
        """
        if not prioritized_classes:
            return 0.0
        
        # Calculer la couverture estimée basée sur le risque couvert
        total_risk = sum(cls.get('risk_score', 0.0) for cls in prioritized_classes)
        if total_risk == 0:
            return 0.0
        
        # Couverture = somme des risk_scores des classes sélectionnées
        # Normalisée par le risque total possible
        coverage = min(1.0, total_risk)
        
        if baseline_coverage is not None:
            gain = coverage - baseline_coverage
            return round(max(0.0, gain), 4)
        
        return round(coverage, 4)
    
    def calculate_all_metrics(
        self,
        prioritized_classes: List[Dict],
        actual_defects: Optional[List[Dict]] = None,
        baseline_coverage: Optional[float] = None
    ) -> Dict:
        """
        Calcule toutes les métriques de performance.
        
        Args:
            prioritized_classes: Liste de classes priorisées
            actual_defects: Liste des classes avec défauts réels (optionnel)
            baseline_coverage: Couverture de base (optionnel)
        
        Returns:
            Dictionnaire avec toutes les métriques
        """
        metrics = {
            'popt20_score': self.calculate_popt20(prioritized_classes, actual_defects),
            'recall_top20': self.calculate_recall_top20(prioritized_classes, actual_defects),
            'coverage_gain': self.calculate_coverage_gain(prioritized_classes, baseline_coverage),
            'total_classes': len(prioritized_classes),
            'total_effort_hours': sum(cls.get('effort_hours', 0.0) for cls in prioritized_classes),
            'total_risk_covered': sum(cls.get('risk_score', 0.0) for cls in prioritized_classes)
        }
        
        # Calculer la moyenne des scores effort-aware
        if prioritized_classes:
            avg_effort_aware = sum(
                cls.get('effort_aware_score', 0.0) for cls in prioritized_classes
            ) / len(prioritized_classes)
            metrics['avg_effort_aware_score'] = round(avg_effort_aware, 4)
        else:
            metrics['avg_effort_aware_score'] = 0.0
        
        return metrics
    
    def compare_strategies(
        self,
        strategies_results: Dict[str, List[Dict]],
        actual_defects: Optional[List[Dict]] = None
    ) -> Dict[str, Dict]:
        """
        Compare les métriques de différentes stratégies.
        
        Args:
            strategies_results: Dictionnaire {strategy_name: [classes]}
            actual_defects: Liste des classes avec défauts réels (optionnel)
        
        Returns:
            Dictionnaire avec métriques par stratégie
        """
        comparison = {}
        
        for strategy_name, classes in strategies_results.items():
            comparison[strategy_name] = self.calculate_all_metrics(
                classes,
                actual_defects
            )
        
        return comparison

