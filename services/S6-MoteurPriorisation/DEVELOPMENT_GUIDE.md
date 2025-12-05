# Guide de Développement - Service 6

## ✅ MTP-79: Structure de base (TERMINÉ)

La structure de base est créée et poussée sur la branche `feature/MTP-79-structure-base-s6`.

## 📋 Prochaines Étapes - Workflow Git

### 1. MTP-40: US-S6-01 - Calcul effort-aware

```bash
# Revenir sur main et mettre à jour
git checkout main
git pull origin main

# Créer la branche feature
git checkout -b feature/MTP-40-effort-aware

# Développer...
# - Créer src/services/effort_calculator.py
# - Implémenter estimate_effort_hours()
# - Implémenter calculate_effort_aware_score()
# - Ajouter tests unitaires

# Commiter et pousser
git add .
git commit -m "MTP-40: Implémenter calcul effort-aware

- Création EffortCalculator
- Calcul effort basé sur LOC et complexité
- Calcul score effort-aware (risk_score / effort_hours)
- Tests unitaires"

git push origin feature/MTP-40-effort-aware
```

### 2. MTP-41: US-S6-02 - Intégration criticité module

```bash
git checkout main
git pull origin main
git checkout -b feature/MTP-41-criticality-module

# Développer...
# - Créer src/services/criticality_service.py
# - Implémenter get_module_criticality()
# - Implémenter apply_criticality_weight()
# - Ajouter tests

git add .
git commit -m "MTP-41: Intégrer criticité module

- Création CriticalityService
- Détection criticité depuis nom de classe
- Application poids selon criticité
- Tests unitaires"

git push origin feature/MTP-41-criticality-module
```

### 3. MTP-42: US-S6-03 - Optimisation avec OR-Tools

```bash
git checkout main
git pull origin main
git checkout -b feature/MTP-42-ortools-optimization

# Développer...
# - Créer src/services/optimization_service.py
# - Implémenter optimisation sous contraintes
# - Intégrer OR-Tools
# - Ajouter tests

git add .
git commit -m "MTP-42: Optimisation avec OR-Tools

- Création OptimizationService
- Intégration OR-Tools pour contraintes
- Optimisation budget/coverage
- Tests unitaires"

git push origin feature/MTP-42-ortools-optimization
```

### 4. MTP-43: US-S6-04 - Stratégies de priorisation

```bash
git checkout main
git pull origin main
git checkout -b feature/MTP-43-prioritization-strategies

# Développer...
# - Créer src/services/prioritization_strategies.py
# - Implémenter top_k_coverage()
# - Implémenter maximize_popt20()
# - Implémenter budget_optimization()
# - Ajouter tests

git add .
git commit -m "MTP-43: Implémenter stratégies de priorisation

- Création PrioritizationStrategies
- Top-K coverage
- Maximisation Popt@20
- Budget optimization
- Tests unitaires"

git push origin feature/MTP-43-prioritization-strategies
```

### 5. MTP-44: US-S6-05 - API de priorisation

```bash
git checkout main
git pull origin main
git checkout -b feature/MTP-44-prioritization-api

# Développer...
# - Compléter src/api/prioritization.py
# - Intégrer tous les services
# - Appeler S5 (MLService) pour récupérer prédictions
# - Ajouter tests d'intégration

git add .
git commit -m "MTP-44: Compléter API de priorisation

- Intégration EffortCalculator
- Intégration CriticalityService
- Intégration PrioritizationStrategies
- Appel S5 pour prédictions ML
- Tests d'intégration"

git push origin feature/MTP-44-prioritization-api
```

### 6. MTP-45: US-S6-06 - Stockage politiques

```bash
git checkout main
git pull origin main
git checkout -b feature/MTP-45-policy-storage

# Développer...
# - Créer src/services/policy_service.py
# - Créer modèles SQLAlchemy
# - Implémenter CRUD pour politiques
# - Ajouter migrations (Alembic)
# - Ajouter tests

git add .
git commit -m "MTP-45: Stockage politiques

- Création PolicyService
- Modèles SQLAlchemy pour politiques
- CRUD complet
- Migrations Alembic
- Tests unitaires et intégration"

git push origin feature/MTP-45-policy-storage
```

### 7. MTP-46: US-S6-07 - Métriques de performance

```bash
git checkout main
git pull origin main
git checkout -b feature/MTP-46-performance-metrics

# Développer...
# - Créer src/services/metrics_service.py
# - Implémenter calcul Popt@20
# - Implémenter calcul Recall@Top20
# - Implémenter calcul coverage gain
# - Ajouter tests

git add .
git commit -m "MTP-46: Métriques de performance

- Création MetricsService
- Calcul Popt@20
- Calcul Recall@Top20
- Calcul coverage gain
- Tests unitaires"

git push origin feature/MTP-46-performance-metrics
```

## 🔄 Workflow de Merge Request

Pour chaque branche feature :

1. **Créer la Merge Request sur GitLab** :
   - Aller sur https://gitlab.com/chakrahossam-group/prioritest/-/merge_requests/new
   - Source: `feature/MTP-XX-...`
   - Target: `main`
   - Titre: `MTP-XX: Description`
   - Description: Détails de l'implémentation
   - Assigner reviewers si nécessaire

2. **Après review et merge** :
   ```bash
   git checkout main
   git pull origin main
   # Supprimer la branche locale
   git branch -d feature/MTP-XX-...
   ```

## 🧪 Tests

Pour chaque feature, ajouter :
- **Tests unitaires** dans `tests/unit/`
- **Tests d'intégration** dans `tests/integration/` (si applicable)

Lancer les tests :
```bash
pytest tests/ -v
```

## 📝 Documentation

Mettre à jour le README.md si nécessaire pour chaque feature.

## 🚀 Démarrage Rapide

```bash
# Installer les dépendances
cd services/S6-MoteurPriorisation
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copier .env
cp .env.example .env
# Éditer .env

# Lancer le service
python src/main.py
# Ou
uvicorn src.main:app --reload --port 8006

# Accéder à Swagger
# http://localhost:8006/docs
```

