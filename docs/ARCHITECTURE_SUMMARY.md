# Résumé de l'Architecture - ML Test Prioritization Platform

## Vue d'Ensemble

Cette plateforme de recommandation automatisée des classes logicielles à tester utilise une architecture microservices distribuée avec 9 services principaux, communiquant via Kafka (asynchrone) et REST API (synchrone).

## Flux Global Simplifié

```
┌─────────────────────────────────────────────────────────────┐
│                    SOURCES EXTERNES                         │
│  GitHub │ GitLab │ Jira │ CI/CD (JaCoCo, Surefire, PIT)    │
└─────────┬───────┬───────┬──────────────────────────────────┘
          │       │       │
          └───────┼───────┘
                  │
          ┌───────▼───────┐
          │   S1: Collecte │
          │   Depots       │
          └───────┬───────┘
                  │
      ┌───────────┼───────────┐
      │           │           │
      ▼           ▼           ▼
  ┌───────┐  ┌────────┐  ┌──────┐
  │ Kafka │  │PostgreSQL│ │ MinIO │
  └───┬───┘  └────────┘  └──────┘
      │
      ▼
  ┌───────┐         ┌──────────┐
  │ S2:   │────────▶│  Feast   │
  │Analyse│         │(Features)│
  └───┬───┘         └────┬─────┘
      │                  │
      ▼                  │
  ┌───────┐              │
  │ S3:   │              │
  │Tests  │              │
  └───┬───┘              │
      │                  │
      ▼                  │
  ┌──────────┐           │
  │TimescaleDB│          │
  └──────────┘           │
                        │
                        ▼
                  ┌──────────┐
                  │ S4: Pretrait│
                  │ Features   │
                  └─────┬──────┘
                        │
                        ▼
                  ┌──────────┐
                  │  Feast   │
                  │(Processed)│
                  └─────┬────┘
                        │
                        ▼
                  ┌──────────┐
                  │ S5: ML   │
                  │ Service  │
                  └─────┬────┘
                        │
            ┌───────────┼───────────┐
            │           │           │
            ▼           ▼           ▼
        ┌──────┐  ┌────────┐  ┌──────┐
        │MLflow│  │ MinIO  │  │  S6  │
        └──────┘  └────────┘  └───┬──┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
                ┌──────┐      ┌──────┐    ┌──────────┐
                │  S7  │      │  S8  │    │PostgreSQL│
                │Scaff │      │Dash  │    └──────────┘
                └───┬──┘      └───┬──┘
                    │            │
                    ▼            ▼
                ┌──────┐    ┌────────┐
                │ Git  │    │React.js│
                └───┬──┘    └────────┘
                    │
                    ▼
                ┌──────┐
                │  S9  │
                │Integr│
                └───┬──┘
                    │
                    ▼
            ┌───────────────┐
            │ GitHub/GitLab │
            │  (CI/CD)      │
            └───────────────┘
```

## Services par Couche

### Couche 1 : Collecte et Ingestion
- **S1 - CollecteDepots** : Ingestion Git/GitHub/GitLab/Jira, artefacts CI/CD
- **S2 - AnalyseStatique** : Extraction métriques de code (LOC, complexité, CK, smells)

### Couche 2 : Tests et Historique
- **S3 - HistoriqueTests** : Agrégation couverture et résultats (JaCoCo, Surefire, PIT)

### Couche 3 : ML et Features
- **S4 - PretraitementFeatures** : Nettoyage, features dérivées (churn, bug-fix proximity)
- **S5 - MLService** : Entraînement et prédiction de risque (XGBoost, LightGBM, SHAP)

### Couche 4 : Priorisation et Génération
- **S6 - MoteurPriorisation** : Transformation scores en liste priorisée (effort-aware, OR-Tools)
- **S7 - TestScaffolder** : Génération squelettes de tests JUnit

### Couche 5 : Visualisation
- **S8 - DashboardQualité** : Interface React.js pour visualiser recommandations

### Couche 6 : Intégrations
- **S9 - Integrations** : CI/CD, Docker/Kubernetes, observabilité, auth SSO

## Technologies Clés

### Messaging
- **Kafka** : Communication asynchrone (S1→S2, S1→S3, S2→S4)

### Bases de Données
- **PostgreSQL** : Métadonnées, plans de priorisation
- **TimescaleDB** : Séries temporelles (historique tests, métriques)

### Storage
- **MinIO** : Artefacts CI/CD, modèles ML
- **Feast** : Feature Store (online/offline)

### ML/Data
- **MLflow** : Tracking d'expériences, model registry
- **XGBoost/LightGBM** : Modèles de prédiction
- **SHAP** : Explicabilité

### APIs
- **REST API** : Communication synchrone (S3→S4/S6/S8, S5→S6/S8, S6→S7/S8)
- **WebSocket** : Temps réel (S8→Frontend)
- **Webhooks** : Événements externes (GitHub/GitLab→S1/S9)

## Points d'Entrée Principaux

1. **Webhooks** : GitHub/GitLab/Jira → S1
2. **API REST** : Collecte manuelle → S1
3. **CI/CD** : Artefacts → S1 → S3

## Points de Sortie Principaux

1. **Dashboard** : S8 → React.js (visualisation)
2. **Git Repository** : S7 → tests-suggestions (génération)
3. **CI/CD** : S9 → GitHub/GitLab (commentaires, checks)

## Flux de Données Clés

### 1. Pipeline de Collecte
```
Sources → S1 → Kafka → S2 → Feast
        ↓
    PostgreSQL + MinIO + TimescaleDB
```

### 2. Pipeline ML
```
Feast → S4 → Feast → S5 → MLflow + MinIO
                  ↓
                S6 → PostgreSQL
```

### 3. Pipeline de Priorisation
```
S5 → S6 → S7 → S8
     ↓
 PostgreSQL
```

## Métriques et KPIs

### Métriques ML
- F1 Score, ROC-AUC, PR-AUC
- Popt@20 (effort-aware)
- Recall@Top20%

### Métriques Business
- Défauts évités
- Temps économisé (heures)
- Gain de couverture

## Documentation Complète

Pour plus de détails, consultez :
- **[ARCHITECTURE_COMPLETE.md](./ARCHITECTURE_COMPLETE.md)** : Documentation complète avec tous les JSON schemas
- **[COMMUNICATION_MATRIX.md](./COMMUNICATION_MATRIX.md)** : Matrice de communication détaillée

## Déploiement

### Docker Compose (Développement)
```bash
docker-compose up -d
```

### Kubernetes (Production)
Voir `services/S9-Integrations/kubernetes/` pour les configurations K8s.

## Configuration

Variables d'environnement principales :
- `KAFKA_BOOTSTRAP_SERVERS` : Kafka brokers
- `DATABASE_URL` : PostgreSQL/TimescaleDB connection
- `FEAST_URL` : Feast server
- `MLFLOW_TRACKING_URI` : MLflow server
- `MINIO_ENDPOINT` : MinIO endpoint

Voir [ARCHITECTURE_COMPLETE.md](./ARCHITECTURE_COMPLETE.md#configuration-et-déploiement) pour la liste complète.

