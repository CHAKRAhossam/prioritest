# Rapport d'Analyse du Projet PRIORITEST

**Date :** 2024  
**Projet :** Plateforme de Recommandation Automatisée des Classes à Tester (ML Test Prioritization)  
**Version :** 1.0

---

## Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Diagramme BPMN avec Description Détaillée des Processus Métiers](#diagramme-bpmn)
3. [Architecture Microservices](#architecture-microservices)
4. [Conception de Chaque Microservice](#conception-microservices)
5. [Maquettes UI/UX](#maquettes-uiux)
6. [Conclusion](#conclusion)

---

## 1. Vue d'Ensemble

PRIORITEST est une plateforme de recommandation automatisée des classes logicielles à tester en priorité, utilisant le Machine Learning pour améliorer la couverture unitaire. Le projet est organisé en **9 microservices** avec une architecture distribuée utilisant Kafka pour la communication asynchrone et des APIs REST pour la communication synchrone.

### Objectif du Projet

Améliorer la qualité logicielle en identifiant automatiquement les classes Java les plus critiques à tester, en combinant :
- Analyse statique du code
- Historique des tests et couverture
- Machine Learning pour prédire les risques
- Optimisation sous contraintes pour la priorisation
- Génération automatique de tests

### Équipe

- **Haytam Ta** : Services S1 (CollecteDepots) & S2 (AnalyseStatique)
- **Hicham Kaou** : Services S4 (PretraitementFeatures) & S5 (MLService)
- **Hossam Chakra** : Services S6 (MoteurPriorisation) & S7 (TestScaffolder)
- **Ilyas Michich** : Service S8 (DashboardQualite)
- **Oussama Boujdig** : Services S3 (HistoriqueTests) & S9 (Integrations)

---

## 2. Diagramme BPMN avec Description Détaillée des Processus Métiers

### 2.1 Diagrammes BPMN Disponibles

Le projet contient plusieurs diagrammes BPMN décrivant les processus métiers :

#### 2.1.1 Service 6 - Moteur de Priorisation

**Fichier :** `docs/diagrams/service6_swimlanes.svg`

**Description du Processus :**

Le workflow principal du Service 6 transforme les scores ML en liste ordonnée en intégrant l'effort, la criticité des modules, les dépendances et les objectifs de sprint.

**Étapes du Processus :**

1. **Réception de la Requête (API Layer)**
   - Début : Réception d'une requête HTTP POST `/prioritize`
   - Input : `PrioritizationRequest` (repository_id, sprint_id, constraints)
   - Query param : `strategy` (maximize_popt20, top_k_coverage, budget_optimization, coverage_optimization, multi_objective)

2. **Validation (API Layer)**
   - Validation de la requête et des paramètres
   - Si invalide → Erreur 422 (Bad Request)
   - Si valide → Continuer

3. **Intégration ML (ML Integration Layer)**
   - Appel au Service S5 (ML Service) : `GET /predictions`
   - Récupération des prédictions (risk_score, loc, complexity)
   - Si aucune prédiction trouvée → Erreur 404
   - Si prédictions disponibles → Continuer

4. **Traitement (Processing Layer)**
   - **Calcul de l'effort** : Calcul de `effort_hours` par classe
     - Formule : `effort_hours = (LOC / loc_per_hour) * complexity_multiplier`
   - **Score effort-aware** : `effort_aware_score = risk_score / effort_hours`
   - **Application de la criticité** : Détection du module (auth, payment, etc.)
     - Poids : high=1.5, medium=1.2, low=1.0
     - Ajustement : `effort_aware_score = effort_aware_score * weight`

5. **Stratégie (Strategy Layer)**
   - Application de la stratégie de priorisation sélectionnée :
     - **maximize_popt20** : Tri simple par score décroissant
     - **top_k_coverage** : Sélection des K meilleures classes
     - **budget_optimization** : Optimisation ILP avec contrainte budget (OR-Tools)
     - **coverage_optimization** : Optimisation ILP avec contrainte couverture (OR-Tools)
     - **multi_objective** : Optimisation ILP multi-contraintes (OR-Tools)
   - Calcul des métriques (Popt@20, Recall@Top20, Coverage Gain)

6. **Sortie (Output Layer)**
   - Construction de la réponse avec plan priorisé
   - Sauvegarde optionnelle dans PostgreSQL
   - Retour HTTP 200 OK avec JSON

**Swimlanes :**
- **API** : Gestion des requêtes HTTP (FastAPI Router)
- **ML INTEGRATION** : Appels externes (ML Service S5)
- **PROCESSING** : Services métier (EffortCalculator, CriticalityService)
- **STRATEGY** : Application des stratégies (PrioritizationStrategies, OptimizationService)
- **OUTPUT** : Transformation de données et stockage

#### 2.1.2 Service 7 - Test Scaffolder

**Fichier :** `docs/diagrams/diagramBPMN_S7.svg`

**Description du Processus :**

Le workflow du Service 7 génère des squelettes de tests JUnit avec suggestions de cas de test.

**Étapes du Processus :**

1. **Réception de la Requête**
   - Début : Réception d'une requête avec code Java
   - Validation des paramètres d'entrée

2. **Validation**
   - Vérification de la validité du code Java
   - Si invalide → Retour d'erreur

3. **Récupération des Données**
   - Appel à un service externe si nécessaire
   - Récupération des données de la source

4. **Transformation**
   - Transformation de la structure des données
   - Enrichissement avec métadonnées

5. **Préparation**
   - Préparation pour le traitement
   - Application de la logique métier

6. **Calcul des Métriques**
   - Calcul des métriques de qualité
   - Assemblage du résultat final

7. **Formatage**
   - Formatage de la réponse
   - Stockage optionnel pour usage futur

8. **Envoi de la Réponse**
   - Envoi de la réponse au client
   - Fin du processus

**Méthodes Disponibles :**
- Tri par priorité
- Filtrage par critères
- Optimisation pour meilleurs résultats

**Opérations de Traitement :**
- Amélioration et enrichissement des données
- Calcul et ajustement des scores

### 2.2 Processus Métiers Globaux

#### 2.2.1 Pipeline de Collecte
```
GitHub/GitLab/Jira → S1 → Kafka → S2 → Feast
                    ↓
              PostgreSQL + MinIO
```

#### 2.2.2 Pipeline ML
```
Feast → S4 → Feast → S5 → MLflow + MinIO
                      ↓
                    S6 → PostgreSQL
```

#### 2.2.3 Pipeline de Priorisation
```
S5 → S6 → S7 → S8
         ↓
    PostgreSQL
```

#### 2.2.4 Pipeline Visualisation
```
S6 + S7 → S8 → Grafana
```

#### 2.2.5 Pipeline Intégrations
```
S9 → GitHub/GitLab (PR Comments)
S9 → Keycloak (Auth)
```

---

## 3. Architecture Microservices

### 3.1 Schéma Vue d'Ensemble

**Fichiers de Diagrammes :**
- `docs/diagrams/Architecture_Prioritest_General.drawio` : Vue générale
- `docs/diagrams/Architecture_Prioritest_Complete.drawio` : Vue complète avec détails techniques

**Architecture Globale :**

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  S8 - Dashboard Qualité (React.js + Vite)          │   │
│  │  localhost:3000                                     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                    API GATEWAY                              │
│  Spring Cloud Gateway - localhost:8080                      │
│  Routage: /s1/**, /s2/**, /s3/**, etc.                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              BACKEND MICROSERVICES LAYER                     │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐         │
│  │  S1  │  │  S2  │  │  S3  │  │  S4  │  │  S5  │         │
│  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘         │
│  ┌──────┐  ┌──────┐  ┌──────┐                              │
│  │  S6  │  │  S7  │  │  S9  │                              │
│  └──────┘  └──────┘  └──────┘                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│           INFRASTRUCTURE & DATA LAYER                        │
│  Kafka | PostgreSQL | TimescaleDB | MinIO | Feast | MLflow  │
│  Keycloak | Grafana | GitHub/GitLab/Jira APIs               │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Rôle de Chaque Microservice

#### S1 - Collecte Depots
**Responsable :** Haytam Ta  
**Rôle :** Ingestion des dépôts Git/GitHub/GitLab, issues/bugs Jira, rapports CI/CD  
**Port :** 8001

**Fonctionnalités principales :**
- Ingestion Git/GitHub/GitLab via JGit et APIs
- Collecte des issues Jira
- Récupération des rapports CI/CD
- Production d'événements Kafka
- Stockage des métadonnées dans PostgreSQL
- Archivage des artefacts dans MinIO

#### S2 - Analyse Statique
**Responsable :** Haytam Ta  
**Rôle :** Extraction de métriques de code (LOC, complexité, CK, dépendances, smells)  
**Port :** 8080

**Fonctionnalités principales :**
- Extraction métriques CK (LOC, WMC, DIT)
- Calcul de la complexité cyclomatique
- Détection des dépendances
- Identification des code smells (PMD)
- Publication des features vers Feast Feature Store

#### S3 - Historique Tests
**Responsable :** Oussama Boujdig  
**Rôle :** Agrégation de la couverture et des résultats de tests  
**Port :** 8003

**Fonctionnalités principales :**
- Parsing des rapports JaCoCo (couverture)
- Parsing des rapports Surefire (résultats tests)
- Parsing des rapports PIT (mutation testing)
- Stockage des séries temporelles dans TimescaleDB
- Calcul des métriques de flakiness

#### S4 - Pretraitement Features
**Responsable :** Hicham Kaou  
**Rôle :** Nettoyage, imputation, construction de features dérivées  
**Port :** 8004

**Fonctionnalités principales :**
- Nettoyage et imputation des données
- Construction de features dérivées (churn, auteurs, bug-fix proximity)
- Balancement des classes avec SMOTE
- Split temporel train/val/test
- Data lineage avec DVC
- Publication vers Feast Feature Store

#### S5 - ML Service
**Responsable :** Hicham Kaou  
**Rôle :** Entraînement et service de modèles de risque de défaut  
**Port :** 8005

**Fonctionnalités principales :**
- Entraînement de modèles (XGBoost, LightGBM)
- Prédictions de risque par classe
- Explicabilité avec SHAP
- Gestion des expériences avec MLflow
- Registry de modèles (MLflow)
- Stockage des modèles dans MinIO

#### S6 - Moteur Priorisation
**Responsable :** Hossam Chakra  
**Rôle :** Transformation des scores ML en liste priorisée  
**Port :** 8006

**Fonctionnalités principales :**
- Calcul effort-aware (LOC, complexité)
- Application de la criticité des modules
- Optimisation sous contraintes (OR-Tools)
- Stratégies de priorisation multiples
- Calcul de métriques (Popt@20, Recall@Top20)
- Stockage des plans dans PostgreSQL

#### S7 - Test Scaffolder
**Responsable :** Hossam Chakra  
**Rôle :** Génération de squelettes de tests JUnit avec suggestions  
**Port :** 8007

**Fonctionnalités principales :**
- Analyse AST Java (tree-sitter)
- Génération de tests JUnit
- Génération de mocks Mockito
- Suggestions de cas de test (équivalence, limites, exceptions)
- Checklist de mutation testing
- Sauvegarde dans Git (optionnel)

#### S8 - Dashboard Qualité
**Responsable :** Ilyas Michich  
**Rôle :** Visualisation des recommandations, couverture, risques  
**Port :** 3000 (frontend), backend FastAPI

**Fonctionnalités principales :**
- Interface React.js avec Vite
- Visualisations avec Plotly.js
- WebSockets pour temps réel
- Affichage des plans de priorisation
- Visualisation de la couverture
- Métriques de risque

#### S9 - Integrations & Ops
**Responsable :** Oussama Boujdig  
**Rôle :** Intégration CI/CD, commentaires PR, authentification SSO  
**Port :** 8009

**Fonctionnalités principales :**
- Intégration CI/CD (GitHub Actions, GitLab CI)
- Commentaires automatiques sur PR/MR
- Authentification SSO (Keycloak)
- Orchestration Docker/Kubernetes
- Observabilité (OpenTelemetry)

### 3.3 Technologies Utilisées par Chaque Microservice

#### S1 - Collecte Depots
- **Langage :** Java
- **Bibliothèques :** JGit, GitHub API, GitLab API, Jira API
- **Messaging :** Apache Kafka (Producer)
- **Base de données :** PostgreSQL
- **Stockage :** MinIO

#### S2 - Analyse Statique
- **Langage :** Java
- **Framework :** Spring Boot 3.2
- **Outils d'analyse :** JavaParser, CK Metrics, PMD
- **Feature Store :** Feast
- **Port :** 8080

#### S3 - Historique Tests
- **Langage :** Java
- **Framework :** Spring Boot 3.1.4, FastAPI
- **Parsers :** JaCoCo, Surefire, PIT
- **Base de données :** TimescaleDB (PostgreSQL avec extension)
- **Stockage :** MinIO

#### S4 - Pretraitement Features
- **Langage :** Python 3.11
- **Bibliothèques :** Pandas, scikit-learn, SMOTE
- **Data Versioning :** DVC
- **Feature Store :** Feast

#### S5 - ML Service
- **Langage :** Python 3.11
- **Framework :** FastAPI
- **ML :** XGBoost, LightGBM
- **Explicabilité :** SHAP
- **MLOps :** MLflow (Experiments, Model Registry)
- **Stockage :** MinIO (modèles)

#### S6 - Moteur Priorisation
- **Langage :** Python 3.11
- **Framework :** FastAPI
- **Optimisation :** OR-Tools (SCIP solver)
- **Base de données :** PostgreSQL
- **Validation :** Pydantic

#### S7 - Test Scaffolder
- **Langage :** Python 3.11
- **Framework :** FastAPI
- **Analyse de code :** tree-sitter-java
- **Templates :** Jinja2
- **Git :** GitPython
- **Mocks :** Mockito (génération)

#### S8 - Dashboard Qualité
- **Frontend :** React.js + Vite, TypeScript
- **Visualisation :** Plotly.js
- **Communication :** WebSockets
- **Backend :** FastAPI (Python)
- **Port :** 3000 (frontend)

#### S9 - Integrations & Ops
- **Langage :** Python
- **APIs :** GitHub API, GitLab API
- **Auth :** Keycloak (SSO)
- **Orchestration :** Docker, Kubernetes
- **Observabilité :** OpenTelemetry

### 3.4 Base de Données Associée à Chaque Microservice

#### S1 - Collecte Depots
- **PostgreSQL** : Métadonnées des dépôts, configurations
- **MinIO** : Artefacts CI/CD (rapports, logs)

#### S2 - Analyse Statique
- **Feast Feature Store** : Features extraites (métriques de code)
- Pas de base de données relationnelle directe

#### S3 - Historique Tests
- **TimescaleDB** : Séries temporelles (couverture, résultats tests par commit)
- **MinIO** : Archivage des rapports bruts

#### S4 - Pretraitement Features
- **Feast Feature Store** : Features traitées (entrées et sorties)
- Pas de base de données relationnelle directe

#### S5 - ML Service
- **MLflow** : Registry de modèles, expériences
- **MinIO** : Fichiers de modèles (.pkl)
- Pas de base de données relationnelle directe

#### S6 - Moteur Priorisation
- **PostgreSQL** : Politiques de priorisation, plans sauvegardés
  - Table `Policy` : Politiques avec stratégies et contraintes
  - Table `PrioritizationPlan` : Plans de priorisation historiques

#### S7 - Test Scaffolder
- Pas de base de données relationnelle
- Stockage optionnel dans Git (fichiers générés)

#### S8 - Dashboard Qualité
- Pas de base de données relationnelle directe
- Données en temps réel depuis S6 et S7
- Métriques vers Grafana (monitoring)

#### S9 - Integrations & Ops
- Pas de base de données relationnelle directe
- Configuration via variables d'environnement

### 3.5 Méthodes de Communication entre Microservices

#### Communication Synchrone (HTTP/REST)

**Via API Gateway :**
- **Frontend (S8) → API Gateway → Services** : HTTP/REST
  - Protocole : HTTP/1.1, HTTP/2
  - Format : JSON
  - Authentification : Keycloak (via S9)

**Inter-services directs :**
- **S6 → S5 (ML Service)** : HTTP REST
  - Endpoint : `GET /api/v1/predictions`
  - Format : JSON
  - Timeout : 30 secondes
  - Client : `MLServiceClient` (httpx)

- **S8 → S6, S7** : HTTP REST
  - Endpoints : `/prioritize`, `/scaffold`
  - Format : JSON
  - WebSockets pour temps réel (S8)

#### Communication Asynchrone (Kafka)

**S1 → S2 :**
- **Outil :** Apache Kafka
- **Topic :** `code-analysis-events`
- **Format :** JSON (événements)
- **Type :** Producer (S1) → Consumer (S2)
- **Contenu :** Événements de collecte (nouveaux commits, fichiers)

**S1 → S3 :**
- **Outil :** Apache Kafka
- **Topic :** `test-reports-events`
- **Format :** JSON
- **Type :** Producer (S1) → Consumer (S3)
- **Contenu :** Événements de rapports de tests

**S2 → S4 (via Feast) :**
- **Outil :** Feast Feature Store
- **Type :** Publication/Consommation de features
- **Format :** Features versionnées

#### Communication via Feature Store (Feast)

**S2 → S4 → S5 :**
- **Outil :** Feast Feature Store
- **Type :** Publication et consommation de features
- **Format :** Features versionnées (Parquet, SQL)
- **Workflow :**
  1. S2 publie features brutes → Feast
  2. S4 lit features brutes, traite, publie features traitées → Feast
  3. S5 lit features traitées pour entraînement/prédiction

#### Communication via Stockage (MinIO)

**S1 → S3, S5 :**
- **Outil :** MinIO (S3-compatible)
- **Type :** Stockage d'objets
- **Format :** Fichiers (rapports XML, modèles .pkl)
- **Protocole :** S3 API

#### Communication via MLflow

**S5 → S6 (indirect) :**
- **Outil :** MLflow Model Registry
- **Type :** Registry de modèles
- **Format :** Métadonnées de modèles (version, métriques)

#### Résumé des Communications

| Source | Destination | Type | Outil | Format |
|--------|-------------|------|-------|--------|
| S8 | API Gateway | Synchrone | HTTP/REST | JSON |
| API Gateway | S1-S9 | Synchrone | HTTP/REST | JSON |
| S6 | S5 | Synchrone | HTTP/REST | JSON |
| S1 | S2 | Asynchrone | Kafka | JSON Events |
| S1 | S3 | Asynchrone | Kafka | JSON Events |
| S2 | S4 | Asynchrone | Feast | Features |
| S4 | S5 | Asynchrone | Feast | Features |
| S1 | S3, S5 | Stockage | MinIO | Fichiers |
| S5 | MLflow | Registry | MLflow | Métadonnées |

---

## 4. Conception de Chaque Microservice

### 4.1 Diagrammes de Classes

**Fichier :** `docs/diagrams/class_diagram_s6_s7.puml`

#### 4.1.1 Service 6 - Moteur de Priorisation

**Structure des Classes :**

**API Layer :**
- `PrioritizationRouter` : Gestion des endpoints FastAPI
  - `prioritize(request: PrioritizationRequest)`: PrioritizationResponse
  - `get_prioritization_plan(plan_id: str)`: PrioritizationPlan

**Models (Pydantic) :**
- `PrioritizationRequest` : Requête de priorisation
  - repository_id: str
  - sprint_id: Optional[str]
  - constraints: Optional[Dict]
- `PrioritizationResponse` : Réponse avec plan priorisé
  - prioritized_plan: List[PrioritizedClass]
  - metrics: PrioritizationMetrics
- `PrioritizedClass` : Classe priorisée
  - class_name: str
  - priority: int
  - risk_score: float
  - effort_hours: float
  - effort_aware_score: float
  - module_criticality: str
  - strategy: str
  - reason: str
- `PrioritizationMetrics` : Métriques de priorisation
  - total_effort_hours: float
  - estimated_coverage_gain: float
  - popt20_score: Optional[float]
  - recall_top20: Optional[float]

**Services :**
- `EffortCalculator` : Calcul de l'effort
  - calculate_for_classes(predictions: List): List[Dict]
  - calculate_effort(loc: int, complexity: float): float
  - calculate_effort_aware_score(risk: float, effort: float): float
- `CriticalityService` : Gestion de la criticité
  - enrich_with_criticality(classes: List): List[Dict]
  - detect_module_criticality(module_name: str): str
  - apply_criticality_weight(risk_score: float, criticality: str): float
- `OptimizationService` : Optimisation avec OR-Tools
  - optimize_with_constraints(classes: List, constraints: Dict): List[Dict]
  - solve_with_ortools(classes: List, constraints: Dict): List[Dict]
  - greedy_fallback(classes: List, constraints: Dict): List[Dict]
- `PrioritizationStrategies` : Stratégies de priorisation
  - maximize_popt20(classes: List): List[Dict]
  - top_k_coverage(classes: List, k: int): List[Dict]
  - budget_optimization(classes: List, budget: float): List[Dict]
  - coverage_optimization(classes: List, target: float): List[Dict]
  - multi_objective(classes: List, constraints: Dict): List[Dict]
- `MLServiceClient` : Client HTTP pour S5
  - get_predictions(repository_id: str, sprint_id: str): List[Dict]
- `MetricsService` : Calcul des métriques
  - calculate_metrics(prioritized_plan: List, baseline: List): PrioritizationMetrics
  - calculate_popt20(plan: List): float
  - calculate_recall_top20(plan: List): float
- `PolicyService` : Gestion des politiques
  - create_policy(policy_data: Dict): Policy
  - get_policy(policy_id: str): Policy
  - save_plan(plan_data: Dict): PrioritizationPlan

**Database Models (SQLAlchemy) :**
- `Policy` : Politique de priorisation
  - id: str
  - name: str
  - strategy: str
  - constraints: JSON
  - effort_config: JSON
- `PrioritizationPlan` : Plan de priorisation sauvegardé
  - id: str
  - repository_id: str
  - prioritized_classes: JSON
  - total_effort_hours: float
  - estimated_coverage_gain: float

#### 4.1.2 Service 7 - Test Scaffolder

**Structure des Classes :**

**API Layer :**
- `ScaffoldRouter` : Gestion des endpoints FastAPI
  - analyze_class(request: AnalyzeClassRequest): AnalyzeClassResponse
  - generate_test(request: GenerateTestRequest): GenerateTestResponse
  - suggest_test_cases(request: SuggestTestCasesRequest): ClassSuggestions
  - mutation_checklist(request: MutationChecklistRequest): ClassMutationChecklist
  - generate_complete(request: CompleteGenerationRequest): CompleteGenerationResponse

**Models (Pydantic) :**
- `AnalyzeClassRequest` : Requête d'analyse
  - java_code: str
  - file_path: Optional[str]
- `ClassAnalysis` : Résultat d'analyse
  - class_name: str
  - package_name: Optional[str]
  - methods: List[MethodInfo]
  - constructors: List[ConstructorInfo]
  - fields: List[FieldInfo]
  - dependencies: List[str]
- `MethodInfo` : Information sur une méthode
  - name: str
  - return_type: Optional[str]
  - parameters: List[MethodParameter]
  - is_public: bool
  - throws_exceptions: List[str]
- `ClassSuggestions` : Suggestions de tests
  - class_name: str
  - method_suggestions: List[MethodSuggestions]
  - total_suggestions: int
- `TestSuggestion` : Suggestion de cas de test
  - type: TestCaseType
  - description: str
  - example_values: Dict[str, str]
  - expected_outcome: str
- `ClassMutationChecklist` : Checklist de mutation testing
  - class_name: str
  - method_checklists: List[MethodMutationChecklist]
  - total_items: int

**Services :**
- `ASTAnalyzer` : Analyse AST Java
  - analyze_class(java_code: str, file_path: str): Optional[Dict]
- `TestGenerator` : Génération de tests JUnit
  - generate_test_class(class_analysis: ClassAnalysis, test_package: str): str
- `MockGenerator` : Génération de mocks Mockito
  - extract_mock_fields(fields: List[FieldInfo]): List[Dict]
- `TestSuggestionsService` : Suggestions de cas de test
  - generate_suggestions(class_analysis: ClassAnalysis): ClassSuggestions
  - _suggest_equivalence_cases(method: MethodInfo): List[TestSuggestion]
  - _suggest_limit_cases(method: MethodInfo): List[TestSuggestion]
  - _suggest_exception_cases(method: MethodInfo): List[TestSuggestion]
- `MutationChecklistService` : Checklist de mutation
  - generate_checklist(class_analysis: ClassAnalysis): ClassMutationChecklist
- `GitStorageService` : Sauvegarde dans Git
  - save_test_file(test_code: str, class_name: str, branch: str): Dict
  - push_changes(branch: str): None

### 4.2 Cas d'Utilisation

**Fichier :** `docs/diagrams/use_case_diagram_s6_s7.puml`

#### 4.2.1 Service 6 - Moteur de Priorisation

**Acteurs :**
- Développeur
- Système CI/CD
- Service ML (S5)
- Administrateur

**Cas d'Utilisation Principaux :**

**Priorisation :**
- UC_S6_01 : Prioriser les classes à tester
  - Inclut : Calculer l'effort, Appliquer la criticité, Optimiser avec contraintes, Calculer les métriques
- UC_S6_02 : Récupérer un plan de priorisation
- UC_S6_03 : Calculer l'effort (LOC, complexité)
- UC_S6_04 : Appliquer la criticité des modules
- UC_S6_05 : Optimiser avec contraintes (OR-Tools)
- UC_S6_06 : Calculer les métriques de performance

**Gestion des Politiques :**
- UC_S6_07 : Créer une politique de priorisation (Admin)
- UC_S6_08 : Modifier une politique (Admin)
- UC_S6_09 : Supprimer une politique (Admin)
- UC_S6_10 : Consulter les politiques (Admin)

**Stratégies :**
- UC_S6_11 : Maximiser Popt@20
- UC_S6_12 : Top K Coverage
- UC_S6_13 : Optimisation Budget
- UC_S6_14 : Optimisation Couverture
- UC_S6_15 : Multi-objectif

**Relations :**
- UC_S6_01 utilise UC_S6_03, UC_S6_04, UC_S6_05, UC_S6_06
- Les stratégies (UC_S6_11 à UC_S6_15) utilisent UC_S6_05

#### 4.2.2 Service 7 - Test Scaffolder

**Acteurs :**
- Développeur
- Système CI/CD
- Git Repository

**Cas d'Utilisation Principaux :**

**Analyse AST :**
- UC_S7_01 : Analyser une classe Java
- UC_S7_02 : Extraire les méthodes publiques
- UC_S7_03 : Extraire les dépendances
- UC_S7_04 : Identifier les annotations

**Génération de Tests :**
- UC_S7_05 : Générer un squelette de test JUnit
  - Inclut : Analyser la classe, Générer les mocks, Créer la structure AAA, Générer le setup/teardown
- UC_S7_06 : Générer les mocks Mockito
- UC_S7_07 : Créer la structure Arrange-Act-Assert
- UC_S7_08 : Générer le setup/teardown

**Suggestions :**
- UC_S7_09 : Suggérer des cas de test d'équivalence
  - Inclut : Analyser la classe
- UC_S7_10 : Suggérer des cas de test limites
- UC_S7_11 : Suggérer des cas de test d'exceptions
- UC_S7_12 : Suggérer des cas de test null
- UC_S7_13 : Suggérer des cas de test collections

**Mutation Testing :**
- UC_S7_14 : Générer une checklist de mutation testing
  - Inclut : Analyser la classe, Identifier les opérateurs, Estimer le score
- UC_S7_15 : Identifier les opérateurs de mutation
- UC_S7_16 : Estimer le score de mutation

**Stockage Git :**
- UC_S7_17 : Sauvegarder les tests générés dans Git
  - Inclut : Générer un test, Créer une branche Git
- UC_S7_18 : Sauvegarder les suggestions dans Git
- UC_S7_19 : Créer une branche Git
- UC_S7_20 : Pousser vers le remote Git (étend UC_S7_17)

**Génération Complète :**
- UC_S7_21 : Générer complètement (workflow intégré)
  - Inclut : Analyser, Générer test, Suggestions, Checklist, Sauvegarde Git (optionnel)

**Relations Inter-Services :**
- UC_S6_01 peut utiliser UC_S7_21 (optionnel) pour générer des tests pour les classes priorisées

### 4.3 Autres Services (Résumé)

#### S1 - Collecte Depots
**Cas d'Utilisation :**
- Collecter les dépôts Git
- Collecter les issues GitHub/GitLab
- Collecter les issues Jira
- Collecter les rapports CI/CD
- Publier des événements Kafka

#### S2 - Analyse Statique
**Cas d'Utilisation :**
- Extraire les métriques CK
- Calculer la complexité cyclomatique
- Détecter les code smells
- Publier vers Feast

#### S3 - Historique Tests
**Cas d'Utilisation :**
- Parser les rapports JaCoCo
- Parser les rapports Surefire
- Parser les rapports PIT
- Stocker les séries temporelles

#### S4 - Pretraitement Features
**Cas d'Utilisation :**
- Nettoyer les données
- Construire des features dérivées
- Balancer les classes
- Publier vers Feast

#### S5 - ML Service
**Cas d'Utilisation :**
- Entraîner des modèles
- Faire des prédictions
- Expliquer avec SHAP
- Gérer les modèles (MLflow)

#### S8 - Dashboard Qualité
**Cas d'Utilisation :**
- Visualiser les recommandations
- Afficher la couverture
- Afficher les risques
- Recevoir des mises à jour en temps réel

#### S9 - Integrations
**Cas d'Utilisation :**
- Intégrer CI/CD
- Commenter automatiquement les PR
- Gérer l'authentification SSO
- Monitorer avec OpenTelemetry

---

## 5. Maquettes UI/UX

### 5.1 État Actuel

**Statut :** Aucune maquette Figma n'a été trouvée dans le projet.

**Recommandations :**
- Créer des maquettes Figma pour le Service S8 (Dashboard Qualité)
- Inclure :
  - Page d'accueil avec vue d'ensemble
  - Page de visualisation des plans de priorisation
  - Page de détails d'une classe
  - Page de visualisation de la couverture
  - Page de métriques et rapports
  - Composants réutilisables (graphiques, tableaux, filtres)

### 5.2 Spécifications UI/UX Attendues

**Technologies Frontend :**
- React.js + Vite
- TypeScript
- Plotly.js pour les visualisations
- WebSockets pour les mises à jour en temps réel

**Composants Principaux :**
- Tableau des classes priorisées
- Graphiques de couverture (ligne, branche)
- Graphiques de risque (heatmap, scatter)
- Filtres et recherche
- Export de rapports

---

## 6. Conclusion

### 6.1 Résumé

Le projet PRIORITEST présente une architecture microservices bien structurée avec :

✅ **Architecture complète :**
- 9 microservices bien définis
- Communication synchrone (HTTP/REST) et asynchrone (Kafka)
- Feature Store (Feast) pour la gestion des features ML
- Infrastructure complète (bases de données, stockage, monitoring)

✅ **Documentation technique :**
- Diagrammes d'architecture (Draw.io)
- Diagrammes BPMN pour les processus métiers
- Diagrammes de classes (PlantUML)
- Diagrammes de cas d'utilisation (PlantUML)

✅ **Conception détaillée :**
- Rôles et responsabilités clairs par service
- Technologies bien documentées
- Bases de données associées identifiées
- Méthodes de communication documentées

### 6.2 Points Forts

1. **Séparation des responsabilités** : Chaque microservice a un rôle clair et bien défini
2. **Architecture scalable** : Utilisation de Kafka pour la communication asynchrone
3. **ML Pipeline complet** : De la collecte à la prédiction avec Feature Store
4. **Documentation technique** : Diagrammes BPMN, classes, et cas d'utilisation
5. **Technologies modernes** : FastAPI, React.js, OR-Tools, MLflow

### 6.3 Améliorations Recommandées

1. **Maquettes UI/UX** : Créer des maquettes Figma pour le Dashboard (S8)
2. **Documentation API** : Compléter la documentation OpenAPI/Swagger pour tous les services
3. **Tests** : Augmenter la couverture de tests (unitaires et d'intégration)
4. **Monitoring** : Compléter l'intégration avec Grafana et Prometheus
5. **Sécurité** : Documenter les mécanismes d'authentification et d'autorisation

### 6.4 Prochaines Étapes

1. Finaliser les maquettes UI/UX du Dashboard
2. Compléter la documentation API de tous les services
3. Mettre en place les tests d'intégration end-to-end
4. Configurer le monitoring complet (Grafana, Prometheus, Alerting)
5. Préparer le déploiement en production

---

**Fin du Rapport**

*Rapport généré le : 2024*  
*Version : 1.0*





