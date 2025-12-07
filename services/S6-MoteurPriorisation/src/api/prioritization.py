"""
API endpoints pour la priorisation
"""
from fastapi import APIRouter, HTTPException, Query
from src.models.prioritization import (
    PrioritizationRequest,
    PrioritizationResponse
)
from typing import Optional

router = APIRouter()

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
    """,
    response_description="Plan de tests priorisé avec métriques"
)
async def prioritize(
    request: PrioritizationRequest,
    strategy: str = Query(
        default="maximize_popt20",
        description="Stratégie de priorisation",
        enum=["maximize_popt20", "top_k_coverage", "budget_optimization"]
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
    # TODO: Implémenter la logique
    raise HTTPException(
        status_code=501,
        detail="Not implemented yet - Structure de base créée"
    )

@router.get(
    "/prioritize/{repository_id}",
    response_model=PrioritizationResponse,
    summary="Récupérer le plan priorisé existant",
    description="Récupère un plan de priorisation existant pour un repository"
)
async def get_prioritization(
    repository_id: str,
    sprint_id: Optional[str] = Query(None, description="ID du sprint")
):
    """
    Récupérer un plan de priorisation existant.
    
    Args:
        repository_id: ID du repository
        sprint_id: ID du sprint (optionnel)
    
    Returns:
        Plan priorisé existant
    """
    # TODO: Implémenter
    raise HTTPException(status_code=501, detail="Not implemented yet")

