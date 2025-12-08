"""
Tests pour le service de suggestions de cas de test
"""
import pytest
from pathlib import Path
from src.services.test_suggestions import TestSuggestionsService
from src.services.ast_analyzer import ASTAnalyzer
from src.models.ast_models import ClassAnalysis, MethodInfo, MethodParameter
from src.models.test_suggestions import TestCaseType

# Chemin vers le fichier de test
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
SAMPLE_JAVA_FILE = FIXTURES_DIR / "sample_java_class.java"


@pytest.fixture
def suggestions_service():
    """Fixture pour créer un service de suggestions"""
    return TestSuggestionsService()


@pytest.fixture
def sample_java_code():
    """Fixture pour charger le code Java de test"""
    if SAMPLE_JAVA_FILE.exists():
        return SAMPLE_JAVA_FILE.read_text(encoding='utf-8')
    return """
package com.example.service;

import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class UserService {
    private UserRepository userRepository;
    
    public User getUserById(Long userId) {
        return null;
    }
    
    public void deleteUser(Long userId) {
    }
}
"""


@pytest.fixture
def sample_class_analysis(sample_java_code):
    """Fixture pour créer une analyse de classe"""
    analyzer = ASTAnalyzer()
    result = analyzer.analyze_class(sample_java_code)
    return ClassAnalysis(**result)


def test_suggestions_service_initialization(suggestions_service):
    """Test que le service s'initialise correctement"""
    assert suggestions_service is not None


def test_generate_suggestions_basic(suggestions_service, sample_class_analysis):
    """Test la génération basique de suggestions"""
    suggestions = suggestions_service.generate_suggestions(sample_class_analysis)
    
    assert suggestions is not None
    assert suggestions.class_name == sample_class_analysis.class_name
    assert suggestions.total_suggestions > 0
    assert len(suggestions.method_suggestions) > 0


def test_generate_suggestions_has_equivalence(suggestions_service, sample_class_analysis):
    """Test que les suggestions incluent des cas d'équivalence"""
    suggestions = suggestions_service.generate_suggestions(sample_class_analysis)
    
    # Vérifier qu'il y a au moins une suggestion d'équivalence
    has_equivalence = False
    for method_suggestions in suggestions.method_suggestions:
        for suggestion in method_suggestions.suggestions:
            if suggestion.type == TestCaseType.EQUIVALENCE:
                has_equivalence = True
                break
    
    assert has_equivalence, "Devrait avoir au moins une suggestion d'équivalence"


def test_generate_suggestions_has_boundary(suggestions_service):
    """Test que les suggestions incluent des cas de limites pour les types numériques"""
    # Créer une méthode avec un paramètre int
    method = MethodInfo(
        name="processValue",
        return_type="void",
        parameters=[
            MethodParameter(name="value", type="int", is_primitive=True, is_collection=False)
        ],
        is_public=True,
        is_static=False,
        is_void=True
    )
    
    method_suggestions = suggestions_service._generate_method_suggestions(method)
    
    # Vérifier qu'il y a des suggestions de limites
    has_boundary = any(s.type == TestCaseType.BOUNDARY for s in method_suggestions.suggestions)
    assert has_boundary, "Devrait avoir des suggestions de limites pour les types numériques"


def test_generate_suggestions_has_null(suggestions_service):
    """Test que les suggestions incluent des cas de null pour les objets"""
    # Créer une méthode avec un paramètre objet
    method = MethodInfo(
        name="processUser",
        return_type="void",
        parameters=[
            MethodParameter(name="user", type="User", is_primitive=False, is_collection=False)
        ],
        is_public=True,
        is_static=False,
        is_void=True
    )
    
    method_suggestions = suggestions_service._generate_method_suggestions(method)
    
    # Vérifier qu'il y a des suggestions de null
    has_null = any(s.type == TestCaseType.NULL for s in method_suggestions.suggestions)
    assert has_null, "Devrait avoir des suggestions de null pour les objets"


def test_generate_suggestions_has_exception(suggestions_service):
    """Test que les suggestions incluent des cas d'exception"""
    # Créer une méthode qui lance une exception
    method = MethodInfo(
        name="getUserById",
        return_type="User",
        parameters=[
            MethodParameter(name="userId", type="Long", is_primitive=False, is_collection=False)
        ],
        is_public=True,
        is_static=False,
        is_void=False,
        throws_exceptions=["UserNotFoundException"]
    )
    
    method_suggestions = suggestions_service._generate_method_suggestions(method)
    
    # Vérifier qu'il y a des suggestions d'exception
    has_exception = any(s.type == TestCaseType.EXCEPTION for s in method_suggestions.suggestions)
    assert has_exception, "Devrait avoir des suggestions d'exception"


def test_generate_suggestions_has_collection(suggestions_service):
    """Test que les suggestions incluent des cas pour les collections"""
    # Créer une méthode avec un paramètre List
    method = MethodInfo(
        name="processUsers",
        return_type="void",
        parameters=[
            MethodParameter(name="users", type="List<User>", is_primitive=False, is_collection=True)
        ],
        is_public=True,
        is_static=False,
        is_void=True
    )
    
    method_suggestions = suggestions_service._generate_method_suggestions(method)
    
    # Vérifier qu'il y a des suggestions pour les collections
    has_collection = any(s.type == TestCaseType.EMPTY for s in method_suggestions.suggestions)
    assert has_collection, "Devrait avoir des suggestions pour les collections"


def test_get_valid_value_primitive(suggestions_service):
    """Test la génération de valeurs valides pour les primitifs"""
    param = MethodParameter(name="value", type="int", is_primitive=True, is_collection=False)
    value = suggestions_service._get_valid_value(param)
    assert value == "1"
    
    param_long = MethodParameter(name="id", type="long", is_primitive=True, is_collection=False)
    value_long = suggestions_service._get_valid_value(param_long)
    assert value_long == "1L"


def test_get_valid_value_collection(suggestions_service):
    """Test la génération de valeurs valides pour les collections"""
    param = MethodParameter(name="users", type="List<User>", is_primitive=False, is_collection=True)
    value = suggestions_service._get_valid_value(param)
    assert "emptyList" in value or "Collections" in value


def test_estimate_coverage(suggestions_service, sample_class_analysis):
    """Test l'estimation de couverture"""
    suggestions = suggestions_service.generate_suggestions(sample_class_analysis)
    
    assert 0.0 <= suggestions.coverage_estimate <= 1.0
    # Si on a des suggestions, la couverture devrait être > 0
    if suggestions.total_suggestions > 0:
        assert suggestions.coverage_estimate > 0.0

