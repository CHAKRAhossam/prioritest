# Matrice de Communication - ML Test Prioritization Platform

## Vue d'Ensemble

Ce document détaille toutes les communications entre les microservices de la plateforme, incluant les protocoles, topics Kafka, endpoints REST, et formats de données.

---

## Légende

- **Kafka** : Communication asynchrone via Apache Kafka
- **REST** : Communication synchrone via API REST
- **SQL** : Communication directe avec base de données
- **S3/MinIO** : Stockage d'objets
- **WebSocket** : Communication temps réel bidirectionnelle
- **Webhook** : Événements externes (GitHub/GitLab/Jira)

---

## Matrice Complète

### S1 → S2 (CollecteDepots → AnalyseStatique)

| Propriété | Détails |
|-----------|---------|
| **Méthode** | Kafka |
| **Topic** | `repository.commits` |
| **Format** | JSON |
| **Direction** | Asynchrone (Producer → Consumer) |
| **Fréquence** | Event-driven (à chaque commit) |
| **Schéma** | Voir [ARCHITECTURE_COMPLETE.md](./ARCHITECTURE_COMPLETE.md#service-1--collectedepots-haytam-ta) |

**Exemple de message :**
```json
{
  "event_id": "evt_123",
  "repository_id": "repo_12345",
  "commit_sha": "abc123",
  "commit_message": "Fix bug in UserService",
  "author_email": "developer@example.com",
  "timestamp": "2025-12-04T10:30:00Z",
  "files_changed": [
    {
      "path": "src/UserService.java",
      "status": "modified"
    }
  ]
}
```

---

### S1 → S3 (CollecteDepots → HistoriqueTests)

| Propriété | Détails |
|-----------|---------|
| **Méthode** | Kafka |
| **Topic** | `ci.artifacts` |
| **Format** | JSON |
| **Direction** | Asynchrone (Producer → Consumer) |
| **Fréquence** | Event-driven (à chaque build CI/CD) |
| **Schéma** | Voir [ARCHITECTURE_COMPLETE.md](./ARCHITECTURE_COMPLETE.md#service-1--collectedepots-haytam-ta) |

**Exemple de message :**
```json
{
  "event_id": "evt_125",
  "repository_id": "repo_12345",
  "build_id": "build_789",
  "commit_sha": "abc123",
  "artifact_type": "jacoco",
  "artifact_url": "s3://minio/artifacts/jacoco_abc123.xml",
  "timestamp": "2025-12-04T10:35:00Z"
}
```

---

### S1 → PostgreSQL (CollecteDepots → Database)

| Propriété | Détails |
|-----------|---------|
| **Méthode** | SQL (via SQLAlchemy/psycopg2) |
| **Tables** | `repositories`, `commits`, `issues` |
| **Format** | SQL INSERT/UPDATE |
| **Direction** | Synchrone |
| **Fréquence** | À chaque collecte |

**Schéma de table `repositories` :**
```sql
CREATE TABLE repositories (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    full_name VARCHAR NOT NULL,
    url VARCHAR NOT NULL,
    source VARCHAR NOT NULL, -- 'github', 'gitlab', etc.
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

### S1 → MinIO (CollecteDepots → Object Storage)

| Propriété | Détails |
|-----------|---------|
| **Méthode** | S3 API (boto3) |
| **Bucket** | `ci-artifacts`, `repository-snapshots` |
| **Format** | Binary (XML, JSON, etc.) |
| **Direction** | Synchrone |
| **Fréquence** | À chaque artefact collecté |

**Exemple de chemin :**
```
s3://minio/ci-artifacts/jacoco_abc123.xml
s3://minio/repository-snapshots/repo_12345_abc123.tar.gz
```

---

### S1 → TimescaleDB (CollecteDepots → Time Series DB)

| Propriété | Détails |
|-----------|---------|
| **Méthode** | SQL (via psycopg2) |
| **Table** | `commit_metrics` (hypertable) |
| **Format** | SQL INSERT |
| **Direction** | Synchrone |
| **Fréquence** | À chaque commit avec métriques |

**Schéma de table `commit_metrics` :**
```sql
CREATE TABLE commit_metrics (
    time TIMESTAMPTZ NOT NULL,
    repository_id VARCHAR NOT NULL,
    commit_sha VARCHAR NOT NULL,
    metric_name VARCHAR NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL
);

SELECT create_hypertable('commit_metrics', 'time');
```

---

### S2 → S4 (AnalyseStatique → PrétraitementFeatures)

| Propriété | Détails |
|-----------|---------|
| **Méthode** | Kafka |
| **Topic** | `code.metrics` |
| **Format** | JSON |
| **Direction** | Asynchrone (Producer → Consumer) |
| **Fréquence** | Event-driven (à chaque analyse) |
| **Schéma** | Voir [ARCHITECTURE_COMPLETE.md](./ARCHITECTURE_COMPLETE.md#service-2--analysestatique-haytam-ta) |

**Exemple de message :**
```json
{
  "event_id": "evt_126",
  "repository_id": "repo_12345",
  "commit_sha": "abc123",
  "class_name": "com.example.UserService",
  "file_path": "src/UserService.java",
  "metrics": {
    "loc": 150,
    "cyclomatic_complexity": 12,
    "ck_metrics": {
      "wmc": 8,
      "dit": 2,
      "cbo": 5
    }
  },
  "timestamp": "2025-12-04T10:40:00Z"
}
```

---

### S2 → Feast (AnalyseStatique → Feature Store)

| Propriété | Détails |
|-----------|---------|
| **Méthode** | Feast SDK (Python) |
| **Feature Store** | `code_metrics` |
| **Format** | Protobuf (via Feast) |
| **Direction** | Synchrone |
| **Fréquence** | À chaque analyse |

**Exemple d'utilisation :**
```python
from feast import FeatureStore

fs = FeatureStore(repo_path="feature_repo")
fs.write_to_online_store(
    feature_data={
        "class_name": "com.example.UserService",
        "repository_id": "repo_12345"
    },
    features={
        "loc": 150,
        "cyclomatic_complexity": 12
    }
)
```

---

### S3 → S4, S6, S8 (HistoriqueTests → Autres Services)

| Propriété | Détails |
|-----------|---------|
| **Méthode** | REST API |
| **Endpoint** | `GET /api/v1/test-metrics` |
| **Format** | JSON |
| **Direction** | Synchrone (Request/Response) |
| **Fréquence** | On-demand |

**Exemple de requête :**
```http
GET /api/v1/test-metrics?class_name=com.example.UserService&repository_id=repo_12345
```

**Exemple de réponse :**
```json
{
  "class_name": "com.example.UserService",
  "repository_id": "repo_12345",
  "current_coverage": {
    "line_coverage": 0.85,
    "branch_coverage": 0.78
  },
  "test_history": [...],
  "test_debt": {
    "has_tests": true,
    "coverage_below_threshold": false
  }
}
```

---

### S3 → TimescaleDB (HistoriqueTests → Time Series DB)

| Propriété | Détails |
|-----------|---------|
| **Méthode** | SQL (via JDBC/HikariCP) |
| **Table** | `test_history` (hypertable) |
| **Format** | SQL INSERT |
| **Direction** | Synchrone |
| **Fréquence** | À chaque traitement d'artefact |

**Schéma de table `test_history` :**
```sql
CREATE TABLE test_history (
    time TIMESTAMPTZ NOT NULL,
    repository_id VARCHAR NOT NULL,
    commit_sha VARCHAR NOT NULL,
    class_name VARCHAR NOT NULL,
    line_coverage DOUBLE PRECISION,
    branch_coverage DOUBLE PRECISION,
    tests_passed INTEGER,
    tests_failed INTEGER,
    mutation_score DOUBLE PRECISION
);

SELECT create_hypertable('test_history', 'time');
```

---

### S4 → S5 (PrétraitementFeatures → MLService)

| Propriété | Détails |
|-----------|---------|
| **Méthode** | Feast Feature Store |
| **Feature Store** | `processed_features` |
| **Format** | Protobuf (via Feast) |
| **Direction** | Synchrone (via Feast) |
| **Fréquence** | À chaque prétraitement |

**Exemple d'utilisation :**
```python
from feast import FeatureStore

fs = FeatureStore(repo_path="feature_repo")
features = fs.get_online_features(
    entity_rows=[{
        "class_name": "com.example.UserService",
        "repository_id": "repo_12345"
    }],
    features=[
        "processed_features:loc",
        "processed_features:churn",
        "processed_features:bug_fix_proximity"
    ]
)
```

---

### S5 → S6, S8 (MLService → MoteurPriorisation, Dashboard)

| Propriété | Détails |
|-----------|---------|
| **Méthode** | REST API |
| **Endpoint** | `POST /api/v1/predict` |
| **Format** | JSON |
| **Direction** | Synchrone (Request/Response) |
| **Fréquence** | On-demand |

**Exemple de requête :**
```http
POST /api/v1/predict
Content-Type: application/json

{
  "class_name": "com.example.UserService",
  "repository_id": "repo_12345",
  "features": {
    "loc": 150,
    "cyclomatic_complexity": 12,
    "churn": 0.15
  }
}
```

**Exemple de réponse :**
```json
{
  "class_name": "com.example.UserService",
  "risk_score": 0.75,
  "risk_level": "high",
  "uncertainty": 0.12,
  "shap_values": {
    "loc": 0.15,
    "cyclomatic_complexity": 0.20,
    "churn": 0.10
  }
}
```

---

### S5 → MLflow (MLService → ML Tracking)

| Propriété | Détails |
|-----------|---------|
| **Méthode** | MLflow Tracking API |
| **Endpoint** | `http://mlflow:5000` |
| **Format** | REST API + Artifacts (MinIO) |
| **Direction** | Synchrone |
| **Fréquence** | À chaque entraînement/expérience |

**Exemple d'utilisation :**
```python
import mlflow

mlflow.set_tracking_uri("http://mlflow:5000")
mlflow.log_metric("f1_score", 0.82)
mlflow.log_model(model, "xgboost_model")
```

---

### S5 → MinIO (MLService → Object Storage)

| Propriété | Détails |
|-----------|---------|
| **Méthode** | S3 API (boto3) |
| **Bucket** | `ml-models` |
| **Format** | Binary (pickle, joblib, etc.) |
| **Direction** | Synchrone |
| **Fréquence** | À chaque sauvegarde de modèle |

**Exemple de chemin :**
```
s3://minio/ml-models/xgboost_v1.pkl
```

---

### S6 → S7, S8 (MoteurPriorisation → TestScaffolder, Dashboard)

| Propriété | Détails |
|-----------|---------|
| **Méthode** | REST API |
| **Endpoint** | `POST /api/v1/prioritize`, `GET /api/v1/prioritize/{repository_id}` |
| **Format** | JSON |
| **Direction** | Synchrone (Request/Response) |
| **Fréquence** | On-demand |

**Exemple de requête :**
```http
POST /api/v1/prioritize
Content-Type: application/json

{
  "repository_id": "repo_12345",
  "sprint_id": "sprint_1",
  "constraints": {
    "budget_hours": 40,
    "target_coverage": 0.85
  }
}
```

**Exemple de réponse :**
```json
{
  "prioritized_plan": [
    {
      "class_name": "com.example.UserService",
      "priority": 1,
      "risk_score": 0.75,
      "effort_hours": 4,
      "effort_aware_score": 0.1875
    }
  ],
  "metrics": {
    "total_effort_hours": 35,
    "popt20_score": 0.85
  }
}
```

---

### S6 → PostgreSQL (MoteurPriorisation → Database)

| Propriété | Détails |
|-----------|---------|
| **Méthode** | SQL (via SQLAlchemy) |
| **Table** | `prioritization_plans` |
| **Format** | SQL INSERT/UPDATE |
| **Direction** | Synchrone |
| **Fréquence** | À chaque priorisation |

**Schéma de table `prioritization_plans` :**
```sql
CREATE TABLE prioritization_plans (
    plan_id VARCHAR PRIMARY KEY,
    sprint_id VARCHAR,
    repository_id VARCHAR NOT NULL,
    prioritized_classes JSONB NOT NULL,
    metrics JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### S7 → S8, S9 (TestScaffolder → Dashboard, Integrations)

| Propriété | Détails |
|-----------|---------|
| **Méthode** | REST API |
| **Endpoint** | `GET /api/v1/test-scaffold`, `POST /api/v1/test-scaffold/batch` |
| **Format** | JSON |
| **Direction** | Synchrone (Request/Response) |
| **Fréquence** | On-demand |

**Exemple de requête :**
```http
GET /api/v1/test-scaffold?class_name=com.example.UserService&priority=1
```

**Exemple de réponse :**
```json
{
  "class_name": "com.example.UserService",
  "test_file_path": "tests/UserServiceTest.java",
  "test_template": "public class UserServiceTest {...}",
  "suggested_test_cases": [...],
  "mutation_checklist": [...]
}
```

---

### S7 → Git Repository (TestScaffolder → Git)

| Propriété | Détails |
|-----------|---------|
| **Méthode** | Git API (GitPython) |
| **Repository** | `tests-suggestions` |
| **Format** | Git commits |
| **Direction** | Synchrone |
| **Fréquence** | À chaque génération de test |

**Exemple d'utilisation :**
```python
from git import Repo

repo = Repo.clone_from("https://github.com/org/tests-suggestions.git", "/tmp/repo")
# Commit test files
repo.index.commit("Add test for UserService")
repo.remote().push()
```

---

### S8 → Frontend (DashboardQualité → React.js)

| Propriété | Détails |
|-----------|---------|
| **Méthode** | REST API + WebSocket |
| **Endpoints** | `GET /api/v1/dashboard/overview`, `WebSocket /ws/dashboard` |
| **Format** | JSON |
| **Direction** | Bidirectionnelle (REST + WebSocket) |
| **Fréquence** | On-demand (REST) + Real-time (WebSocket) |

**Exemple WebSocket :**
```json
{
  "event_type": "coverage_update",
  "data": {
    "repository_id": "repo_12345",
    "class_name": "com.example.UserService",
    "current_coverage": 0.85,
    "risk_score": 0.75
  },
  "timestamp": "2025-12-04T11:05:00Z"
}
```

---

### S9 → GitHub/GitLab (Integrations → CI/CD)

| Propriété | Détails |
|-----------|---------|
| **Méthode** | GitHub/GitLab API |
| **Endpoints** | GitHub Checks API, GitLab MR API |
| **Format** | JSON |
| **Direction** | Synchrone |
| **Fréquence** | Event-driven (webhooks) |

**Exemple GitHub Check :**
```json
{
  "state": "failure",
  "description": "Test prioritization check",
  "details": {
    "high_risk_classes_modified": 2,
    "tests_added": 0,
    "recommendation": "Add tests for UserService"
  }
}
```

**Exemple GitLab Comment :**
```json
{
  "body": "⚠️ Warning: Modified class 'UserService' has high risk score (0.75) but no tests added."
}
```

---

## Diagramme de Flux de Communication

```
┌─────────────┐
│   GitHub    │
│  GitLab     │──Webhook──→┌──────────────┐
│   Jira      │            │      S1       │
└─────────────┘            │  Collecte    │
                           └──────┬───────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ↓             ↓             ↓
              ┌─────────┐   ┌─────────┐   ┌─────────┐
              │  Kafka   │   │PostgreSQL│   │  MinIO   │
              └────┬─────┘   └─────────┘   └────┬─────┘
                   │                            │
                   ↓                            ↓
              ┌─────────┐                  ┌─────────┐
              │   S2    │                  │   S3    │
              │ Analyse │                  │Historique│
              └────┬─────┘                  └────┬─────┘
                   │                             │
                   ↓                             ↓
              ┌─────────┐                  ┌─────────┐
              │  Feast   │                  │TimescaleDB│
              └────┬─────┘                  └─────────┘
                   │
                   ↓
              ┌─────────┐
              │   S4    │
              │Pretrait │
              └────┬─────┘
                   │
                   ↓
              ┌─────────┐
              │  Feast   │
              └────┬─────┘
                   │
                   ↓
              ┌─────────┐
              │   S5    │
              │   ML    │
              └────┬─────┘
                   │
         ┌─────────┼─────────┐
         ↓         ↓         ↓
    ┌─────────┐ ┌──────┐ ┌──────┐
    │ MLflow  │ │MinIO │ │  S6  │
    └─────────┘ └──────┘ └───┬──┘
                             │
                    ┌────────┼────────┐
                    ↓        ↓        ↓
               ┌──────┐ ┌──────┐ ┌──────┐
               │  S7  │ │  S8  │ │PostgreSQL│
               └───┬──┘ └───┬──┘ └─────────┘
                   │        │
                   ↓        ↓
              ┌──────┐ ┌──────┐
              │ Git  │ │React │
              └──────┘ └──────┘
                   │
                   ↓
              ┌──────┐
              │  S9  │
              └───┬──┘
                  │
                  ↓
         ┌─────────────┐
         │ GitHub/GitLab│
         └─────────────┘
```

---

## Résumé des Protocoles

| Protocole | Services Utilisés | Cas d'Usage |
|-----------|-------------------|------------|
| **Kafka** | S1→S2, S1→S3, S2→S4 | Communication asynchrone événementielle |
| **REST API** | S3→S4/S6/S8, S5→S6/S8, S6→S7/S8, S7→S8/S9 | Communication synchrone on-demand |
| **SQL** | S1→PostgreSQL, S3→TimescaleDB, S6→PostgreSQL | Stockage persistant |
| **S3/MinIO** | S1→MinIO, S5→MinIO | Stockage d'objets (artefacts, modèles) |
| **Feast** | S2→Feast, S4→Feast, S5→Feast | Feature Store (online/offline) |
| **MLflow** | S5→MLflow | Tracking d'expériences ML |
| **WebSocket** | S8→Frontend | Communication temps réel |
| **Webhook** | GitHub/GitLab→S1/S9 | Événements externes |
| **Git API** | S7→Git | Versioning de tests générés |

---

## Configuration des Topics Kafka

### Topics Principaux

1. **repository.commits**
   - Producer : S1
   - Consumer : S2
   - Partitions : 3
   - Replication : 1

2. **repository.issues**
   - Producer : S1
   - Consumer : S6 (optionnel)
   - Partitions : 3
   - Replication : 1

3. **ci.artifacts**
   - Producer : S1
   - Consumer : S3
   - Partitions : 3
   - Replication : 1

4. **code.metrics**
   - Producer : S2
   - Consumer : S4
   - Partitions : 3
   - Replication : 1

---

## Configuration des Endpoints REST

### Base URLs par Service

- **S1 - CollecteDepots** : `http://collecte-depots:8001`
- **S3 - HistoriqueTests** : `http://historique-tests:8003`
- **S5 - MLService** : `http://ml-service:8005`
- **S6 - MoteurPriorisation** : `http://moteur-priorisation:8006`
- **S7 - TestScaffolder** : `http://test-scaffolder:8007`
- **S8 - DashboardQualité** : `http://dashboard:8008`
- **S9 - Integrations** : `http://integrations:8009`

---

## Gestion des Erreurs

### Retry Policies

- **Kafka** : Retry automatique avec backoff exponentiel (max 3 tentatives)
- **REST API** : Retry avec circuit breaker (max 3 tentatives)
- **SQL** : Retry avec connection pooling (max 5 tentatives)

### Timeouts

- **Kafka** : 30 secondes
- **REST API** : 10 secondes
- **SQL** : 5 secondes
- **S3/MinIO** : 60 secondes

---

## Monitoring et Observabilité

### Métriques de Communication

- **Latence** : Temps de réponse par endpoint/topic
- **Throughput** : Messages/seconde par topic
- **Erreurs** : Taux d'erreur par service
- **Disponibilité** : Uptime par service

### Traces Distribuées

- **OpenTelemetry** : Traces pour toutes les communications
- **Correlation IDs** : Propagation des IDs de corrélation entre services

---

## Conclusion

Cette matrice de communication fournit une vue complète de toutes les interactions entre les microservices de la plateforme. Elle permet de comprendre les flux de données, les dépendances, et les points d'intégration pour le développement, le debugging, et l'optimisation.

