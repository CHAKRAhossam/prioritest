"""
API endpoints pour la priorisation
"""
from fastapi import APIRouter, HTTPException, Query
from src.models.prioritization import (
    PrioritizationRequest,
    PrioritizationResponse,
    PrioritizedClass,
    PrioritizationMetrics
)
from src.services.effort_calculator import EffortCalculator
from src.services.criticality_service import CriticalityService
from src.services.prioritization_strategies import PrioritizationStrategies
from src.services.ml_service_client import MLServiceClient
from src.services.metrics_service import MetricsService
from typing import Optional, List

router = APIRouter()

# Services (singletons)
effort_calculator = EffortCalculator()
criticality_service = CriticalityService()
strategies = PrioritizationStrategies()
ml_client = MLServiceClient()
metrics_service = MetricsService()

@router.post(
    "/prioritize",
    response_model=PrioritizationResponse,
    summary="Prioriser les classes à tester",
    description="""
    Transforme les scores ML en liste priorisée en intégrant :
    - Effort (LOC, complexité)
    - Criticité module
    - Dépendances
    - Objectifs de sprint
    
    **Processus de priorisation :**
    1. Récupère les prédictions ML depuis S5
    2. Calcule l'effort et les scores effort-aware
    3. Applique la criticité des modules
    4. Applique la stratégie de priorisation sélectionnée
    5. Retourne le plan priorisé avec métriques
    """,
    response_description="Plan de tests priorisé avec métriques"
)
async def prioritize(
    request: PrioritizationRequest,
    strategy: str = Query(
        default="maximize_popt20",
        description="Stratégie de priorisation",
        enum=[
            "maximize_popt20",
            "top_k_coverage",
            "budget_optimization",
            "coverage_optimization",
            "multi_objective"
        ]
    )
):
    """
    Prioriser les classes à tester.
    
    Args:
        request: Requête de priorisation
        strategy: Stratégie à utiliser
    
    Returns:
        Plan priorisé avec métriques
    
    Raises:
        HTTPException: Si la priorisation échoue
    """
    try:
        # Étape 1: Récupérer les prédictions depuis S5 (MLService)
        predictions = await ml_client.get_predictions(
            repository_id=request.repository_id,
            sprint_id=request.sprint_id
        )
        
        if not predictions:
            raise HTTPException(
                status_code=404,
                detail=f"Aucune prédiction trouvée pour le repository {request.repository_id}"
            )
        
        # Étape 2: Calculer l'effort et les scores effort-aware
        classes_with_effort = effort_calculator.calculate_for_classes(predictions)
        
        # Étape 3: Appliquer la criticité des modules
        classes_with_criticality = criticality_service.enrich_with_criticality(
            classes_with_effort
        )
        
        # Étape 4: Appliquer la stratégie de priorisation
        constraints = request.constraints or {}
        
        # Préparer les paramètres selon la stratégie
        strategy_kwargs = {}
        if strategy == "top_k_coverage":
            strategy_kwargs['k'] = constraints.get('k', 20)
        elif strategy == "budget_optimization":
            strategy_kwargs['budget_hours'] = constraints.get('budget_hours', 40.0)
        elif strategy == "coverage_optimization":
            strategy_kwargs['target_coverage'] = constraints.get('target_coverage', 0.8)
        elif strategy == "multi_objective":
            strategy_kwargs['budget_hours'] = constraints.get('budget_hours')
            strategy_kwargs['target_coverage'] = constraints.get('target_coverage')
            strategy_kwargs['max_classes'] = constraints.get('max_classes')
        
        prioritized_classes = strategies.apply_strategy(
            strategy,
            classes_with_criticality,
            **strategy_kwargs
        )
        
        # Étape 5: Créer la réponse avec priorités
        prioritized_plan = []
        for idx, cls in enumerate(prioritized_classes, start=1):
            prioritized_plan.append(
                PrioritizedClass(
                    class_name=cls['class_name'],
                    priority=idx,
                    risk_score=cls['risk_score'],
                    effort_hours=cls['effort_hours'],
                    effort_aware_score=cls['effort_aware_score'],
                    module_criticality=cls['module_criticality'],
                    strategy=strategy,
                    reason=_generate_reason(cls, strategy)
                )
            )
        
        # Étape 6: Calculer les métriques
        total_effort = sum(c.effort_hours for c in prioritized_plan)
        total_risk = sum(c.risk_score for c in prioritized_plan)
        total_risk_all = sum(cls.get('risk_score', 0.0) for cls in classes_with_criticality)
        
        estimated_coverage_gain = total_risk / total_risk_all if total_risk_all > 0 else 0.0
        
        # Calculer les métriques de performance
        # Convertir PrioritizedClass en dict pour le service de métriques
        classes_for_metrics = [
            {
                'class_name': c.class_name,
                'risk_score': c.risk_score,
                'effort_hours': c.effort_hours,
                'effort_aware_score': c.effort_aware_score
            }
            for c in prioritized_plan
        ]
        
        # Calculer Popt@20 et Recall@Top20
        popt20_score = metrics_service.calculate_popt20(classes_for_metrics)
        recall_top20 = metrics_service.calculate_recall_top20(classes_for_metrics)
        
        metrics = PrioritizationMetrics(
            total_effort_hours=total_effort,
            estimated_coverage_gain=round(estimated_coverage_gain, 4),
            popt20_score=popt20_score,
            recall_top20=recall_top20
        )
        
        return PrioritizationResponse(
            prioritized_plan=prioritized_plan,
            metrics=metrics
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la priorisation: {str(e)}"
        )


def _generate_reason(cls: dict, strategy: str) -> str:
    """
    Génère une raison pour la priorisation d'une classe.
    
    Args:
        cls: Classe avec ses métriques
        strategy: Stratégie utilisée
    
    Returns:
        Raison de la priorisation
    """
    criticality = cls.get('module_criticality', 'low')
    risk_score = cls.get('risk_score', 0.0)
    effort_aware_score = cls.get('effort_aware_score', 0.0)
    
    reasons = []
    
    if criticality == 'high':
        reasons.append("High criticality module")
    elif criticality == 'medium':
        reasons.append("Medium criticality module")
    
    if risk_score > 0.7:
        reasons.append("High risk score")
    elif risk_score > 0.5:
        reasons.append("Moderate risk score")
    
    if effort_aware_score > 0.3:
        reasons.append("Excellent effort/risk ratio")
    elif effort_aware_score > 0.15:
        reasons.append("Good effort/risk ratio")
    
    if not reasons:
        reasons.append("Selected by strategy")
    
    return f"{', '.join(reasons)} ({strategy})"

@router.get(
    "/prioritize/{repository_id}",
    response_model=PrioritizationResponse,
    summary="Récupérer le plan priorisé existant",
    description="Récupère un plan de priorisation existant pour un repository"
)
async def get_prioritization(
    repository_id: str,
    sprint_id: Optional[str] = Query(None, description="ID du sprint"),
    strategy: str = Query(
        default="maximize_popt20",
        description="Stratégie de priorisation",
        enum=[
            "maximize_popt20",
            "top_k_coverage",
            "budget_optimization",
            "coverage_optimization",
            "multi_objective"
        ]
    )
):
    """
    Récupérer un plan de priorisation existant.
    
    Note: Pour l'instant, génère un nouveau plan. Dans le futur,
    pourra récupérer un plan stocké en base de données.
    
    Args:
        repository_id: ID du repository
        sprint_id: ID du sprint (optionnel)
        strategy: Stratégie de priorisation
    
    Returns:
        Plan priorisé
    """
    # Pour l'instant, génère un nouveau plan
    # TODO: Implémenter le stockage/récupération depuis la base de données
    request = PrioritizationRequest(
        repository_id=repository_id,
        sprint_id=sprint_id
    )
    
    return await prioritize(request, strategy=strategy)


