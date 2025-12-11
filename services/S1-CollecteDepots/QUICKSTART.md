# Guide de Démarrage Rapide - S1-CollecteDepots

## 🚀 Démarrage en 5 minutes

### 1. Prérequis

- Docker et Docker Compose installés
- Python 3.11+ (pour développement local)

### 2. Configuration rapide

```bash
# Cloner le projet (si pas déjà fait)
cd prioritest/services/S1-CollecteDepots

# Copier le fichier d'environnement
cp .env.example .env

# Éditer .env et configurer vos tokens (optionnel pour tester)
# GITHUB_TOKEN=your_token_here
# GITLAB_TOKEN=your_token_here
# JIRA_URL=https://your-domain.atlassian.net
```

### 3. Démarrer avec Docker Compose

```bash
# Depuis la racine du projet
docker-compose up -d collecte-depots

# Vérifier que le service est démarré
docker-compose ps collecte-depots

# Voir les logs
docker-compose logs -f collecte-depots
```

### 4. Vérifier que tout fonctionne

```bash
# Health check
curl http://localhost:8001/health

# Status des services
curl http://localhost:8001/api/v1/collect/status
```

### 5. Tester la collecte manuelle

```bash
# Collecter des commits depuis GitHub
curl -X POST http://localhost:8001/api/v1/collect \
  -H "Content-Type: application/json" \
  -d '{
    "repository_url": "https://github.com/org/repo",
    "collect_type": "commits",
    "date_range": {
      "start": "2025-01-01",
      "end": "2025-12-04"
    }
  }'
```

### 6. Accéder à la documentation

Ouvrir dans le navigateur :
- **Swagger UI** : http://localhost:8001/docs
- **ReDoc** : http://localhost:8001/redoc

## 📝 Configuration des Webhooks

### GitHub

1. Aller dans les paramètres du repository GitHub
2. Webhooks → Add webhook
3. URL : `http://your-domain:8001/api/v1/webhooks/github`
4. Content type : `application/json`
5. Secret : Configurer dans `.env` (`GITHUB_WEBHOOK_SECRET`)
6. Events : Sélectionner `push` et `issues`

### GitLab

1. Aller dans Settings → Webhooks du projet GitLab
2. URL : `http://your-domain:8001/api/v1/webhooks/gitlab`
3. Secret token : Configurer dans `.env` (`GITLAB_WEBHOOK_SECRET`)
4. Trigger : Sélectionner `Push events` et `Issue events`

### Jira

1. Aller dans Settings → System → Webhooks
2. Créer un nouveau webhook
3. URL : `http://your-domain:8001/api/v1/webhooks/jira`
4. Events : Sélectionner `Issue created` et `Issue updated`

## 🔍 Vérification des données collectées

### Vérifier dans Kafka

```bash
# Consulter les topics
docker exec -it prioritest-kafka kafka-topics --list --bootstrap-server localhost:9092

# Consulter les messages du topic commits
docker exec -it prioritest-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic repository.commits \
  --from-beginning
```

### Vérifier dans PostgreSQL

```bash
# Se connecter à la base de données
docker exec -it prioritest-postgres psql -U prioritest -d prioritest

# Voir les repositories
SELECT * FROM repositories;

# Voir les commits
SELECT commit_sha, commit_message, author_email, timestamp FROM commits LIMIT 10;

# Voir les issues
SELECT issue_key, summary, status, created_at FROM issues LIMIT 10;
```

### Vérifier dans MinIO

1. Accéder à l'interface MinIO : http://localhost:9001
2. Login : `minioadmin` / `minioadmin`
3. Vérifier les buckets : `ci-artifacts` et `repository-snapshots`

## 🧪 Tests

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer les tests
pytest tests/ -v

# Avec couverture
pytest tests/ --cov=src --cov-report=html
```

## 🐛 Dépannage

### Le service ne démarre pas

```bash
# Vérifier les logs
docker-compose logs collecte-depots

# Vérifier que les dépendances sont démarrées
docker-compose ps
```

### Erreur de connexion Kafka

```bash
# Vérifier que Kafka est démarré
docker-compose ps kafka

# Vérifier les variables d'environnement
docker-compose exec collecte-depots env | grep KAFKA
```

### Erreur de connexion base de données

```bash
# Vérifier que PostgreSQL est démarré
docker-compose ps postgres

# Tester la connexion
docker-compose exec postgres psql -U prioritest -d prioritest -c "SELECT 1;"
```

## 📚 Documentation complète

Voir [README.md](README.md) pour la documentation complète.

