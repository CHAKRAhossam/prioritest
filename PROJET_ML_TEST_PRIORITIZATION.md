# Projet ML Test Prioritization

**Clé du projet :** MTP  
**Nom du projet :** ML Test Prioritization  
**Type :** Scrum

---

## 📋 Vue d'ensemble du projet

Ce projet vise à créer une plateforme de recommandation automatisée des classes logicielles à tester en priorité, en utilisant le Machine Learning pour améliorer la couverture unitaire. Le système analyse les métriques de code, l'historique des commits, la couverture et les bugs pour identifier les classes à haut risque de défaut.

---

## 🎯 Les 9 Épics du projet

### Epic 1 : S1 - Collecte de Dépôts
**Responsable :** Haytam Ta  
**Description :** Ingestion des dépôts (Git/GitHub/GitLab), issues/bugs (Jira/GitHub Issues), artefacts CI (rapports tests/couverture)

### Epic 2 : S2 - Analyse Statique
**Responsable :** Haytam Ta  
**Description :** Extraction de métriques de code : LOC, complexité cyclomatique (McCabe), CK (WMC, DIT, NOC, CBO, RFC, LCOM), dépendances, smells

### Epic 3 : S3 - Historique des Tests
**Responsable :** Oussama Boujdig  
**Description :** Agréger couverture et résultats : line/branch coverage, tests KO/OK, flakiness, mutation score

### Epic 4 : S4 - Prétraitement des Features
**Responsable :** Hicham Kaou  
**Description :** Nettoyage, imputation, encodage ; construction de features dérivées (churn, nb auteurs, fréquence modifs, proximité avec bug-fix commits)

### Epic 5 : S5 - Service ML
**Responsable :** Hicham Kaou  
**Description :** Entraîner/servir modèles de risque de défaut par classe et priorisation effort-aware

### Epic 6 : S6 - Moteur de Priorisation
**Responsable :** Hossam Chakra  
**Description :** Transformer scores en liste ordonnée en intégrant effort (LOC), criticité module, dépendances et objectifs de sprint

### Epic 7 : S7 - Test Scaffolder
**Responsable :** Hossam Chakra  
**Description :** Générer des squelettes JUnit pour classes prioritaires, suggestions de cas (équivalence, limites, mocks)

### Epic 8 : S8 - Dashboard Qualité
**Responsable :** Ilyas Michich  
**Description :** Visualiser recommandations, couverture, risques, tendances et impact (défauts évités)

### Epic 9 : S9 - Intégrations & Ops
**Responsable :** Oussama Boujdig  
**Description :** Intégration CI/CD (GitHub Checks/GitLab MR), commentaires automatiques sur PR, triggers d'entraînement, auth/SSO

---

## 📖 User Stories par Epic

### Epic 1 : S1 - Collecte de Dépôts (Haytam)

1. **US-S1-01: Intégration Git/GitHub**
   - En tant que développeur, je veux que le système collecte automatiquement les commits et métadonnées depuis Git/GitHub pour analyser l'historique du code.

2. **US-S1-02: Intégration GitLab**
   - En tant que développeur, je veux que le système collecte également les données depuis GitLab pour supporter plusieurs plateformes.

3. **US-S1-03: Intégration Jira**
   - En tant que développeur, je veux que le système collecte les issues et bugs depuis Jira pour corréler avec les commits.

4. **US-S1-04: Collecte des rapports CI/CD**
   - En tant que développeur, je veux que le système collecte les rapports de tests et de couverture depuis les pipelines CI/CD.

5. **US-S1-05: Pipeline Kafka et stockage**
   - En tant que développeur, je veux que les données collectées soient publiées dans Kafka et stockées de manière structurée.

### Epic 2 : S2 - Analyse Statique (Haytam)

1. **US-S2-01: Extraction métriques Java**
   - En tant que développeur, je veux que le système extraie toutes les métriques de code pour les classes Java.

2. **US-S2-02: Extraction métriques Python**
   - En tant que développeur, je veux que le système supporte également l'analyse de code Python.

3. **US-S2-03: Analyse des dépendances**
   - En tant que développeur, je veux que le système analyse les dépendances entre classes pour identifier les zones critiques.

4. **US-S2-04: Feature Store avec Feast**
   - En tant que data scientist, je veux que les métriques soient stockées dans Feast pour réutilisation online/offline.

5. **US-S2-05: Support multi-projets**
   - En tant que développeur, je veux que le système gère l'analyse de plusieurs projets simultanément.

### Epic 3 : S3 - Historique des Tests (Oussama)

1. **US-S3-01: Parser rapports JaCoCo**
   - En tant que développeur, je veux que le système parse les rapports JaCoCo pour extraire la couverture par classe.

2. **US-S3-02: Parser rapports Surefire**
   - En tant que développeur, je veux que le système parse les rapports Surefire pour connaître les résultats des tests.

3. **US-S3-03: Parser rapports PIT**
   - En tant que développeur, je veux que le système parse les rapports PIT pour évaluer la qualité des tests.

4. **US-S3-04: Stockage historique TimescaleDB**
   - En tant que développeur, je veux que l'historique de couverture soit stocké dans TimescaleDB pour analyse temporelle.

5. **US-S3-05: Calcul dette de test**
   - En tant que développeur, je veux connaître la dette de test (classes sans tests ou faible couverture).

6. **US-S3-06: API REST pour métriques tests**
   - En tant que développeur, je veux accéder aux métriques de tests via une API REST.

### Epic 4 : S4 - Prétraitement des Features (Hicham)

1. **US-S4-01: Pipeline de nettoyage**
   - En tant que data scientist, je veux que les données soient nettoyées et préparées pour l'apprentissage.

2. **US-S4-02: Features dérivées - Churn**
   - En tant que data scientist, je veux calculer le churn (fréquence de modifications) par classe.

3. **US-S4-03: Features dérivées - Auteurs**
   - En tant que data scientist, je veux calculer les métriques liées aux auteurs pour chaque classe.

4. **US-S4-04: Features dérivées - Bug-fix proximity**
   - En tant que data scientist, je veux calculer la proximité des classes avec les commits de bug-fix.

5. **US-S4-05: Split temporel train/val/test**
   - En tant que data scientist, je veux que les données soient divisées de manière temporelle pour éviter la fuite de données.

6. **US-S4-06: Balancement de classes**
   - En tant que data scientist, je veux équilibrer les classes pour améliorer l'apprentissage.

7. **US-S4-07: Data lineage avec DVC**
   - En tant que data scientist, je veux tracer la provenance des données avec DVC.

8. **US-S4-08: Feature Store Feast**
   - En tant que data scientist, je veux que les features soient versionnées dans Feast.

### Epic 5 : S5 - Service ML (Hicham)

1. **US-S5-01: Modèles de classification**
   - En tant que data scientist, je veux entraîner plusieurs modèles pour prédire le risque de défaut par classe.

2. **US-S5-02: Validation temporelle**
   - En tant que data scientist, je veux valider les modèles avec une stratégie temporelle réaliste.

3. **US-S5-03: Calibration des probabilités**
   - En tant que data scientist, je veux que les probabilités du modèle soient calibrées.

4. **US-S5-04: Détection d'anomalies**
   - En tant que data scientist, je veux utiliser des méthodes non supervisées pour détecter les classes anormales.

5. **US-S5-05: Explicabilité avec SHAP**
   - En tant que développeur, je veux comprendre pourquoi une classe est prédite à risque avec SHAP.

6. **US-S5-06: MLflow - Experiments**
   - En tant que data scientist, je veux tracker tous les experiments ML avec MLflow.

7. **US-S5-07: MLflow - Model Registry**
   - En tant que data scientist, je veux gérer le cycle de vie des modèles avec MLflow Model Registry.

8. **US-S5-08: Service de prédiction**
   - En tant que développeur, je veux un service API pour obtenir les prédictions de risque.

9. **US-S5-09: Stockage modèles**
   - En tant que développeur, je veux que les modèles soient stockés de manière fiable.

### Epic 6 : S6 - Moteur de Priorisation (Hossam)

1. **US-S6-01: Calcul effort-aware**
   - En tant que développeur, je veux que la priorisation tienne compte de l'effort nécessaire (LOC, complexité).

2. **US-S6-02: Intégration criticité module**
   - En tant que développeur, je veux que les classes des modules critiques soient priorisées.

3. **US-S6-03: Optimisation avec OR-Tools**
   - En tant que développeur, je veux optimiser la sélection des classes sous contraintes (budget, temps).

4. **US-S6-04: Stratégies de priorisation**
   - En tant que développeur, je veux différentes stratégies de priorisation selon les objectifs.

5. **US-S6-05: API de priorisation**
   - En tant que développeur, je veux une API pour obtenir le plan de tests priorisé.

6. **US-S6-06: Stockage politiques**
   - En tant que développeur, je veux stocker et gérer les politiques de priorisation.

7. **US-S6-07: Métriques de performance**
   - En tant que développeur, je veux évaluer la performance de la priorisation.

### Epic 7 : S7 - Test Scaffolder (Hossam)

1. **US-S7-01: Analyse AST pour génération**
   - En tant que développeur, je veux que le système analyse l'AST des classes pour générer des tests.

2. **US-S7-02: Génération templates JUnit**
   - En tant que développeur, je veux que le système génère des squelettes de tests JUnit.

3. **US-S7-03: Suggestions cas de test**
   - En tant que développeur, je veux des suggestions de cas de test (équivalence, limites).

4. **US-S7-04: Génération mocks**
   - En tant que développeur, je veux que le système suggère les mocks nécessaires.

5. **US-S7-05: Checklist mutation testing**
   - En tant que développeur, je veux une checklist pour guider les tests de mutation.

6. **US-S7-06: Stockage suggestions**
   - En tant que développeur, je veux que les suggestions soient stockées dans un repo dédié.

7. **US-S7-07: API de génération**
   - En tant que développeur, je veux une API pour générer les tests à la demande.

### Epic 8 : S8 - Dashboard Qualité (Ilyas)

1. **US-S8-01: Interface React.js**
   - En tant que développeur, je veux une interface web moderne pour visualiser les données.

2. **US-S8-02: Vue recommandations**
   - En tant que développeur, je veux voir la liste des classes recommandées à tester.

3. **US-S8-03: Visualisation couverture**
   - En tant que développeur, je veux visualiser la couverture de code par module/classe.

4. **US-S8-04: Visualisation risques**
   - En tant que développeur, je veux visualiser les risques par classe avec SHAP.

5. **US-S8-05: Vue tendances**
   - En tant que développeur, je veux voir les tendances de qualité dans le temps.

6. **US-S8-06: Vue impact**
   - En tant que développeur, je veux voir l'impact du système (défauts évités, temps économisé).

7. **US-S8-07: Vue par repo/module/classe**
   - En tant que développeur, je veux naviguer par repo, module puis classe.

8. **US-S8-08: Exports PDF/CSV**
   - En tant que développeur, je veux exporter les données en PDF/CSV.

9. **US-S8-09: WebSockets temps réel**
   - En tant que développeur, je veux que le dashboard se mette à jour en temps réel.

10. **US-S8-10: API Backend FastAPI**
    - En tant que développeur, je veux une API backend pour alimenter le dashboard.

### Epic 9 : S9 - Intégrations & Ops (Oussama)

1. **US-S9-01: GitHub Checks Integration**
   - En tant que développeur, je veux que le système crée des checks GitHub sur les PR.

2. **US-S9-02: GitLab MR Integration**
   - En tant que développeur, je veux que le système commente automatiquement les MR GitLab.

3. **US-S9-03: Commentaires automatiques PR**
   - En tant que développeur, je veux recevoir des commentaires automatiques sur les PR avec recommandations.

4. **US-S9-04: Policy gate optionnelle**
   - En tant que développeur, je veux une politique de gate (alerte si classe risquée modifiée sans tests).

5. **US-S9-05: Triggers d'entraînement**
   - En tant que data scientist, je veux que les modèles se réentraînent automatiquement.

6. **US-S9-06: Docker & Kubernetes**
   - En tant que développeur, je veux que tous les services soient containerisés et déployables.

7. **US-S9-07: Observabilité OpenTelemetry**
   - En tant que développeur, je veux monitorer tous les services avec OpenTelemetry.

8. **US-S9-08: Authentification SSO Keycloak**
   - En tant que développeur, je veux une authentification centralisée avec Keycloak.

9. **US-S9-09: CI/CD Pipeline**
   - En tant que développeur, je veux un pipeline CI/CD complet.

10. **US-S9-10: Documentation & Guide**
    - En tant que développeur, je veux une documentation complète du système.

---

## 👥 Répartition des tâches par personne (10-12 tâches chacun)

### Haytam Ta (Services 1 & 2) - 12 tâches

**Service 1 - Collecte de Dépôts :**
1. Configurer l'authentification GitHub API (OAuth/Personal Access Token)
2. Implémenter le service de collecte de commits avec JGit
3. Créer le modèle de données pour stocker les commits (PostgreSQL)
4. Configurer l'authentification GitLab API
5. Implémenter le service de collecte GitLab (commits, branches, MR)
6. Configurer l'authentification Jira API (API Token)
7. Implémenter le service de collecte d'issues Jira
8. Implémenter le parser pour rapports JaCoCo (XML)
9. Implémenter le parser pour rapports Surefire
10. Configurer les topics Kafka (commits, issues, coverage)
11. Implémenter le stockage dans PostgreSQL (métadonnées)
12. Implémenter le stockage dans MinIO (artefacts)

**Service 2 - Analyse Statique :**
- Les tâches du Service 2 seront réparties si nécessaire

### Hicham Kaou (Services 4 & 5) - 12 tâches

**Service 4 - Prétraitement des Features :**
1. Implémenter la détection et gestion des valeurs manquantes
2. Implémenter l'imputation des valeurs manquantes (moyenne, médiane, mode)
3. Normaliser les features numériques (StandardScaler, MinMaxScaler)
4. Calculer le nombre de commits par classe sur une période
5. Calculer le nombre de lignes modifiées (added/deleted)
6. Calculer le nombre d'auteurs uniques par classe
7. Identifier les commits de bug-fix (analyse messages, issues)
8. Implémenter le split temporel (train sur anciens commits, test sur récents)
9. Implémenter SMOTE pour sur-échantillonnage
10. Configurer DVC pour versioning des données
11. Définir les feature definitions dans Feast
12. Implémenter l'ingestion des features transformées

**Service 5 - Service ML :**
- Les tâches du Service 5 seront réparties si nécessaire

### Hossam Chakra (Services 6 & 7) - 12 tâches

**Service 6 - Moteur de Priorisation :**
1. Calculer l'effort estimé par classe (basé sur LOC)
2. Implémenter la formule effort-aware (score / effort)
3. Créer les métriques effort-aware (Popt@20)
4. Définir les niveaux de criticité (critique, important, normal)
5. Installer et configurer OR-Tools
6. Définir le problème d'optimisation (maximiser couverture, minimiser effort)
7. Implémenter stratégie top-K couvertures manquantes
8. Implémenter stratégie maximisation Popt@20
9. Créer l'API REST FastAPI
10. Implémenter POST /prioritize (retourne plan JSON)
11. Calculer Popt@20 (effort-aware)
12. Comparer avec baseline heuristiques

**Service 7 - Test Scaffolder :**
- Les tâches du Service 7 seront réparties si nécessaire

### Ilyas Michich (Service 8) - 12 tâches

**Service 8 - Dashboard Qualité :**
1. Créer le projet React.js avec Vite
2. Configurer le routing (React Router)
3. Créer la structure des composants
4. Créer le composant liste des recommandations
5. Afficher le score de risque par classe
6. Créer les graphiques de couverture (Plotly)
7. Afficher l'évolution temporelle de couverture
8. Créer les graphiques SHAP (waterfall, bar)
9. Afficher l'importance globale des features
10. Créer les graphiques de tendances (Grafana/Plotly)
11. Implémenter l'export CSV des recommandations
12. Créer l'API FastAPI backend

### Oussama Boujdig (Services 3 & 9) - 12 tâches

**Service 3 - Historique des Tests :**
1. Implémenter le parser XML JaCoCo
2. Extraire line coverage et branch coverage par classe
3. Implémenter le parser XML Surefire
4. Extraire les tests OK/KO par classe de test
5. Implémenter le parser XML PIT (mutation testing)
6. Créer le schéma TimescaleDB pour séries temporelles
7. Implémenter le calcul de dette de test par classe
8. Créer l'API REST FastAPI
9. Implémenter GET /coverage/{class_name}

**Service 9 - Intégrations & Ops :**
10. Configurer GitHub App ou OAuth
11. Implémenter le service GitHub Checks API
12. Configurer GitLab API (token)

---

## 📚 Guide de compréhension du projet par personne

### 🎯 Haytam Ta - Services 1 & 2

**Pour comprendre le projet, vous devez :**

1. **Comprendre l'architecture globale :**
   - Lire la documentation du projet (PROJECT_OVERVIEW.md si disponible)
   - Comprendre le flux de données : Dépôts Git → Collecte → Analyse → ML → Priorisation → Dashboard

2. **Service 1 - Collecte de Dépôts :**
   - **Étudier :** GitHub API, GitLab API, Jira API
   - **Comprendre :** Comment collecter les commits, issues, et rapports CI/CD
   - **Technologies :** JGit (Java), REST APIs, Kafka, PostgreSQL, MinIO
   - **Objectif :** Créer un pipeline d'ingestion de données depuis plusieurs sources

3. **Service 2 - Analyse Statique :**
   - **Étudier :** Métriques de code (LOC, complexité cyclomatique, métriques CK)
   - **Comprendre :** Comment extraire les métriques depuis le code source
   - **Technologies :** JavaParser, CK (Chidamber & Kemerer), PMD, SonarQube, radon (Python)
   - **Objectif :** Extraire des features pour le modèle ML

4. **Livrables attendus :**
   - Pipeline de collecte fonctionnel
   - Extraction de métriques de code
   - Stockage dans PostgreSQL et MinIO
   - Intégration avec Feast (feature store)

**Ressources à consulter :**
- Documentation GitHub API : https://docs.github.com/en/rest
- Documentation GitLab API : https://docs.gitlab.com/ee/api/
- Documentation Jira API : https://developer.atlassian.com/cloud/jira/platform/rest/v3/
- JavaParser : https://javaparser.org/
- CK Metrics : https://www.spinellis.gr/sw/ckjm/

---

### 🎯 Hicham Kaou - Services 4 & 5

**Pour comprendre le projet, vous devez :**

1. **Comprendre le contexte ML :**
   - Lire sur la prédiction de défauts logiciels (defect prediction)
   - Comprendre les métriques de code et leur impact sur les bugs
   - Étudier les jeux de données PROMISE

2. **Service 4 - Prétraitement des Features :**
   - **Étudier :** Feature engineering, imputation, normalisation, encodage
   - **Comprendre :** Comment créer des features dérivées (churn, bus factor, bug-fix proximity)
   - **Technologies :** Pandas, scikit-learn, DVC, Feast
   - **Objectif :** Préparer les données pour l'apprentissage ML

3. **Service 5 - Service ML :**
   - **Étudier :** Classification binaire, validation temporelle, calibration
   - **Comprendre :** XGBoost, LightGBM, SHAP, MLflow
   - **Technologies :** XGBoost, LightGBM, scikit-learn, SHAP, MLflow
   - **Objectif :** Entraîner un modèle qui prédit le risque de défaut par classe

4. **Livrables attendus :**
   - Pipeline de prétraitement complet
   - Modèle ML entraîné et validé
   - Service API de prédiction
   - Intégration MLflow pour tracking

**Ressources à consulter :**
- PROMISE Repository : http://promise.site.uottawa.ca/SERepository/
- XGBoost Documentation : https://xgboost.readthedocs.io/
- SHAP Documentation : https://shap.readthedocs.io/
- MLflow Documentation : https://www.mlflow.org/docs/latest/index.html
- Feature Engineering : "Feature Engineering for Machine Learning" par Alice Zheng

---

### 🎯 Hossam Chakra - Services 6 & 7

**Pour comprendre le projet, vous devez :**

1. **Comprendre la priorisation :**
   - Lire sur l'effort-aware prioritization (Popt@20)
   - Comprendre comment combiner risque et effort
   - Étudier les stratégies d'optimisation

2. **Service 6 - Moteur de Priorisation :**
   - **Étudier :** Optimisation sous contraintes, effort-aware metrics
   - **Comprendre :** Comment transformer les scores ML en plan de tests priorisé
   - **Technologies :** OR-Tools, PostgreSQL, FastAPI
   - **Objectif :** Créer un moteur qui génère une liste ordonnée de classes à tester

3. **Service 7 - Test Scaffolder :**
   - **Étudier :** Analyse AST, génération de code, templates
   - **Comprendre :** Comment analyser le code et générer des squelettes de tests
   - **Technologies :** Spoon, JavaParser, Mustache, JUnit, Mockito
   - **Objectif :** Accélérer l'écriture de tests en générant des squelettes

4. **Livrables attendus :**
   - Moteur de priorisation avec différentes stratégies
   - API de priorisation
   - Générateur de squelettes de tests
   - API de génération de tests

**Ressources à consulter :**
- OR-Tools Documentation : https://developers.google.com/optimization
- Effort-Aware Defect Prediction : Rechercher "Popt@20" et "effort-aware"
- Spoon Documentation : https://spoon.gforge.inria.fr/
- JavaParser Documentation : https://javaparser.org/

---

### 🎯 Ilyas Michich - Service 8

**Pour comprendre le projet, vous devez :**

1. **Comprendre les besoins utilisateurs :**
   - Lire les user stories du dashboard
   - Comprendre quelles visualisations sont nécessaires
   - Étudier les métriques à afficher (couverture, risques, tendances)

2. **Service 8 - Dashboard Qualité :**
   - **Étudier :** React.js, visualisation de données, WebSockets
   - **Comprendre :** Comment créer une interface intuitive pour visualiser les recommandations
   - **Technologies :** React.js, Vite, Plotly, FastAPI, WebSockets
   - **Objectif :** Créer un dashboard interactif et en temps réel

3. **Livrables attendus :**
   - Interface React.js complète
   - Visualisations (couverture, risques, tendances, SHAP)
   - Exports PDF/CSV
   - API backend FastAPI
   - WebSockets pour mises à jour temps réel

**Ressources à consulter :**
- React.js Documentation : https://react.dev/
- Plotly.js Documentation : https://plotly.com/javascript/
- FastAPI Documentation : https://fastapi.tiangolo.com/
- WebSockets : https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API

---

### 🎯 Oussama Boujdig - Services 3 & 9

**Pour comprendre le projet, vous devez :**

1. **Comprendre l'intégration :**
   - Lire sur l'intégration CI/CD
   - Comprendre les webhooks et APIs
   - Étudier Docker et Kubernetes

2. **Service 3 - Historique des Tests :**
   - **Étudier :** Parsing XML (JaCoCo, Surefire, PIT), TimescaleDB
   - **Comprendre :** Comment extraire et stocker les métriques de tests
   - **Technologies :** XML parsing, TimescaleDB, FastAPI
   - **Objectif :** Agréger l'historique de couverture et résultats de tests

3. **Service 9 - Intégrations & Ops :**
   - **Étudier :** GitHub Checks API, GitLab MR API, Docker, Kubernetes, OpenTelemetry
   - **Comprendre :** Comment intégrer le système dans le workflow de développement
   - **Technologies :** GitHub/GitLab APIs, Docker, Kubernetes, OpenTelemetry, Keycloak
   - **Objectif :** Intégrer le système dans CI/CD et monitorer les services

4. **Livrables attendus :**
   - Parsers pour rapports de tests
   - Stockage historique dans TimescaleDB
   - Intégration GitHub/GitLab
   - Dockerfiles et Kubernetes manifests
   - Observabilité complète

**Ressources à consulter :**
- JaCoCo Documentation : https://www.jacoco.org/jacoco/trunk/doc/
- TimescaleDB Documentation : https://docs.timescale.com/
- GitHub Checks API : https://docs.github.com/en/rest/checks
- Docker Documentation : https://docs.docker.com/
- Kubernetes Documentation : https://kubernetes.io/docs/
- OpenTelemetry Documentation : https://opentelemetry.io/docs/

---

## 🚀 Étapes pour démarrer

### Pour tous les membres :

1. **Lire la documentation du projet** (ce document et autres fichiers de documentation)
2. **Comprendre l'architecture globale** (9 microservices)
3. **Étudier les technologies** assignées à votre service
4. **Configurer l'environnement de développement**
5. **Créer un prototype simple** pour valider la compréhension
6. **Participer aux réunions d'équipe** pour synchroniser

### Checklist de démarrage :

- [ ] Lire ce document en entier
- [ ] Comprendre votre service assigné
- [ ] Étudier les technologies nécessaires
- [ ] Configurer l'environnement de développement
- [ ] Créer un dépôt Git pour votre service
- [ ] Créer un README pour votre service
- [ ] Faire un prototype simple
- [ ] Partager avec l'équipe

---

## 📊 Métriques de succès du projet

- **Modèle performant** : F1 > 0.7, PR-AUC > 0.8
- **Effort-aware** : Popt@20 > baseline heuristiques
- **Couverture** : Augmentation de 20% de la couverture unitaire
- **Temps économisé** : Réduction de 30% du temps de sélection manuelle
- **Pipeline complet** : Tous les services déployés et fonctionnels

---

## 📞 Contacts et ressources

- **Projet Jira :** https://prioritest.atlassian.net/browse/MTP
- **Repository Git :** (à créer)
- **Documentation :** (à créer dans le repo)

---

**Bonne chance à toute l'équipe ! 🚀**

