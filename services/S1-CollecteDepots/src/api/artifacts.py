"""API endpoints for CI/CD artifacts."""
import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from datetime import datetime
import uuid

from src.services.minio_service import MinIOService
from src.services.kafka_service import KafkaService
from src.services.database_service import DatabaseService
from src.services.cicd_parser import get_parser
from src.models.events import CIArtifactEvent
from src.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/artifacts", tags=["Artifacts"])


def get_services():
    """Dependency to get service instances."""
    return {
        "minio": MinIOService(),
        "kafka": KafkaService(),
        "db": DatabaseService()
    }


@router.post("/upload/{artifact_type}")
async def upload_artifact(
    artifact_type: str,
    repository_id: str,
    commit_sha: str,
    build_id: Optional[str] = None,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    services: dict = Depends(get_services)
):
    """
    Upload CI/CD artifact (JaCoCo, Surefire, or PIT report).
    
    Args:
        artifact_type: Type of artifact (jacoco, surefire, pit)
        repository_id: Repository identifier
        commit_sha: Commit SHA
        build_id: Build identifier (optional, auto-generated if not provided)
        file: Artifact file to upload
    """
    if artifact_type.lower() not in ["jacoco", "surefire", "pit"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid artifact type. Must be one of: jacoco, surefire, pit"
        )
    
    try:
        minio = services["minio"]
        kafka = services["kafka"]
        db = services["db"]
        
        # Ensure repository exists (required for foreign key constraint)
        db.get_or_create_repository(
            repository_id=repository_id,
            name=repository_id.split("/")[-1] if "/" in repository_id else repository_id,
            full_name=repository_id,
            url=f"https://github.com/{repository_id}" if not repository_id.startswith("jira_") and not repository_id.startswith("gitlab_") else f"https://example.com/{repository_id}",
            source="github" if not repository_id.startswith("jira_") and not repository_id.startswith("gitlab_") else ("jira" if repository_id.startswith("jira_") else "gitlab"),
            default_branch="main"
        )
        
        # Generate build_id if not provided
        if not build_id:
            build_id = f"build_{uuid.uuid4().hex[:8]}"
        
        # Read file content
        content = await file.read()
        
        # Upload to MinIO
        artifact_url = minio.upload_artifact(
            artifact_type=artifact_type.lower(),
            repository_id=repository_id,
            commit_sha=commit_sha,
            build_id=build_id,
            content=content,
            content_type=file.content_type or "application/xml"
        )
        
        # Create event
        event = CIArtifactEvent(
            event_id=f"evt_artifact_{uuid.uuid4().hex[:12]}",
            repository_id=repository_id,
            build_id=build_id,
            commit_sha=commit_sha,
            artifact_type=artifact_type.lower(),
            artifact_url=artifact_url,
            timestamp=datetime.utcnow(),
            metadata={
                "filename": file.filename,
                "size": len(content),
                "content_type": file.content_type
            }
        )
        
        # Publish to Kafka
        kafka.publish_artifact(event)
        
        # Store in database
        # Note: artifact_size is stored in metadata_json, not as a separate field
        artifact_metadata = event.metadata.copy()
        artifact_metadata["size"] = len(content)
        
        db.store_artifact({
            "event_id": event.event_id,
            "repository_id": repository_id,
            "build_id": build_id,
            "commit_sha": commit_sha,
            "artifact_type": artifact_type.lower(),
            "artifact_url": artifact_url,
            "timestamp": datetime.utcnow(),
            "metadata_json": artifact_metadata
        })
        
        kafka.flush()
        
        # Parse artifact in background if parser available
        parser = get_parser(artifact_type.lower())
        if parser and background_tasks:
            background_tasks.add_task(
                _parse_artifact,
                parser,
                content,
                repository_id,
                commit_sha,
                db
            )
        
        return {
            "status": "uploaded",
            "artifact_url": artifact_url,
            "event_id": event.event_id,
            "build_id": build_id
        }
        
    except Exception as e:
        logger.error(f"Error uploading artifact: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _parse_artifact(parser, content: bytes, repository_id: str, commit_sha: str, db: DatabaseService):
    """Parse artifact and store metrics in background."""
    try:
        parsed_data = parser.parse_from_content(content)
        
        if "error" not in parsed_data:
            # Store metrics in TimescaleDB
            db.store_repository_metrics({
                "repository_id": repository_id,
                "commit_sha": commit_sha,
                "timestamp": datetime.utcnow(),
                "metrics_json": parsed_data
            })
            logger.info(f"Parsed and stored metrics for {repository_id}@{commit_sha}")
    except Exception as e:
        logger.error(f"Error parsing artifact: {e}")


@router.get("/{repository_id}/{commit_sha}")
async def get_artifacts(
    repository_id: str,
    commit_sha: str,
    artifact_type: Optional[str] = None,
    services: dict = Depends(get_services)
):
    """
    Get artifacts for a specific commit.
    
    Args:
        repository_id: Repository identifier
        commit_sha: Commit SHA
        artifact_type: Optional filter by artifact type
    """
    try:
        db = services["db"]
        
        with db.get_session() as session:
            from src.models.database import CIArtifact
            from sqlalchemy import and_
            
            query = session.query(CIArtifact).filter(
                and_(
                    CIArtifact.repository_id == repository_id,
                    CIArtifact.commit_sha == commit_sha
                )
            )
            
            if artifact_type:
                query = query.filter(CIArtifact.artifact_type == artifact_type.lower())
            
            artifacts = query.all()
            
            return {
                "repository_id": repository_id,
                "commit_sha": commit_sha,
                "artifacts": [
                    {
                        "build_id": a.build_id,
                        "artifact_type": a.artifact_type,
                        "artifact_url": a.artifact_url,
                        "timestamp": a.timestamp.isoformat(),
                        "size": a.artifact_size
                    }
                    for a in artifacts
                ]
            }
    except Exception as e:
        logger.error(f"Error getting artifacts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

