"""
API endpoints pour la génération de tests
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from src.services.ast_analyzer import ASTAnalyzer
from src.services.test_generator import TestGenerator
from src.models.ast_models import ClassAnalysis

router = APIRouter()
ast_analyzer = ASTAnalyzer()
test_generator = TestGenerator()


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


class GenerateTestRequest(BaseModel):
    """Requête pour générer un test JUnit"""
    java_code: str = Field(..., description="Code source Java de la classe à tester", example="package com.example; public class UserService {}")
    test_package: Optional[str] = Field(None, description="Package pour la classe de test (défaut: package.class + '.test')", example="com.example.test")
    test_class_suffix: str = Field("Test", description="Suffixe pour le nom de la classe de test", example="Test")
    file_path: Optional[str] = Field(None, description="Chemin du fichier source (optionnel)", example="src/main/java/com/example/UserService.java")


class GenerateTestResponse(BaseModel):
    """Réponse de génération de test"""
    test_code: str = Field(..., description="Code source Java de la classe de test générée")
    test_class_name: str = Field(..., description="Nom de la classe de test générée")
    test_package: str = Field(..., description="Package de la classe de test")
    analysis: ClassAnalysis = Field(..., description="Analyse AST de la classe source")


@router.post(
    "/generate-test",
    response_model=GenerateTestResponse,
    summary="Générer squelette de test JUnit",
    description="""
    Génère un squelette de test JUnit complet pour une classe Java.
    
    **Processus :**
    1. Analyse la classe Java fournie (AST)
    2. Génère une classe de test JUnit 5 avec Mockito
    3. Crée des méthodes de test pour chaque méthode publique
    4. Génère les mocks nécessaires pour les dépendances
    
    **Fonctionnalités générées :**
    - Classe de test avec annotations JUnit 5 (@ExtendWith, @DisplayName)
    - Méthodes de test pour chaque méthode publique
    - Mocks Mockito pour les dépendances (@Mock, @InjectMocks)
    - Setup/teardown avec @BeforeEach
    - Structure Arrange-Act-Assert dans chaque test
    
    **Utilisation :**
    Envoyez le code source Java complet de la classe à tester.
    Le service génère automatiquement un squelette de test prêt à être complété.
    """,
    response_description="Code source Java de la classe de test générée"
)
def generate_test(request: GenerateTestRequest):
    """
    Génère un squelette de test JUnit pour une classe Java.
    
    Args:
        request: Requête contenant le code Java et les options de génération
    
    Returns:
        Code source Java de la classe de test générée avec l'analyse AST
    """
    try:
        # Étape 1: Analyser la classe
        analysis_result = ast_analyzer.analyze_class(
            java_code=request.java_code,
            file_path=request.file_path
        )
        
        if not analysis_result:
            raise HTTPException(
                status_code=400,
                detail="Impossible d'analyser la classe Java"
            )
        
        # Convertir en ClassAnalysis
        analysis = ClassAnalysis(**analysis_result)
        
        # Étape 2: Générer le test
        test_code = test_generator.generate_test_class(
            class_analysis=analysis,
            test_package=request.test_package,
            test_class_suffix=request.test_class_suffix
        )
        
        # Déterminer le package de test
        if request.test_package:
            test_package = request.test_package
        elif analysis.package_name:
            test_package = analysis.package_name + ".test"
        else:
            test_package = "test"
        
        # Nom de la classe de test
        test_class_name = f"{analysis.class_name}{request.test_class_suffix}"
        
        return GenerateTestResponse(
            test_code=test_code,
            test_class_name=test_class_name,
            test_package=test_package,
            analysis=analysis
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération du test: {str(e)}"
        )

