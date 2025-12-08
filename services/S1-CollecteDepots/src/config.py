"""Configuration management for S1-CollecteDepots service."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "CollecteDepots"
    app_version: str = "1.0.0"
    log_level: str = "INFO"
    environment: str = "development"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8001
    
    # GitHub API
    github_token: Optional[str] = None
    github_webhook_secret: Optional[str] = None
    
    # GitLab API
    gitlab_token: Optional[str] = None
    gitlab_url: str = "https://gitlab.com"
    gitlab_webhook_secret: Optional[str] = None
    
    # Jira API
    jira_url: Optional[str] = None
    jira_email: Optional[str] = None
    jira_api_token: Optional[str] = None
    
    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic_commits: str = "repository.commits"
    kafka_topic_issues: str = "repository.issues"
    kafka_topic_artifacts: str = "ci.artifacts"
    
    # PostgreSQL/TimescaleDB
    database_url: str = "postgresql://prioritest:prioritest@localhost:5432/prioritest"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    
    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_secure: bool = False
    minio_bucket_artifacts: str = "ci-artifacts"
    minio_bucket_repos: str = "repository-snapshots"
    
    # DVC
    dvc_remote: str = "s3"
    dvc_s3_endpoint_url: str = "http://localhost:9000"
    dvc_s3_access_key_id: str = "minioadmin"
    dvc_s3_secret_access_key: str = "minioadmin"
    dvc_data_dir: str = "./data"
    enable_dvc: bool = True
    
    # Git operations
    git_temp_dir: str = "./temp-repos"
    git_clone_timeout: int = 300
    
    # Retry configuration
    max_retries: int = 3
    retry_delay: int = 1
    
    # Feature flags
    enable_timescale: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()

