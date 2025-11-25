# Guide Complet - Organisation des Sprints

## ✅ État Actuel

- ✅ Board Scrum créé (ID: 134)
- ✅ Sprint 1 créé : "MTP Sprint 1" avec 6 user stories
- ⏳ 61 user stories dans le backlog à organiser
- ⏳ 6 sprints supplémentaires à créer

## 📋 Structure des 7 Sprints

### ✅ Sprint 1 - Infrastructure & Collecte (DÉJÀ CRÉÉ)
**6 user stories :**
- MTP-2 : US-S1-01: Intégration Git/GitHub
- MTP-3 : US-S1-02: Intégration GitLab
- MTP-4 : US-S1-03: Intégration Jira
- MTP-6 : US-S1-05: Pipeline Kafka et stockage
- MTP-8 : US-S2-01: Extraction métriques Java
- MTP-9 : US-S2-02: Extraction métriques Python

### Sprint 2 - Analyse & Historique (À CRÉER)
**9 user stories :**
- MTP-10 : US-S2-03: Analyse des dépendances
- MTP-11 : US-S2-04: Feature Store avec Feast
- MTP-12 : US-S2-05: Support multi-projets
- MTP-14 : US-S3-01: Parser rapports JaCoCo
- MTP-15 : US-S3-02: Parser rapports Surefire
- MTP-16 : US-S3-03: Parser rapports PIT
- MTP-17 : US-S3-04: Stockage historique TimescaleDB
- MTP-19 : US-S3-06: API REST pour métriques tests
- MTP-5 : US-S1-04: Collecte des rapports CI/CD

### Sprint 3 - Prétraitement & ML (À CRÉER)
**11 user stories :**
- MTP-21 : US-S4-01: Pipeline de nettoyage
- MTP-22 : US-S4-02: Features dérivées - Churn
- MTP-23 : US-S4-03: Features dérivées - Auteurs
- MTP-24 : US-S4-04: Features dérivées - Bug-fix proximity
- MTP-25 : US-S4-05: Split temporel train/val/test
- MTP-26 : US-S4-06: Balancement de classes
- MTP-27 : US-S4-07: Data lineage avec DVC
- MTP-28 : US-S4-08: Feature Store Feast
- MTP-30 : US-S5-01: Modèles de classification
- MTP-31 : US-S5-02: Validation temporelle
- MTP-32 : US-S5-03: Calibration des probabilités

### Sprint 4 - ML Avancé & Priorisation (À CRÉER)
**11 user stories :**
- MTP-33 : US-S5-04: Détection d'anomalies
- MTP-34 : US-S5-05: Explicabilité avec SHAP
- MTP-35 : US-S5-06: MLflow - Experiments
- MTP-36 : US-S5-07: MLflow - Model Registry
- MTP-37 : US-S5-08: Service de prédiction
- MTP-38 : US-S5-09: Stockage modèles
- MTP-40 : US-S6-01: Calcul effort-aware
- MTP-41 : US-S6-02: Intégration criticité module
- MTP-42 : US-S6-03: Optimisation avec OR-Tools
- MTP-43 : US-S6-04: Stratégies de priorisation
- MTP-44 : US-S6-05: API de priorisation

### Sprint 5 - Priorisation & Test Scaffolder (À CRÉER)
**10 user stories :**
- MTP-45 : US-S6-06: Stockage politiques
- MTP-46 : US-S6-07: Métriques de performance
- MTP-48 : US-S7-01: Analyse AST pour génération
- MTP-49 : US-S7-02: Génération templates JUnit
- MTP-50 : US-S7-03: Suggestions cas de test
- MTP-51 : US-S7-04: Génération mocks
- MTP-52 : US-S7-05: Checklist mutation testing
- MTP-53 : US-S7-06: Stockage suggestions
- MTP-54 : US-S7-07: API de génération
- MTP-18 : US-S3-05: Calcul dette de test

### Sprint 6 - Dashboard & Intégrations (À CRÉER)
**10 user stories :**
- MTP-56 : US-S8-01: Interface React.js
- MTP-57 : US-S8-02: Vue recommandations
- MTP-58 : US-S8-03: Visualisation couverture
- MTP-59 : US-S8-04: Visualisation risques
- MTP-60 : US-S8-05: Vue tendances
- MTP-61 : US-S8-06: Vue impact
- MTP-62 : US-S8-07: Vue par repo/module/classe
- MTP-63 : US-S8-08: Exports PDF/CSV
- MTP-64 : US-S8-09: WebSockets temps réel
- MTP-65 : US-S8-10: API Backend FastAPI

### Sprint 7 - Intégrations & Finalisation (À CRÉER)
**10 user stories :**
- MTP-67 : US-S9-01: GitHub Checks Integration
- MTP-68 : US-S9-02: GitLab MR Integration
- MTP-69 : US-S9-03: Commentaires automatiques PR
- MTP-70 : US-S9-04: Policy gate optionnelle
- MTP-71 : US-S9-05: Triggers d'entraînement
- MTP-72 : US-S9-06: Docker & Kubernetes
- MTP-73 : US-S9-07: Observabilité OpenTelemetry
- MTP-74 : US-S9-08: Authentification SSO Keycloak
- MTP-75 : US-S9-09: CI/CD Pipeline
- MTP-76 : US-S9-10: Documentation & Guide

---

## 🚀 Instructions Étape par Étape

### Étape 1 : Créer les 6 sprints restants

Dans votre backlog Jira (https://prioritest.atlassian.net/jira/software/projects/MTP/boards/134) :

1. **Cliquez sur "Create sprint"** (bouton visible dans le backlog)
2. **Créez les 6 sprints suivants** (un par un) avec ces noms **EXACTS** :

   ```
   Sprint 2 - Analyse & Historique
   Sprint 3 - Prétraitement & ML
   Sprint 4 - ML Avancé & Priorisation
   Sprint 5 - Priorisation & Test Scaffolder
   Sprint 6 - Dashboard & Intégrations
   Sprint 7 - Intégrations & Finalisation
   ```

### Étape 2 : Organiser automatiquement les user stories

Une fois les 6 sprints créés, exécutez :

```bash
python organize_sprints.py
```

Le script va automatiquement :
- Détecter tous les sprints créés
- Organiser les 61 user stories restantes dans les bons sprints

### Étape 3 : Vérifier l'organisation

Vérifiez dans Jira que :
- Chaque sprint contient le bon nombre de user stories
- Toutes les user stories sont bien assignées

---

## 📊 Résumé Final

- **7 sprints** au total
- **67 user stories** réparties
- **Durée :** 14 semaines (3.5 mois)
- **Sprint 1 :** Déjà organisé ✅
- **Sprints 2-7 :** À créer et organiser

---

## ⚡ Alternative Rapide

Si vous préférez organiser manuellement :

1. Dans le backlog, faites glisser chaque user story dans le sprint correspondant
2. Utilisez la liste ci-dessus pour savoir quelle user story va dans quel sprint

