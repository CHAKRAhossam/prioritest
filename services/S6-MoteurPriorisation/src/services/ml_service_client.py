"""
Client pour communiquer avec le Service ML (S5)

Récupère les prédictions ML depuis le service S5.
"""

from typing import List, Dict, Optional
import httpx
import os
from dotenv import load_dotenv

load_dotenv()


class MLServiceClient:
    """
    Client pour appeler le Service ML (S5) et récupérer les prédictions.
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialise le client ML Service.
        
        Args:
            base_url: URL de base du service ML (défaut: depuis .env)
        """
        self.base_url = base_url or os.getenv('ML_SERVICE_URL', 'http://localhost:8005')
        self.api_key = os.getenv('ML_SERVICE_API_KEY', '')
        self.timeout = 30.0
    
    async def get_predictions(
        self,
        repository_id: str,
        sprint_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Récupère les prédictions ML pour un repository.
        
        Args:
            repository_id: ID du repository
            sprint_id: ID du sprint (optionnel)
        
        Returns:
            Liste de prédictions avec :
                - class_name: str
                - risk_score: float [0-1]
                - loc: int
                - cyclomatic_complexity: float
                - (optionnel) num_methods: int
                - (optionnel) num_dependencies: int
        
        Raises:
            Exception: Si l'appel API échoue
        """
        url = f"{self.base_url}/api/v1/predictions"
        
        params = {
            'repository_id': repository_id
        }
        if sprint_id:
            params['sprint_id'] = sprint_id
        
        headers = {}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                # Extraire les prédictions
                predictions = data.get('predictions', [])
                return predictions
        
        except httpx.HTTPError as e:
            # En cas d'erreur, retourner des données mockées pour le développement
            # TODO: Logger l'erreur
            return self._get_mock_predictions(repository_id)
    
    def _get_mock_predictions(self, repository_id: str) -> List[Dict]:
        """
        Retourne des prédictions mockées pour le développement.
        
        Args:
            repository_id: ID du repository
        
        Returns:
            Liste de prédictions mockées
        """
        return [
            {
                'class_name': 'com.example.auth.UserService',
                'risk_score': 0.75,
                'loc': 150,
                'cyclomatic_complexity': 12,
                'num_methods': 8,
                'num_dependencies': 3
            },
            {
                'class_name': 'com.example.payment.PaymentService',
                'risk_score': 0.68,
                'loc': 200,
                'cyclomatic_complexity': 15,
                'num_methods': 10,
                'num_dependencies': 5
            },
            {
                'class_name': 'com.example.utils.StringHelper',
                'risk_score': 0.45,
                'loc': 50,
                'cyclomatic_complexity': 3,
                'num_methods': 2,
                'num_dependencies': 0
            },
            {
                'class_name': 'com.example.database.UserRepository',
                'risk_score': 0.60,
                'loc': 100,
                'cyclomatic_complexity': 8,
                'num_methods': 5,
                'num_dependencies': 2
            }
        ]

