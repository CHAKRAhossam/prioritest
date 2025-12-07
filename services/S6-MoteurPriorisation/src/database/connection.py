"""
Configuration de la connexion à la base de données
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

# URL de la base de données
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://prioritest:prioritest@localhost:5432/prioritest'
)

# Engine et SessionLocal seront créés à la première utilisation
_engine: Optional[object] = None
_SessionLocal: Optional[sessionmaker] = None


def get_engine():
    """Crée et retourne l'engine (lazy initialization)"""
    global _engine
    if _engine is None:
        _engine = create_engine(
            DATABASE_URL,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Vérifier les connexions avant utilisation
            echo=False  # Mettre à True pour voir les requêtes SQL
        )
    return _engine


def get_session_local():
    """Crée et retourne la session factory (lazy initialization)"""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


def get_db() -> Session:
    """
    Dependency pour obtenir une session de base de données.
    
    Usage:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialise la base de données en créant toutes les tables.
    """
    from src.database.models import Base
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def drop_db():
    """
    Supprime toutes les tables de la base de données.
    """
    from src.database.models import Base
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)

