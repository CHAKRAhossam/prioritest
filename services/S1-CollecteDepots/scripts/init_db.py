#!/usr/bin/env python3
"""Script to initialize database schema."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import settings
from src.services.database_service import DatabaseService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Initialize database schema."""
    logger.info("Initializing database schema...")
    
    try:
        db = DatabaseService()
        logger.info("Database schema initialized successfully")
        
        # Verify tables exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        logger.info(f"Created tables: {', '.join(tables)}")
        
        # Check TimescaleDB extension
        if settings.enable_timescale:
            with db.engine.connect() as conn:
                from sqlalchemy import text
                result = conn.execute(text(
                    "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'timescaledb');"
                ))
                if result.scalar():
                    logger.info("TimescaleDB extension is enabled")
                else:
                    logger.warning("TimescaleDB extension not found")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

