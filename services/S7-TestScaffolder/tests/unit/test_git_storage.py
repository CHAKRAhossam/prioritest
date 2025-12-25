"""
Tests pour le service de stockage Git
"""
import pytest
import tempfile
import os
from pathlib import Path
from src.services.git_storage import GitStorageService


@pytest.fixture
def temp_repo():
    """Fixture pour créer un dépôt Git temporaire"""
    from git import Repo
    temp_dir = tempfile.mkdtemp(prefix='test_git_storage_')
    repo = Repo.init(temp_dir)
    
    # Créer un fichier initial pour avoir un commit
    readme = Path(temp_dir) / "README.md"
    readme.write_text("# Test Repository")
    repo.index.add([str(readme)])
    repo.index.commit("Initial commit")
    
    yield temp_dir, repo
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_git_storage_service_initialization():
    """Test que le service s'initialise correctement"""
    service = GitStorageService()
    assert service is not None
    assert service.repo is None


def test_git_storage_with_repo_path(temp_repo):
    """Test l'initialisation avec un chemin de dépôt"""
    temp_dir, _ = temp_repo
    service = GitStorageService(repo_path=temp_dir)
    assert service.repo_path == temp_dir


def test_initialize_repo_with_existing_path(temp_repo):
    """Test l'initialisation d'un dépôt existant"""
    temp_dir, _ = temp_repo
    service = GitStorageService(repo_path=temp_dir)
    result = service.initialize_repo(clone_if_not_exists=False)
    assert result is True
    assert service.repo is not None


def test_save_test_file(temp_repo):
    """Test la sauvegarde d'un fichier de test"""
    temp_dir, _ = temp_repo
    service = GitStorageService(repo_path=temp_dir)
    service.initialize_repo(clone_if_not_exists=False)
    
    test_code = """
package com.example.test;

import org.junit.jupiter.api.Test;

class UserServiceTest {
    @Test
    void testMethod() {
    }
}
"""
    
    result = service.save_test_file(
        test_code=test_code,
        class_name="UserService",
        test_class_name="UserServiceTest",
        test_package="com.example.test"
    )
    
    assert result is not None
    assert 'commit_sha' in result
    assert 'file_path' in result
    assert 'branch' in result
    
    # Vérifier que le fichier existe
    file_path = Path(temp_dir) / result['file_path']
    assert file_path.exists()
    assert file_path.read_text(encoding='utf-8') == test_code


def test_save_suggestions_file(temp_repo):
    """Test la sauvegarde d'un fichier de suggestions"""
    temp_dir, _ = temp_repo
    service = GitStorageService(repo_path=temp_dir)
    service.initialize_repo(clone_if_not_exists=False)
    
    suggestions = {
        'class_name': 'UserService',
        'suggestions': [
            {'type': 'equivalence', 'description': 'Test avec valeur valide'}
        ]
    }
    
    result = service.save_suggestions_file(
        suggestions=suggestions,
        class_name="UserService"
    )
    
    assert result is not None
    assert 'commit_sha' in result
    assert 'file_path' in result
    
    # Vérifier que le fichier existe
    file_path = Path(temp_dir) / result['file_path']
    assert file_path.exists()


def test_create_branch(temp_repo):
    """Test la création d'une branche"""
    temp_dir, _ = temp_repo
    service = GitStorageService(repo_path=temp_dir)
    service.initialize_repo(clone_if_not_exists=False)
    
    result = service.create_branch("feature/test-branch")
    assert result is True
    assert service.repo.active_branch.name == "feature/test-branch"


def test_save_test_file_with_branch(temp_repo):
    """Test la sauvegarde dans une branche spécifique"""
    temp_dir, _ = temp_repo
    service = GitStorageService(repo_path=temp_dir)
    service.initialize_repo(clone_if_not_exists=False)
    
    # Créer une branche
    service.create_branch("feature/tests")
    
    test_code = "package test; class Test {}"
    
    result = service.save_test_file(
        test_code=test_code,
        class_name="Test",
        test_class_name="TestTest",
        test_package="test",
        branch="feature/tests"
    )
    
    assert result['branch'] == "feature/tests"












