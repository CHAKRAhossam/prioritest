"""
Modèles de base de données pour le stockage des politiques et plans
"""
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class Policy(Base):
    """
    Modèle pour stocker les politiques de priorisation.
    
    Une politique définit les règles et contraintes pour la priorisation.
    """
    __tablename__ = 'policies'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    # Configuration de la stratégie
    strategy = Column(String(50), nullable=False)  # maximize_popt20, top_k_coverage, etc.
    constraints = Column(JSON, nullable=True)  # {budget_hours: 40, target_coverage: 0.8, etc.}
    
    # Configuration des services
    effort_config = Column(JSON, nullable=True)  # {loc_per_hour: 50, complexity_factor: 1.5}
    criticality_config = Column(JSON, nullable=True)  # {critical_modules: {...}, weights: {...}}
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(255), nullable=True)
    is_active = Column(Integer, default=1, nullable=False)  # 1 = active, 0 = inactive
    
    # Relations
    prioritization_plans = relationship("PrioritizationPlan", back_populates="policy")


class PrioritizationPlan(Base):
    """
    Modèle pour stocker les plans de priorisation générés.
    
    Un plan contient le résultat d'une priorisation pour un repository/sprint.
    """
    __tablename__ = 'prioritization_plans'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    repository_id = Column(String(255), nullable=False, index=True)
    sprint_id = Column(String(255), nullable=True, index=True)
    
    # Référence à la politique utilisée
    policy_id = Column(String, ForeignKey('policies.id'), nullable=True)
    policy = relationship("Policy", back_populates="prioritization_plans")
    
    # Stratégie utilisée
    strategy = Column(String(50), nullable=False)
    
    # Plan priorisé (JSON)
    prioritized_classes = Column(JSON, nullable=False)  # Liste de PrioritizedClass
    
    # Métriques
    total_effort_hours = Column(Float, nullable=False)
    estimated_coverage_gain = Column(Float, nullable=True)
    popt20_score = Column(Float, nullable=True)
    recall_top20 = Column(Float, nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Index composite pour recherche rapide
    __table_args__ = (
        {'mysql_engine': 'InnoDB'}
    )

