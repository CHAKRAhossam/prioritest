"""
Service de stockage Git pour les suggestions de tests

MTP-S7-06: Stockage suggestions
- Sauvegarde les tests générés dans un dépôt Git
- Organise les fichiers par classe
- Crée des commits avec les suggestions
- Gère les branches si nécessaire
"""
import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, List
from git import Repo, GitCommandError
from datetime import datetime


class GitStorageService:
    """
    Service pour stocker les suggestions de tests dans un dépôt Git.
    
    Fonctionnalités :
    - Cloner ou utiliser un dépôt Git existant
    - Créer les fichiers de test dans la structure appropriée
    - Faire des commits avec les suggestions
    - Gérer les branches
    """
    
    def __init__(self, repo_url: Optional[str] = None, repo_path: Optional[str] = None):
        """
        Initialise le service de stockage Git.
        
        Args:
            repo_url: URL du dépôt Git (pour cloner)
            repo_path: Chemin local du dépôt Git (si déjà cloné)
        """
        self.repo_url = repo_url or os.getenv('GIT_REPO_URL', '')
        self.repo_path = repo_path
        self.repo = None
    
    def initialize_repo(self, clone_if_not_exists: bool = True) -> bool:
        """
        Initialise ou clone le dépôt Git.
        
        Args:
            clone_if_not_exists: Si True, clone le dépôt s'il n'existe pas
        
        Returns:
            True si le dépôt est prêt, False sinon
        """
        if self.repo_path and Path(self.repo_path).exists():
            try:
                self.repo = Repo(self.repo_path)
                return True
            except Exception as e:
                print(f"Erreur lors de l'ouverture du dépôt: {e}")
                return False
        
        if clone_if_not_exists and self.repo_url:
            try:
                # Créer un répertoire temporaire pour le dépôt
                temp_dir = tempfile.mkdtemp(prefix='test_scaffolder_')
                self.repo = Repo.clone_from(self.repo_url, temp_dir)
                self.repo_path = temp_dir
                return True
            except Exception as e:
                print(f"Erreur lors du clonage du dépôt: {e}")
                return False
        
        return False
    
    def save_test_file(
        self,
        test_code: str,
        class_name: str,
        test_class_name: str,
        test_package: str,
        branch: Optional[str] = None,
        commit_message: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Sauvegarde un fichier de test dans le dépôt Git.
        
        Args:
            test_code: Code source Java du test
            class_name: Nom de la classe testée
            test_class_name: Nom de la classe de test
            test_package: Package de la classe de test
            branch: Branche où sauvegarder (défaut: branche actuelle)
            commit_message: Message de commit (défaut: généré automatiquement)
        
        Returns:
            Dictionnaire avec les informations du commit (sha, file_path, etc.)
        """
        if not self.repo:
            if not self.initialize_repo():
                raise Exception("Impossible d'initialiser le dépôt Git")
        
        # Créer le chemin du fichier basé sur le package
        package_path = test_package.replace('.', '/')
        test_file_path = Path(self.repo_path) / "src" / "test" / "java" / package_path / f"{test_class_name}.java"
        
        # Créer les répertoires si nécessaire
        test_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Écrire le fichier
        test_file_path.write_text(test_code, encoding='utf-8')
        
        # Changer de branche si nécessaire
        if branch and branch != self.repo.active_branch.name:
            try:
                if branch in [b.name for b in self.repo.branches]:
                    self.repo.git.checkout(branch)
                else:
                    self.repo.git.checkout('-b', branch)
            except GitCommandError as e:
                print(f"Erreur lors du changement de branche: {e}")
        
        # Ajouter le fichier
        self.repo.index.add([str(test_file_path.relative_to(self.repo_path))])
        
        # Créer le commit
        if not commit_message:
            commit_message = f"feat(test): Ajouter tests générés pour {class_name}"
        
        commit = self.repo.index.commit(commit_message)
        
        return {
            'commit_sha': commit.hexsha,
            'file_path': str(test_file_path.relative_to(self.repo_path)),
            'branch': self.repo.active_branch.name,
            'message': commit_message
        }
    
    def save_suggestions_file(
        self,
        suggestions: Dict,
        class_name: str,
        branch: Optional[str] = None,
        commit_message: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Sauvegarde un fichier de suggestions (JSON) dans le dépôt Git.
        
        Args:
            suggestions: Dictionnaire contenant les suggestions
            class_name: Nom de la classe
            branch: Branche où sauvegarder
            commit_message: Message de commit
        
        Returns:
            Dictionnaire avec les informations du commit
        """
        import json
        
        if not self.repo:
            if not self.initialize_repo():
                raise Exception("Impossible d'initialiser le dépôt Git")
        
        # Créer le chemin du fichier de suggestions
        suggestions_dir = Path(self.repo_path) / "test-suggestions"
        suggestions_dir.mkdir(exist_ok=True)
        
        suggestions_file = suggestions_dir / f"{class_name}_suggestions.json"
        
        # Écrire le fichier JSON
        suggestions_file.write_text(
            json.dumps(suggestions, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        
        # Changer de branche si nécessaire
        if branch and branch != self.repo.active_branch.name:
            try:
                if branch in [b.name for b in self.repo.branches]:
                    self.repo.git.checkout(branch)
                else:
                    self.repo.git.checkout('-b', branch)
            except GitCommandError as e:
                print(f"Erreur lors du changement de branche: {e}")
        
        # Ajouter le fichier
        self.repo.index.add([str(suggestions_file.relative_to(self.repo_path))])
        
        # Créer le commit
        if not commit_message:
            commit_message = f"docs(test): Ajouter suggestions de tests pour {class_name}"
        
        commit = self.repo.index.commit(commit_message)
        
        return {
            'commit_sha': commit.hexsha,
            'file_path': str(suggestions_file.relative_to(self.repo_path)),
            'branch': self.repo.active_branch.name,
            'message': commit_message
        }
    
    def push_changes(
        self,
        branch: Optional[str] = None,
        remote: str = 'origin'
    ) -> bool:
        """
        Pousse les changements vers le dépôt distant.
        
        Args:
            branch: Branche à pousser (défaut: branche actuelle)
            remote: Nom du remote (défaut: origin)
        
        Returns:
            True si le push a réussi, False sinon
        """
        if not self.repo:
            return False
        
        try:
            branch_name = branch or self.repo.active_branch.name
            self.repo.remote(remote).push(branch_name)
            return True
        except Exception as e:
            print(f"Erreur lors du push: {e}")
            return False
    
    def create_branch(self, branch_name: str) -> bool:
        """
        Crée une nouvelle branche.
        
        Args:
            branch_name: Nom de la branche
        
        Returns:
            True si la branche a été créée, False sinon
        """
        if not self.repo:
            if not self.initialize_repo():
                return False
        
        try:
            if branch_name not in [b.name for b in self.repo.branches]:
                self.repo.git.checkout('-b', branch_name)
                return True
            else:
                self.repo.git.checkout(branch_name)
                return True
        except Exception as e:
            print(f"Erreur lors de la création de la branche: {e}")
            return False
    
    def cleanup(self):
        """Nettoie les ressources temporaires"""
        # Si on a cloné dans un répertoire temporaire, on peut le supprimer
        # (mais attention, cela supprimera aussi les changements non commités)
        pass

