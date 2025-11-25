# Service 1 - Collecte de Dépôts

**Responsable :** Haytam Ta  
**Email :** haytamnajam14@gmail.com

## Description

Ingestion des dépôts (Git/GitHub/GitLab), issues/bugs (Jira/GitHub Issues), artefacts CI (rapports tests/couverture).

## Technologies

- JGit (Java) pour Git
- GitHub API / GitLab API
- Jira API
- Kafka pour le streaming
- PostgreSQL pour les métadonnées
- MinIO pour les artefacts
- TimescaleDB pour les séries temporelles

## User Stories

- US-S1-01: Intégration Git/GitHub
- US-S1-02: Intégration GitLab
- US-S1-03: Intégration Jira
- US-S1-04: Collecte des rapports CI/CD
- US-S1-05: Pipeline Kafka et stockage

## Installation

```bash
cd services/S1-CollecteDepots
pip install -r requirements.txt
```

## Configuration

Copiez `.env.example` vers `.env` et configurez :
- GitHub API token
- GitLab API token
- Jira API credentials
- Kafka brokers
- PostgreSQL connection
- MinIO credentials

