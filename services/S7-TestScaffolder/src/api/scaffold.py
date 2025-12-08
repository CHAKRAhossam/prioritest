"""
API endpoints pour la génération de tests
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/test-scaffold", summary="Générer squelette de test")
def generate_test_scaffold():
    """
    Génère un squelette de test JUnit pour une classe.
    
    Returns:
        dict: Template de test généré
    """
    return {"message": "Test scaffold endpoint - À implémenter"}

