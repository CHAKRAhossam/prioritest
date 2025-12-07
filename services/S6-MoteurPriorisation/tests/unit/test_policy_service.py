"""
Tests unitaires pour PolicyService
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base
from src.services.policy_service import PolicyService


@pytest.fixture
def db_session():
    """Fixture pour créer une session de test"""
    # Base de données en mémoire pour les tests
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


class TestPolicyService:
    """Tests pour PolicyService"""
    
    def test_create_policy(self, db_session):
        """Test création d'une politique"""
        service = PolicyService(db_session)
        
        policy = service.create_policy(
            name="Test Policy",
            strategy="maximize_popt20",
            description="Test description",
            constraints={"budget_hours": 40}
        )
        
        assert policy.id is not None
        assert policy.name == "Test Policy"
        assert policy.strategy == "maximize_popt20"
        assert policy.is_active == 1
    
    def test_create_policy_duplicate_name(self, db_session):
        """Test création avec nom dupliqué"""
        service = PolicyService(db_session)
        
        service.create_policy(name="Test Policy", strategy="maximize_popt20")
        
        with pytest.raises(ValueError, match="existe déjà"):
            service.create_policy(name="Test Policy", strategy="budget_optimization")
    
    def test_get_policy(self, db_session):
        """Test récupération d'une politique"""
        service = PolicyService(db_session)
        
        created = service.create_policy(
            name="Test Policy",
            strategy="maximize_popt20"
        )
        
        retrieved = service.get_policy(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Test Policy"
    
    def test_get_policy_by_name(self, db_session):
        """Test récupération par nom"""
        service = PolicyService(db_session)
        
        service.create_policy(name="Test Policy", strategy="maximize_popt20")
        
        policy = service.get_policy_by_name("Test Policy")
        
        assert policy is not None
        assert policy.name == "Test Policy"
    
    def test_list_policies(self, db_session):
        """Test liste des politiques"""
        service = PolicyService(db_session)
        
        service.create_policy(name="Policy 1", strategy="maximize_popt20")
        service.create_policy(name="Policy 2", strategy="budget_optimization")
        
        policies = service.list_policies()
        
        assert len(policies) == 2
    
    def test_list_policies_active_only(self, db_session):
        """Test liste avec seulement les actives"""
        service = PolicyService(db_session)
        
        policy1 = service.create_policy(name="Policy 1", strategy="maximize_popt20")
        service.create_policy(name="Policy 2", strategy="budget_optimization")
        
        service.delete_policy(policy1.id)  # Soft delete
        
        policies = service.list_policies(active_only=True)
        
        assert len(policies) == 1
        assert policies[0].name == "Policy 2"
    
    def test_update_policy(self, db_session):
        """Test mise à jour d'une politique"""
        service = PolicyService(db_session)
        
        policy = service.create_policy(
            name="Test Policy",
            strategy="maximize_popt20"
        )
        
        updated = service.update_policy(
            policy.id,
            name="Updated Policy",
            strategy="budget_optimization"
        )
        
        assert updated.name == "Updated Policy"
        assert updated.strategy == "budget_optimization"
    
    def test_delete_policy(self, db_session):
        """Test suppression d'une politique"""
        service = PolicyService(db_session)
        
        policy = service.create_policy(name="Test Policy", strategy="maximize_popt20")
        
        result = service.delete_policy(policy.id)
        
        assert result is True
        retrieved = service.get_policy(policy.id)
        assert retrieved.is_active == 0
    
    def test_save_plan(self, db_session):
        """Test sauvegarde d'un plan"""
        service = PolicyService(db_session)
        
        plan = service.save_plan(
            repository_id="repo_123",
            strategy="maximize_popt20",
            prioritized_classes=[
                {"class_name": "TestClass", "priority": 1}
            ],
            metrics={"total_effort_hours": 10.0}
        )
        
        assert plan.id is not None
        assert plan.repository_id == "repo_123"
        assert len(plan.prioritized_classes) == 1
    
    def test_get_latest_plan(self, db_session):
        """Test récupération du plan le plus récent"""
        service = PolicyService(db_session)
        
        service.save_plan(
            repository_id="repo_123",
            strategy="maximize_popt20",
            prioritized_classes=[],
            metrics={"total_effort_hours": 5.0}
        )
        
        plan2 = service.save_plan(
            repository_id="repo_123",
            strategy="budget_optimization",
            prioritized_classes=[],
            metrics={"total_effort_hours": 10.0}
        )
        
        latest = service.get_latest_plan("repo_123")
        
        assert latest.id == plan2.id
        assert latest.strategy == "budget_optimization"
    
    def test_list_plans(self, db_session):
        """Test liste des plans"""
        service = PolicyService(db_session)
        
        service.save_plan(
            repository_id="repo_123",
            strategy="maximize_popt20",
            prioritized_classes=[],
            metrics={"total_effort_hours": 5.0}
        )
        
        service.save_plan(
            repository_id="repo_456",
            strategy="budget_optimization",
            prioritized_classes=[],
            metrics={"total_effort_hours": 10.0}
        )
        
        plans = service.list_plans()
        assert len(plans) == 2
        
        plans_repo = service.list_plans(repository_id="repo_123")
        assert len(plans_repo) == 1
    
    def test_delete_plan(self, db_session):
        """Test suppression d'un plan"""
        service = PolicyService(db_session)
        
        plan = service.save_plan(
            repository_id="repo_123",
            strategy="maximize_popt20",
            prioritized_classes=[],
            metrics={"total_effort_hours": 5.0}
        )
        
        result = service.delete_plan(plan.id)
        
        assert result is True
        retrieved = service.get_plan(plan.id)
        assert retrieved is None

