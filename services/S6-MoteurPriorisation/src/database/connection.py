"""
Configuration de la connexion à la base de données
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import os
from dotenv import load_dotenv

load_dotenv()

# URL de la base de données
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://prioritest:prioritest@localhost:5432/prioritest'
)

# Créer l'engine
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Vérifier les connexions avant utilisation
    echo=False  # Mettre à True pour voir les requêtes SQL
)

# Créer la session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Dependency pour obtenir une session de base de données.
    
    Usage:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
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
    Base.metadata.create_all(bind=engine)


def drop_db():
    """
    Supprime toutes les tables de la base de données.
    """
    from src.database.models import Base
    Base.metadata.drop_all(bind=engine)

