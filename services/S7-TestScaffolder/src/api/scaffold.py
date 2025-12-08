"""
API endpoints pour la génération de tests
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from src.services.ast_analyzer import ASTAnalyzer
from src.models.ast_models import ClassAnalysis

router = APIRouter()
ast_analyzer = ASTAnalyzer()


class AnalyzeClassRequest(BaseModel):
    """Requête pour analyser une classe Java"""
    java_code: str = Field(..., description="Code source Java de la classe", example="package com.example; public class UserService {}")
    file_path: Optional[str] = Field(None, description="Chemin du fichier (optionnel)", example="src/main/java/com/example/UserService.java")


class AnalyzeClassResponse(BaseModel):
    """Réponse de l'analyse AST"""
    analysis: ClassAnalysis = Field(..., description="Analyse complète de la classe")


@router.post(
    "/analyze",
    response_model=AnalyzeClassResponse,
    summary="Analyser une classe Java",
    description="""
    Analyse une classe Java et extrait ses informations pour la génération de tests.
    
    **Informations extraites :**
    - Nom de classe et package
    - Méthodes publiques (nom, paramètres, type de retour, exceptions)
    - Constructeurs
    - Champs et dépendances
    - Imports et annotations
    
    **Utilisation :**
    Envoyez le code source Java complet de la classe à analyser.
    """,
    response_description="Analyse AST complète de la classe"
)
def analyze_class(request: AnalyzeClassRequest):
    """
    Analyse une classe Java et retourne ses informations.
    
    Args:
        request: Requête contenant le code Java à analyser
    
    Returns:
        Analyse complète de la classe avec toutes ses informations
    """
    try:
        result = ast_analyzer.analyze_class(
            java_code=request.java_code,
            file_path=request.file_path
        )
        
        if not result:
            raise HTTPException(
                status_code=400,
                detail="Impossible d'analyser la classe Java"
            )
        
        # Convertir le dict en ClassAnalysis
        analysis = ClassAnalysis(**result)
        
        return AnalyzeClassResponse(analysis=analysis)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse: {str(e)}"
        )


@router.get("/test-scaffold", summary="Générer squelette de test")
def generate_test_scaffold():
    """
    Génère un squelette de test JUnit pour une classe.
    
    Returns:
        dict: Template de test généré
    """
    return {"message": "Test scaffold endpoint - À implémenter"}

