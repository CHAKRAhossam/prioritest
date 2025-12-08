"""
Point d'entrée du Service 7 - Test Scaffolder
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import scaffold

app = FastAPI(
    title="Test Scaffolder API",
    description="""
    API pour générer des squelettes de tests JUnit avec suggestions.
    
    ## Fonctionnalités
    
    * **Analyse AST** : Analyse du code Java pour extraire méthodes et dépendances
    * **Génération templates** : Génération de squelettes JUnit
    * **Suggestions** : Suggestions de cas de test (équivalence, limites, exceptions)
    * **Mocks** : Génération automatique de mocks Mockito
    * **Checklist** : Checklist pour mutation testing
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS pour permettre les appels depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routers
app.include_router(
    scaffold.router,
    prefix="/api/v1",
    tags=["Test Scaffolding"]
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
        "service": "TestScaffolder",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)

