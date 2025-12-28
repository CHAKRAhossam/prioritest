"""
Modèles de données pour la priorisation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class PrioritizationRequest(BaseModel):
    """
    Requête de priorisation alignée avec les spécifications d'architecture.
    
    Format from architecture spec:
    {
      "repository_id": "repo_12345",
      "branch": "main",
      "sprint_id": "sprint_1",
      "constraints": {
        "budget_hours": 40,
        "target_coverage": 0.85,
        "priority_modules": ["auth", "payment"]
      }
    }
    """
    repository_id: str = Field(..., description="ID du repository", example="repo_12345")
    branch: Optional[str] = Field(None, description="Nom de la branche Git", example="main")
    sprint_id: Optional[str] = Field(None, description="ID du sprint", example="sprint_1")
    constraints: Optional[Dict] = Field(
        None,
        description="Contraintes de priorisation",
        example={
            "budget_hours": 40,
            "target_coverage": 0.85,
            "priority_modules": ["auth", "payment"]
        }
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "repository_id": "repo_12345",
                "branch": "main",
                "sprint_id": "sprint_1",
                "constraints": {
                    "budget_hours": 40,
                    "target_coverage": 0.85
                }
            }
        }


class PrioritizedClass(BaseModel):
    """
    Classe priorisée alignée avec les spécifications d'architecture.
    
    Format from architecture spec:
    {
      "class_name": "com.example.UserService",
      "priority": 1,
      "risk_score": 0.75,
      "effort_hours": 4,
      "effort_aware_score": 0.1875,
      "module_criticality": "high",
      "strategy": "maximize_popt20",
      "reason": "High risk with moderate effort in critical module"
    }
    """
    class_name: str = Field(..., description="Nom de la classe", example="com.example.UserService")
    priority: int = Field(..., description="Priorité (1 = plus haute)", example=1)
    risk_score: float = Field(..., description="Score de risque [0-1]", example=0.75)
    effort_hours: float = Field(..., description="Effort estimé en heures", example=4.0)
    effort_aware_score: float = Field(..., description="Score effort-aware", example=0.1875)
    module_criticality: str = Field(..., description="Criticité du module", example="high")
    strategy: str = Field(..., description="Stratégie utilisée", example="maximize_popt20")
    reason: str = Field(..., description="Raison de la priorisation", example="High risk with moderate effort")


class PrioritizationMetrics(BaseModel):
    """Métriques de priorisation"""
    total_effort_hours: float = Field(..., description="Effort total en heures", example=35.0)
    estimated_coverage_gain: float = Field(..., description="Gain de couverture estimé", example=0.12)
    popt20_score: Optional[float] = Field(None, description="Score Popt@20", example=0.85)
    recall_top20: Optional[float] = Field(None, description="Recall@Top20%", example=0.78)


class PrioritizationResponse(BaseModel):
    """Réponse de priorisation"""
    prioritized_plan: List[PrioritizedClass] = Field(..., description="Plan priorisé")
    metrics: PrioritizationMetrics = Field(..., description="Métriques de performance")


    metrics: PrioritizationMetrics = Field(..., description="Métriques de performance")

