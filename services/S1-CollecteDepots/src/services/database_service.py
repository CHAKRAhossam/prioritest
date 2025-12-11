"""Database service for PostgreSQL/TimescaleDB operations."""
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from src.config import settings
from src.models.database import Base, Repository, Commit, Issue, CIArtifact, RepositoryMetadata

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for database operations."""
    
    def __init__(self):
        """Initialize database connection."""
        self.engine = create_engine(
            settings.database_url,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_pre_ping=True,
            echo=False
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema and TimescaleDB extension if enabled."""
        try:
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created/verified")
            
            # Enable TimescaleDB extension if configured
            if settings.enable_timescale:
                try:
                    with self.engine.connect() as conn:
                        conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"))
                        conn.commit()
                        logger.info("TimescaleDB extension enabled")
                        
                        # Convert repository_metrics to hypertable if not already
                        try:
                            conn.execute(text(
                                "SELECT create_hypertable('repository_metrics', 'timestamp', "
                                "if_not_exists => TRUE);"
                            ))
                            conn.commit()
                            logger.info("TimescaleDB hypertable created for repository_metrics")
                        except Exception as e:
                            if "already a hypertable" in str(e).lower():
                                logger.debug("repository_metrics already a hypertable")
                            else:
                                logger.warning(f"Could not create hypertable: {e}")
                except Exception as e:
                    logger.warning(f"TimescaleDB not available: {e}")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    @contextmanager
    def get_session(self):
        """Get database session context manager."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def get_or_create_repository(
        self,
        repository_id: str,
        name: str,
        full_name: str,
        url: str,
        source: str,
        default_branch: str = "main",
        metadata_json: dict = None
    ) -> Repository:
        """Get or create a repository record."""
        with self.get_session() as session:
            repo = session.query(Repository).filter(Repository.id == repository_id).first()
            if not repo:
                repo = Repository(
                    id=repository_id,
                    name=name,
                    full_name=full_name,
                    url=url,
                    source=source,
                    default_branch=default_branch,
                    metadata_json=metadata_json
                )
                session.add(repo)
                session.commit()
                session.refresh(repo)
                logger.info(f"Created repository {repository_id}")
            return repo
    
    def store_commit(self, commit_data: dict) -> Commit:
        """Store commit in database."""
        with self.get_session() as session:
            # Check if commit already exists
            existing = session.query(Commit).filter(
                Commit.repository_id == commit_data['repository_id'],
                Commit.commit_sha == commit_data['commit_sha']
            ).first()
            
            if existing:
                logger.debug(f"Commit {commit_data['commit_sha']} already exists")
                return existing
            
            commit = Commit(**commit_data)
            session.add(commit)
            session.commit()
            session.refresh(commit)
            logger.info(f"Stored commit {commit_data['commit_sha']}")
            return commit
    
    def store_issue(self, issue_data: dict) -> Issue:
        """Store issue in database."""
        with self.get_session() as session:
            # Check if issue already exists
            existing = session.query(Issue).filter(
                Issue.repository_id == issue_data['repository_id'],
                Issue.issue_key == issue_data['issue_key']
            ).first()
            
            if existing:
                # Update existing issue
                for key, value in issue_data.items():
                    if key != 'id':
                        setattr(existing, key, value)
                session.commit()
                session.refresh(existing)
                logger.debug(f"Updated issue {issue_data['issue_key']}")
                return existing
            
            issue = Issue(**issue_data)
            session.add(issue)
            session.commit()
            session.refresh(issue)
            logger.info(f"Stored issue {issue_data['issue_key']}")
            return issue
    
    def store_artifact(self, artifact_data: dict) -> CIArtifact:
        """Store CI artifact in database."""
        with self.get_session() as session:
            artifact = CIArtifact(**artifact_data)
            session.add(artifact)
            session.commit()
            session.refresh(artifact)
            logger.info(f"Stored artifact {artifact_data['build_id']}")
            return artifact
    
    def store_repository_metrics(self, metrics_data: dict) -> RepositoryMetadata:
        """Store repository metrics in TimescaleDB."""
        with self.get_session() as session:
            metrics = RepositoryMetadata(**metrics_data)
            session.add(metrics)
            session.commit()
            session.refresh(metrics)
            logger.info(f"Stored metrics for {metrics_data['repository_id']} at {metrics_data['commit_sha']}")
            return metrics

