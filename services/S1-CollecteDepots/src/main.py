"""Main FastAPI application for S1-CollecteDepots service."""
import logging
import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.api import collect, webhooks

# Eureka Client
try:
    import py_eureka_client.eureka_client as eureka_client
    EUREKA_ENABLED = os.getenv("EUREKA_ENABLED", "true").lower() == "true"
except ImportError:
    EUREKA_ENABLED = False

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def register_eureka():
    """Register service with Eureka server."""
    if not EUREKA_ENABLED:
        logger.info("Eureka registration disabled")
        return
    
    eureka_server = os.getenv("EUREKA_URI", "http://eureka:eureka123@localhost:8761/eureka/")
    service_name = "COLLECTE-DEPOTS"
    instance_port = int(os.getenv("PORT", "8001"))
    instance_host = os.getenv("HOSTNAME", "localhost")
    
    try:
        await eureka_client.init_async(
            eureka_server=eureka_server,
            app_name=service_name,
            instance_port=instance_port,
            instance_host=instance_host,
            renewal_interval_in_secs=30,
            duration_in_secs=90
        )
        logger.info(f"Registered {service_name} with Eureka at {eureka_server}")
    except Exception as e:
        logger.warning(f"Failed to register with Eureka: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    await register_eureka()
    yield
    # Shutdown
    if EUREKA_ENABLED:
        try:
            await eureka_client.stop_async()
            logger.info("Unregistered from Eureka")
        except Exception as e:
            logger.warning(f"Error stopping Eureka client: {e}")


app = FastAPI(
    title="Service S1 - Collecte de Dépôts",
    description="""
    Service d'ingestion des dépôts Git/GitHub/GitLab, issues Jira, et artefacts CI/CD.
    
    ## Fonctionnalités
    
    * **Collecte automatique** : Webhooks GitHub/GitLab/Jira
    * **Collecte manuelle** : API REST pour déclencher la collecte
    * **Stockage** : PostgreSQL (métadonnées), MinIO (artefacts), TimescaleDB (métriques)
    * **Streaming** : Publication vers Kafka (topics: repository.commits, repository.issues, ci.artifacts)
    * **Versioning** : DVC pour versionner les jeux de données internes
    """,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(collect.router)
app.include_router(webhooks.router)

# Import artifacts router
try:
    from src.api import artifacts
    app.include_router(artifacts.router)
except ImportError:
    logger.warning("Artifacts router not available")


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Service health status
    """
    return {
        "status": "healthy",
        "service": "CollecteDepots",
        "version": settings.app_version
    }


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Initialize database
    try:
        from src.services.database_service import DatabaseService
        db = DatabaseService()
        logger.info("Database service initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    # Initialize MinIO
    try:
        from src.services.minio_service import MinIOService
        minio = MinIOService()
        logger.info("MinIO service initialized")
    except Exception as e:
        logger.error(f"MinIO initialization failed: {e}")
    
    # Initialize Kafka
    try:
        from src.services.kafka_service import KafkaService
        kafka = KafkaService()
        logger.info("Kafka service initialized")
    except Exception as e:
        logger.warning(f"Kafka initialization failed: {e}")
    
    # Initialize DVC if enabled
    if settings.enable_dvc:
        try:
            from src.services.dvc_service import DVCService
            dvc = DVCService()
            logger.info("DVC service initialized")
        except Exception as e:
            logger.warning(f"DVC initialization failed: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down CollecteDepots service")
    
    # Flush Kafka producer
    try:
        from src.services.kafka_service import KafkaService
        kafka = KafkaService()
        kafka.close()
    except Exception:
        pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development"
    )

