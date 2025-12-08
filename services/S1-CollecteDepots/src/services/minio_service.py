"""MinIO service for storing CI/CD artifacts."""
import logging
from io import BytesIO
from typing import Optional
from minio import Minio
from minio.error import S3Error

from src.config import settings

logger = logging.getLogger(__name__)


class MinIOService:
    """Service for MinIO object storage operations."""
    
    def __init__(self):
        """Initialize MinIO client."""
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure
        )
        self._ensure_buckets_exist()
    
    def _ensure_buckets_exist(self):
        """Ensure required buckets exist."""
        buckets = [
            settings.minio_bucket_artifacts,
            settings.minio_bucket_repos
        ]
        
        for bucket in buckets:
            try:
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)
                    logger.info(f"Created bucket: {bucket}")
                else:
                    logger.debug(f"Bucket {bucket} already exists")
            except S3Error as e:
                logger.error(f"Error creating bucket {bucket}: {e}")
                raise
    
    def upload_artifact(
        self,
        artifact_type: str,
        repository_id: str,
        commit_sha: str,
        build_id: str,
        content: bytes,
        content_type: str = "application/xml"
    ) -> str:
        """
        Upload CI/CD artifact to MinIO.
        
        Args:
            artifact_type: Type of artifact (jacoco, surefire, pit)
            repository_id: Repository identifier
            commit_sha: Commit SHA
            build_id: Build identifier
            content: Artifact content as bytes
            content_type: Content type (default: application/xml)
            
        Returns:
            str: Object path in MinIO
        """
        try:
            # Construct object path: artifacts/{repo_id}/{commit_sha}/{artifact_type}_{build_id}.xml
            object_path = f"{repository_id}/{commit_sha}/{artifact_type}_{build_id}.xml"
            
            # Upload to MinIO
            self.client.put_object(
                settings.minio_bucket_artifacts,
                object_path,
                BytesIO(content),
                length=len(content),
                content_type=content_type
            )
            
            # Construct URL
            protocol = "https" if settings.minio_secure else "http"
            url = f"{protocol}://{settings.minio_endpoint}/{settings.minio_bucket_artifacts}/{object_path}"
            
            logger.info(f"Uploaded artifact {object_path} to MinIO")
            return url
            
        except S3Error as e:
            logger.error(f"Error uploading artifact to MinIO: {e}")
            raise
    
    def upload_repository_snapshot(
        self,
        repository_id: str,
        commit_sha: str,
        content: bytes,
        filename: str
    ) -> str:
        """
        Upload repository snapshot to MinIO.
        
        Args:
            repository_id: Repository identifier
            commit_sha: Commit SHA
            content: Snapshot content as bytes
            filename: Filename for the snapshot
            
        Returns:
            str: Object path in MinIO
        """
        try:
            object_path = f"{repository_id}/{commit_sha}/{filename}"
            
            self.client.put_object(
                settings.minio_bucket_repos,
                object_path,
                BytesIO(content),
                length=len(content)
            )
            
            protocol = "https" if settings.minio_secure else "http"
            url = f"{protocol}://{settings.minio_endpoint}/{settings.minio_bucket_repos}/{object_path}"
            
            logger.info(f"Uploaded snapshot {object_path} to MinIO")
            return url
            
        except S3Error as e:
            logger.error(f"Error uploading snapshot to MinIO: {e}")
            raise
    
    def download_artifact(self, object_path: str) -> Optional[bytes]:
        """
        Download artifact from MinIO.
        
        Args:
            object_path: Path to object in bucket
            
        Returns:
            bytes: Artifact content or None if not found
        """
        try:
            response = self.client.get_object(settings.minio_bucket_artifacts, object_path)
            content = response.read()
            response.close()
            response.release_conn()
            return content
        except S3Error as e:
            logger.error(f"Error downloading artifact from MinIO: {e}")
            return None
    
    def delete_artifact(self, object_path: str) -> bool:
        """
        Delete artifact from MinIO.
        
        Args:
            object_path: Path to object in bucket
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            self.client.remove_object(settings.minio_bucket_artifacts, object_path)
            logger.info(f"Deleted artifact {object_path} from MinIO")
            return True
        except S3Error as e:
            logger.error(f"Error deleting artifact from MinIO: {e}")
            return False

