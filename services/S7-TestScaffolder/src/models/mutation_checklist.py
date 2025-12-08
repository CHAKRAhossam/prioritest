"""
Modèles de données pour la checklist de mutation testing
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum


class MutationOperator(str, Enum):
    """Opérateurs de mutation courants"""
    RETURN_VALS = "return_vals"  # Remplacer valeur de retour par null
    CONDITIONALS_BOUNDARY = "conditionals_boundary"  # Changer limites conditionnelles
    MATH = "math"  # Changer opérateurs mathématiques
    NEGATE_CONDITIONALS = "negate_conditionals"  # Négation de conditions
    INCREMENTS = "increments"  # Changer incréments/décréments
    INVERT_NEGS = "invert_negs"  # Inverser négations
    VOID_METHOD_CALLS = "void_method_calls"  # Supprimer appels void
    REMOVE_CONDITIONALS = "remove_conditionals"  # Supprimer conditions
    REMOVE_INCREMENTS = "remove_increments"  # Supprimer incréments


class MutationChecklistItem(BaseModel):
    """Item de checklist pour mutation testing"""
    operator: MutationOperator = Field(..., description="Opérateur de mutation", example=MutationOperator.RETURN_VALS)
    description: str = Field(..., description="Description de la mutation", example="Remplacer valeur de retour par null")
    test_suggestion: str = Field(..., description="Suggestion de test pour détecter cette mutation", example="Vérifier que le résultat n'est pas null")
    priority: int = Field(1, description="Priorité (1=haute, 3=basse)", example=1)
    applicable: bool = Field(True, description="Si cette mutation est applicable à la méthode", example=True)


class MethodMutationChecklist(BaseModel):
    """Checklist de mutation testing pour une méthode"""
    method_name: str = Field(..., description="Nom de la méthode", example="getUserById")
    items: List[MutationChecklistItem] = Field(default_factory=list, description="Items de checklist")
    total_items: int = Field(0, description="Nombre total d'items")
    applicable_items: int = Field(0, description="Nombre d'items applicables")


class ClassMutationChecklist(BaseModel):
    """Checklist de mutation testing pour une classe complète"""
    class_name: str = Field(..., description="Nom de la classe", example="UserService")
    method_checklists: List[MethodMutationChecklist] = Field(default_factory=list, description="Checklists par méthode")
    total_items: int = Field(0, description="Nombre total d'items")
    coverage_estimate: float = Field(0.0, description="Estimation de couverture mutation", example=0.75)

