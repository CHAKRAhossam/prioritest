"""
Point d'entrée du Service 6 - Moteur de Priorisation
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import prioritization

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Eureka Client
try:
    import py_eureka_client.eureka_client as eureka_client
    EUREKA_ENABLED = os.getenv("EUREKA_ENABLED", "true").lower() == "true"
except ImportError:
    EUREKA_ENABLED = False


async def register_eureka():
    """Register service with Eureka server."""
    if not EUREKA_ENABLED:
        logger.info("Eureka registration disabled")
        return
    
    eureka_server = os.getenv("EUREKA_URI", "http://eureka:eureka123@localhost:8761/eureka/")
    service_name = "MOTEUR-PRIORISATION"
    instance_port = int(os.getenv("PORT", "8006"))
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
    await register_eureka()
    yield
    if EUREKA_ENABLED:
        try:
            await eureka_client.stop_async()
            logger.info("Unregistered from Eureka")
        except Exception as e:
            logger.warning(f"Error stopping Eureka client: {e}")


app = FastAPI(
    title="Moteur de Priorisation API",
    description="""
    API pour transformer les scores ML en liste priorisée.
    
    ## Fonctionnalités
    
    * **Priorisation effort-aware** : Intègre l'effort (LOC, complexité)
    * **Criticité module** : Pondère par criticité des modules
    * **Optimisation** : Utilise OR-Tools pour optimiser sous contraintes
    * **Stratégies** : Top-K, Popt@20, budget de tests
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS pour permettre les appels depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les origines
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routers
app.include_router(
    prioritization.router,
    prefix="/api/v1",
    tags=["Priorisation"]
)

@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Status de l'API
    """
    return {
        "status": "healthy",
        "service": "MoteurPriorisation",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)


