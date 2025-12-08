from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import sys
import os

# Ensure the parent directory is in the python path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main_pipeline import main as run_pipeline

app = FastAPI(
    title="Microservice 4 - Feature Engineering API",
    description="API for the Preprocessing and Feature Engineering Microservice",
    version="1.0.0"
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
