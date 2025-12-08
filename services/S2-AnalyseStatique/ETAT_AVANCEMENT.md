# 📊 État d'Avancement du Projet - Recommandation Automatisée des Classes à Tester

## 🎯 Vue d'Ensemble

**Projet** : Recommandation Automatisée des Classes Logicielles à Tester (ML pour améliorer la couverture unitaire)

**Date** : 30 novembre 2025

**Progression Globale** : ~15% (1 microservice sur 9 partiellement implémenté)

---

## 📋 État des 9 Microservices

### 1. ❌ CollecteDepots - **NON COMMENCÉ**
**Rôle** : Ingestion des dépôts (Git/GitHub/GitLab), issues/bugs, artefacts CI

**État** :
- ❌ Pas de code
- ❌ Pas d'intégration GitHub/GitLab API
- ❌ Pas de Kafka
- ❌ Pas de PostgreSQL/TimescaleDB
- ❌ Pas de MinIO
- ❌ Pas de webhooks/cron

**Priorité** : 🔴 Haute (nécessaire pour alimenter les autres services)

---

### 2. ⚠️ AnalyseStatique - **PARTIELLEMENT IMPLÉMENTÉ (~50%)**
**Rôle** : Extraction de métriques de code (LOC, complexité, CK, dépendances, smells)

**État** :

#### ✅ **FAIT** :
- ✅ API REST fonctionnelle (`POST /metrics/analyze`)
- ✅ Extraction ZIP de projets
- ✅ Découverte automatique des fichiers Java
- ✅ Métriques CK implémentées :
  - ✅ LOC (Lines of Code)
  - ✅ WMC (Weighted Methods per Class) - Complexité cyclomatique
  - ✅ DIT (Depth of Inheritance Tree) - Version simplifiée
  - ✅ CBO (Coupling Between Objects) - Version approximative
  - ✅ RFC (Response For Class)
  - ✅ LCOM (Lack of Cohesion of Methods)
- ✅ Utilisation de JavaParser pour AST
- ✅ Bibliothèque CK intégrée (mais peu exploitée)
- ✅ Code professionnel (logging, DI, exception handling, tests)
- ✅ Application Spring Boot opérationnelle sur port 8080

#### ⚠️ **PARTIELLEMENT FAIT** :
- ⚠️ Extraction dépendances : Structure présente mais **vide** (retourne liste vide)
- ⚠️ Détection smells : Structure présente mais **vide** (retourne liste vide)

#### ❌ **MANQUE** :
- ❌ NOC (Number of Children) - Non calculé (nécessite vue globale projet)
- ❌ Dépendances in/out degree - Non calculées
- ❌ Smells réels - Non détectés (God Class, Long Method, etc.)
- ❌ PostgreSQL/TimescaleDB - Utilise H2 en mémoire
- ❌ Feast (Feature Store) - Pas implémenté
- ❌ Normalisation par module/langage - Pas fait
- ❌ Gestion multi-projets - Pas fait
- ❌ Support multi-langages (Python/radon) - Seulement Java
- ❌ API gRPC - Seulement REST
- ❌ Intégration Kafka - Pas fait

**Priorité** : 🟡 Moyenne (compléter dépendances et smells)

---

### 3. ❌ HistoriqueTests - **NON COMMENCÉ**
**Rôle** : Agréger couverture et résultats (JaCoCo, Surefire, PIT)

**État** :
- ❌ Pas de code
- ❌ Pas de parsers JaCoCo/Surefire/PIT
- ❌ Pas de TimescaleDB pour évolution
- ❌ Pas de calcul de dette de test

**Priorité** : 🔴 Haute (nécessaire pour ML)

---

### 4. ❌ PrétraitementFeatures - **NON COMMENCÉ**
**Rôle** : Nettoyage, imputation, encodage, features dérivées

**État** :
- ❌ Pas de code
- ❌ Pas de Python/Pandas/scikit-learn
- ❌ Pas de DVC pour data lineage
- ❌ Pas de Feast pour features versionnées
- ❌ Pas de balancement (SMOTE/cost-sensitive)
- ❌ Pas de split train/val/test time-aware

**Priorité** : 🔴 Haute (nécessaire pour ML)

---

### 5. ❌ MLService - **NON COMMENCÉ**
**Rôle** : Entraîner/servir modèles de risque de défaut

**État** :
- ❌ Pas de code
- ❌ Pas de XGBoost/LightGBM/LogReg/RandomForest
- ❌ Pas de MLflow (experiments, model registry)
- ❌ Pas de validation time-aware
- ❌ Pas de calibration des probabilités
- ❌ Pas de SHAP pour explicabilité

**Priorité** : 🔴 Haute (cœur du projet)

---

### 6. ❌ MoteurPriorisation - **NON COMMENCÉ**
**Rôle** : Transformer scores en liste ordonnée (effort-aware, Popt@20)

**État** :
- ❌ Pas de code
- ❌ Pas d'OR-Tools pour optimisation
- ❌ Pas de stratégies effort-aware
- ❌ Pas de PostgreSQL pour politiques

**Priorité** : 🟡 Moyenne

---

### 7. ❌ TestScaffolder - **NON COMMENCÉ**
**Rôle** : Générer squelettes JUnit pour classes prioritaires

**État** :
- ❌ Pas de code
- ❌ Pas d'analyse AST (Spoon/JavaParser)
- ❌ Pas de templates Mustache

**Priorité** : 🟢 Basse (optionnel)

---

### 8. ❌ DashboardQualité - **NON COMMENCÉ**
**Rôle** : Visualiser recommandations, couverture, risques, tendances

**État** :
- ❌ Pas de code
- ❌ Pas de React.js
- ❌ Pas de FastAPI
- ❌ Pas de websockets
- ❌ Pas de Grafana/Plotly

**Priorité** : 🟡 Moyenne (important pour démonstration)

---

### 9. ❌ Intégrations & Ops - **NON COMMENCÉ**
**Rôle** : Intégration CI/CD, commentaires PR, triggers, auth

**État** :
- ❌ Pas de code
- ❌ Pas de GitHub Actions/GitLab CI
- ❌ Pas de Docker/Kubernetes
- ❌ Pas d'OpenTelemetry
- ❌ Pas de Keycloak

**Priorité** : 🟡 Moyenne

---

## 📈 Résumé par Catégorie

### Infrastructure & Base de Données
- ❌ PostgreSQL/TimescaleDB : 0%
- ❌ MinIO : 0%
- ❌ Kafka : 0%
- ❌ Feast : 0%
- ❌ MLflow : 0%
- ❌ DVC : 0%

### Services Backend
- ⚠️ AnalyseStatique : ~50%
- ❌ CollecteDepots : 0%
- ❌ HistoriqueTests : 0%
- ❌ PrétraitementFeatures : 0%
- ❌ MLService : 0%
- ❌ MoteurPriorisation : 0%
- ❌ TestScaffolder : 0%

### Frontend & Visualisation
- ❌ DashboardQualité : 0%

### DevOps & Intégration
- ❌ Intégrations & Ops : 0%

---

## 🎯 Prochaines Étapes Prioritaires

### Phase 1 : Compléter AnalyseStatique (2-3 semaines)
1. ✅ Implémenter extraction dépendances (graphe in/out degree)
2. ✅ Implémenter détection smells (God Class, Long Method, etc.)
3. ✅ Calculer NOC (analyse globale projet)
4. ⚠️ Ajouter PostgreSQL/TimescaleDB pour persistance
5. ⚠️ Intégrer Feast pour feature store

### Phase 2 : CollecteDepots (3-4 semaines)
1. ❌ Intégration GitHub/GitLab API
2. ❌ Setup Kafka pour ingestion
3. ❌ Setup PostgreSQL + TimescaleDB
4. ❌ Setup MinIO pour artefacts
5. ❌ Webhooks et cron jobs

### Phase 3 : HistoriqueTests (2-3 semaines)
1. ❌ Parsers JaCoCo/Surefire/PIT
2. ❌ Stockage dans TimescaleDB
3. ❌ Calcul dette de test

### Phase 4 : PrétraitementFeatures (2-3 semaines)
1. ❌ Pipeline Python (Pandas, scikit-learn)
2. ❌ Features dérivées (churn, nb auteurs, etc.)
3. ❌ Split time-aware
4. ❌ Intégration Feast

### Phase 5 : MLService (4-5 semaines)
1. ❌ Entraînement modèles (XGBoost, LightGBM)
2. ❌ MLflow pour tracking
3. ❌ Validation time-aware
4. ❌ SHAP pour explicabilité

### Phase 6 : MoteurPriorisation (2 semaines)
1. ❌ OR-Tools pour optimisation
2. ❌ Stratégies effort-aware (Popt@20)

### Phase 7 : DashboardQualité (3-4 semaines)
1. ❌ Frontend React.js
2. ❌ Backend FastAPI
3. ❌ Visualisations (Grafana/Plotly)

### Phase 8 : Intégrations & Ops (2-3 semaines)
1. ❌ CI/CD (GitHub Actions)
2. ❌ Docker/Kubernetes
3. ❌ Observabilité (OpenTelemetry)

---

## 📊 Métriques de Progression

- **Microservices implémentés** : 0/9 (0%)
- **Microservices partiellement implémentés** : 1/9 (AnalyseStatique ~50%)
- **Code qualité** : ✅ Professionnel (8.5/10)
- **Tests** : ⚠️ Partiels (tests unitaires de base)
- **Documentation** : ✅ JavaDoc complète
- **Infrastructure** : ❌ Aucune (H2 en mémoire seulement)

---

## 🚀 Conclusion

**État actuel** : Le projet est au stade initial. Seul le microservice **AnalyseStatique** est partiellement implémenté avec une base solide et du code professionnel. Les métriques CK de base fonctionnent, mais il manque :
- L'extraction complète des dépendances
- La détection des smells
- Toute l'infrastructure (BDD, Kafka, Feast, MLflow)
- Les 8 autres microservices

**Recommandation** : Compléter d'abord AnalyseStatique (dépendances + smells), puis implémenter CollecteDepots et HistoriqueTests pour avoir des données, avant de passer au ML.



