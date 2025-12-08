"""
Service de génération de checklist pour mutation testing

MTP-S7-05: Checklist mutation testing
- Génère une checklist de tests pour détecter les mutations courantes
- Basé sur les opérateurs de mutation PIT (Pitest)
- Suggère des tests spécifiques pour chaque type de mutation
"""
from typing import List, Dict, Optional
from src.models.ast_models import ClassAnalysis, MethodInfo, MethodParameter
from src.models.mutation_checklist import (
    MutationChecklistItem, MethodMutationChecklist, ClassMutationChecklist, MutationOperator
)


class MutationChecklistService:
    """
    Service pour générer des checklists de mutation testing.
    
    Génère des suggestions de tests basées sur les opérateurs de mutation courants :
    - ReturnValsMutator : Tests pour valeurs de retour null
    - ConditionalsBoundaryMutator : Tests pour limites conditionnelles
    - MathMutator : Tests pour opérateurs mathématiques
    - NegateConditionalsMutator : Tests pour négation de conditions
    - Etc.
    """
    
    def __init__(self):
        """Initialise le service de checklist"""
        pass
    
    def generate_checklist(
        self,
        class_analysis: ClassAnalysis,
        include_private: bool = False
    ) -> ClassMutationChecklist:
        """
        Génère une checklist complète de mutation testing pour une classe.
        
        Args:
            class_analysis: Analyse AST de la classe
            include_private: Inclure les méthodes privées (défaut: False)
        
        Returns:
            Checklist complète de mutation testing
        """
        method_checklists = []
        total_items = 0
        
        for method in class_analysis.methods:
            # Ne générer des checklists que pour les méthodes publiques (ou privées si demandé)
            if method.is_public or (include_private and not method.is_static):
                method_checklist = self._generate_method_checklist(method)
                method_checklists.append(method_checklist)
                total_items += method_checklist.total_items
        
        # Estimer la couverture mutation
        coverage_estimate = self._estimate_mutation_coverage(method_checklists)
        
        return ClassMutationChecklist(
            class_name=class_analysis.class_name,
            method_checklists=method_checklists,
            total_items=total_items,
            coverage_estimate=coverage_estimate
        )
    
    def _generate_method_checklist(self, method: MethodInfo) -> MethodMutationChecklist:
        """
        Génère une checklist pour une méthode spécifique.
        
        Args:
            method: Information sur la méthode
        
        Returns:
            Checklist pour la méthode
        """
        items = []
        
        # 1. ReturnValsMutator - Remplacer valeur de retour par null
        if not method.is_void and method.return_type:
            items.append(MutationChecklistItem(
                operator=MutationOperator.RETURN_VALS,
                description="Remplacer valeur de retour par null",
                test_suggestion=f"Vérifier que {method.name}() ne retourne pas null avec des paramètres valides",
                priority=1,
                applicable=True
            ))
        
        # 2. ConditionalsBoundaryMutator - Changer limites conditionnelles
        if self._has_conditionals(method):
            items.append(MutationChecklistItem(
                operator=MutationOperator.CONDITIONALS_BOUNDARY,
                description="Changer limites conditionnelles (>, >=, <, <=)",
                test_suggestion=f"Tester avec des valeurs aux limites (min, max, égalité) pour {method.name}()",
                priority=1,
                applicable=True
            ))
        
        # 3. MathMutator - Changer opérateurs mathématiques
        if self._has_math_operations(method):
            items.append(MutationChecklistItem(
                operator=MutationOperator.MATH,
                description="Changer opérateurs mathématiques (+, -, *, /)",
                test_suggestion=f"Tester les calculs mathématiques dans {method.name}() avec différentes valeurs",
                priority=2,
                applicable=True
            ))
        
        # 4. NegateConditionalsMutator - Négation de conditions
        if self._has_conditionals(method):
            items.append(MutationChecklistItem(
                operator=MutationOperator.NEGATE_CONDITIONALS,
                description="Négation de conditions (== devient !=, etc.)",
                test_suggestion=f"Tester les cas où les conditions sont vraies ET fausses dans {method.name}()",
                priority=1,
                applicable=True
            ))
        
        # 5. InvertNegsMutator - Inverser négations
        if self._has_negations(method):
            items.append(MutationChecklistItem(
                operator=MutationOperator.INVERT_NEGS,
                description="Inverser négations (! devient non-!)",
                test_suggestion=f"Tester les cas avec et sans négation dans {method.name}()",
                priority=2,
                applicable=True
            ))
        
        # 6. VoidMethodCallsMutator - Supprimer appels void
        if method.is_void:
            items.append(MutationChecklistItem(
                operator=MutationOperator.VOID_METHOD_CALLS,
                description="Supprimer appels de méthodes void",
                test_suggestion=f"Vérifier les effets de bord de {method.name}() avec verify() sur les mocks",
                priority=1,
                applicable=True
            ))
        
        # 7. RemoveConditionalsMutator - Supprimer conditions
        if self._has_conditionals(method):
            items.append(MutationChecklistItem(
                operator=MutationOperator.REMOVE_CONDITIONALS,
                description="Supprimer conditions (if, switch)",
                test_suggestion=f"Tester tous les chemins d'exécution possibles dans {method.name}()",
                priority=1,
                applicable=True
            ))
        
        # 8. Tests pour exceptions
        if method.throws_exceptions:
            for exception in method.throws_exceptions:
                items.append(MutationChecklistItem(
                    operator=MutationOperator.NEGATE_CONDITIONALS,
                    description=f"Tester que {exception} est bien lancée",
                    test_suggestion=f"Vérifier que {method.name}() lance {exception} dans les cas appropriés",
                    priority=1,
                    applicable=True
                ))
        
        # 9. Tests pour paramètres null
        if any(not p.is_primitive for p in method.parameters):
            items.append(MutationChecklistItem(
                operator=MutationOperator.RETURN_VALS,
                description="Tester avec paramètres null",
                test_suggestion=f"Vérifier le comportement de {method.name}() avec des paramètres null",
                priority=2,
                applicable=True
            ))
        
        # 10. Tests pour collections vides
        if any(p.is_collection for p in method.parameters):
            items.append(MutationChecklistItem(
                operator=MutationOperator.CONDITIONALS_BOUNDARY,
                description="Tester avec collections vides",
                test_suggestion=f"Vérifier le comportement de {method.name}() avec des collections vides",
                priority=2,
                applicable=True
            ))
        
        applicable_items = sum(1 for item in items if item.applicable)
        
        return MethodMutationChecklist(
            method_name=method.name,
            items=items,
            total_items=len(items),
            applicable_items=applicable_items
        )
    
    def _has_conditionals(self, method: MethodInfo) -> bool:
        """
        Vérifie si une méthode contient probablement des conditionnelles.
        
        Args:
            method: Information sur la méthode
        
        Returns:
            True si la méthode contient probablement des conditionnelles
        """
        # Heuristique basique : méthodes avec exceptions ou plusieurs paramètres
        # ont souvent des conditionnelles
        return len(method.throws_exceptions) > 0 or len(method.parameters) > 1
    
    def _has_math_operations(self, method: MethodInfo) -> bool:
        """
        Vérifie si une méthode contient probablement des opérations mathématiques.
        
        Args:
            method: Information sur la méthode
        
        Returns:
            True si la méthode contient probablement des opérations mathématiques
        """
        # Heuristique : méthodes avec paramètres numériques
        return any(p.is_primitive and p.type in ['int', 'long', 'double', 'float'] for p in method.parameters)
    
    def _has_negations(self, method: MethodInfo) -> bool:
        """
        Vérifie si une méthode contient probablement des négations.
        
        Args:
            method: Information sur la méthode
        
        Returns:
            True si la méthode contient probablement des négations
        """
        # Heuristique : méthodes avec exceptions ou void
        return method.is_void or len(method.throws_exceptions) > 0
    
    def _estimate_mutation_coverage(self, method_checklists: List[MethodMutationChecklist]) -> float:
        """
        Estime la couverture de mutation basée sur la checklist.
        
        Args:
            method_checklists: Liste des checklists par méthode
        
        Returns:
            Estimation de couverture [0-1]
        """
        if not method_checklists:
            return 0.0
        
        # Calculer un score basé sur le nombre d'items applicables
        total_score = 0.0
        for checklist in method_checklists:
            if checklist.total_items > 0:
                # Score basé sur le ratio d'items applicables
                applicable_ratio = checklist.applicable_items / checklist.total_items
                # Bonus pour diversité d'opérateurs
                operators = set(item.operator for item in checklist.items)
                diversity_bonus = len(operators) * 0.05
                
                total_score += min(applicable_ratio + diversity_bonus, 1.0)
        
        return min(total_score / len(method_checklists), 1.0)

