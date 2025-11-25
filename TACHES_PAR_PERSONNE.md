# Répartition détaillée des tâches par personne

## Haytam Ta - Services 1 & 2 (12 tâches)

### Service 1 - Collecte de Dépôts (6 tâches)

1. **Configurer l'authentification GitHub API (OAuth/Personal Access Token)**
   - Créer un Personal Access Token GitHub
   - Implémenter l'authentification OAuth si nécessaire
   - Tester la connexion à l'API GitHub

2. **Implémenter le service de collecte de commits avec JGit**
   - Intégrer la bibliothèque JGit
   - Créer un service qui clone/analyse les dépôts Git
   - Extraire les commits avec métadonnées (auteur, date, message, fichiers modifiés)

3. **Créer le modèle de données pour stocker les commits (PostgreSQL)**
   - Concevoir le schéma de base de données
   - Créer les tables (commits, files_changed, authors)
   - Implémenter les migrations avec un outil (Flyway, Liquibase)

4. **Configurer l'authentification GitLab API**
   - Créer un token GitLab
   - Implémenter l'authentification GitLab API
   - Tester la connexion

5. **Implémenter le service de collecte GitLab (commits, branches, MR)**
   - Utiliser GitLab API pour récupérer commits, branches, merge requests
   - Adapter le format de données pour correspondre au modèle PostgreSQL
   - Gérer la pagination GitLab

6. **Configurer l'authentification Jira API (API Token)**
   - Créer un API token Jira
   - Implémenter l'authentification Jira API
   - Tester la connexion

### Service 1 - Suite (6 tâches supplémentaires)

7. **Implémenter le service de collecte d'issues Jira**
   - Utiliser Jira API pour récupérer les issues
   - Filtrer les bugs/defects
   - Extraire les métadonnées (priorité, statut, assigné, dates)

8. **Implémenter le parser pour rapports JaCoCo (XML)**
   - Parser les fichiers XML JaCoCo
   - Extraire line coverage et branch coverage par classe
   - Calculer les pourcentages de couverture

9. **Implémenter le parser pour rapports Surefire**
   - Parser les fichiers XML Surefire
   - Extraire les résultats de tests (OK/KO)
   - Identifier les tests flaky

10. **Configurer les topics Kafka (commits, issues, coverage)**
    - Créer les topics Kafka nécessaires
    - Définir les schémas de messages (Avro ou JSON)
    - Configurer les partitions et réplication

11. **Implémenter le stockage dans PostgreSQL (métadonnées)**
    - Créer les producers Kafka
    - Implémenter les consumers qui écrivent dans PostgreSQL
    - Gérer les transactions et la cohérence

12. **Implémenter le stockage dans MinIO (artefacts)**
    - Configurer MinIO (S3-compatible)
    - Implémenter le stockage des rapports (JaCoCo, Surefire, PIT)
    - Organiser par projet/commit

---

## Hicham Kaou - Services 4 & 5 (12 tâches)

### Service 4 - Prétraitement des Features (6 tâches)

1. **Implémenter la détection et gestion des valeurs manquantes**
   - Identifier les colonnes avec valeurs manquantes
   - Décider de la stratégie (suppression, imputation)
   - Implémenter la détection automatique

2. **Implémenter l'imputation des valeurs manquantes (moyenne, médiane, mode)**
   - Implémenter différentes stratégies d'imputation
   - Choisir la meilleure stratégie par feature
   - Valider l'imputation

3. **Normaliser les features numériques (StandardScaler, MinMaxScaler)**
   - Implémenter StandardScaler (moyenne=0, écart-type=1)
   - Implémenter MinMaxScaler (0-1)
   - Choisir la normalisation appropriée

4. **Calculer le nombre de commits par classe sur une période**
   - Agréger les commits par classe
   - Calculer sur différentes périodes (7j, 30j, 90j)
   - Créer les features temporelles

5. **Calculer le nombre de lignes modifiées (added/deleted)**
   - Analyser les diffs des commits
   - Calculer added_lines et deleted_lines par classe
   - Créer des ratios (churn normalisé)

6. **Calculer le nombre d'auteurs uniques par classe**
   - Compter les auteurs distincts par classe
   - Calculer la diversité des auteurs
   - Identifier le bus factor

### Service 4 - Suite (6 tâches)

7. **Identifier les commits de bug-fix (analyse messages, issues)**
   - Analyser les messages de commit (mots-clés: fix, bug, defect)
   - Corréler avec les issues Jira marquées comme bugs
   - Créer un label bug-fix pour chaque commit

8. **Implémenter le split temporel (train sur anciens commits, test sur récents)**
   - Diviser les données par timestamp
   - Créer train/val/test sets temporels
   - Valider l'absence de fuite temporelle

9. **Implémenter SMOTE pour sur-échantillonnage**
   - Implémenter SMOTE pour équilibrer les classes
   - Gérer les classes minoritaires (classes avec bugs)
   - Évaluer l'impact sur les performances

10. **Configurer DVC pour versioning des données**
    - Initialiser DVC dans le projet
    - Créer les fichiers .dvc pour chaque dataset
    - Configurer le stockage distant (S3, MinIO)

11. **Définir les feature definitions dans Feast**
    - Créer les feature definitions (métriques de code, churn, etc.)
    - Définir les feature views
    - Configurer les sources de données

12. **Implémenter l'ingestion des features transformées**
    - Créer le pipeline d'ingestion Feast
    - Implémenter l'écriture dans Feast
    - Tester la récupération des features

### Service 5 - Service ML (tâches supplémentaires si nécessaire)

---

## Hossam Chakra - Services 6 & 7 (12 tâches)

### Service 6 - Moteur de Priorisation (6 tâches)

1. **Calculer l'effort estimé par classe (basé sur LOC)**
   - Utiliser Lines of Code comme proxy d'effort
   - Optionnellement intégrer la complexité cyclomatique
   - Créer une formule d'effort

2. **Implémenter la formule effort-aware (score / effort)**
   - Diviser le score de risque par l'effort
   - Créer un score effort-aware
   - Normaliser le score

3. **Créer les métriques effort-aware (Popt@20)**
   - Implémenter le calcul de Popt@20
   - Comparer avec baseline (random, complexité seule)
   - Visualiser les résultats

4. **Définir les niveaux de criticité (critique, important, normal)**
   - Créer une taxonomie de criticité
   - Assigner les niveaux aux modules
   - Créer un mapping module → criticité

5. **Installer et configurer OR-Tools**
   - Installer OR-Tools (Python ou Java)
   - Comprendre les concepts d'optimisation
   - Créer un exemple simple

6. **Définir le problème d'optimisation (maximiser couverture, minimiser effort)**
   - Formuler le problème comme optimisation linéaire/mixte
   - Définir les variables de décision
   - Définir les contraintes (budget, temps)

### Service 6 - Suite (6 tâches)

7. **Implémenter stratégie top-K couvertures manquantes**
   - Identifier les classes sans couverture
   - Trier par score de risque
   - Retourner top-K

8. **Implémenter stratégie maximisation Popt@20**
   - Utiliser OR-Tools pour maximiser Popt@20
   - Résoudre le problème d'optimisation
   - Retourner la solution optimale

9. **Créer l'API REST FastAPI**
   - Créer la structure FastAPI
   - Définir les endpoints
   - Implémenter la validation des données

10. **Implémenter POST /prioritize (retourne plan JSON)**
    - Accepter les paramètres (stratégie, budget, contraintes)
    - Appeler le moteur de priorisation
    - Retourner le plan JSON formaté

11. **Calculer Popt@20 (effort-aware)**
    - Implémenter l'algorithme Popt@20
    - Calculer pour différentes stratégies
    - Comparer les résultats

12. **Comparer avec baseline heuristiques**
    - Implémenter baseline (complexité seule, couverture seule)
    - Comparer les métriques
    - Générer un rapport de comparaison

### Service 7 - Test Scaffolder (tâches supplémentaires si nécessaire)

---

## Ilyas Michich - Service 8 (12 tâches)

### Service 8 - Dashboard Qualité

1. **Créer le projet React.js avec Vite**
   - Initialiser le projet avec Vite
   - Configurer TypeScript (optionnel)
   - Installer les dépendances de base

2. **Configurer le routing (React Router)**
   - Installer React Router
   - Créer les routes principales
   - Implémenter la navigation

3. **Créer la structure des composants**
   - Organiser les composants (atoms, molecules, organisms)
   - Créer les composants de base (Header, Sidebar, Layout)
   - Implémenter le design system

4. **Créer le composant liste des recommandations**
   - Afficher la liste des classes recommandées
   - Implémenter le tri et filtrage
   - Ajouter la pagination

5. **Afficher le score de risque par classe**
   - Créer un composant de visualisation du score
   - Utiliser des barres de progression ou graphiques
   - Colorer selon le niveau de risque

6. **Créer les graphiques de couverture (Plotly)**
   - Intégrer Plotly.js
   - Créer des graphiques de couverture (bar, line)
   - Implémenter l'interactivité

7. **Afficher l'évolution temporelle de couverture**
   - Créer un graphique temporel (line chart)
   - Afficher l'évolution par classe/module
   - Permettre le zoom et le filtrage

8. **Créer les graphiques SHAP (waterfall, bar)**
   - Intégrer les visualisations SHAP
   - Créer waterfall plot pour explication locale
   - Créer bar plot pour importance globale

9. **Afficher l'importance globale des features**
   - Créer un graphique d'importance des features
   - Trier par importance
   - Permettre le drill-down

10. **Créer les graphiques de tendances (Grafana/Plotly)**
    - Créer des graphiques de tendances temporelles
    - Afficher l'évolution des métriques clés
    - Implémenter les alertes visuelles

11. **Implémenter l'export CSV des recommandations**
    - Créer une fonction d'export CSV
    - Formater les données correctement
    - Télécharger le fichier

12. **Créer l'API FastAPI backend**
    - Créer la structure FastAPI
    - Implémenter GET /recommendations
    - Implémenter GET /coverage, GET /risks, GET /trends
    - Documenter avec Swagger

---

## Oussama Boujdig - Services 3 & 9 (12 tâches)

### Service 3 - Historique des Tests (6 tâches)

1. **Implémenter le parser XML JaCoCo**
   - Parser les fichiers XML JaCoCo
   - Extraire line coverage et branch coverage
   - Mapper aux classes Java

2. **Extraire line coverage et branch coverage par classe**
   - Agréger les données par classe
   - Calculer les pourcentages
   - Gérer les classes partiellement couvertes

3. **Implémenter le parser XML Surefire**
   - Parser les fichiers XML Surefire
   - Extraire les résultats de tests
   - Identifier les tests qui échouent

4. **Extraire les tests OK/KO par classe de test**
   - Mapper les classes de test aux classes testées
   - Compter les tests OK/KO
   - Calculer le taux de succès

5. **Implémenter le parser XML PIT (mutation testing)**
   - Parser les fichiers XML PIT
   - Extraire le mutation score
   - Identifier les mutations non tuées

6. **Créer le schéma TimescaleDB pour séries temporelles**
   - Concevoir le schéma pour séries temporelles
   - Créer les hypertables
   - Définir les index

### Service 3 - Suite (3 tâches)

7. **Implémenter le calcul de dette de test par classe**
   - Calculer la dette (objectif - couverture actuelle)
   - Identifier les classes sans tests
   - Créer un score de dette

8. **Créer l'API REST FastAPI**
   - Créer la structure FastAPI
   - Définir les endpoints
   - Implémenter la validation

9. **Implémenter GET /coverage/{class_name}**
   - Récupérer la couverture d'une classe
   - Retourner l'historique si disponible
   - Gérer les erreurs (classe non trouvée)

### Service 9 - Intégrations & Ops (3 tâches)

10. **Configurer GitHub App ou OAuth**
    - Créer une GitHub App
    - Configurer OAuth si nécessaire
    - Obtenir les permissions nécessaires

11. **Implémenter le service GitHub Checks API**
    - Créer des checks sur les PR
    - Afficher les recommandations dans les checks
    - Gérer les statuts (success, failure, neutral)

12. **Configurer GitLab API (token)**
    - Créer un token GitLab
    - Implémenter l'authentification
    - Tester la connexion

---

## 📝 Notes importantes

- **Chaque personne a 10-12 tâches principales** à réaliser
- **Les tâches sont ordonnées par priorité** (les premières sont les plus importantes)
- **Certaines tâches peuvent être faites en parallèle**
- **Il est recommandé de commencer par les tâches d'infrastructure** (authentification, stockage)
- **Les tests doivent être écrits au fur et à mesure** (TDD recommandé)

---

**Total : 60 tâches réparties sur 5 personnes (12 tâches chacune)**

