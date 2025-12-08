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

### Endpoint Principal ⭐

**POST /api/v1/generate-complete** : Endpoint complet qui exécute tout le workflow :
1. Analyse AST de la classe
2. Génération de test JUnit avec Mockito
3. Suggestions de cas de test
4. Checklist mutation testing
5. Stockage Git (optionnel)

C'est l'endpoint recommandé pour une utilisation complète du service.

Voir la section "API Endpoints" ci-dessous pour tous les détails.

## Docker

```bash
# Construire et lancer avec Docker Compose
docker-compose up --build

# Ou construire l'image Docker
docker build -t s7-test-scaffolder .
docker run -p 8007:8007 s7-test-scaffolder
```

## User Stories

- **MTP-78** : Créer la structure de base ✅
- **MTP-48** : Analyse AST pour génération ✅
- **MTP-49** : Génération templates JUnit ✅
- **MTP-50** : Suggestions cas de test ✅
- **MTP-51** : Génération mocks ✅
- **MTP-52** : Checklist mutation testing ✅
- **MTP-53** : Stockage suggestions ✅
- **MTP-54** : API de génération complète ✅

## API Endpoints

### POST /api/v1/analyze
Analyse une classe Java et extrait ses informations (AST).

**Request:**
```json
{
  "java_code": "package com.example; public class UserService {}",
  "file_path": "src/main/java/com/example/UserService.java"
}
```

**Response:**
```json
{
  "analysis": {
    "class_name": "UserService",
    "package_name": "com.example",
    "methods": [...],
    "fields": [...],
    "imports": [...]
  }
}
```

### POST /api/v1/generate-test
Génère un squelette de test JUnit complet.

**Request:**
```json
{
  "java_code": "...",
  "test_package": "com.example.test",
  "test_class_suffix": "Test"
}
```

**Response:**
```json
{
  "test_code": "package com.example.test; ...",
  "test_class_name": "UserServiceTest",
  "test_package": "com.example.test",
  "analysis": {...}
}
```

### POST /api/v1/suggest-test-cases
Génère des suggestions de cas de test.

**Request:**
```json
{
  "java_code": "...",
  "include_private": false
}
```

**Response:**
```json
{
  "class_name": "UserService",
  "method_suggestions": [...],
  "total_suggestions": 15,
  "coverage_estimate": 0.75
}
```

### POST /api/v1/mutation-checklist
Génère une checklist de mutation testing.

**Request:**
```json
{
  "java_code": "...",
  "include_private": false
}
```

**Response:**
```json
{
  "class_name": "UserService",
  "method_checklists": [...],
  "total_items": 20,
  "coverage_estimate": 0.80
}
```

### POST /api/v1/save-suggestions
Sauvegarde les tests et suggestions dans Git.

**Request:**
```json
{
  "java_code": "...",
  "branch": "feature/add-tests",
  "commit_message": "feat: Add generated tests",
  "push": false
}
```

**Response:**
```json
{
  "success": true,
  "test_file_commit": {...},
  "suggestions_file_commit": {...},
  "message": "Suggestions sauvegardées avec succès"
}
```

### POST /api/v1/generate-complete ⭐
**Endpoint principal** : Génération complète en une seule requête.

**Request:**
```json
{
  "java_code": "package com.example; public class UserService {}",
  "test_package": "com.example.test",
  "include_suggestions": true,
  "include_mutation_checklist": true,
  "save_to_git": false,
  "git_branch": "feature/add-tests",
  "git_push": false
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {...},
  "test_code": "...",
  "test_class_name": "UserServiceTest",
  "test_package": "com.example.test",
  "suggestions": {...},
  "mutation_checklist": {...},
  "git_storage": {...},
  "summary": {
    "class_name": "UserService",
    "methods_count": 5,
    "public_methods_count": 4,
    "test_generated": true,
    "suggestions_count": 15,
    "mutation_items_count": 20,
    "saved_to_git": false
  }
}
```

