"""
API endpoints pour la génération de tests
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from src.services.ast_analyzer import ASTAnalyzer
from src.services.test_generator import TestGenerator
from src.services.test_suggestions import TestSuggestionsService
from src.services.mock_generator import MockGenerator
from src.services.mutation_checklist import MutationChecklistService
from src.services.git_storage import GitStorageService
from src.models.ast_models import ClassAnalysis
from src.models.test_suggestions import ClassSuggestions
from src.models.mutation_checklist import ClassMutationChecklist
from datetime import datetime
import os

router = APIRouter()
ast_analyzer = ASTAnalyzer()
test_generator = TestGenerator()
suggestions_service = TestSuggestionsService()
mock_generator = MockGenerator()
mutation_checklist_service = MutationChecklistService()
git_storage = GitStorageService(repo_url=os.getenv('GIT_REPO_URL'))


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


class SuggestTestCasesRequest(BaseModel):
    """Requête pour obtenir des suggestions de cas de test"""
    java_code: str = Field(..., description="Code source Java de la classe", example="package com.example; public class UserService {}")
    include_private: bool = Field(False, description="Inclure les méthodes privées", example=False)
    file_path: Optional[str] = Field(None, description="Chemin du fichier (optionnel)", example="src/main/java/com/example/UserService.java")


@router.post(
    "/suggest-test-cases",
    response_model=ClassSuggestions,
    summary="Suggérer des cas de test",
    description="""
    Génère des suggestions de cas de test pour une classe Java.
    
    **Types de suggestions générées :**
    - **Équivalence** : Valeurs valides et invalides
    - **Limites** : Valeurs aux limites (min, max, zéro)
    - **Exceptions** : Cas qui déclenchent des exceptions
    - **Null** : Tests avec paramètres null
    - **Collections** : Tests avec collections vides/pleines
    
    **Utilisation :**
    Envoyez le code source Java de la classe.
    Le service analyse la classe et génère des suggestions de cas de test
    avec des exemples de valeurs et des assertions suggérées.
    """,
    response_description="Suggestions de cas de test pour la classe"
)
def suggest_test_cases(request: SuggestTestCasesRequest):
    """
    Génère des suggestions de cas de test pour une classe Java.
    
    Args:
        request: Requête contenant le code Java et les options
    
    Returns:
        Suggestions complètes de cas de test
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
        
        # Étape 2: Générer les suggestions
        suggestions = suggestions_service.generate_suggestions(
            class_analysis=analysis,
            include_private=request.include_private
        )
        
        return suggestions
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération des suggestions: {str(e)}"
        )


class MutationChecklistRequest(BaseModel):
    """Requête pour obtenir une checklist de mutation testing"""
    java_code: str = Field(..., description="Code source Java de la classe", example="package com.example; public class UserService {}")
    include_private: bool = Field(False, description="Inclure les méthodes privées", example=False)
    file_path: Optional[str] = Field(None, description="Chemin du fichier (optionnel)", example="src/main/java/com/example/UserService.java")


@router.post(
    "/mutation-checklist",
    response_model=ClassMutationChecklist,
    summary="Générer checklist de mutation testing",
    description="""
    Génère une checklist de mutation testing pour une classe Java.
    
    **Types de mutations couvertes :**
    - **ReturnValsMutator** : Tests pour valeurs de retour null
    - **ConditionalsBoundaryMutator** : Tests pour limites conditionnelles
    - **MathMutator** : Tests pour opérateurs mathématiques
    - **NegateConditionalsMutator** : Tests pour négation de conditions
    - **VoidMethodCallsMutator** : Tests pour effets de bord
    - **RemoveConditionalsMutator** : Tests pour tous les chemins d'exécution
    
    **Utilisation :**
    Envoyez le code source Java de la classe.
    Le service génère une checklist avec des suggestions de tests
    pour détecter les mutations courantes (basé sur PIT/Pitest).
    """,
    response_description="Checklist complète de mutation testing"
)
def generate_mutation_checklist(request: MutationChecklistRequest):
    """
    Génère une checklist de mutation testing pour une classe Java.
    
    Args:
        request: Requête contenant le code Java et les options
    
    Returns:
        Checklist complète de mutation testing
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
        
        # Étape 2: Générer la checklist
        checklist = mutation_checklist_service.generate_checklist(
            class_analysis=analysis,
            include_private=request.include_private
        )
        
        return checklist
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération de la checklist: {str(e)}"
        )


class SaveSuggestionsRequest(BaseModel):
    """Requête pour sauvegarder les suggestions dans Git"""
    java_code: str = Field(..., description="Code source Java de la classe", example="package com.example; public class UserService {}")
    test_code: Optional[str] = Field(None, description="Code source Java du test généré (optionnel, sera généré si absent)")
    test_package: Optional[str] = Field(None, description="Package pour la classe de test", example="com.example.test")
    test_class_suffix: str = Field("Test", description="Suffixe pour le nom de la classe de test", example="Test")
    branch: Optional[str] = Field(None, description="Branche Git où sauvegarder (défaut: branche actuelle)", example="feature/add-tests")
    commit_message: Optional[str] = Field(None, description="Message de commit (défaut: généré automatiquement)")
    include_suggestions: bool = Field(True, description="Inclure les suggestions dans un fichier JSON", example=True)
    push: bool = Field(False, description="Pousser les changements vers le remote", example=False)
    file_path: Optional[str] = Field(None, description="Chemin du fichier source (optionnel)", example="src/main/java/com/example/UserService.java")


class SaveSuggestionsResponse(BaseModel):
    """Réponse de sauvegarde des suggestions"""
    success: bool = Field(..., description="Si la sauvegarde a réussi", example=True)
    test_file_commit: Optional[Dict[str, str]] = Field(None, description="Informations du commit pour le fichier de test")
    suggestions_file_commit: Optional[Dict[str, str]] = Field(None, description="Informations du commit pour le fichier de suggestions")
    message: str = Field(..., description="Message de statut", example="Suggestions sauvegardées avec succès")


@router.post(
    "/save-suggestions",
    response_model=SaveSuggestionsResponse,
    summary="Sauvegarder suggestions dans Git",
    description="""
    Sauvegarde les tests générés et les suggestions dans un dépôt Git.
    
    **Processus :**
    1. Génère le test JUnit (si non fourni)
    2. Génère les suggestions de cas de test
    3. Sauvegarde le fichier de test dans src/test/java/
    4. Sauvegarde les suggestions dans test-suggestions/
    5. Crée des commits Git
    6. Pousse vers le remote (optionnel)
    
    **Configuration requise :**
    - Variable d'environnement GIT_REPO_URL doit être définie
    - Ou fournir repo_url dans la requête
    
    **Utilisation :**
    Envoyez le code source Java de la classe.
    Le service génère et sauvegarde automatiquement les tests et suggestions.
    """,
    response_description="Résultat de la sauvegarde"
)
def save_suggestions(request: SaveSuggestionsRequest):
    """
    Sauvegarde les suggestions de tests dans un dépôt Git.
    
    Args:
        request: Requête contenant le code Java et les options de sauvegarde
    
    Returns:
        Résultat de la sauvegarde avec informations des commits
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
        
        analysis = ClassAnalysis(**analysis_result)
        
        # Étape 2: Générer le test si non fourni
        if not request.test_code:
            test_code = test_generator.generate_test_class(
                class_analysis=analysis,
                test_package=request.test_package,
                test_class_suffix=request.test_class_suffix
            )
        else:
            test_code = request.test_code
        
        # Déterminer le package de test
        if request.test_package:
            test_package = request.test_package
        elif analysis.package_name:
            test_package = analysis.package_name + ".test"
        else:
            test_package = "test"
        
        test_class_name = f"{analysis.class_name}{request.test_class_suffix}"
        
        # Étape 3: Sauvegarder le fichier de test
        test_file_commit = None
        try:
            test_file_commit = git_storage.save_test_file(
                test_code=test_code,
                class_name=analysis.class_name,
                test_class_name=test_class_name,
                test_package=test_package,
                branch=request.branch,
                commit_message=request.commit_message or f"feat(test): Ajouter tests générés pour {analysis.class_name}"
            )
        except Exception as e:
            # Si le stockage Git échoue, on continue quand même
            print(f"Erreur lors de la sauvegarde du test: {e}")
        
        # Étape 4: Générer et sauvegarder les suggestions si demandé
        suggestions_file_commit = None
        if request.include_suggestions:
            try:
                suggestions = suggestions_service.generate_suggestions(analysis)
                checklist = mutation_checklist_service.generate_checklist(analysis)
                
                suggestions_data = {
                    'class_name': analysis.class_name,
                    'suggestions': suggestions.dict(),
                    'mutation_checklist': checklist.dict(),
                    'generated_at': datetime.now().isoformat()
                }
                
                suggestions_file_commit = git_storage.save_suggestions_file(
                    suggestions=suggestions_data,
                    class_name=analysis.class_name,
                    branch=request.branch,
                    commit_message=f"docs(test): Ajouter suggestions de tests pour {analysis.class_name}"
                )
            except Exception as e:
                print(f"Erreur lors de la sauvegarde des suggestions: {e}")
        
        # Étape 5: Pousser si demandé
        if request.push and (test_file_commit or suggestions_file_commit):
            try:
                git_storage.push_changes(branch=request.branch or git_storage.repo.active_branch.name if git_storage.repo else None)
            except Exception as e:
                print(f"Erreur lors du push: {e}")
        
        return SaveSuggestionsResponse(
            success=True,
            test_file_commit=test_file_commit,
            suggestions_file_commit=suggestions_file_commit,
            message="Suggestions sauvegardées avec succès"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la sauvegarde: {str(e)}"
        )

