"""DVC service for dataset versioning."""
import logging
import subprocess
import os
from pathlib import Path
from typing import Optional

from src.config import settings

logger = logging.getLogger(__name__)


class DVCService:
    """Service for DVC (Data Version Control) operations."""
    
    def __init__(self):
        """Initialize DVC service."""
        self.data_dir = Path(settings.dvc_data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        if not settings.enable_dvc:
            logger.info("DVC is disabled")
            return
        
        # Initialize DVC if not already initialized
        self._init_dvc()
    
    def _init_dvc(self):
        """Initialize DVC repository."""
        try:
            # Check if DVC is already initialized
            if (self.data_dir / ".dvc").exists():
                logger.debug("DVC already initialized")
                return
            
            # Initialize DVC
            subprocess.run(
                ["dvc", "init", "--no-scm"],
                cwd=self.data_dir,
                check=True,
                capture_output=True
            )
            logger.info("DVC initialized")
            
            # Configure remote if not already configured
            self._configure_remote()
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"DVC initialization failed: {e}")
        except FileNotFoundError:
            logger.warning("DVC not installed, skipping initialization")
    
    def _configure_remote(self):
        """Configure DVC remote storage."""
        try:
            # Check if remote already exists
            result = subprocess.run(
                ["dvc", "remote", "list"],
                cwd=self.data_dir,
                capture_output=True,
                text=True
            )
            
            if settings.dvc_remote in result.stdout:
                logger.debug("DVC remote already configured")
                return
            
            # Configure S3 remote
            subprocess.run(
                [
                    "dvc", "remote", "add", "-d", settings.dvc_remote,
                    f"s3://dvc-data"
                ],
                cwd=self.data_dir,
                check=True,
                capture_output=True
            )
            
            # Set S3 endpoint
            subprocess.run(
                [
                    "dvc", "remote", "modify", settings.dvc_remote,
                    "endpointurl", settings.dvc_s3_endpoint_url
                ],
                cwd=self.data_dir,
                check=True,
                capture_output=True
            )
            
            # Set credentials via environment
            os.environ["AWS_ACCESS_KEY_ID"] = settings.dvc_s3_access_key_id
            os.environ["AWS_SECRET_ACCESS_KEY"] = settings.dvc_s3_secret_access_key
            
            logger.info("DVC remote configured")
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"DVC remote configuration failed: {e}")
    
    def add_and_commit(self, file_path: str, message: str = "Update dataset") -> bool:
        """
        Add file to DVC and commit.
        
        Args:
            file_path: Path to file relative to data directory
            message: Commit message
            
        Returns:
            bool: True if successful
        """
        if not settings.enable_dvc:
            return False
        
        try:
            full_path = self.data_dir / file_path
            
            if not full_path.exists():
                logger.error(f"File not found: {full_path}")
                return False
            
            # Add file to DVC
            subprocess.run(
                ["dvc", "add", file_path],
                cwd=self.data_dir,
                check=True,
                capture_output=True
            )
            
            # Push to remote
            subprocess.run(
                ["dvc", "push"],
                cwd=self.data_dir,
                check=True,
                capture_output=True
            )
            
            logger.info(f"Added and committed {file_path} to DVC")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"DVC add/commit failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Error in DVC operation: {e}")
            return False
    
    def get_file(self, file_path: str) -> Optional[Path]:
        """
        Get file from DVC (pull if needed).
        
        Args:
            file_path: Path to file relative to data directory
            
        Returns:
            Path to file or None if not found
        """
        if not settings.enable_dvc:
            return None
        
        try:
            full_path = self.data_dir / file_path
            
            # Pull from remote if needed
            subprocess.run(
                ["dvc", "pull", file_path],
                cwd=self.data_dir,
                check=False,
                capture_output=True
            )
            
            if full_path.exists():
                return full_path
            else:
                logger.warning(f"File not found after pull: {file_path}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting file from DVC: {e}")
            return None

