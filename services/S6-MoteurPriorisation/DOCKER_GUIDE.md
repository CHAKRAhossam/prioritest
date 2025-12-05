# Guide Docker - Service 6

## Prérequis

1. **Docker Desktop** installé et démarré
2. **Docker Compose** (inclus avec Docker Desktop)

## Vérification

```bash
# Vérifier que Docker est démarré
docker --version
docker ps

# Si erreur "cannot connect to Docker daemon", démarrer Docker Desktop
```

## Construction de l'image

```bash
# Construire l'image
docker build -t s6-moteur-priorisation:latest .

# Vérifier l'image
docker images | grep s6-moteur-priorisation
```

## Utilisation avec Docker Compose

### Démarrer les services

```bash
# Démarrer le service et PostgreSQL
docker-compose up -d

# Voir les logs
docker-compose logs -f moteur-priorisation

# Vérifier le statut
docker-compose ps
```

### Accéder au service

- **API** : http://localhost:8006
- **Swagger UI** : http://localhost:8006/docs
- **Health Check** : http://localhost:8006/health

### Arrêter les services

```bash
# Arrêter
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v
```

## Utilisation directe avec Docker

### Lancer le conteneur

```bash
# Lancer le conteneur
docker run -d \
  --name s6-moteur-priorisation \
  -p 8006:8006 \
  s6-moteur-priorisation:latest

# Voir les logs
docker logs -f s6-moteur-priorisation

# Arrêter
docker stop s6-moteur-priorisation
docker rm s6-moteur-priorisation
```

### Mode développement (avec volumes)

```bash
# Lancer avec hot-reload
docker run -d \
  --name s6-moteur-priorisation-dev \
  -p 8006:8006 \
  -v ${PWD}/src:/app/src \
  s6-moteur-priorisation:latest \
  uvicorn src.main:app --host 0.0.0.0 --port 8006 --reload
```

## Tests dans Docker

```bash
# Exécuter les tests dans un conteneur
docker run --rm \
  -v ${PWD}:/app \
  -w /app \
  s6-moteur-priorisation:latest \
  pytest tests/ -v
```

## Health Check

Le conteneur inclut un health check automatique :

```bash
# Vérifier le statut
docker ps
# La colonne STATUS montre "healthy" si tout va bien

# Tester manuellement
curl http://localhost:8006/health
```

## Dépannage

### Erreur : "cannot connect to Docker daemon"
- **Solution** : Démarrer Docker Desktop

### Erreur : "port already in use"
- **Solution** : Changer le port dans `docker-compose.yml` ou arrêter le service qui utilise le port 8006

### Erreur : "module not found"
- **Solution** : Vérifier que `requirements.txt` contient toutes les dépendances

### Voir les logs détaillés
```bash
docker-compose logs -f --tail=100 moteur-priorisation
```

## Production

Pour la production, utilisez :
- Variables d'environnement via `.env` ou secrets
- Reverse proxy (nginx/traefik)
- Orchestration (Kubernetes)
- Monitoring et logging

