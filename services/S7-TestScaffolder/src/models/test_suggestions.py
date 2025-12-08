"""
Modèles de données pour les suggestions de cas de test
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum


class TestCaseType(str, Enum):
    """Type de cas de test"""
    EQUIVALENCE = "equivalence"
    BOUNDARY = "boundary"
    EXCEPTION = "exception"
    NULL = "null"
    EMPTY = "empty"
    EDGE_CASE = "edge_case"


class TestSuggestion(BaseModel):
    """Suggestion de cas de test"""
    type: TestCaseType = Field(..., description="Type de cas de test", example=TestCaseType.EQUIVALENCE)
    method_name: str = Field(..., description="Nom de la méthode à tester", example="getUserById")
    description: str = Field(..., description="Description du cas de test", example="Tester avec un ID valide")
    test_name: str = Field(..., description="Nom suggéré pour le test", example="testGetUserById_WithValidId")
    parameters: Dict[str, str] = Field(default_factory=dict, description="Valeurs suggérées pour les paramètres", example={"userId": "1L"})
    expected_result: Optional[str] = Field(None, description="Résultat attendu (si applicable)", example="assertNotNull(result)")
    expected_exception: Optional[str] = Field(None, description="Exception attendue (si applicable)", example="UserNotFoundException")
    priority: int = Field(1, description="Priorité de la suggestion (1=haute, 3=basse)", example=1)
    category: str = Field(..., description="Catégorie de la suggestion", example="Équivalence - Valeur valide")


class MethodSuggestions(BaseModel):
    """Suggestions de cas de test pour une méthode"""
    method_name: str = Field(..., description="Nom de la méthode", example="getUserById")
    suggestions: List[TestSuggestion] = Field(default_factory=list, description="Liste des suggestions")
    total_count: int = Field(0, description="Nombre total de suggestions")


class ClassSuggestions(BaseModel):
    """Suggestions de cas de test pour une classe complète"""
    class_name: str = Field(..., description="Nom de la classe", example="UserService")
    method_suggestions: List[MethodSuggestions] = Field(default_factory=list, description="Suggestions par méthode")
    total_suggestions: int = Field(0, description="Nombre total de suggestions")
    coverage_estimate: float = Field(0.0, description="Estimation de couverture de test", example=0.75)

