"""
SQLAlchemy database models for S1-CollecteDepots service.

This module defines the database schema for storing:
- Repository metadata
- Commits
- Issues
- CI/CD artifacts
- Repository metrics (TimescaleDB)
"""
from sqlalchemy import (
    Column, String, Integer, DateTime, Text, JSON, ForeignKey,
    Boolean, Float, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Repository(Base):
    """Repository metadata table."""
    __tablename__ = "repositories"
    
    id = Column(String, primary_key=True, index=True, comment="Repository ID")
    name = Column(String, nullable=False, comment="Repository name")
    full_name = Column(String, nullable=False, index=True, comment="Full name (owner/repo)")
    url = Column(String, nullable=False, comment="Repository URL")
    source = Column(String, nullable=False, index=True, comment="Source (github, gitlab, etc.)")
    default_branch = Column(String, default="main", comment="Default branch")
    metadata_json = Column(JSON, comment="Additional metadata as JSON")
    created_at = Column(DateTime, default=datetime.utcnow, comment="Creation timestamp")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="Update timestamp")
    
    # Relationships
    commits = relationship("Commit", back_populates="repository", cascade="all, delete-orphan")
    issues = relationship("Issue", back_populates="repository", cascade="all, delete-orphan")
    artifacts = relationship("CIArtifact", back_populates="repository", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Repository(id={self.id}, name={self.name})>"


class Commit(Base):
    """Commit table for storing commit information."""
    __tablename__ = "commits"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String, unique=True, index=True, comment="Event ID from Kafka")
    repository_id = Column(String, ForeignKey("repositories.id"), nullable=False, index=True)
    commit_sha = Column(String, nullable=False, index=True, comment="Commit SHA")
    commit_message = Column(Text, comment="Commit message")
    author_email = Column(String, index=True, comment="Author email")
    author_name = Column(String, comment="Author name")
    timestamp = Column(DateTime, nullable=False, index=True, comment="Commit timestamp")
    files_changed = Column(JSON, comment="List of files changed with status")
    metadata_json = Column(JSON, comment="Additional metadata (source, branch, etc.)")
    created_at = Column(DateTime, default=datetime.utcnow, comment="Record creation timestamp")
    
    # Relationships
    repository = relationship("Repository", back_populates="commits")
    
    # Indexes
    __table_args__ = (
        Index('idx_commits_repo_sha', 'repository_id', 'commit_sha'),
        Index('idx_commits_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<Commit(sha={self.commit_sha[:8]}, repo={self.repository_id})>"


class Issue(Base):
    """Issue table for storing issue/bug information."""
    __tablename__ = "issues"
    
    id = Column[int](Integer, primary_key=True, autoincrement=True)
    event_id = Column(String, unique=True, index=True, comment="Event ID from Kafka")
    repository_id = Column(String, ForeignKey("repositories.id"), nullable=False, index=True)
    issue_key = Column(String, nullable=False, index=True, comment="Issue key (e.g., MTP-77)")
    issue_type = Column(String, comment="Issue type (Bug, Feature, etc.)")
    summary = Column(Text, comment="Issue summary/title")
    status = Column(String, index=True, comment="Issue status (Open, Closed, etc.)")
    created_at = Column(DateTime, nullable=False, index=True, comment="Issue creation timestamp")
    linked_commits = Column(JSON, comment="List of commit SHAs linked to this issue")
    metadata_json = Column(JSON, comment="Additional metadata")
    created_at_record = Column(DateTime, default=datetime.utcnow, comment="Record creation timestamp")
    
    # Relationships
    repository = relationship("Repository", back_populates="issues")
    
    # Indexes
    __table_args__ = (
        Index('idx_issues_repo_key', 'repository_id', 'issue_key'),
        Index('idx_issues_status', 'status'),
    )
    
    def __repr__(self):
        return f"<Issue(key={self.issue_key}, repo={self.repository_id})>"


class CIArtifact(Base):
    """CI/CD artifact table for storing artifact metadata."""
    __tablename__ = "ci_artifacts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String, unique=True, index=True, comment="Event ID from Kafka")
    repository_id = Column(String, ForeignKey("repositories.id"), nullable=False, index=True)
    build_id = Column(String, nullable=False, index=True, comment="Build ID")
    commit_sha = Column(String, nullable=False, index=True, comment="Commit SHA")
    artifact_type = Column(String, nullable=False, index=True, comment="Artifact type (jacoco, surefire, pit)")
    artifact_url = Column(String, nullable=False, comment="Artifact URL in MinIO")
    timestamp = Column(DateTime, nullable=False, index=True, comment="Artifact timestamp")
    metadata_json = Column(JSON, comment="Additional metadata")
    created_at = Column(DateTime, default=datetime.utcnow, comment="Record creation timestamp")
    
    # Relationships
    repository = relationship("Repository", back_populates="artifacts")
    
    # Indexes
    __table_args__ = (
        Index('idx_artifacts_repo_commit', 'repository_id', 'commit_sha'),
        Index('idx_artifacts_type', 'artifact_type'),
    )
    
    def __repr__(self):
        return f"<CIArtifact(type={self.artifact_type}, build={self.build_id})>"


class RepositoryMetadata(Base):
    """
    Repository metrics table for TimescaleDB.
    This table is converted to a hypertable for time-series data.
    """
    __tablename__ = "repository_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    repository_id = Column(String, ForeignKey("repositories.id"), nullable=False, index=True)
    commit_sha = Column(String, nullable=False, index=True, comment="Commit SHA")
    timestamp = Column(DateTime, nullable=False, index=True, comment="Metrics timestamp (for TimescaleDB)")
    
    # Metrics
    lines_added = Column(Integer, default=0, comment="Lines added in commit")
    lines_deleted = Column(Integer, default=0, comment="Lines deleted in commit")
    files_changed = Column(Integer, default=0, comment="Number of files changed")
    num_commits = Column(Integer, default=1, comment="Number of commits")
    num_issues = Column(Integer, default=0, comment="Number of issues")
    
    # Additional metrics as JSON
    metrics_json = Column(JSON, comment="Additional metrics as JSON")
    created_at = Column(DateTime, default=datetime.utcnow, comment="Record creation timestamp")
    
    # Indexes for TimescaleDB
    __table_args__ = (
        Index('idx_metrics_repo_timestamp', 'repository_id', 'timestamp'),
        Index('idx_metrics_commit', 'commit_sha'),
    )
    
    def __repr__(self):
        return f"<RepositoryMetadata(repo={self.repository_id}, commit={self.commit_sha[:8]})>"

