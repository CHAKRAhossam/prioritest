"""
Tests pour le service de checklist de mutation testing
"""
import pytest
from src.services.mutation_checklist import MutationChecklistService
from src.services.ast_analyzer import ASTAnalyzer
from src.models.ast_models import ClassAnalysis, MethodInfo, MethodParameter
from src.models.mutation_checklist import MutationOperator


@pytest.fixture
def mutation_checklist_service():
    """Fixture pour créer un service de checklist"""
    return MutationChecklistService()


@pytest.fixture
def sample_java_code():
    """Fixture pour charger le code Java de test"""
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


def test_mutation_checklist_service_initialization(mutation_checklist_service):
    """Test que le service s'initialise correctement"""
    assert mutation_checklist_service is not None


def test_generate_checklist_basic(mutation_checklist_service, sample_class_analysis):
    """Test la génération basique d'une checklist"""
    checklist = mutation_checklist_service.generate_checklist(sample_class_analysis)
    
    assert checklist is not None
    assert checklist.class_name == sample_class_analysis.class_name
    assert checklist.total_items > 0
    assert len(checklist.method_checklists) > 0


def test_generate_checklist_has_return_vals(mutation_checklist_service):
    """Test que la checklist inclut ReturnValsMutator pour méthodes avec retour"""
    method = MethodInfo(
        name="getUserById",
        return_type="User",
        parameters=[
            MethodParameter(name="userId", type="Long", is_primitive=False, is_collection=False)
        ],
        is_public=True,
        is_static=False,
        is_void=False
    )
    
    method_checklist = mutation_checklist_service._generate_method_checklist(method)
    
    # Vérifier qu'il y a une suggestion pour ReturnValsMutator
    has_return_vals = any(
        item.operator == MutationOperator.RETURN_VALS 
        for item in method_checklist.items
    )
    assert has_return_vals, "Devrait avoir une suggestion pour ReturnValsMutator"


def test_generate_checklist_has_void_method_calls(mutation_checklist_service):
    """Test que la checklist inclut VoidMethodCallsMutator pour méthodes void"""
    method = MethodInfo(
        name="deleteUser",
        return_type="void",
        parameters=[
            MethodParameter(name="userId", type="Long", is_primitive=False, is_collection=False)
        ],
        is_public=True,
        is_static=False,
        is_void=True
    )
    
    method_checklist = mutation_checklist_service._generate_method_checklist(method)
    
    # Vérifier qu'il y a une suggestion pour VoidMethodCallsMutator
    has_void_calls = any(
        item.operator == MutationOperator.VOID_METHOD_CALLS 
        for item in method_checklist.items
    )
    assert has_void_calls, "Devrait avoir une suggestion pour VoidMethodCallsMutator"


def test_generate_checklist_has_conditionals(mutation_checklist_service):
    """Test que la checklist inclut des suggestions pour conditionnelles"""
    method = MethodInfo(
        name="processValue",
        return_type="int",
        parameters=[
            MethodParameter(name="value", type="int", is_primitive=True, is_collection=False),
            MethodParameter(name="threshold", type="int", is_primitive=True, is_collection=False)
        ],
        is_public=True,
        is_static=False,
        is_void=False,
        throws_exceptions=["IllegalArgumentException"]
    )
    
    method_checklist = mutation_checklist_service._generate_method_checklist(method)
    
    # Vérifier qu'il y a des suggestions pour conditionnelles
    has_conditionals = any(
        item.operator in [MutationOperator.CONDITIONALS_BOUNDARY, MutationOperator.NEGATE_CONDITIONALS]
        for item in method_checklist.items
    )
    assert has_conditionals, "Devrait avoir des suggestions pour conditionnelles"


def test_generate_checklist_has_exceptions(mutation_checklist_service):
    """Test que la checklist inclut des suggestions pour exceptions"""
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
    
    method_checklist = mutation_checklist_service._generate_method_checklist(method)
    
    # Vérifier qu'il y a des suggestions pour exceptions
    has_exceptions = any(
        "exception" in item.description.lower() or "Exception" in item.description
        for item in method_checklist.items
    )
    assert has_exceptions, "Devrait avoir des suggestions pour exceptions"


def test_estimate_mutation_coverage(mutation_checklist_service, sample_class_analysis):
    """Test l'estimation de couverture mutation"""
    checklist = mutation_checklist_service.generate_checklist(sample_class_analysis)
    
    assert 0.0 <= checklist.coverage_estimate <= 1.0
    # Si on a des items, la couverture devrait être > 0
    if checklist.total_items > 0:
        assert checklist.coverage_estimate > 0.0


