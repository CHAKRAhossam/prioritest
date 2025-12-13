# Architecture Complète - ML Test Prioritization Platform

## Vue d'Ensemble

Cette documentation détaille l'architecture complète de la plateforme de recommandation automatisée des classes logicielles à tester, avec tous les inputs/outputs JSON, les communications entre services et les détails de chaque microservice.

## Flux Global

```
S1 (Collecte) → Kafka → S2 (Analyse) → Feast
 ↓
S3 (Historique) → TimescaleDB → S4 (Prétraitement) → Feast
 ↓
 S5 (ML) → MLflow
 ↓
 S6 (Priorisation) → PostgreSQL
 ↓
 S7 (Scaffolder) ← S8 (Dashboard) → React.js
 ↓
 S9 (Intégrations) → CI/CD
```

---

## Service 1 : CollecteDepots (Haytam Ta)

### Rôle
Ingestion des dépôts Git/GitHub/GitLab, issues Jira, artefacts CI/CD.

### Input (API REST / Webhooks)

#### Webhook GitHub/GitLab
```json
{
  "event_type": "push|pull_request|issue",
  "repository": {
    "id": "12345",
    "name": "my-repo",
    "full_name": "org/my-repo",
    "url": "https://github.com/org/my-repo"
  },
  "commit": {
    "sha": "abc123",
    "message": "Fix bug in UserService",
    "author": "developer@example.com",
    "timestamp": "2025-12-04T10:30:00Z",
    "files": [
      {
        "path": "src/UserService.java",
        "status": "modified"
      }
    ]
  }
}
```

#### Webhook Jira
```json
{
  "event_type": "jira:issue_created|jira:issue_updated",
  "issue": {
    "key": "MTP-77",
    "summary": "Bug in authentication",
    "type": "Bug",
    "status": "Open",
    "created": "2025-12-04T10:30:00Z"
  }
}
```

#### API Request (manuel)
```json
POST /api/v1/collect
{
  "repository_url": "https://github.com/org/repo",
  "collect_type": "commits|issues|ci_reports",
  "date_range": {
    "start": "2025-01-01",
    "end": "2025-12-04"
  }
}
```

### Output (Kafka Topics)

#### Topic: repository.commits
```json
{
  "event_id": "evt_123",
  "repository_id": "repo_12345",
  "commit_sha": "abc123",
  "commit_message": "Fix bug in UserService",
  "author_email": "developer@example.com",
  "author_name": "John Doe",
  "timestamp": "2025-12-04T10:30:00Z",
  "files_changed": [
    {
      "path": "src/UserService.java",
      "status": "modified",
      "additions": 10,
      "deletions": 5
    }
  ],
  "metadata": {
    "source": "github",
    "branch": "main"
  }
}
```

#### Topic: repository.issues
```json
{
  "event_id": "evt_124",
  "repository_id": "repo_12345",
  "issue_key": "MTP-77",
  "issue_type": "Bug",
  "summary": "Bug in authentication",
  "status": "Open",
  "created_at": "2025-12-04T10:30:00Z",
  "linked_commits": ["abc123"]
}
```

#### Topic: ci.artifacts
```json
{
  "event_id": "evt_125",
  "repository_id": "repo_12345",
  "build_id": "build_789",
  "commit_sha": "abc123",
  "artifact_type": "jacoco|surefire|pit",
  "artifact_url": "s3://minio/artifacts/jacoco_abc123.xml",
  "timestamp": "2025-12-04T10:35:00Z"
}
```

### Envoie vers
- **Kafka Topics** : `repository.commits`, `repository.issues`, `ci.artifacts`
- **PostgreSQL** : métadonnées des dépôts
- **MinIO** : artefacts CI/CD (rapports JaCoCo, Surefire, PIT)
- **TimescaleDB** : séries temporelles de métriques par commit

### Détails
1. Écoute webhooks GitHub/GitLab/Jira
2. Collecte commits via API Git/GitHub/GitLab
3. Collecte issues/bugs via API Jira/GitHub Issues
4. Télécharge rapports CI/CD (JaCoCo, Surefire, PIT)
5. Publie dans Kafka (topics dédiés)
6. Stocke métadonnées dans PostgreSQL
7. Stocke artefacts dans MinIO
8. Versionne jeux internes avec DVC

---

## Service 2 : AnalyseStatique (Haytam Ta)

### Rôle
Extraction de métriques de code (LOC, complexité cyclomatique, CK, dépendances, smells).

### Input (Kafka)

#### Topic: repository.commits (consommé depuis S1)
```json
{
  "event_id": "evt_123",
  "repository_id": "repo_12345",
  "commit_sha": "abc123",
  "files_changed": [
    {
      "path": "src/UserService.java",
      "status": "modified"
    }
  ]
}
```

### Output (Feast Feature Store + Kafka)

#### Topic: code.metrics
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
      "noc": 0,
      "cbo": 5,
      "rfc": 15,
      "lcom": 0.75
    },
    "dependencies": {
      "in_degree": 3,
      "out_degree": 5,
      "dependencies_list": [
        "com.example.UserRepository",
        "com.example.EmailService"
      ]
    },
    "code_smells": [
      {
        "type": "LongMethod",
        "severity": "medium",
        "line": 45
      }
    ]
  },
  "timestamp": "2025-12-04T10:40:00Z"
}
```

#### Feast Feature Store (online/offline)
```json
{
  "entity": {
    "class_name": "com.example.UserService",
    "repository_id": "repo_12345"
  },
  "features": {
    "loc": 150,
    "cyclomatic_complexity": 12,
    "wmc": 8,
    "dit": 2,
    "cbo": 5,
    "rfc": 15,
    "lcom": 0.75,
    "in_degree": 3,
    "out_degree": 5
  },
  "timestamp": "2025-12-04T10:40:00Z"
}
```

### Envoie vers
- **Feast Feature Store** : métriques versionnées
- **Kafka Topic** `code.metrics` : pour S4 (Prétraitement)
- **PostgreSQL** : indices par classe

### Détails
1. Consomme `repository.commits` depuis Kafka
2. Clone/analyse le code au commit donné
3. Extrait métriques Java (JavaParser, CK, PMD, SonarQube)
4. Extrait métriques Python (radon)
5. Analyse dépendances (JGraphT/networkx)
6. Détecte code smells
7. Normalise par module/langage
8. Publie dans Feast et Kafka

---

## Service 3 : HistoriqueTests (Oussama Boujdig)

### Rôle
Agrégation de couverture et résultats de tests (JaCoCo, Surefire, PIT).

### Input (MinIO + Kafka)

#### Depuis MinIO (artefacts CI/CD)
```json
{
  "artifact_url": "s3://minio/artifacts/jacoco_abc123.xml",
  "artifact_type": "jacoco",
  "commit_sha": "abc123",
  "repository_id": "repo_12345"
}
```

#### Depuis Kafka (topic: ci.artifacts)
```json
{
  "event_id": "evt_125",
  "repository_id": "repo_12345",
  "build_id": "build_789",
  "commit_sha": "abc123",
  "artifact_type": "jacoco",
  "artifact_url": "s3://minio/artifacts/jacoco_abc123.xml"
}
```

### Output (TimescaleDB + REST API)

#### Stockage TimescaleDB (séries temporelles)
```json
{
  "repository_id": "repo_12345",
  "commit_sha": "abc123",
  "class_name": "com.example.UserService",
  "timestamp": "2025-12-04T10:35:00Z",
  "coverage_metrics": {
    "line_coverage": 0.85,
    "branch_coverage": 0.78,
    "instruction_coverage": 0.82,
    "method_coverage": 0.90
  },
  "test_results": {
    "total_tests": 15,
    "passed": 14,
    "failed": 1,
    "skipped": 0,
    "flakiness_score": 0.05
  },
  "mutation_score": 0.75,
  "test_debt": {
    "has_tests": true,
    "coverage_below_threshold": false,
    "threshold": 0.80
  }
}
```

#### REST API Response
```json
GET /api/v1/test-metrics?class_name=com.example.UserService&repository_id=repo_12345
{
  "class_name": "com.example.UserService",
  "repository_id": "repo_12345",
  "current_coverage": {
    "line_coverage": 0.85,
    "branch_coverage": 0.78
  },
  "test_history": [
    {
      "commit_sha": "abc123",
      "timestamp": "2025-12-04T10:35:00Z",
      "line_coverage": 0.85,
      "tests_passed": 14,
      "tests_failed": 1
    }
  ],
  "test_debt": {
    "has_tests": true,
    "coverage_below_threshold": false
  }
}
```

### Envoie vers
- **TimescaleDB** : historique de couverture par classe/commit
- **PostgreSQL** : indices par classe
- **REST API** : pour S4, S6, S8

### Détails
1. Parse rapports JaCoCo (couverture)
2. Parse rapports Surefire (résultats)
3. Parse rapports PIT (mutation)
4. Calcule métriques agrégées
5. Calcule dette de test
6. Relie classes ↔ tests couvrants
7. Stocke dans TimescaleDB (séries temporelles)
8. Expose API REST

---

## Service 4 : PrétraitementFeatures (Hicham Kaou)

### Rôle
Nettoyage, imputation, encodage, construction de features dérivées.

### Input (Feast + TimescaleDB + Kafka)

#### Depuis Feast (métriques de code)
```json
{
  "class_name": "com.example.UserService",
  "repository_id": "repo_12345",
  "features": {
    "loc": 150,
    "cyclomatic_complexity": 12,
    "wmc": 8,
    "cbo": 5
  }
}
```

#### Depuis TimescaleDB (historique tests)
```json
{
  "class_name": "com.example.UserService",
  "coverage_history": [...],
  "test_results_history": [...]
}
```

#### Depuis Kafka (commits)
```json
{
  "commit_sha": "abc123",
  "author_email": "developer@example.com",
  "files_changed": [...]
}
```

### Output (Feast Feature Store)

#### Features dérivées dans Feast
```json
{
  "entity": {
    "class_name": "com.example.UserService",
    "repository_id": "repo_12345"
  },
  "features": {
    "loc": 150,
    "cyclomatic_complexity": 12,
    "wmc": 8,
    "cbo": 5,
    "churn": 0.15,
    "num_authors": 3,
    "modification_frequency": 0.25,
    "bug_fix_proximity": 0.8,
    "age_days": 120,
    "last_modified_days_ago": 5,
    "current_line_coverage": 0.85,
    "coverage_trend": "increasing",
    "test_debt_score": 0.2,
    "has_tests": 1,
    "is_critical_module": 1,
    "language": "java"
  },
  "timestamp": "2025-12-04T10:45:00Z"
}
```

#### Datasets train/val/test (time-aware split)
```json
{
  "dataset_type": "train|val|test",
  "split_date": "2025-10-01",
  "features": [...],
  "target": 1,
  "metadata": {
    "repository_id": "repo_12345",
    "class_name": "com.example.UserService"
  }
}
```

### Envoie vers
- **Feast Feature Store** : features versionnées (online/offline)
- **S5 (MLService)** : datasets train/val/test

### Détails
1. Récupère métriques depuis Feast
2. Récupère historique depuis TimescaleDB
3. Calcule churn, auteurs, fréquence modifs
4. Calcule proximité avec bug-fix commits
5. Nettoyage/imputation des valeurs manquantes
6. Encodage (one-hot, label)
7. Split temporel (train/val/test)
8. Balancement (SMOTE/cost-sensitive)
9. Normalisation par repository
10. Publie dans Feast

---

## Service 5 : MLService (Hicham Kaou)

### Rôle
Entraînement et service de modèles de prédiction de risque de défaut.

### Input (Feast)

#### Features depuis Feast
```json
{
  "class_name": "com.example.UserService",
  "repository_id": "repo_12345",
  "features": {
    "loc": 150,
    "cyclomatic_complexity": 12,
    "churn": 0.15,
    "num_authors": 3,
    "bug_fix_proximity": 0.8,
    "current_line_coverage": 0.85,
    "test_debt_score": 0.2
  }
}
```

#### Dataset pour entraînement
```json
{
  "train_data": [...],
  "val_data": [...],
  "test_data": [...]
}
```

### Output (MLflow + REST API)

#### Prédiction (REST API)
```json
POST /api/v1/predict
{
  "class_name": "com.example.UserService",
  "repository_id": "repo_12345",
  "features": {...}
}

Response:
{
  "class_name": "com.example.UserService",
  "risk_score": 0.75,
  "risk_level": "high",
  "uncertainty": 0.12,
  "top_k_recommendations": [
    {
      "class_name": "com.example.UserService",
      "risk_score": 0.75,
      "priority": 1
    }
  ],
  "shap_values": {
    "loc": 0.15,
    "cyclomatic_complexity": 0.20,
    "churn": 0.10,
    "bug_fix_proximity": 0.25
  },
  "explanation": "High risk due to high complexity and proximity to bug-fix commits"
}
```

#### MLflow Experiment
```json
{
  "experiment_id": "exp_123",
  "run_id": "run_456",
  "metrics": {
    "f1_score": 0.82,
    "roc_auc": 0.89,
    "pr_auc": 0.85,
    "precision": 0.80,
    "recall": 0.84
  },
  "model_type": "XGBoost",
  "model_uri": "s3://mlflow/models/xgboost_v1"
}
```

### Envoie vers
- **MLflow** : experiments, model registry
- **MinIO** : modèles stockés
- **REST API** : pour S6 (MoteurPriorisation) et S8 (Dashboard)
- **Feast** : online features pour prédictions

### Détails
1. Charge datasets depuis Feast
2. Entraîne modèles (XGBoost, LightGBM, LogReg, RandomForest)
3. Validation temporelle (train ancien, test récent)
4. Calibration des probabilités
5. Détection d'anomalies (IsolationForest, LOF)
6. Explicabilité SHAP (local/global)
7. Enregistre dans MLflow
8. Expose API de prédiction

---

## Service 6 : MoteurPriorisation (Hossam Chakra)

### Rôle
Transformation des scores ML en liste priorisée (effort-aware, contraintes).

### Input (REST API S5 + PostgreSQL)

#### Depuis S5 (MLService)
```json
{
  "predictions": [
    {
      "class_name": "com.example.UserService",
      "risk_score": 0.75,
      "shap_values": {...}
    }
  ]
}
```

#### Contraintes depuis PostgreSQL
```json
{
  "sprint_objectives": {
    "budget_hours": 40,
    "target_coverage": 0.85,
    "priority_modules": ["auth", "payment"]
  },
  "effort_estimates": {
    "com.example.UserService": {
      "loc": 150,
      "estimated_hours": 4
    }
  }
}
```

### Output (REST API + PostgreSQL)

#### Plan de tests priorisé
```json
POST /api/v1/prioritize
{
  "repository_id": "repo_12345",
  "sprint_id": "sprint_1",
  "constraints": {
    "budget_hours": 40,
    "target_coverage": 0.85
  }
}

Response:
{
  "prioritized_plan": [
    {
      "class_name": "com.example.UserService",
      "priority": 1,
      "risk_score": 0.75,
      "effort_hours": 4,
      "effort_aware_score": 0.1875,
      "module_criticality": "high",
      "strategy": "maximize_popt20",
      "reason": "High risk with moderate effort in critical module"
    },
    {
      "class_name": "com.example.OrderService",
      "priority": 2,
      "risk_score": 0.68,
      "effort_hours": 3,
      "effort_aware_score": 0.2267,
      "module_criticality": "medium",
      "strategy": "top_k_coverage",
      "reason": "Good risk/effort ratio"
    }
  ],
  "metrics": {
    "total_effort_hours": 35,
    "estimated_coverage_gain": 0.12,
    "popt20_score": 0.85,
    "recall_top20": 0.78
  }
}
```

#### Stockage dans PostgreSQL
```json
{
  "plan_id": "plan_123",
  "sprint_id": "sprint_1",
  "repository_id": "repo_12345",
  "prioritized_classes": [...],
  "created_at": "2025-12-04T11:00:00Z"
}
```

### Envoie vers
- **PostgreSQL** : politiques et plans de priorisation
- **REST API** : pour S7 (TestScaffolder) et S8 (Dashboard)

### Détails
1. Récupère prédictions depuis S5
2. Intègre effort (LOC, complexité)
3. Intègre criticité module
4. Intègre dépendances
5. Applique stratégies (top-K, Popt@20, budget)
6. Optimisation avec OR-Tools (contraintes)
7. Calcule métriques effort-aware
8. Stocke plan dans PostgreSQL

---

## Service 7 : TestScaffolder (Hossam Chakra)

### Rôle
Génération de squelettes de tests JUnit avec suggestions.

### Input (REST API S6)

#### Depuis S6 (MoteurPriorisation)
```json
GET /api/v1/test-scaffold?class_name=com.example.UserService&priority=1

// Ou batch
POST /api/v1/test-scaffold/batch
{
  "prioritized_classes": [
    {
      "class_name": "com.example.UserService",
      "priority": 1,
      "file_path": "src/UserService.java"
    }
  ]
}
```

### Output (Git Repository + REST API)

#### Templates de tests générés
```json
{
  "class_name": "com.example.UserService",
  "test_file_path": "tests/UserServiceTest.java",
  "test_template": "public class UserServiceTest {\n @Test\n public void testUserCreation() {...}\n}",
  "suggested_test_cases": [
    {
      "type": "equivalence",
      "description": "Test with valid user data",
      "method": "testUserCreation_ValidInput"
    },
    {
      "type": "boundary",
      "description": "Test with null input",
      "method": "testUserCreation_NullInput"
    },
    {
      "type": "mocks",
      "description": "Mock UserRepository",
      "code": "@Mock\nprivate UserRepository userRepository;"
    }
  ],
  "mutation_checklist": [
    "Test all public methods",
    "Cover edge cases",
    "Verify exception handling"
  ],
  "repository_url": "https://github.com/org/tests-suggestions"
}
```

### Envoie vers
- **Repository Git "tests-suggestions"** : templates de tests
- **REST API** : pour S8 (Dashboard) et S9 (Intégrations)

### Détails
1. Analyse AST de la classe (Spoon/JavaParser)
2. Génère squelette JUnit
3. Suggère cas de test (équivalence, limites)
4. Suggère mocks nécessaires
5. Génère checklist mutation testing
6. Stocke dans repo Git dédié
7. Expose API de génération

---

## Service 8 : DashboardQualité (Ilyas Michich)

### Rôle
Interface web pour visualiser recommandations, couverture, risques, tendances.

### Input (REST APIs)

#### Depuis S6 (MoteurPriorisation)
```json
GET /api/v1/prioritize?repository_id=repo_12345
```

#### Depuis S5 (MLService)
```json
GET /api/v1/predict?class_name=com.example.UserService
```

#### Depuis S3 (HistoriqueTests)
```json
GET /api/v1/test-metrics?repository_id=repo_12345
```

### Output (WebSocket + REST API)

#### WebSocket (temps réel)
```json
{
  "event_type": "coverage_update|risk_update|recommendation_update",
  "data": {
    "repository_id": "repo_12345",
    "class_name": "com.example.UserService",
    "current_coverage": 0.85,
    "risk_score": 0.75,
    "recommendation_priority": 1
  },
  "timestamp": "2025-12-04T11:05:00Z"
}
```

#### REST API Response
```json
GET /api/v1/dashboard/overview?repository_id=repo_12345
{
  "repository_id": "repo_12345",
  "summary": {
    "total_classes": 150,
    "classes_with_tests": 120,
    "average_coverage": 0.78,
    "high_risk_classes": 15,
    "recommended_classes": 20
  },
  "recommendations": [...],
  "coverage_trends": [...],
  "risk_distribution": [...],
  "impact_metrics": {
    "defects_prevented": 12,
    "time_saved_hours": 45,
    "coverage_gain": 0.15
  }
}
```

#### Export PDF/CSV
```json
GET /api/v1/dashboard/export?format=pdf&repository_id=repo_12345
```

### Envoie vers
- **Frontend React.js** : visualisations
- **WebSocket** : mises à jour temps réel
- **Exports PDF/CSV** : rapports

### Détails
1. Consolide données depuis S3, S5, S6
2. Visualise recommandations par repo/module/classe
3. Affiche couverture avec drill-down
4. Visualise risques avec SHAP
5. Affiche tendances temporelles
6. Calcule impact (défauts évités, temps économisé)
7. Comparaison avant/après
8. Exports PDF/CSV
9. WebSocket pour temps réel

---

## Service 9 : Intégrations & Ops (Oussama Boujdig)

### Rôle
Intégration CI/CD, Docker/Kubernetes, observabilité, authentification.

### Input (Webhooks CI/CD)

#### Webhook GitHub Actions
```json
{
  "event": "pull_request",
  "action": "opened|synchronize",
  "pull_request": {
    "number": 123,
    "head": {
      "sha": "abc123",
      "ref": "feature/new-feature"
    },
    "files": [
      {
        "path": "src/UserService.java",
        "status": "modified"
      }
    ]
  }
}
```

#### Webhook GitLab MR
```json
{
  "event_type": "merge_request",
  "object_attributes": {
    "iid": 45,
    "source_branch": "feature/new-feature",
    "last_commit": {
      "id": "abc123"
    }
  }
}
```

### Output (CI/CD Comments + Checks)

#### Commentaire automatique sur PR/MR
```json
{
  "comment": "⚠️ Warning: Modified class 'UserService' has high risk score (0.75) but no tests added.\n\nRecommendation: Add tests before merging.\n\nRisk factors:\n- High cyclomatic complexity (12)\n- Proximity to bugfix commits (0.8)\n- Low test coverage (0.65)\n\nSuggested test cases: [View in TestScaffolder]"
}
```

#### GitHub Check / GitLab Status
```json
{
  "state": "failure|success|warning",
  "description": "Test prioritization check",
  "details": {
    "high_risk_classes_modified": 2,
    "tests_added": 0,
    "recommendation": "Add tests for UserService and OrderService"
  }
}
```

### Envoie vers
- **GitHub/GitLab** : checks et commentaires
- **CI/CD pipelines** : triggers d'entraînement
- **Keycloak** : authentification SSO
- **OpenTelemetry** : observabilité

### Détails
1. Intègre GitHub Checks API
2. Intègre GitLab MR API
3. Commentaires automatiques sur PR/MR
4. Policy gate (alerte si classe risquée sans tests)
5. Triggers d'entraînement automatiques
6. Configuration Docker/Kubernetes
7. Observabilité OpenTelemetry
8. Authentification Keycloak SSO

---

## Matrice de Communication

| Service | Envoie vers | Méthode | Topic/Endpoint |
|---------|-------------|---------|----------------|
| S1 | S2, S3 | Kafka | `repository.commits`, `repository.issues`, `ci.artifacts` |
| S1 | PostgreSQL | REST | `/api/v1/repositories` |
| S1 | MinIO | S3 API | Bucket `artifacts` |
| S1 | TimescaleDB | SQL | Table `commit_metrics` |
| S2 | S4 | Kafka | `code.metrics` |
| S2 | Feast | Feature Store | Features `code_metrics` |
| S3 | S4, S6, S8 | REST API | `/api/v1/test-metrics` |
| S3 | TimescaleDB | SQL | Table `test_history` |
| S4 | S5 | Feast | Features `processed_features` |
| S5 | S6, S8 | REST API | `/api/v1/predict` |
| S5 | MLflow | MLflow API | Experiments & Models |
| S6 | S7, S8 | REST API | `/api/v1/prioritize` |
| S6 | PostgreSQL | SQL | Table `prioritization_plans` |
| S7 | S8, S9 | REST API | `/api/v1/test-scaffold` |
| S7 | Git Repo | Git API | Repository `tests-suggestions` |
| S8 | Frontend | WebSocket | `/ws/dashboard` |
| S9 | GitHub/GitLab | Webhooks | Checks & Comments |

---

## Technologies par Service

### S1: CollecteDepots
- **Langages** : Python/Java
- **APIs** : JGit, GitHub/GitLab/Jira APIs
- **Messaging** : Kafka
- **Databases** : PostgreSQL, TimescaleDB
- **Storage** : MinIO
- **Versioning** : DVC

### S2: AnalyseStatique
- **Langages** : Python/Java
- **Analysis** : JavaParser, CK, PMD, SonarQube, radon
- **Graphs** : JGraphT/networkx
- **Feature Store** : Feast

### S3: HistoriqueTests
- **Langages** : Python
- **Parsers** : JaCoCo/Surefire/PIT
- **API** : REST API
- **Database** : TimescaleDB, PostgreSQL

### S4: PretraitementFeatures
- **Langages** : Python
- **Libraries** : Pandas, scikit-learn
- **Versioning** : DVC
- **Feature Store** : Feast

### S5: MLService
- **Langages** : Python
- **ML** : XGBoost, LightGBM, scikit-learn
- **Explainability** : SHAP
- **MLOps** : MLflow
- **Feature Store** : Feast

### S6: MoteurPriorisation
- **Langages** : Python
- **Optimization** : OR-Tools
- **Database** : PostgreSQL

### S7: TestScaffolder
- **Langages** : Java/Python
- **Analysis** : Spoon/JavaParser
- **Templates** : Mustache
- **Git** : Git API

### S8: DashboardQualité
- **Frontend** : React.js
- **Backend** : FastAPI
- **Real-time** : WebSocket
- **Visualization** : Grafana/Plotly
- **Database** : PostgreSQL/TimescaleDB

### S9: Integrations
- **Languages** : Python
- **CI/CD** : GitHub Actions, GitLab CI
- **Containers** : Docker/Kubernetes
- **Observability** : OpenTelemetry
- **Auth** : Keycloak

---

## Schémas de Base de Données

### PostgreSQL (Métadonnées)
- `repositories` : Informations sur les dépôts
- `commits` : Métadonnées des commits
- `issues` : Issues Jira/GitHub
- `prioritization_plans` : Plans de priorisation
- `policies` : Politiques de priorisation

### TimescaleDB (Séries Temporelles)
- `commit_metrics` : Métriques par commit (hypertable)
- `test_history` : Historique de couverture par classe/commit (hypertable)

### Feast Feature Store
- `code_metrics` : Métriques de code (online/offline)
- `processed_features` : Features prétraitées (online/offline)

### MLflow
- Experiments : Expériences ML
- Model Registry : Registre des modèles
- Artifacts : Modèles stockés dans MinIO

---

## Endpoints API Principaux

### S1 - CollecteDepots
- `POST /api/v1/collect` : Collecte manuelle
- `POST /api/v1/webhooks/github` : Webhook GitHub
- `POST /api/v1/webhooks/gitlab` : Webhook GitLab
- `POST /api/v1/webhooks/jira` : Webhook Jira

### S3 - HistoriqueTests
- `GET /api/v1/test-metrics` : Métriques de tests
- `GET /api/v1/coverage` : Couverture par classe
- `GET /api/v1/flakiness` : Flakiness des tests
- `GET /api/v1/test-debt` : Dette de test

### S5 - MLService
- `POST /api/v1/predict` : Prédiction de risque
- `GET /api/v1/models` : Liste des modèles
- `POST /api/v1/train` : Entraînement de modèle

### S6 - MoteurPriorisation
- `POST /api/v1/prioritize` : Priorisation
- `GET /api/v1/prioritize/{repository_id}` : Plan existant

### S7 - TestScaffolder
- `GET /api/v1/test-scaffold` : Génération de test
- `POST /api/v1/test-scaffold/batch` : Génération batch

### S8 - DashboardQualité
- `GET /api/v1/dashboard/overview` : Vue d'ensemble
- `WebSocket /ws/dashboard` : Temps réel
- `GET /api/v1/dashboard/export` : Export PDF/CSV

### S9 - Integrations
- `POST /api/v1/webhooks/github` : Webhook GitHub
- `POST /api/v1/webhooks/gitlab` : Webhook GitLab
- `GET /api/v1/health` : Health check

---

## Flux de Données Complets

### 1. Pipeline de Collecte
```
GitHub/GitLab/Jira → S1 → Kafka (repository.commits, repository.issues, ci.artifacts)
                    ↓
              PostgreSQL (métadonnées)
                    ↓
              MinIO (artefacts)
                    ↓
              TimescaleDB (métriques temporelles)
```

### 2. Pipeline d'Analyse
```
Kafka (repository.commits) → S2 → Feast (code_metrics)
                          ↓
                    Kafka (code.metrics)
```

### 3. Pipeline de Tests
```
MinIO (artefacts) → S3 → TimescaleDB (test_history)
                ↓
          REST API → S4, S6, S8
```

### 4. Pipeline ML
```
Feast (code_metrics) → S4 → Feast (processed_features)
                    ↓
              S5 → MLflow (experiments)
                ↓
          REST API → S6, S8
```

### 5. Pipeline de Priorisation
```
S5 (predictions) → S6 → PostgreSQL (prioritization_plans)
                ↓
          REST API → S7, S8
```

### 6. Pipeline de Génération
```
S6 (prioritized_classes) → S7 → Git Repo (tests-suggestions)
                        ↓
                  REST API → S8, S9
```

### 7. Pipeline de Visualisation
```
S3, S5, S6, S7 → S8 → React.js (Dashboard)
              ↓
        WebSocket (temps réel)
```

### 8. Pipeline d'Intégration
```
GitHub/GitLab (webhooks) → S9 → GitHub/GitLab (checks/comments)
                        ↓
                  CI/CD (triggers)
```

---

## Configuration et Déploiement

### Variables d'Environnement Principales

#### S1 - CollecteDepots
- `KAFKA_BOOTSTRAP_SERVERS` : Kafka brokers
- `DATABASE_URL` : PostgreSQL connection string
- `MINIO_ENDPOINT` : MinIO endpoint
- `GITHUB_TOKEN`, `GITLAB_TOKEN`, `JIRA_API_TOKEN` : API tokens

#### S2 - AnalyseStatique
- `KAFKA_BOOTSTRAP_SERVERS` : Kafka brokers
- `FEAST_URL` : Feast server URL
- `GIT_TEMP_DIR` : Temporary directory for cloning repos

#### S3 - HistoriqueTests
- `DATABASE_URL` : TimescaleDB connection string
- `MINIO_ENDPOINT` : MinIO endpoint for artifacts

#### S4 - PretraitementFeatures
- `FEAST_URL` : Feast server URL
- `DATABASE_URL` : TimescaleDB connection string

#### S5 - MLService
- `FEAST_URL` : Feast server URL
- `MLFLOW_TRACKING_URI` : MLflow server URL
- `MINIO_ENDPOINT` : MinIO endpoint for models

#### S6 - MoteurPriorisation
- `DATABASE_URL` : PostgreSQL connection string
- `ML_SERVICE_URL` : S5 MLService URL

#### S7 - TestScaffolder
- `GIT_REPO_URL` : Git repository for test suggestions
- `GIT_TOKEN` : Git authentication token

#### S8 - DashboardQualité
- `ML_SERVICE_URL` : S5 MLService URL
- `PRIORITIZATION_SERVICE_URL` : S6 MoteurPriorisation URL
- `TEST_METRICS_SERVICE_URL` : S3 HistoriqueTests URL

#### S9 - Integrations
- `GITHUB_TOKEN`, `GITLAB_TOKEN` : API tokens
- `KEYCLOAK_URL` : Keycloak server URL
- `ML_SERVICE_URL` : S5 MLService URL

---

## Métriques et Observabilité

### Métriques ML
- F1 Score, ROC-AUC, PR-AUC
- Precision, Recall
- Popt@20 (effort-aware)
- Recall@Top20%

### Métriques Business
- Défauts évités
- Temps économisé (heures)
- Gain de couverture
- Classes priorisées

### Observabilité
- OpenTelemetry : Traces distribuées
- Prometheus : Métriques
- Grafana : Visualisation
- Logs : Centralisés (ELK/Loki)

---

## Sécurité

### Authentification
- Keycloak SSO pour tous les services
- API tokens pour GitHub/GitLab/Jira
- Secrets management (Vault/Kubernetes Secrets)

### Autorisation
- RBAC via Keycloak
- API rate limiting
- CORS configuration

### Données
- Encryption at rest (PostgreSQL, MinIO)
- Encryption in transit (TLS)
- PII anonymization

---

## Conclusion

Cette architecture complète permet de :
1. Collecter automatiquement les données depuis Git/GitHub/GitLab/Jira
2. Analyser le code statiquement pour extraire des métriques
3. Agréger l'historique des tests
4. Prétraiter et créer des features dérivées
5. Entraîner et servir des modèles ML pour prédire les risques
6. Prioriser les classes à tester avec effort-aware
7. Générer des squelettes de tests
8. Visualiser les recommandations dans un dashboard
9. Intégrer avec CI/CD pour des commentaires automatiques

Tous les services communiquent via Kafka (asynchrone) ou REST API (synchrone), avec des bases de données dédiées pour chaque type de données (PostgreSQL pour métadonnées, TimescaleDB pour séries temporelles, Feast pour features, MLflow pour modèles).

