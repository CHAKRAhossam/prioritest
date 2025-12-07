"""
Service d'optimisation avec OR-Tools

US-S6-03: Optimisation avec OR-Tools
- Optimisation sous contraintes (budget, coverage)
- Sélection optimale de classes à tester
- Maximisation du score effort-aware sous contraintes
"""

from typing import Dict, List, Optional
from ortools.linear_solver import pywraplp
from ortools.sat.python import cp_model
import math


class OptimizationService:
    """
    Service d'optimisation utilisant OR-Tools pour sélectionner les classes
    à tester sous contraintes (budget, coverage, etc.).
    """
    
    def __init__(self):
        """Initialise le service d'optimisation"""
        pass
    
    def optimize_with_budget_constraint(
        self,
        classes: List[Dict],
        budget_hours: float,
        maximize_score: str = 'effort_aware_score'
    ) -> List[Dict]:
        """
        Optimise la sélection de classes sous contrainte de budget.
        
        Utilise la programmation linéaire en nombres entiers (ILP) pour
        sélectionner les classes qui maximisent le score sous contrainte
        de budget.
        
        Args:
            classes: Liste de classes avec effort_hours et effort_aware_score
            budget_hours: Budget total en heures
            maximize_score: Nom du champ à maximiser (défaut: 'effort_aware_score')
        
        Returns:
            Liste de classes sélectionnées (sous-ensemble optimal)
        """
        if not classes:
            return []
        
        # Créer le solveur
        solver = pywraplp.Solver.CreateSolver('SCIP')
        if not solver:
            # Fallback sur un algorithme glouton si SCIP n'est pas disponible
            return self._greedy_budget_selection(classes, budget_hours, maximize_score)
        
        # Variables de décision : x[i] = 1 si classe i est sélectionnée, 0 sinon
        n = len(classes)
        x = [solver.IntVar(0, 1, f'x_{i}') for i in range(n)]
        
        # Objectif : Maximiser la somme des scores
        objective = solver.Objective()
        for i in range(n):
            score = classes[i].get(maximize_score, 0.0)
            objective.SetCoefficient(x[i], score)
        objective.SetMaximization()
        
        # Contrainte : Budget total
        budget_constraint = solver.Constraint(0, budget_hours)
        for i in range(n):
            effort = classes[i].get('effort_hours', 0.0)
            budget_constraint.SetCoefficient(x[i], effort)
        
        # Résoudre
        status = solver.Solve()
        
        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            # Extraire la solution
            selected = []
            for i in range(n):
                if x[i].solution_value() > 0.5:  # > 0.5 car variables binaires
                    selected.append(classes[i])
            return selected
        else:
            # Si pas de solution optimale, utiliser algorithme glouton
            return self._greedy_budget_selection(classes, budget_hours, maximize_score)
    
    def optimize_with_coverage_constraint(
        self,
        classes: List[Dict],
        target_coverage: float,
        maximize_score: str = 'effort_aware_score'
    ) -> List[Dict]:
        """
        Optimise la sélection pour atteindre une couverture cible.
        
        Sélectionne les classes qui maximisent le score tout en atteignant
        la couverture cible (basée sur le risque total couvert).
        
        Args:
            classes: Liste de classes avec risk_score
            target_coverage: Couverture cible (0.0 - 1.0)
            maximize_score: Nom du champ à maximiser
        
        Returns:
            Liste de classes sélectionnées
        """
        if not classes:
            return []
        
        # Calculer le risque total
        total_risk = sum(cls.get('risk_score', 0.0) for cls in classes)
        target_risk = total_risk * target_coverage
        
        # Utiliser l'optimisation avec contrainte de risque
        return self.optimize_with_risk_constraint(
            classes,
            target_risk,
            maximize_score
        )
    
    def optimize_with_risk_constraint(
        self,
        classes: List[Dict],
        target_risk: float,
        maximize_score: str = 'effort_aware_score'
    ) -> List[Dict]:
        """
        Optimise la sélection sous contrainte de risque total.
        
        Args:
            classes: Liste de classes avec risk_score
            target_risk: Risque total cible à couvrir
            maximize_score: Nom du champ à maximiser
        
        Returns:
            Liste de classes sélectionnées
        """
        if not classes:
            return []
        
        # Créer le solveur
        solver = pywraplp.Solver.CreateSolver('SCIP')
        if not solver:
            return self._greedy_risk_selection(classes, target_risk, maximize_score)
        
        # Variables de décision
        n = len(classes)
        x = [solver.IntVar(0, 1, f'x_{i}') for i in range(n)]
        
        # Objectif : Maximiser le score
        objective = solver.Objective()
        for i in range(n):
            score = classes[i].get(maximize_score, 0.0)
            objective.SetCoefficient(x[i], score)
        objective.SetMaximization()
        
        # Contrainte : Risque total
        risk_constraint = solver.Constraint(target_risk, solver.infinity())
        for i in range(n):
            risk = classes[i].get('risk_score', 0.0)
            risk_constraint.SetCoefficient(x[i], risk)
        
        # Résoudre
        status = solver.Solve()
        
        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            selected = []
            for i in range(n):
                if x[i].solution_value() > 0.5:
                    selected.append(classes[i])
            return selected
        else:
            return self._greedy_risk_selection(classes, target_risk, maximize_score)
    
    def optimize_multi_constraint(
        self,
        classes: List[Dict],
        budget_hours: Optional[float] = None,
        target_coverage: Optional[float] = None,
        max_classes: Optional[int] = None,
        maximize_score: str = 'effort_aware_score'
    ) -> List[Dict]:
        """
        Optimise avec plusieurs contraintes simultanées.
        
        Args:
            classes: Liste de classes
            budget_hours: Budget maximum (optionnel)
            target_coverage: Couverture cible (optionnel)
            max_classes: Nombre maximum de classes (optionnel)
            maximize_score: Nom du champ à maximiser
        
        Returns:
            Liste de classes sélectionnées
        """
        if not classes:
            return []
        
        # Créer le solveur
        solver = pywraplp.Solver.CreateSolver('SCIP')
        if not solver:
            return self._greedy_multi_constraint(
                classes, budget_hours, target_coverage, max_classes, maximize_score
            )
        
        # Variables de décision
        n = len(classes)
        x = [solver.IntVar(0, 1, f'x_{i}') for i in range(n)]
        
        # Objectif : Maximiser le score
        objective = solver.Objective()
        for i in range(n):
            score = classes[i].get(maximize_score, 0.0)
            objective.SetCoefficient(x[i], score)
        objective.SetMaximization()
        
        # Contrainte : Budget
        if budget_hours is not None:
            budget_constraint = solver.Constraint(0, budget_hours)
            for i in range(n):
                effort = classes[i].get('effort_hours', 0.0)
                budget_constraint.SetCoefficient(x[i], effort)
        
        # Contrainte : Couverture
        if target_coverage is not None:
            total_risk = sum(cls.get('risk_score', 0.0) for cls in classes)
            target_risk = total_risk * target_coverage
            risk_constraint = solver.Constraint(target_risk, solver.infinity())
            for i in range(n):
                risk = classes[i].get('risk_score', 0.0)
                risk_constraint.SetCoefficient(x[i], risk)
        
        # Contrainte : Nombre maximum de classes
        if max_classes is not None:
            count_constraint = solver.Constraint(0, max_classes)
            for i in range(n):
                count_constraint.SetCoefficient(x[i], 1)
        
        # Résoudre
        status = solver.Solve()
        
        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            selected = []
            for i in range(n):
                if x[i].solution_value() > 0.5:
                    selected.append(classes[i])
            return selected
        else:
            return self._greedy_multi_constraint(
                classes, budget_hours, target_coverage, max_classes, maximize_score
            )
    
    def _greedy_budget_selection(
        self,
        classes: List[Dict],
        budget_hours: float,
        maximize_score: str
    ) -> List[Dict]:
        """Algorithme glouton de fallback pour sélection sous budget"""
        # Trier par ratio score/effort décroissant
        sorted_classes = sorted(
            classes,
            key=lambda x: x.get(maximize_score, 0.0) / max(x.get('effort_hours', 1.0), 0.1),
            reverse=True
        )
        
        selected = []
        total_effort = 0.0
        
        for cls in sorted_classes:
            effort = cls.get('effort_hours', 0.0)
            if total_effort + effort <= budget_hours:
                selected.append(cls)
                total_effort += effort
        
        return selected
    
    def _greedy_risk_selection(
        self,
        classes: List[Dict],
        target_risk: float,
        maximize_score: str
    ) -> List[Dict]:
        """Algorithme glouton de fallback pour sélection sous risque"""
        sorted_classes = sorted(
            classes,
            key=lambda x: x.get(maximize_score, 0.0),
            reverse=True
        )
        
        selected = []
        total_risk = 0.0
        
        for cls in sorted_classes:
            risk = cls.get('risk_score', 0.0)
            if total_risk < target_risk:
                selected.append(cls)
                total_risk += risk
            else:
                break
        
        return selected
    
    def _greedy_multi_constraint(
        self,
        classes: List[Dict],
        budget_hours: Optional[float],
        target_coverage: Optional[float],
        max_classes: Optional[int],
        maximize_score: str
    ) -> List[Dict]:
        """Algorithme glouton de fallback multi-contraintes"""
        sorted_classes = sorted(
            classes,
            key=lambda x: x.get(maximize_score, 0.0),
            reverse=True
        )
        
        selected = []
        total_effort = 0.0
        total_risk = 0.0
        total_risk_all = sum(cls.get('risk_score', 0.0) for cls in classes)
        target_risk = total_risk_all * target_coverage if target_coverage else None
        
        for cls in sorted_classes:
            # Vérifier les contraintes
            if max_classes and len(selected) >= max_classes:
                break
            
            effort = cls.get('effort_hours', 0.0)
            if budget_hours and total_effort + effort > budget_hours:
                continue
            
            risk = cls.get('risk_score', 0.0)
            if target_risk and total_risk >= target_risk:
                break
            
            selected.append(cls)
            total_effort += effort
            total_risk += risk
        
        return selected

