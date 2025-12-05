"""
Point d'entrée du Service 6 - Moteur de Priorisation
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import prioritization

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
    openapi_url="/openapi.json"
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

