# Service 6 - Moteur de Priorisation

**Responsable :** Hossam Chakra  
**Email :** hchakra8@gmail.com

## Description

Transformer scores en liste ordonnée en intégrant effort (LOC), criticité module, dépendances et objectifs de sprint.

## Technologies

- **FastAPI** : Framework API REST
- **OR-Tools** : Optimisation sous contraintes
- **PostgreSQL** : Stockage des politiques et plans
- **Pydantic** : Validation des données
- **Python 3.11+** : Langage de programmation

## Structure du Projet

```
S6-MoteurPriorisation/
├── src/
│   ├── main.py              # Point d'entrée FastAPI
│   ├── api/                 # Endpoints API
│   │   └── prioritization.py
│   ├── models/              # Modèles de données (Pydantic)
│   │   └── prioritization.py
│   ├── services/            # Logique métier
│   └── utils/               # Utilitaires
├── tests/
│   ├── unit/                # Tests unitaires
│   ├── integration/         # Tests d'intégration
│   └── fixtures/            # Données de test
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

## Installation

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Copier le fichier d'environnement
cp .env.example .env
# Éditer .env avec vos configurations
```

## Démarrage

```bash
# Mode développement
python src/main.py

# Ou avec uvicorn
uvicorn src.main:app --reload --port 8006
```

## API Documentation

Une fois le service démarré :
- **Swagger UI** : http://localhost:8006/docs
- **ReDoc** : http://localhost:8006/redoc
- **OpenAPI JSON** : http://localhost:8006/openapi.json

## User Stories

- **MTP-79** : Créer la structure de base ✅
- **MTP-40** : US-S6-01: Calcul effort-aware
- **MTP-41** : US-S6-02: Intégration criticité module
- **MTP-42** : US-S6-03: Optimisation avec OR-Tools
- **MTP-43** : US-S6-04: Stratégies de priorisation
- **MTP-44** : US-S6-05: API de priorisation
- **MTP-45** : US-S6-06: Stockage politiques
- **MTP-46** : US-S6-07: Métriques de performance

## Tests

```bash
# Lancer les tests
pytest tests/

# Avec couverture
pytest tests/ --cov=src --cov-report=html
```

## Docker

### Construction et lancement

```bash
# Construire l'image
docker build -t s6-moteur-priorisation:latest .

# Lancer avec docker-compose (recommandé)
docker-compose up -d

# Ou lancer directement
docker run -d -p 8006:8006 --name s6-moteur-priorisation s6-moteur-priorisation:latest
```

### Tests Docker

```bash
# Windows PowerShell
.\docker-test.ps1

# Linux/Mac
chmod +x docker-test.sh
./docker-test.sh
```

Voir `DOCKER_GUIDE.md` pour plus de détails.

## Configuration

Voir `.env.example` pour les variables d'environnement nécessaires.

## Endpoints API

### POST /api/v1/prioritize
Priorise les classes à tester.

**Request:**
```json
{
  "repository_id": "repo_12345",
  "sprint_id": "sprint_1",
  "constraints": {
    "budget_hours": 40,
    "target_coverage": 0.85
  }
}
```

**Response:**
```json
{
  "prioritized_plan": [...],
  "metrics": {...}
}
```

### GET /api/v1/prioritize/{repository_id}
Récupère un plan de priorisation existant.

### GET /health
Health check endpoint.

