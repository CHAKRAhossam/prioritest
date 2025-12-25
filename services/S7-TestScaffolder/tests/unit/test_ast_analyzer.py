"""
Tests pour l'analyseur AST
"""
import pytest
from pathlib import Path
from src.services.ast_analyzer import ASTAnalyzer
from src.models.ast_models import ClassAnalysis, MethodInfo, FieldInfo

# Chemin vers le fichier de test
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
SAMPLE_JAVA_FILE = FIXTURES_DIR / "sample_java_class.java"


@pytest.fixture
def ast_analyzer():
    """Fixture pour créer un analyseur AST"""
    return ASTAnalyzer()


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
    public User getUserById(Long userId) {
        return null;
    }
}
"""


def test_ast_analyzer_initialization(ast_analyzer):
    """Test que l'analyseur AST s'initialise correctement"""
    assert ast_analyzer is not None


def test_analyze_class_basic(ast_analyzer, sample_java_code):
    """Test l'analyse basique d'une classe"""
    result = ast_analyzer.analyze_class(sample_java_code)
    
    assert result is not None
    assert 'class_name' in result
    assert 'methods' in result
    assert 'fields' in result
    assert 'imports' in result


def test_extract_class_name(ast_analyzer, sample_java_code):
    """Test l'extraction du nom de classe"""
    result = ast_analyzer.analyze_class(sample_java_code)
    
    assert result['class_name'] == 'UserService'


def test_extract_package(ast_analyzer, sample_java_code):
    """Test l'extraction du package"""
    result = ast_analyzer.analyze_class(sample_java_code)
    
    assert result['package_name'] == 'com.example.service'


def test_extract_methods(ast_analyzer, sample_java_code):
    """Test l'extraction des méthodes"""
    result = ast_analyzer.analyze_class(sample_java_code)
    
    assert len(result['methods']) > 0
    # Vérifier qu'on trouve au moins getUserById
    method_names = [m['name'] for m in result['methods']]
    assert 'getUserById' in method_names


def test_extract_imports(ast_analyzer, sample_java_code):
    """Test l'extraction des imports"""
    result = ast_analyzer.analyze_class(sample_java_code)
    
    assert len(result['imports']) > 0
    assert 'org.springframework.stereotype.Service' in result['imports']


def test_full_qualified_name(ast_analyzer, sample_java_code):
    """Test la construction du nom qualifié complet"""
    result = ast_analyzer.analyze_class(sample_java_code)
    
    assert result['full_qualified_name'] == 'com.example.service.UserService'


def test_parse_basic_fallback(ast_analyzer):
    """Test le parser basique en fallback"""
    simple_code = """
package com.test;
public class SimpleClass {
    public void method() {}
}
"""
    result = ast_analyzer._parse_basic(simple_code)
    
    assert result is not None
    assert result['class_name'] == 'SimpleClass'
    assert result['package_name'] == 'com.test'












