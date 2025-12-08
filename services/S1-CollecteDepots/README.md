# Service S1 - Collecte de Dépôts

**Responsable :** Haytam Ta  
**Email :** haytamnajam14@gmail.com

## Description

Service d'ingestion des dépôts Git/GitHub/GitLab, issues/bugs (Jira/GitHub Issues), et artefacts CI/CD (rapports tests/couverture).

Ce service collecte automatiquement ou manuellement :
- **Commits** : Historique des commits avec fichiers modifiés
- **Issues** : Bugs et features depuis Jira/GitHub Issues
- **Artefacts CI/CD** : Rapports JaCoCo, Surefire, PIT

## Architecture

### Entrées

1. **Webhooks** (automatique)
   - GitHub : `/api/v1/webhooks/github`
   - GitLab : `/api/v1/webhooks/gitlab`
   - Jira : `/api/v1/webhooks/jira`

2. **API REST** (manuel)
   - `POST /api/v1/collect` : Déclencher une collecte manuelle

### Sorties (Kafka Topics)

- `repository.commits` : Événements de commits
- `repository.issues` : Événements d'issues
- `ci.artifacts` : Événements d'artefacts CI/CD

### Stockage

- **PostgreSQL/TimescaleDB** : Métadonnées des dépôts, commits, issues
- **MinIO** : Artefacts CI/CD (rapports JaCoCo, Surefire, PIT)
- **DVC** : Versioning des jeux de données internes

## Technologies

- **FastAPI** : Framework web Python
- **Kafka** : Streaming d'événements
- **PostgreSQL/TimescaleDB** : Base de données relationnelle et time-series
- **MinIO** : Stockage objet S3-compatible
- **PyGithub** : Client GitHub API
- **python-gitlab** : Client GitLab API
- **jira** : Client Jira API
- **DVC** : Data Version Control
- **SQLAlchemy** : ORM Python
- **confluent-kafka** : Client Kafka Python

## Installation

### Prérequis

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL/TimescaleDB
- Kafka
- MinIO

### Installation locale

```bash
cd services/S1-CollecteDepots
pip install -r requirements.txt
```

### Configuration

1. Copier `.env.example` vers `.env` :
```bash
cp .env.example .env
```

2. Configurer les variables d'environnement :
```env
# GitHub
GITHUB_TOKEN=your_github_token_here
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here

# GitLab
GITLAB_TOKEN=your_gitlab_token_here
GITLAB_URL=https://gitlab.com
GITLAB_WEBHOOK_SECRET=your_webhook_secret_here

# Jira
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your_email@example.com
JIRA_API_TOKEN=your_jira_api_token_here

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/prioritest

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

### Démarrage

#### Avec Docker Compose (recommandé)

```bash
# Depuis la racine du projet
docker-compose up -d collecte-depots
```

#### Localement

```bash
# Démarrer les dépendances (PostgreSQL, Kafka, MinIO)
docker-compose up -d postgres kafka minio

# Démarrer le service
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

## API Documentation

Une fois le service démarré, accéder à la documentation interactive :
- **Swagger UI** : http://localhost:8001/docs
- **ReDoc** : http://localhost:8001/redoc

### Endpoints principaux

#### Health Check
```http
GET /health
```

#### Collecte manuelle
```http
POST /api/v1/collect
Content-Type: application/json

{
  "repository_url": "https://github.com/org/repo",
  "collect_type": "commits|issues|ci_reports",
  "date_range": {
    "start": "2025-01-01",
    "end": "2025-12-04"
  }
}
```

#### Webhooks

**GitHub**
```http
POST /api/v1/webhooks/github
X-GitHub-Event: push
X-Hub-Signature-256: sha256=...
```

**GitLab**
```http
POST /api/v1/webhooks/gitlab
X-Gitlab-Event: Push Hook
X-Gitlab-Token: ...
```

**Jira**
```http
POST /api/v1/webhooks/jira
```

## Structure du projet

```
S1-CollecteDepots/
├── src/
│   ├── api/              # Endpoints FastAPI
│   │   ├── collect.py   # API de collecte manuelle
│   │   └── webhooks.py  # Webhooks GitHub/GitLab/Jira
│   ├── models/          # Modèles de données
│   │   ├── events.py    # Modèles Pydantic pour Kafka
│   │   └── database.py  # Modèles SQLAlchemy
│   ├── services/        # Services métier
│   │   ├── github_service.py
│   │   ├── gitlab_service.py
│   │   ├── jira_service.py
│   │   ├── kafka_service.py
│   │   ├── database_service.py
│   │   ├── minio_service.py
│   │   ├── cicd_parser.py
│   │   └── dvc_service.py
│   ├── config.py        # Configuration
│   └── main.py          # Application FastAPI
├── tests/               # Tests unitaires
├── requirements.txt     # Dépendances Python
├── Dockerfile          # Image Docker
├── .env.example        # Exemple de configuration
└── README.md           # Documentation
```

## User Stories

- ✅ **US-S1-01** : Intégration Git/GitHub
- ✅ **US-S1-02** : Intégration GitLab
- ✅ **US-S1-03** : Intégration Jira
- ✅ **US-S1-04** : Collecte des rapports CI/CD
- ✅ **US-S1-05** : Pipeline Kafka et stockage

## Fonctionnalités

### 1. Collecte de commits

- Collecte via API GitHub/GitLab
- Parsing des webhooks push
- Extraction des fichiers modifiés
- Publication vers Kafka topic `repository.commits`
- Stockage dans PostgreSQL

### 2. Collecte d'issues

- Collecte via API Jira/GitHub Issues
- Parsing des webhooks issues
- Extraction des commits liés
- Publication vers Kafka topic `repository.issues`
- Stockage dans PostgreSQL

### 3. Collecte d'artefacts CI/CD

- Parsers pour JaCoCo, Surefire, PIT
- Téléchargement depuis URLs
- Upload vers MinIO
- Publication vers Kafka topic `ci.artifacts`
- Stockage des métadonnées dans PostgreSQL

### 4. Versioning DVC

- Initialisation automatique de DVC
- Configuration du remote S3 (MinIO)
- Versioning des datasets internes

## Tests

```bash
# Exécuter les tests
pytest tests/

# Avec couverture
pytest tests/ --cov=src --cov-report=html
```

## Développement

### Ajout d'un nouveau parser CI/CD

1. Créer une classe héritant de `CIArtifactParser`
2. Implémenter `parse_from_content(content: bytes) -> Dict[str, Any]`
3. Ajouter dans `get_parser()` dans `cicd_parser.py`

### Ajout d'un nouveau service d'intégration

1. Créer un service dans `src/services/`
2. Implémenter les méthodes `collect_commits()` et/ou `collect_issues()`
3. Implémenter `parse_webhook()` pour les webhooks
4. Ajouter les endpoints dans `src/api/webhooks.py`

## Monitoring

- **Health check** : `GET /health`
- **Status** : `GET /api/v1/collect/status`

## Troubleshooting

### Kafka connection failed
- Vérifier que Kafka est démarré : `docker-compose ps kafka`
- Vérifier `KAFKA_BOOTSTRAP_SERVERS` dans `.env`

### Database connection failed
- Vérifier que PostgreSQL est démarré : `docker-compose ps postgres`
- Vérifier `DATABASE_URL` dans `.env`
- Vérifier les credentials PostgreSQL

### MinIO connection failed
- Vérifier que MinIO est démarré : `docker-compose ps minio`
- Vérifier `MINIO_ENDPOINT` et les credentials dans `.env`

## Contribution

Pour contribuer au service :

1. Créer une branche depuis `main`
2. Implémenter les fonctionnalités
3. Ajouter les tests
4. Vérifier que tous les tests passent
5. Créer une pull request

## Licence

Ce projet fait partie du projet PRIORITEST.
