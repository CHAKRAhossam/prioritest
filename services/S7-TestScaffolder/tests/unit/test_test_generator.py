"""
Tests pour le générateur de tests JUnit
"""
import pytest
from pathlib import Path
from src.services.test_generator import TestGenerator
from src.services.ast_analyzer import ASTAnalyzer
from src.models.ast_models import ClassAnalysis

# Chemin vers le fichier de test
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
SAMPLE_JAVA_FILE = FIXTURES_DIR / "sample_java_class.java"


@pytest.fixture
def test_generator():
    """Fixture pour créer un générateur de tests"""
    return TestGenerator()


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
}
"""


@pytest.fixture
def sample_class_analysis(sample_java_code):
    """Fixture pour créer une analyse de classe"""
    analyzer = ASTAnalyzer()
    result = analyzer.analyze_class(sample_java_code)
    return ClassAnalysis(**result)


def test_test_generator_initialization(test_generator):
    """Test que le générateur s'initialise correctement"""
    assert test_generator is not None
    assert test_generator.template_dir.exists()


def test_generate_test_class_basic(test_generator, sample_class_analysis):
    """Test la génération basique d'une classe de test"""
    test_code = test_generator.generate_test_class(sample_class_analysis)
    
    assert test_code is not None
    assert len(test_code) > 0
    # Vérifier que le code contient des éléments JUnit
    assert "@Test" in test_code or "@ExtendWith" in test_code
    assert "class" in test_code


def test_generate_test_class_contains_test_methods(test_generator, sample_class_analysis):
    """Test que la classe générée contient des méthodes de test"""
    test_code = test_generator.generate_test_class(sample_class_analysis)
    
    # Vérifier qu'il y a au moins une méthode de test
    assert "@Test" in test_code or "void test" in test_code.lower()


def test_generate_test_class_contains_mocks(test_generator, sample_class_analysis):
    """Test que la classe générée contient des mocks"""
    test_code = test_generator.generate_test_class(sample_class_analysis)
    
    # Si la classe a des dépendances, vérifier les mocks
    if sample_class_analysis.fields:
        assert "@Mock" in test_code or "Mockito" in test_code


def test_generate_test_class_package(test_generator, sample_class_analysis):
    """Test que le package de test est correct"""
    test_code = test_generator.generate_test_class(
        sample_class_analysis,
        test_package="com.example.test"
    )
    
    assert "package com.example.test;" in test_code


def test_generate_test_class_name(test_generator, sample_class_analysis):
    """Test que le nom de la classe de test est correct"""
    test_code = test_generator.generate_test_class(
        sample_class_analysis,
        test_class_suffix="Test"
    )
    
    expected_class_name = f"{sample_class_analysis.class_name}Test"
    assert expected_class_name in test_code


def test_extract_mock_fields(test_generator):
    """Test l'extraction des champs à mocker"""
    from src.models.ast_models import FieldInfo
    
    fields = [
        FieldInfo(
            name="userRepository",
            type="UserRepository",
            is_private=True,
            is_public=False,
            is_final=False,
            is_static=False,
            annotations=[]
        ),
        FieldInfo(
            name="count",
            type="int",
            is_private=True,
            is_public=False,
            is_final=False,
            is_static=False,
            annotations=[]
        )
    ]
    
    mock_fields = test_generator._extract_mock_fields(fields)
    
    # Seul userRepository devrait être mocké (pas int)
    assert len(mock_fields) == 1
    assert mock_fields[0]['name'] == "userRepository"


def test_get_default_value(test_generator):
    """Test la génération de valeurs par défaut"""
    assert test_generator._get_default_value("int", True) == "0"
    assert test_generator._get_default_value("boolean", True) == "false"
    assert test_generator._get_default_value("String", False) == "null"
    assert "emptyList" in test_generator._get_default_value("List<String>", False)


def test_to_camel_case(test_generator):
    """Test la conversion en camelCase"""
    assert test_generator._to_camel_case("UserService") == "userService"
    assert test_generator._to_camel_case("Test") == "test"
    assert test_generator._to_camel_case("") == ""

