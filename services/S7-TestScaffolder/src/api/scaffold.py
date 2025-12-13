"""
API endpoints pour la génération de tests
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from src.services.ast_analyzer import ASTAnalyzer
from src.services.test_generator import TestGenerator
from src.services.test_suggestions import TestSuggestionsService
from src.services.mock_generator import MockGenerator
from src.services.mutation_checklist import MutationChecklistService
from src.services.git_storage import GitStorageService
from src.models.ast_models import ClassAnalysis
from src.models.test_suggestions import ClassSuggestions
from src.models.mutation_checklist import ClassMutationChecklist
from src.models.generation import CompleteGenerationRequest, CompleteGenerationResponse
from datetime import datetime
import os

router = APIRouter()
ast_analyzer = ASTAnalyzer()
test_generator = TestGenerator()
suggestions_service = TestSuggestionsService()
mock_generator = MockGenerator()
mutation_checklist_service = MutationChecklistService()
git_storage = GitStorageService(repo_url=os.getenv('GIT_REPO_URL'))


# Architecture specification endpoints
class TestScaffoldRequest(BaseModel):
    """Request model aligned with architecture specification."""
    class_name: str = Field(..., description="Fully qualified class name", example="com.example.UserService")
    priority: Optional[int] = Field(None, description="Priority from prioritization service", example=1)
    file_path: Optional[str] = Field(None, description="File path", example="src/UserService.java")


class TestScaffoldBatchRequest(BaseModel):
    """Batch request model aligned with architecture specification."""
    prioritized_classes: List[dict] = Field(..., description="List of prioritized classes from S6", example=[
        {
            "class_name": "com.example.UserService",
            "priority": 1,
            "file_path": "src/UserService.java"
        }
    ])


class TestScaffoldResponse(BaseModel):
    """
    Response model aligned with architecture specification.
    
    Format from architecture spec:
    {
      "class_name": "com.example.UserService",
      "test_file_path": "tests/UserServiceTest.java",
      "test_template": "...",
      "suggested_test_cases": [...],
      "mutation_checklist": [...],
      "repository_url": "..."
    }
    """
    class_name: str
    test_file_path: str
    test_template: str
    suggested_test_cases: List[dict]
    mutation_checklist: List[str]
    repository_url: Optional[str] = None


@router.get(
    "/test-scaffold",
    response_model=TestScaffoldResponse,
    summary="Generate test scaffold for a class (Architecture Spec)",
    description="""
    Generate test scaffold aligned with architecture specification.
    
    GET /api/v1/test-scaffold?class_name=com.example.UserService&priority=1
    
    This endpoint matches the architecture specification format.
    """
)
def get_test_scaffold(
    class_name: str,
    priority: Optional[int] = None
):
    """
    Generate test scaffold for a single class.
    Aligned with architecture specification.
    """
    # This is a placeholder - would need to fetch class code from repository
    # For now, return a template response
    return TestScaffoldResponse(
        class_name=class_name,
        test_file_path=f"tests/{class_name.split('.')[-1]}Test.java",
        test_template=f"public class {class_name.split('.')[-1]}Test {{\n @Test\n public void test() {{...}}\n}}",
        suggested_test_cases=[
            {
                "type": "equivalence",
                "description": "Test with valid input",
                "method": "testValidInput"
            }
        ],
        mutation_checklist=[
            "Test all public methods",
            "Cover edge cases",
            "Verify exception handling"
        ],
        repository_url=os.getenv('GIT_REPO_URL')
    )


@router.post(
    "/test-scaffold/batch",
    response_model=List[TestScaffoldResponse],
    summary="Generate test scaffolds in batch (Architecture Spec)",
    description="""
    Generate test scaffolds for multiple classes in batch.
    
    POST /api/v1/test-scaffold/batch
    {
      "prioritized_classes": [
        {
          "class_name": "com.example.UserService",
          "priority": 1,
          "file_path": "src/UserService.java"
        }
      ]
    }
    
    This endpoint matches the architecture specification format.
    """
)
def batch_test_scaffold(request: TestScaffoldBatchRequest):
    """
    Generate test scaffolds for multiple classes.
    Aligned with architecture specification.
    """
    results = []
    for cls in request.prioritized_classes:
        result = get_test_scaffold(
            class_name=cls.get("class_name"),
            priority=cls.get("priority")
        )
        results.append(result)
    return results


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


@router.post(
    "/generate-complete",
    response_model=CompleteGenerationResponse,
    summary="Génération complète de tests (workflow intégré)",
    description="""
    Endpoint complet qui exécute tout le workflow de génération de tests en une seule requête.
    
    **Workflow complet :**
    1. **Analyse AST** : Analyse la classe Java et extrait toutes les informations
    2. **Génération de test** : Génère une classe de test JUnit complète avec Mockito
    3. **Suggestions** : Génère des suggestions de cas de test (équivalence, limites, exceptions, etc.)
    4. **Checklist mutation** : Génère une checklist de mutation testing
    5. **Stockage Git** (optionnel) : Sauvegarde les tests et suggestions dans un dépôt Git
    
    **Avantages :**
    - Un seul appel API pour tout le processus
    - Cohérence entre tous les résultats
    - Option de sauvegarde automatique dans Git
    - Retourne un résumé complet avec toutes les informations
    
    **Utilisation :**
    Envoyez le code source Java de la classe.
    Le service génère automatiquement tout ce qui est nécessaire pour tester la classe.
    """,
    response_description="Résultat complet de la génération avec test, suggestions et checklist"
)
def generate_complete(request: CompleteGenerationRequest):
    """
    Génère complètement les tests pour une classe Java.
    
    Exécute tout le workflow :
    - Analyse AST
    - Génération de test JUnit
    - Suggestions de cas de test
    - Checklist mutation testing
    - Stockage Git (optionnel)
    
    Args:
        request: Requête contenant le code Java et toutes les options
    
    Returns:
        Résultat complet avec test, suggestions, checklist et stockage
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
        
        # Étape 2: Générer le test JUnit
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
        
        test_class_name = f"{analysis.class_name}{request.test_class_suffix}"
        
        # Étape 3: Générer les suggestions (si demandé)
        suggestions = None
        if request.include_suggestions:
            try:
                suggestions = suggestions_service.generate_suggestions(
                    class_analysis=analysis,
                    include_private=request.include_private
                )
            except Exception as e:
                print(f"Erreur lors de la génération des suggestions: {e}")
        
        # Étape 4: Générer la checklist mutation (si demandé)
        mutation_checklist = None
        if request.include_mutation_checklist:
            try:
                mutation_checklist = mutation_checklist_service.generate_checklist(
                    class_analysis=analysis,
                    include_private=request.include_private
                )
            except Exception as e:
                print(f"Erreur lors de la génération de la checklist: {e}")
        
        # Étape 5: Sauvegarder dans Git (si demandé)
        git_storage_info = None
        if request.save_to_git:
            try:
                # Sauvegarder le fichier de test
                test_commit = git_storage.save_test_file(
                    test_code=test_code,
                    class_name=analysis.class_name,
                    test_class_name=test_class_name,
                    test_package=test_package,
                    branch=request.git_branch,
                    commit_message=request.git_commit_message or f"feat(test): Ajouter tests générés pour {analysis.class_name}"
                )
                
                # Sauvegarder les suggestions si disponibles
                suggestions_commit = None
                if suggestions or mutation_checklist:
                    suggestions_data = {
                        'class_name': analysis.class_name,
                        'generated_at': datetime.now().isoformat()
                    }
                    if suggestions:
                        suggestions_data['suggestions'] = suggestions.dict()
                    if mutation_checklist:
                        suggestions_data['mutation_checklist'] = mutation_checklist.dict()
                    
                    suggestions_commit = git_storage.save_suggestions_file(
                        suggestions=suggestions_data,
                        class_name=analysis.class_name,
                        branch=request.git_branch,
                        commit_message=f"docs(test): Ajouter suggestions de tests pour {analysis.class_name}"
                    )
                
                git_storage_info = {
                    'test_file_commit': test_commit,
                    'suggestions_file_commit': suggestions_commit,
                    'branch': request.git_branch or git_storage.repo.active_branch.name if git_storage.repo else None
                }
                
                # Pousser si demandé
                if request.git_push:
                    git_storage.push_changes(branch=request.git_branch)
                    git_storage_info['pushed'] = True
                
            except Exception as e:
                print(f"Erreur lors de la sauvegarde Git: {e}")
                git_storage_info = {'error': str(e)}
        
        # Construire le résumé
        summary = {
            'class_name': analysis.class_name,
            'methods_count': len(analysis.methods),
            'public_methods_count': sum(1 for m in analysis.methods if m.is_public),
            'test_generated': True,
            'suggestions_count': suggestions.total_suggestions if suggestions else 0,
            'mutation_items_count': mutation_checklist.total_items if mutation_checklist else 0,
            'saved_to_git': request.save_to_git and git_storage_info is not None
        }
        
        return CompleteGenerationResponse(
            success=True,
            analysis=analysis,
            test_code=test_code,
            test_class_name=test_class_name,
            test_package=test_package,
            suggestions=suggestions,
            mutation_checklist=mutation_checklist,
            git_storage=git_storage_info,
            summary=summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération complète: {str(e)}"
        )

