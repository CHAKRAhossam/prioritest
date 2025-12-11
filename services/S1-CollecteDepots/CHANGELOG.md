# Changelog

All notable changes to the S1-CollecteDepots service will be documented in this file.

## [1.0.0] - 2025-12-04

### Added
- **GitHub Integration**
  - Collect commits via GitHub API
  - Collect issues via GitHub Issues API
  - Webhook support for push and issue events
  - Automatic signature verification

- **GitLab Integration**
  - Collect commits via GitLab API
  - Collect issues via GitLab Issues API
  - Webhook support for push and issue events
  - Token-based authentication

- **Jira Integration**
  - Collect issues from Jira projects
  - Webhook support for issue created/updated events
  - JQL query support

- **CI/CD Artifacts**
  - Upload endpoint for JaCoCo, Surefire, and PIT reports
  - Parsers for all three artifact types
  - Automatic storage in MinIO
  - Metrics extraction and storage

- **Kafka Integration**
  - Producer for publishing events to Kafka topics
  - Topics: `repository.commits`, `repository.issues`, `ci.artifacts`
  - Automatic topic creation

- **Database Integration**
  - PostgreSQL/TimescaleDB support
  - SQLAlchemy ORM models
  - Automatic schema initialization
  - TimescaleDB hypertable support for time-series metrics

- **MinIO Integration**
  - Artifact storage in S3-compatible object storage
  - Automatic bucket creation
  - Repository snapshot storage

- **DVC Integration**
  - Data versioning support
  - S3 remote configuration
  - Dataset versioning

- **API Endpoints**
  - Manual collection endpoint (`POST /api/v1/collect`)
  - Webhook endpoints for GitHub, GitLab, and Jira
  - Artifact upload endpoint (`POST /api/v1/artifacts/upload/{type}`)
  - Health check endpoint (`GET /health`)
  - Status endpoint (`GET /api/v1/collect/status`)

- **Testing**
  - Unit tests for services
  - Unit tests for parsers
  - Unit tests for Kafka service

- **Documentation**
  - Comprehensive README
  - API documentation (Swagger/ReDoc)
  - Configuration guide

### Technical Details
- FastAPI framework
- Python 3.11+
- Docker support
- Alembic for database migrations
- Comprehensive error handling and logging

