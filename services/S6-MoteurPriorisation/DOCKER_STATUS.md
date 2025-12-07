# 🐳 Service 6 - Statut Docker

## ✅ Service en cours d'exécution

### Conteneurs actifs

- **s6-moteur-priorisation** : ✅ Healthy
  - Port : `8006`
  - Status : `Up` (healthy)
  - URL : http://localhost:8006

- **s6-postgres** : ✅ Healthy
  - Port : `5432`
  - Status : `Up` (healthy)

## 🔗 Accès au service

### Endpoints disponibles

- **Health Check** : http://localhost:8006/health
  ```json
  {
    "status": "healthy",
    "service": "MoteurPriorisation",
    "version": "1.0.0"
  }
  ```

- **Swagger UI** : http://localhost:8006/docs
- **ReDoc** : http://localhost:8006/redoc
- **OpenAPI JSON** : http://localhost:8006/openapi.json

## 📋 Commandes utiles

### Voir les logs
```bash
docker-compose logs -f moteur-priorisation
```

### Arrêter le service
```bash
docker-compose down
```

### Redémarrer le service
```bash
docker-compose restart moteur-priorisation
```

### Voir le statut
```bash
docker-compose ps
```

### Accéder au conteneur
```bash
docker exec -it s6-moteur-priorisation /bin/bash
```

## 🧪 Tests

Le service est prêt pour les tests. Vous pouvez :
1. Accéder à Swagger UI pour tester les endpoints
2. Utiliser curl/Postman pour les requêtes API
3. Lancer les tests unitaires dans le conteneur


