"""
Tests pour le générateur de mocks
"""
import pytest
from src.services.mock_generator import MockGenerator
from src.models.ast_models import FieldInfo, MethodInfo, MethodParameter, ClassAnalysis


@pytest.fixture
def mock_generator():
    """Fixture pour créer un générateur de mocks"""
    return MockGenerator()


def test_mock_generator_initialization(mock_generator):
    """Test que le générateur s'initialise correctement"""
    assert mock_generator is not None


def test_generate_mock_declarations(mock_generator):
    """Test la génération de déclarations de mocks"""
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
    
    mock_declarations = mock_generator.generate_mock_declarations(fields)
    
    # Seul userRepository devrait être mocké (pas int)
    assert len(mock_declarations) == 1
    assert mock_declarations[0]['name'] == "userRepository"


def test_generate_mock_setup(mock_generator):
    """Test la génération de configuration de mocks"""
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
    
    mock_fields = [
        {'name': 'userRepository', 'type': 'UserRepository', 'annotations': [], 'is_final': False}
    ]
    
    setup_lines = mock_generator.generate_mock_setup(method, mock_fields, "userService")
    
    assert isinstance(setup_lines, list)


def test_generate_mock_verify(mock_generator):
    """Test la génération de verify() pour méthodes void"""
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
    
    mock_fields = [
        {'name': 'userRepository', 'type': 'UserRepository', 'annotations': [], 'is_final': False}
    ]
    
    verify_lines = mock_generator.generate_mock_verify(method, mock_fields)
    
    assert isinstance(verify_lines, list)
    # Pour une méthode void avec un Repository, on devrait avoir des suggestions de verify
    if verify_lines:
        assert any('verify' in line.lower() for line in verify_lines)


def test_generate_mock_for_collection(mock_generator):
    """Test la génération de mocks pour collections"""
    list_mock = mock_generator.generate_mock_for_collection("mockList", "List<String>")
    assert "emptyList" in list_mock or "Collections" in list_mock
    
    set_mock = mock_generator.generate_mock_for_collection("mockSet", "Set<String>")
    assert "emptySet" in set_mock or "Collections" in set_mock


def test_generate_mock_for_optional(mock_generator):
    """Test la génération de mocks pour Optional"""
    optional_mock = mock_generator.generate_mock_for_optional("mockOptional", "Optional<User>")
    assert "Optional" in optional_mock


def test_generate_complete_mock_setup(mock_generator):
    """Test la génération complète de configuration de mocks"""
    class_analysis = ClassAnalysis(
        class_name="UserService",
        full_qualified_name="com.example.UserService",
        fields=[
            FieldInfo(
                name="userRepository",
                type="UserRepository",
                is_private=True,
                is_public=False,
                is_final=False,
                is_static=False,
                annotations=[]
            )
        ],
        methods=[
            MethodInfo(
                name="getUserById",
                return_type="User",
                parameters=[
                    MethodParameter(name="userId", type="Long", is_primitive=False, is_collection=False)
                ],
                is_public=True,
                is_static=False,
                is_void=False
            )
        ]
    )
    
    method = class_analysis.methods[0]
    mock_config = mock_generator.generate_complete_mock_setup(class_analysis, method)
    
    assert 'setup' in mock_config
    assert 'verify' in mock_config
    assert isinstance(mock_config['setup'], list)
    assert isinstance(mock_config['verify'], list)


def test_get_default_return_value(mock_generator):
    """Test la génération de valeurs de retour par défaut"""
    assert mock_generator._get_default_return_value("int") == "0"
    assert mock_generator._get_default_return_value("long") == "0L"
    assert mock_generator._get_default_return_value("boolean") == "false"
    assert "emptyList" in mock_generator._get_default_return_value("List<String>")
    assert "Optional" in mock_generator._get_default_return_value("Optional<User>")


