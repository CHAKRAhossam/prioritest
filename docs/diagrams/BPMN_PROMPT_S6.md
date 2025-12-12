# Prompt pour créer le diagramme BPMN - Service 6 (Moteur de Priorisation)

## Contexte du Service

Le Service 6 transforme les scores ML en liste ordonnée en intégrant :
- Effort (LOC, complexité)
- Criticité module
- Dépendances
- Objectifs de sprint

## Workflow Principal : Endpoint POST /prioritize

### Étapes du Processus

1. **Start Event** : Réception d'une requête HTTP POST `/prioritize`
   - Input : `PrioritizationRequest` (repository_id, sprint_id, constraints)
   - Query param : `strategy` (maximize_popt20, top_k_coverage, budget_optimization, coverage_optimization, multi_objective)

2. **Validate Request** (Task - Validation)
   - Vérifier que repository_id est fourni
   - Valider le format de la requête (Pydantic)
   - Si invalide → **Error End Event** (400 Bad Request)

3. **Get ML Predictions** (Task - External Service Call)
   - Appeler `MLServiceClient.get_predictions(repository_id, sprint_id)`
   - Service externe : S5 (ML Service)
   - URL : `{ML_SERVICE_URL}/api/v1/predictions`
   - Timeout : 30 secondes

4. **Gateway : Predictions Found?** (Exclusive Gateway)
   - **Non** → **Error End Event** (404 Not Found) : "Aucune prédiction trouvée"
   - **Oui** → Continuer

5. **Calculate Effort** (Task - Business Logic)
   - Service : `EffortCalculator.calculate_for_classes(predictions)`
   - Pour chaque classe :
     - Calculer `effort_hours` = (LOC / loc_per_hour) * complexity_multiplier
     - Calculer `effort_aware_score` = risk_score / effort_hours
   - Output : Liste enrichie avec `effort_hours` et `effort_aware_score`

6. **Apply Criticality** (Task - Business Logic)
   - Service : `CriticalityService.enrich_with_criticality(classes_with_effort)`
   - Pour chaque classe :
     - Détecter `module_criticality` (high/medium/low) depuis le nom de classe
     - Appliquer poids : high=1.5, medium=1.2, low=1.0
     - Ajuster `effort_aware_score` = effort_aware_score * weight
   - Output : Liste enrichie avec `module_criticality` et `effort_aware_score` ajusté

7. **Prepare Strategy Parameters** (Task - Business Logic)
   - Extraire `constraints` de la requête
   - Selon la stratégie :
     - `top_k_coverage` → `k` = constraints.get('k', 20)
     - `budget_optimization` → `budget_hours` = constraints.get('budget_hours', 40.0)
     - `coverage_optimization` → `target_coverage` = constraints.get('target_coverage', 0.8)
     - `multi_objective` → `budget_hours`, `target_coverage`, `max_classes`

8. **Apply Prioritization Strategy** (Task - Business Logic)
   - Service : `PrioritizationStrategies.apply_strategy(strategy, classes, **kwargs)`
   - Stratégies possibles :
     - **maximize_popt20** : Trier par `effort_aware_score` décroissant
     - **top_k_coverage** : Sélectionner les K meilleures classes
     - **budget_optimization** : Utiliser `OptimizationService.optimize_with_budget_constraint()` (OR-Tools)
     - **coverage_optimization** : Utiliser `OptimizationService.optimize_with_coverage_constraint()` (OR-Tools)
     - **multi_objective** : Utiliser `OptimizationService.optimize_multi_constraint()` (OR-Tools)
   - Output : Liste de classes priorisées (sous-ensemble ou tri complet)

9. **Create Prioritized Plan** (Task - Data Transformation)
   - Pour chaque classe (avec index) :
     - Créer `PrioritizedClass` :
       - `priority` = index (1, 2, 3, ...)
       - `class_name`, `risk_score`, `effort_hours`, `effort_aware_score`
       - `module_criticality`, `strategy`, `reason` (généré)
   - Output : Liste de `PrioritizedClass`

10. **Calculate Metrics** (Task - Business Logic)
    - Service : `MetricsService`
    - Calculer :
      - `total_effort` = somme des effort_hours
      - `total_risk` = somme des risk_score (plan priorisé)
      - `total_risk_all` = somme des risk_score (toutes les classes)
      - `estimated_coverage_gain` = total_risk / total_risk_all
      - `popt20_score` = `MetricsService.calculate_popt20(classes)`
      - `recall_top20` = `MetricsService.calculate_recall_top20(classes)`
    - Créer `PrioritizationMetrics`

11. **Build Response** (Task - Data Transformation)
    - Créer `PrioritizationResponse` :
      - `prioritized_plan` : Liste de `PrioritizedClass`
      - `metrics` : `PrioritizationMetrics`

12. **Return Response** (Task - API Response)
    - Retourner HTTP 200 OK avec `PrioritizationResponse` (JSON)

13. **End Event** : Succès

### Gestion des Erreurs

- **Error 400** : Requête invalide (validation Pydantic échoue)
- **Error 404** : Aucune prédiction trouvée pour le repository
- **Error 500** : Erreur lors de la priorisation (exception non gérée)

## Workflow Secondaire : Endpoint GET /prioritize/{repository_id}

1. **Start Event** : Réception d'une requête HTTP GET `/prioritize/{repository_id}`
2. **Create Request** : Créer `PrioritizationRequest` depuis les paramètres
3. **Call Prioritize** : Appeler le workflow principal `prioritize()`
4. **Return Response** : Retourner le résultat
5. **End Event** : Succès

## Swimlanes (Couches)

1. **API Controller** : Gestion des requêtes HTTP (FastAPI Router)
2. **Business Logic** : Services métier (EffortCalculator, CriticalityService, PrioritizationStrategies, MetricsService)
3. **External Services** : Appels externes (ML Service S5)
4. **Data & Storage** : Transformation de données et stockage (optionnel, via PolicyService)

## Détails Techniques

### Services Utilisés

- **EffortCalculator** : Calcul effort et score effort-aware
- **CriticalityService** : Détection et application de criticité
- **OptimizationService** : Optimisation avec OR-Tools (SCIP solver)
- **PrioritizationStrategies** : Application des stratégies
- **MLServiceClient** : Client HTTP pour S5
- **MetricsService** : Calcul des métriques (Popt@20, Recall@Top20, Coverage Gain)
- **PolicyService** : Stockage des politiques et plans (optionnel, non utilisé dans le workflow principal actuel)

### Stratégies de Priorisation

1. **maximize_popt20** : Simple tri par score décroissant
2. **top_k_coverage** : Sélection des K meilleures classes
3. **budget_optimization** : Optimisation ILP avec contrainte budget (OR-Tools)
4. **coverage_optimization** : Optimisation ILP avec contrainte couverture (OR-Tools)
5. **multi_objective** : Optimisation ILP multi-contraintes (OR-Tools)

### Fallback

- Si OR-Tools (SCIP) n'est pas disponible → Algorithme glouton
- Si ML Service S5 n'est pas disponible → Données mockées (développement)

## Instructions pour le Diagramme BPMN

1. **Utiliser des swimlanes** pour séparer les couches (API, Logic, External, Data)
2. **Marquer les appels externes** avec des tâches de type "Service Task" (appel S5)
3. **Utiliser des gateways exclusifs** pour les décisions (Predictions Found?, Strategy Selection)
4. **Inclure les erreurs** avec des événements d'erreur et des flux de sortie
5. **Montrer les données** : Input/Output de chaque tâche principale
6. **Utiliser des annotations** pour les détails techniques (OR-Tools, formules)
7. **Style** : Général, lisible, sans couleurs (noir et blanc), espacement généreux
8. **Titre** : "Workflow de Priorisation - Service 6"

## Format de Sortie

Créer un fichier SVG avec le diagramme BPMN complet, similaire au style du diagramme S7 (général, épuré, bien espacé).




