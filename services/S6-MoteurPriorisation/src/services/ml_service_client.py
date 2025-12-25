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
        sprint_id: Optional[str] = None,
        branch: Optional[str] = None
    ) -> List[Dict]:
        """
        Récupère les prédictions ML pour un repository.
        
        Args:
            repository_id: ID du repository
            sprint_id: ID du sprint (optionnel)
            branch: Nom de la branche Git (optionnel)
        
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
        if branch:
            params['branch'] = branch
        
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
            # En cas d'erreur, logger et retourner une liste vide
            # Ne plus utiliser de données mockées pour éviter d'afficher des classes qui n'existent pas
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to get predictions from S5 for repository {repository_id}: {e}")
            logger.warning("S5 endpoint /api/v1/predictions does not exist. Returning empty list.")
            return []
    
    def _get_mock_predictions(self, repository_id: str, branch: Optional[str] = None) -> List[Dict]:
        """
        Retourne des prédictions mockées pour le développement.
        Les données varient selon le repository_id ET la branche pour démontrer le caractère dynamique.
        
        Args:
            repository_id: ID du repository
            branch: Nom de la branche Git (optionnel, défaut: 'main')
        
        Returns:
            Liste de prédictions mockées
        """
        import hashlib
        import random
        
        # Utiliser le branch passé en paramètre ou 'main' par défaut
        repo_name = repository_id
        branch_name = branch or 'main'
        
        # Générer une seed basée sur repository ET branch pour des données différentes par branche
        combined_id = f"{repo_name}:{branch_name}"
        seed = int(hashlib.md5(combined_id.encode()).hexdigest()[:8], 16)
        random.seed(seed)
        
        # Différents ensembles de données selon le repository
        repo_datasets = {
            'spring-petclinic': [
                {'class_name': 'org.petclinic.owner.OwnerController', 'base_risk': 0.82},
                {'class_name': 'org.petclinic.vet.VetService', 'base_risk': 0.71},
                {'class_name': 'org.petclinic.visit.VisitRepository', 'base_risk': 0.65},
                {'class_name': 'org.petclinic.pet.PetValidator', 'base_risk': 0.53},
                {'class_name': 'org.petclinic.system.CrashController', 'base_risk': 0.44},
            ],
            'demo': [
                {'class_name': 'com.demo.api.UserController', 'base_risk': 0.88},
                {'class_name': 'com.demo.service.OrderService', 'base_risk': 0.76},
                {'class_name': 'com.demo.repository.ProductRepo', 'base_risk': 0.62},
                {'class_name': 'com.demo.util.JsonParser', 'base_risk': 0.41},
            ],
            'test': [
                {'class_name': 'com.test.auth.LoginService', 'base_risk': 0.91},
                {'class_name': 'com.test.payment.StripeGateway', 'base_risk': 0.79},
                {'class_name': 'com.test.email.NotificationSender', 'base_risk': 0.58},
            ],
        }
        
        # Ajouter des variations basées sur la branche
        branch_modifiers = {
            'main': {'risk_modifier': 0, 'prefix': ''},
            'develop': {'risk_modifier': 0.1, 'prefix': 'dev'},
            'master': {'risk_modifier': 0, 'prefix': ''},
            'feature': {'risk_modifier': 0.15, 'prefix': 'feat'},
        }
        
        modifier = branch_modifiers.get(branch_name.split('/')[0].lower(), {'risk_modifier': 0.05, 'prefix': 'branch'})
        
        # Trouver le dataset correspondant ou utiliser un dataset généré dynamiquement
        dataset = None
        for key in repo_datasets:
            if key in repo_name.lower():
                # Appliquer les modifications de branche aux datasets prédéfinis
                dataset = []
                for item in repo_datasets[key]:
                    # Modifier le nom de classe avec le préfixe de branche si nécessaire
                    class_name = item['class_name']
                    if modifier['prefix'] and branch_name != 'main' and branch_name != 'master':
                        # Insérer le préfixe dans le package
                        parts = class_name.split('.')
                        if len(parts) > 2:
                            class_name = '.'.join(parts[:-1]) + f".{modifier['prefix']}." + parts[-1]
                    
                    # Ajuster le risque selon la branche
                    base_risk = min(0.99, item['base_risk'] + modifier['risk_modifier'])
                    dataset.append({'class_name': class_name, 'base_risk': base_risk})
                break
        
        if not dataset:
            # Générer des données dynamiques basées sur le repository_id ET branch
            num_classes = random.randint(3, 8)
            packages = ['auth', 'payment', 'order', 'user', 'product', 'api', 'service', 'repository', 'util', 'config']
            class_types = ['Service', 'Controller', 'Repository', 'Handler', 'Manager', 'Validator', 'Processor']
            
            dataset = []
            for i in range(num_classes):
                pkg = random.choice(packages)
                cls_type = random.choice(class_types)
                prefix = f"{modifier['prefix']}." if modifier['prefix'] else ""
                class_name = f"com.{repo_name.replace('-', '.').lower()}.{prefix}{pkg}.{pkg.capitalize()}{cls_type}"
                base_risk = round(random.uniform(0.3, 0.95) + modifier['risk_modifier'], 2)
                base_risk = min(0.99, base_risk)  # Cap at 0.99
                dataset.append({'class_name': class_name, 'base_risk': base_risk})
        
        # Construire les prédictions complètes avec variation
        predictions = []
        for item in dataset:
            # Ajouter une légère variation aléatoire
            risk_variation = random.uniform(-0.05, 0.05)
            risk_score = max(0.1, min(0.99, item['base_risk'] + risk_variation))
            
            predictions.append({
                'class_name': item['class_name'],
                'risk_score': round(risk_score, 2),
                'loc': random.randint(50, 500),
                'cyclomatic_complexity': random.randint(3, 25),
                'num_methods': random.randint(3, 20),
                'num_dependencies': random.randint(0, 10)
            })
        
        # Trier par risk_score décroissant
        predictions.sort(key=lambda x: x['risk_score'], reverse=True)
        return predictions

