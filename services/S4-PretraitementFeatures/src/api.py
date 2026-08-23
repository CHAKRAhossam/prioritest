from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import sys
import os
import logging

# Ensure the parent directory is in the python path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main_pipeline import main as run_pipeline

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
    service_name = "PRETRAITEMENT-FEATURES"
    instance_port = int(os.getenv("PORT", "8000"))
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
    title="Microservice 4 - Feature Engineering API",
    description="API for the Preprocessing and Feature Engineering Microservice",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}

@app.post("/run-pipeline")
async def trigger_pipeline():
    """
    Trigger the main data processing pipeline.
    """
    try:
        run_pipeline()
        return JSONResponse(content={"message": "Pipeline executed successfully"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)
