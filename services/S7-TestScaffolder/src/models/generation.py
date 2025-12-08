"""
Modèles de données pour la génération complète de tests
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from src.models.ast_models import ClassAnalysis
from src.models.test_suggestions import ClassSuggestions
from src.models.mutation_checklist import ClassMutationChecklist


class CompleteGenerationRequest(BaseModel):
    """Requête pour génération complète de tests"""
    java_code: str = Field(..., description="Code source Java de la classe", example="package com.example; public class UserService {}")
    file_path: Optional[str] = Field(None, description="Chemin du fichier source (optionnel)", example="src/main/java/com/example/UserService.java")
    test_package: Optional[str] = Field(None, description="Package pour la classe de test", example="com.example.test")
    test_class_suffix: str = Field("Test", description="Suffixe pour le nom de la classe de test", example="Test")
    include_suggestions: bool = Field(True, description="Inclure les suggestions de cas de test", example=True)
    include_mutation_checklist: bool = Field(True, description="Inclure la checklist de mutation testing", example=True)
    include_private: bool = Field(False, description="Inclure les méthodes privées", example=False)
    save_to_git: bool = Field(False, description="Sauvegarder dans Git", example=False)
    git_branch: Optional[str] = Field(None, description="Branche Git où sauvegarder", example="feature/add-tests")
    git_commit_message: Optional[str] = Field(None, description="Message de commit Git", example="feat: Add generated tests")
    git_push: bool = Field(False, description="Pousser vers le remote Git", example=False)


class CompleteGenerationResponse(BaseModel):
    """Réponse de génération complète"""
    success: bool = Field(..., description="Si la génération a réussi", example=True)
    analysis: ClassAnalysis = Field(..., description="Analyse AST de la classe")
    test_code: str = Field(..., description="Code source Java de la classe de test générée")
    test_class_name: str = Field(..., description="Nom de la classe de test", example="UserServiceTest")
    test_package: str = Field(..., description="Package de la classe de test", example="com.example.test")
    suggestions: Optional[ClassSuggestions] = Field(None, description="Suggestions de cas de test")
    mutation_checklist: Optional[ClassMutationChecklist] = Field(None, description="Checklist de mutation testing")
    git_storage: Optional[Dict[str, str]] = Field(None, description="Informations de stockage Git")
    summary: Dict[str, any] = Field(..., description="Résumé de la génération")

