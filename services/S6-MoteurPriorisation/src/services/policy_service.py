"""
Service de gestion des politiques de priorisation

US-S6-06: Stockage politiques
- CRUD pour les politiques
- Stockage et récupération des plans de priorisation
"""

from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.database.models import Policy, PrioritizationPlan
from src.database.connection import get_db
from datetime import datetime
import json


class PolicyService:
    """
    Service pour gérer les politiques et plans de priorisation.
    """
    
    def __init__(self, db: Session):
        """
        Initialise le service avec une session de base de données.
        
        Args:
            db: Session SQLAlchemy
        """
        self.db = db
    
    # ========== CRUD Policies ==========
    
    def create_policy(
        self,
        name: str,
        strategy: str,
        description: Optional[str] = None,
        constraints: Optional[Dict] = None,
        effort_config: Optional[Dict] = None,
        criticality_config: Optional[Dict] = None,
        created_by: Optional[str] = None
    ) -> Policy:
        """
        Crée une nouvelle politique.
        
        Args:
            name: Nom de la politique
            strategy: Stratégie de priorisation
            description: Description (optionnel)
            constraints: Contraintes (optionnel)
            effort_config: Configuration effort (optionnel)
            criticality_config: Configuration criticité (optionnel)
            created_by: Créateur (optionnel)
        
        Returns:
            Politique créée
        
        Raises:
            ValueError: Si le nom existe déjà
        """
        # Vérifier si le nom existe déjà
        existing = self.db.query(Policy).filter(Policy.name == name).first()
        if existing:
            raise ValueError(f"Une politique avec le nom '{name}' existe déjà")
        
        policy = Policy(
            name=name,
            description=description,
            strategy=strategy,
            constraints=constraints or {},
            effort_config=effort_config or {},
            criticality_config=criticality_config or {},
            created_by=created_by,
            is_active=1
        )
        
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)
        
        return policy
    
    def get_policy(self, policy_id: str) -> Optional[Policy]:
        """
        Récupère une politique par ID.
        
        Args:
            policy_id: ID de la politique
        
        Returns:
            Politique ou None
        """
        return self.db.query(Policy).filter(Policy.id == policy_id).first()
    
    def get_policy_by_name(self, name: str) -> Optional[Policy]:
        """
        Récupère une politique par nom.
        
        Args:
            name: Nom de la politique
        
        Returns:
            Politique ou None
        """
        return self.db.query(Policy).filter(Policy.name == name).first()
    
    def list_policies(
        self,
        active_only: bool = True,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Policy]:
        """
        Liste les politiques.
        
        Args:
            active_only: Si True, retourne seulement les politiques actives
            limit: Nombre maximum de résultats
            offset: Offset pour pagination
        
        Returns:
            Liste de politiques
        """
        query = self.db.query(Policy)
        
        if active_only:
            query = query.filter(Policy.is_active == 1)
        
        query = query.order_by(Policy.created_at.desc())
        
        if offset:
            query = query.offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def update_policy(
        self,
        policy_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        strategy: Optional[str] = None,
        constraints: Optional[Dict] = None,
        effort_config: Optional[Dict] = None,
        criticality_config: Optional[Dict] = None,
        is_active: Optional[int] = None
    ) -> Optional[Policy]:
        """
        Met à jour une politique.
        
        Args:
            policy_id: ID de la politique
            name: Nouveau nom (optionnel)
            description: Nouvelle description (optionnel)
            strategy: Nouvelle stratégie (optionnel)
            constraints: Nouvelles contraintes (optionnel)
            effort_config: Nouvelle config effort (optionnel)
            criticality_config: Nouvelle config criticité (optionnel)
            is_active: Nouveau statut actif (optionnel)
        
        Returns:
            Politique mise à jour ou None si non trouvée
        """
        policy = self.get_policy(policy_id)
        if not policy:
            return None
        
        if name is not None:
            # Vérifier si le nouveau nom existe déjà (sauf pour cette politique)
            existing = self.db.query(Policy).filter(
                and_(Policy.name == name, Policy.id != policy_id)
            ).first()
            if existing:
                raise ValueError(f"Une politique avec le nom '{name}' existe déjà")
            policy.name = name
        
        if description is not None:
            policy.description = description
        if strategy is not None:
            policy.strategy = strategy
        if constraints is not None:
            policy.constraints = constraints
        if effort_config is not None:
            policy.effort_config = effort_config
        if criticality_config is not None:
            policy.criticality_config = criticality_config
        if is_active is not None:
            policy.is_active = is_active
        
        policy.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(policy)
        
        return policy
    
    def delete_policy(self, policy_id: str) -> bool:
        """
        Supprime une politique (soft delete).
        
        Args:
            policy_id: ID de la politique
        
        Returns:
            True si supprimée, False si non trouvée
        """
        policy = self.get_policy(policy_id)
        if not policy:
            return False
        
        # Soft delete
        policy.is_active = 0
        policy.updated_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    # ========== CRUD Prioritization Plans ==========
    
    def save_plan(
        self,
        repository_id: str,
        strategy: str,
        prioritized_classes: List[Dict],
        metrics: Dict,
        sprint_id: Optional[str] = None,
        policy_id: Optional[str] = None
    ) -> PrioritizationPlan:
        """
        Sauvegarde un plan de priorisation.
        
        Args:
            repository_id: ID du repository
            strategy: Stratégie utilisée
            prioritized_classes: Liste de classes priorisées
            metrics: Métriques du plan
            sprint_id: ID du sprint (optionnel)
            policy_id: ID de la politique utilisée (optionnel)
        
        Returns:
            Plan sauvegardé
        """
        plan = PrioritizationPlan(
            repository_id=repository_id,
            sprint_id=sprint_id,
            policy_id=policy_id,
            strategy=strategy,
            prioritized_classes=prioritized_classes,
            total_effort_hours=metrics.get('total_effort_hours', 0.0),
            estimated_coverage_gain=metrics.get('estimated_coverage_gain'),
            popt20_score=metrics.get('popt20_score'),
            recall_top20=metrics.get('recall_top20')
        )
        
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        
        return plan
    
    def get_plan(self, plan_id: str) -> Optional[PrioritizationPlan]:
        """
        Récupère un plan par ID.
        
        Args:
            plan_id: ID du plan
        
        Returns:
            Plan ou None
        """
        return self.db.query(PrioritizationPlan).filter(
            PrioritizationPlan.id == plan_id
        ).first()
    
    def get_latest_plan(
        self,
        repository_id: str,
        sprint_id: Optional[str] = None
    ) -> Optional[PrioritizationPlan]:
        """
        Récupère le plan le plus récent pour un repository/sprint.
        
        Args:
            repository_id: ID du repository
            sprint_id: ID du sprint (optionnel)
        
        Returns:
            Plan le plus récent ou None
        """
        query = self.db.query(PrioritizationPlan).filter(
            PrioritizationPlan.repository_id == repository_id
        )
        
        if sprint_id:
            query = query.filter(PrioritizationPlan.sprint_id == sprint_id)
        
        return query.order_by(PrioritizationPlan.created_at.desc()).first()
    
    def list_plans(
        self,
        repository_id: Optional[str] = None,
        sprint_id: Optional[str] = None,
        strategy: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[PrioritizationPlan]:
        """
        Liste les plans de priorisation.
        
        Args:
            repository_id: Filtrer par repository (optionnel)
            sprint_id: Filtrer par sprint (optionnel)
            strategy: Filtrer par stratégie (optionnel)
            limit: Nombre maximum de résultats
            offset: Offset pour pagination
        
        Returns:
            Liste de plans
        """
        query = self.db.query(PrioritizationPlan)
        
        if repository_id:
            query = query.filter(PrioritizationPlan.repository_id == repository_id)
        if sprint_id:
            query = query.filter(PrioritizationPlan.sprint_id == sprint_id)
        if strategy:
            query = query.filter(PrioritizationPlan.strategy == strategy)
        
        query = query.order_by(PrioritizationPlan.created_at.desc())
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def delete_plan(self, plan_id: str) -> bool:
        """
        Supprime un plan.
        
        Args:
            plan_id: ID du plan
        
        Returns:
            True si supprimé, False si non trouvé
        """
        plan = self.get_plan(plan_id)
        if not plan:
            return False
        
        self.db.delete(plan)
        self.db.commit()
        return True

