# Service 7 - Test Scaffolder

**Responsable :** Hossam Chakra  
**Email :** hchakra8@gmail.com

## Description

Générer des squelettes JUnit pour classes prioritaires, suggestions de cas (équivalence, limites, mocks).

## Technologies

- **FastAPI** : Framework API REST
- **tree-sitter-java** : Analyse AST Java
- **Jinja2** : Templates pour génération de code
- **GitPython** : Manipulation Git
- **Python 3.11+** : Langage de programmation

## Structure du Projet

```
S7-TestScaffolder/
├── src/
│   ├── main.py              # Point d'entrée FastAPI
│   ├── api/                 # Endpoints API
│   │   └── scaffold.py
│   ├── models/              # Modèles de données (Pydantic)
│   ├── services/            # Logique métier
│   └── templates/           # Templates Jinja2
├── tests/
│   ├── unit/                # Tests unitaires
│   └── integration/        # Tests d'intégration
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Installation

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Copier le fichier d'environnement (si nécessaire)
# cp .env.example .env
# Éditer .env avec vos configurations
```

## Démarrage

```bash
# Mode développement
python src/main.py

# Ou avec uvicorn
uvicorn src.main:app --reload --port 8007
```

## API Documentation

Une fois le service démarré :
- **Swagger UI** : http://localhost:8007/docs
- **ReDoc** : http://localhost:8007/redoc
- **OpenAPI JSON** : http://localhost:8007/openapi.json

## Docker

```bash
# Construire et lancer avec Docker Compose
docker-compose up --build

# Ou construire l'image Docker
docker build -t s7-test-scaffolder .
docker run -p 8007:8007 s7-test-scaffolder
```

## User Stories

- **MTP-S7-79** : Créer la structure de base ✅
- **US-S7-01** : Analyse AST pour génération
- **US-S7-02** : Génération templates JUnit
- **US-S7-03** : Suggestions cas de test
- **US-S7-04** : Génération mocks
- **US-S7-05** : Checklist mutation testing
- **US-S7-06** : Stockage suggestions
- **US-S7-07** : API de génération

