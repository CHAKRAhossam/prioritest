# Guide d'Architecture Complète - ML Test Prioritization

## Vue d'Ensemble

Le projet est organisé en **9 microservices** avec une architecture distribuée utilisant Kafka pour la communication asynchrone et des APIs REST pour la communication synchrone.

## Architecture des Services

### Couche 1 : Collecte et Ingestion (Bleu clair - #E1F5FF)

#### S1 - Collecte Depots
- **Technologies** : JGit (Java), GitHub API, GitLab API, Jira API, Kafka Producer
- **Responsable** : Haytam Ta
- **Rôle** : Ingestion des dépôts Git, issues/bugs, rapports CI/CD
- **Sorties** : 
  - Events vers Kafka
  - Métadonnées vers PostgreSQL
  - Artefacts vers MinIO

#### S2 - Analyse Statique
- **Technologies** : JavaParser, CK Metrics, PMD (Smells), Feast Feature Store
- **Responsable** : Haytam Ta
- **Rôle** : Extraction métriques de code (LOC, complexité, CK, dépendances, smells)
- **Sorties** :
  - Features vers Feast Feature Store

### Couche 2 : Tests et Historique (Orange clair - #FFF4E6)

#### S3 - Historique Tests
- **Technologies** : JaCoCo Parser, Surefire Parser, PIT Parser, TimescaleDB, FastAPI
- **Responsable** : Oussama Boujdig
- **Rôle** : Agréger couverture et résultats de tests
- **Sorties** :
  - Séries temporelles vers TimescaleDB

### Couche 3 : ML et Features (Violet clair - #F3E5F5)

#### S4 - Pretraitement Features
- **Technologies** : Pandas, scikit-learn, SMOTE, DVC, Feast
- **Responsable** : Hicham Kaou
- **Rôle** : Nettoyage, imputation, features dérivées
- **Entrées** : Raw Features depuis Feast
- **Sorties** : Processed Features vers Feast

#### S5 - ML Service
- **Technologies** : XGBoost, LightGBM, SHAP, MLflow, FastAPI, MinIO
- **Responsable** : Hicham Kaou
- **Rôle** : Entraîner/servir modèles de risque de défaut
- **Entrées** : Training Features depuis Feast
- **Sorties** :
  - Prédictions (risk_score) vers S6
  - Modèles vers MLflow
  - Fichiers modèles vers MinIO

### Couche 4 : Priorisation et Génération (Vert clair - #E8F5E9)

#### S6 - Moteur Priorisation
- **Technologies** : FastAPI, OR-Tools, PostgreSQL, Pydantic
- **Responsable** : Hossam Chakra
- **Rôle** : Transformer scores ML en liste priorisée
- **Entrées** : Prédictions depuis S5
- **Sorties** :
  - Plans priorisés vers S7 et S8
  - Politiques et plans vers PostgreSQL

#### S7 - Test Scaffolder
- **Technologies** : FastAPI, tree-sitter-java, Jinja2, GitPython, Mockito
- **Responsable** : Hossam Chakra
- **Rôle** : Générer squelettes de tests JUnit avec suggestions
- **Entrées** : Classes priorisées depuis S6
- **Sorties** : Tests générés vers S8

### Couche 5 : Visualisation (Jaune clair - #FFF9C4)

#### S8 - Dashboard Qualité
- **Technologies** : React.js + Vite, Plotly.js, FastAPI Backend, WebSockets
- **Responsable** : Ilyas Michich
- **Rôle** : Visualiser recommandations, couverture, risques
- **Entrées** : Résultats depuis S6 et S7
- **Sorties** : Métriques vers Grafana

### Couche 6 : Intégrations (Orange clair - #FFF4E6)

#### S9 - Integrations & Ops
- **Technologies** : GitHub/GitLab API, Docker/Kubernetes, OpenTelemetry, Keycloak (SSO), CI/CD
- **Responsable** : Oussama Boujdig
- **Rôle** : Intégration CI/CD, commentaires PR, auth SSO
- **Sorties** :
  - Commentaires vers GitHub/GitLab
  - Auth vers Keycloak

## Infrastructure et Services Externes

### Bases de Données (Bleu foncé - #336791)

- **PostgreSQL** : Métadonnées, politiques, plans de priorisation
- **TimescaleDB** : Séries temporelles pour historique des tests

### Stockage (Jaune - #FFC107)

- **MinIO** : Object Storage pour artefacts CI/CD et modèles ML

### Messaging (Noir - #000000)

- **Apache Kafka** : Message broker pour événements asynchrones

### ML/Data (Vert - #4CAF50, Bleu - #0194E2)

- **Feast** : Feature Store pour versioning des features
- **MLflow** : Experiments, Model Registry, Tracking

### Sécurité (Violet - #7B68EE)

- **Keycloak** : SSO/Auth, Identity Provider

### Monitoring (Orange - #F46800)

- **Grafana** : Monitoring et visualisation

## Flux de Données Principaux

### 1. Pipeline de Collecte
```
GitHub/GitLab/Jira → S1 → Kafka → S2 → Feast
                    ↓
              PostgreSQL + MinIO
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

### 4. Pipeline Visualisation
```
S6 + S7 → S8 → Grafana
```

### 5. Pipeline Intégrations
```
S9 → GitHub/GitLab (PR Comments)
S9 → Keycloak (Auth)
```

## Technologies par Catégorie

### Langages
- **Java** : S1, S2, S3
- **Python** : S4, S5, S6, S7, S8 (backend)
- **JavaScript/TypeScript** : S8 (frontend React)

### Frameworks Web
- **FastAPI** : S3, S5, S6, S7, S8 (backend)
- **React.js + Vite** : S8 (frontend)
- **Spring Boot** : S2

### ML/Data Science
- **XGBoost, LightGBM** : S5
- **Pandas, scikit-learn** : S4
- **SHAP** : S5 (explicabilité)
- **MLflow** : S5 (experiments)

### Bases de Données
- **PostgreSQL** : S1, S6
- **TimescaleDB** : S3
- **Feast** : S2, S4, S5 (feature store)

### Messaging
- **Apache Kafka** : S1, S2, S3

### Storage
- **MinIO** : S1, S5

### Optimisation
- **OR-Tools** : S6 (optimisation sous contraintes)

### Code Analysis
- **JavaParser** : S2, S7
- **CK Metrics** : S2
- **PMD** : S2 (smells)
- **tree-sitter-java** : S7

### Testing
- **JaCoCo, Surefire, PIT** : S3 (parsers)
- **Mockito** : S7 (génération mocks)

### DevOps
- **Docker, Kubernetes** : S9
- **OpenTelemetry** : S9 (observabilité)
- **Keycloak** : S9 (SSO)
- **GitHub Actions / GitLab CI** : S9

### Visualisation
- **Plotly.js** : S8
- **Grafana** : Monitoring

## Ports par Service (si applicable)

- **S1** : Port à définir
- **S2** : 8080 (Spring Boot)
- **S3** : Port FastAPI à définir
- **S4** : Port FastAPI à définir
- **S5** : 8005 (FastAPI)
- **S6** : 8006 (FastAPI)
- **S7** : 8007 (FastAPI)
- **S8** : Port React + FastAPI backend à définir
- **S9** : Port à définir

## Couleurs pour Draw.io

- **Services Collecte/Analyse** : Bleu clair (#E1F5FF) - Bordure bleue (#01579B)
- **Services Tests/Historique** : Orange clair (#FFF4E6) - Bordure orange (#E65100)
- **Services ML/Features** : Violet clair (#F3E5F5) - Bordure violette (#4A148C)
- **Services Priorisation/Scaffolding** : Vert clair (#E8F5E9) - Bordure verte (#1B5E20)
- **Service Dashboard** : Jaune clair (#FFF9C4) - Bordure jaune (#F57F17)
- **Services Infrastructure** : Noir (#000000) - Texte blanc
- **Bases de Données** : Bleu foncé (#336791) - Texte blanc
- **Stockage** : Jaune (#FFC107) - Texte noir
- **Feature Store** : Vert (#4CAF50) - Texte blanc
- **MLflow** : Bleu (#0194E2) - Texte blanc
- **Keycloak** : Violet (#7B68EE) - Texte blanc
- **Grafana** : Orange (#F46800) - Texte blanc

## Instructions pour Draw.io

1. Ouvrir draw.io (https://app.diagrams.net/)
2. Créer un nouveau diagramme
3. Utiliser les couleurs définies ci-dessus
4. Organiser les services en couches horizontales
5. Placer les services infrastructure en bas
6. Utiliser des flèches colorées selon le type de flux :
   - Bleu : Données/Events
   - Vert : Features
   - Orange : Résultats/Visualisation
   - Noir : Infrastructure
7. Ajouter une légende en bas à gauche




