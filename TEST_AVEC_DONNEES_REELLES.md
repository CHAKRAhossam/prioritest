# 🚀 Guide de Test avec Données Réelles - S1 CollecteDepots

## 📋 Prérequis

### 1. Tokens d'Accès (Optionnels pour dépôts publics)

Pour collecter des données de dépôts **privés**, vous aurez besoin de tokens:

#### GitHub Token
1. Allez sur https://github.com/settings/tokens
2. Créez un nouveau token avec les permissions:
   - `repo` (accès complet aux dépôts)
   - `read:org` (lire les organisations)
3. Copiez le token

#### GitLab Token
1. Allez sur https://gitlab.com/-/profile/personal_access_tokens
2. Créez un token avec les permissions:
   - `read_api`
   - `read_repository`
3. Copiez le token

#### Jira (Optionnel)
- URL de votre instance Jira
- Email + API Token

### 2. Configuration des Variables d'Environnement

Créez un fichier `.env` dans `services/S1-CollecteDepots/`:

```bash
# GitHub
GITHUB_TOKEN=ghp_votre_token_ici

# GitLab
GITLAB_TOKEN=glpat_votre_token_ici
GITLAB_URL=https://gitlab.com

# Jira (optionnel)
JIRA_URL=https://votre-instance.atlassian.net
JIRA_EMAIL=votre.email@example.com
JIRA_API_TOKEN=votre_token_jira

# Base de données
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=collecte_db
POSTGRES_USER=collecte_user
POSTGRES_PASSWORD=collecte_pass

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

---

## 🎯 Test 1: Collecter un Dépôt GitHub Public Réel

### Dépôts Publics Recommandés (Petits et Actifs)

1. **octocat/Hello-World** - Le plus simple (quelques commits)
2. **microsoft/TypeScript-Node-Starter** - Petit projet TypeScript
3. **spring-projects/spring-petclinic** - Projet Java Spring classique
4. **facebook/react** - Projet React (attention: gros dépôt)

### Test dans Swagger

1. Ouvrez http://localhost:8001/docs
2. Allez sur `POST /api/v1/collect`
3. Cliquez sur "Try it out"
4. Utilisez ce JSON:

```json
{
  "repository_url": "https://github.com/octocat/Hello-World",
  "collect_type": "commits",
  "date_range": {
    "start": "2020-01-01",
    "end": "2025-12-13"
  }
}
```

5. Cliquez sur "Execute"
6. **Résultat attendu**: 202 Accepted (traitement en background)

### Vérification des Données Collectées

```powershell
# Vérifier les logs
docker-compose logs --tail=50 collecte-depots | Select-String -Pattern "Stored commit|Published commit"

# Vérifier dans la base de données
docker exec -it prioritest-postgres psql -U collecte_user -d collecte_db -c "SELECT COUNT(*) FROM commits;"
docker exec -it prioritest-postgres psql -U collecte_user -d collecte_db -c "SELECT commit_sha, commit_message FROM commits LIMIT 5;"
```

---

## 🎯 Test 2: Collecter Issues depuis GitHub

### Test dans Swagger

```json
{
  "repository_url": "https://github.com/spring-projects/spring-petclinic",
  "collect_type": "issues",
  "date_range": {
    "start": "2024-01-01",
    "end": "2025-12-13"
  }
}
```

### Vérification

```powershell
docker exec -it prioritest-postgres psql -U collecte_user -d collecte_db -c "SELECT COUNT(*) FROM issues;"
docker exec -it prioritest-postgres psql -U collecte_user -d collecte_db -c "SELECT issue_key, summary FROM issues LIMIT 5;"
```

---

## 🎯 Test 3: Collecter un Dépôt GitLab Public

### Dépôts GitLab Publics Recommandés

1. **gitlab-org/gitlab** - GitLab lui-même
2. **fdroid/fdroidclient** - Application Android
3. **inkscape/inkscape** - Application de dessin vectoriel

### Test dans Swagger

```json
{
  "repository_url": "https://gitlab.com/inkscape/inkscape",
  "collect_type": "commits",
  "date_range": {
    "start": "2024-01-01",
    "end": "2025-12-13"
  }
}
```

---

## 🎯 Test 4: Simuler un Webhook GitHub Réel

### Obtenir un Vrai Payload GitHub

1. Allez sur https://github.com/{votre-repo}/settings/hooks
2. Créez un webhook avec l'URL: `http://localhost:8001/api/v1/webhooks/github`
3. Sélectionnez "Push events"
4. GitHub enverra automatiquement un webhook à chaque push

### Alternative: Tester avec un Payload Réel Capturé

Utilisez un payload réel depuis https://docs.github.com/en/webhooks/webhook-events-and-payloads#push

```json
{
  "ref": "refs/heads/main",
  "before": "abc123",
  "after": "def456",
  "repository": {
    "id": 123456789,
    "name": "my-real-repo",
    "full_name": "username/my-real-repo",
    "owner": {
      "name": "username",
      "email": "user@example.com"
    }
  },
  "pusher": {
    "name": "username",
    "email": "user@example.com"
  },
  "commits": [
    {
      "id": "7fd1a60b01f91b314f59955a4e4d4e80d8edf11d",
      "tree_id": "7d1b31e74ee336d15cbd21741bc88a537ed063a0",
      "message": "Add real feature",
      "timestamp": "2025-12-13T10:00:00+00:00",
      "url": "https://github.com/username/my-real-repo/commit/7fd1a60b",
      "author": {
        "name": "John Doe",
        "email": "john@example.com",
        "username": "johndoe"
      },
      "committer": {
        "name": "John Doe",
        "email": "john@example.com",
        "username": "johndoe"
      },
      "added": ["src/NewFeature.java"],
      "removed": [],
      "modified": ["README.md"]
    }
  ]
}
```

---

## 🎯 Test 5: Uploader un Vrai Rapport JaCoCo

### Générer un Rapport JaCoCo Réel

#### Option 1: Télécharger un Exemple
```powershell
# Télécharger un exemple de rapport JaCoCo
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/jacoco/jacoco/master/org.jacoco.report.test/src/org/jacoco/report/internal/html/resources/report.css" -OutFile "jacoco-example.xml"
```

#### Option 2: Créer un Fichier XML Simple
```powershell
@"
<?xml version="1.0" encoding="UTF-8"?>
<report name="Test Coverage">
  <sessioninfo id="test-session" start="1702468800000" dump="1702555200000"/>
  <package name="com/example">
    <class name="com/example/UserService">
      <method name="createUser" desc="(Ljava/lang/String;)V">
        <counter type="INSTRUCTION" missed="0" covered="50"/>
        <counter type="BRANCH" missed="2" covered="8"/>
        <counter type="LINE" missed="0" covered="15"/>
      </method>
    </class>
  </package>
  <counter type="INSTRUCTION" missed="0" covered="50"/>
  <counter type="BRANCH" missed="2" covered="8"/>
  <counter type="LINE" missed="0" covered="15"/>
  <counter type="COMPLEXITY" missed="1" covered="5"/>
  <counter type="METHOD" missed="0" covered="1"/>
  <counter type="CLASS" missed="0" covered="1"/>
</report>
"@ | Out-File -FilePath "jacoco-real.xml" -Encoding UTF8
```

### Uploader dans Swagger

1. Ouvrez http://localhost:8001/docs
2. Allez sur `POST /api/v1/artifacts/upload/jacoco`
3. Cliquez sur "Try it out"
4. Remplissez:
   - `artifact_type`: `jacoco`
   - `repository_id`: `my-real-repo`
   - `commit_sha`: `7fd1a60b01f91b314f59955a4e4d4e80d8edf11d`
   - `build_id`: `build-123`
   - `file`: Sélectionnez `jacoco-real.xml`
5. Cliquez sur "Execute"

### Vérification

```powershell
# Vérifier dans MinIO
docker exec -it prioritest-minio mc ls minio/artifacts/

# Vérifier dans la base de données
docker exec -it prioritest-postgres psql -U collecte_user -d collecte_db -c "SELECT * FROM ci_artifacts WHERE commit_sha='7fd1a60b01f91b314f59955a4e4d4e80d8edf11d';"
```

---

## 🎯 Test 6: Collecter un Projet Java Complet

### Projet Recommandé: Spring PetClinic

```json
{
  "repository_url": "https://github.com/spring-projects/spring-petclinic",
  "collect_type": "commits|issues",
  "date_range": {
    "start": "2024-01-01",
    "end": "2025-12-13"
  }
}
```

Ce projet contient:
- ✅ Commits réguliers
- ✅ Issues GitHub
- ✅ Code Java avec classes
- ✅ Historique de tests
- ✅ Rapports de couverture

---

## 📊 Visualiser les Données Collectées

### Dans PostgreSQL

```powershell
# Se connecter à PostgreSQL
docker exec -it prioritest-postgres psql -U collecte_user -d collecte_db

# Voir les dépôts collectés
SELECT id, name, url, created_at FROM repositories;

# Voir les commits collectés
SELECT commit_sha, LEFT(commit_message, 50) as message, author_name, timestamp 
FROM commits 
ORDER BY timestamp DESC 
LIMIT 10;

# Voir les issues collectées
SELECT issue_key, LEFT(summary, 50) as summary, status, created_at 
FROM issues 
ORDER BY created_at DESC 
LIMIT 10;

# Statistiques
SELECT 
    (SELECT COUNT(*) FROM repositories) as repos,
    (SELECT COUNT(*) FROM commits) as commits,
    (SELECT COUNT(*) FROM issues) as issues,
    (SELECT COUNT(*) FROM ci_artifacts) as artifacts;
```

### Dans MinIO

```powershell
# Lister les buckets
docker exec -it prioritest-minio mc ls minio/

# Lister les artefacts
docker exec -it prioritest-minio mc ls minio/artifacts/

# Télécharger un artefact
docker exec -it prioritest-minio mc cp minio/artifacts/jacoco_7fd1a60b.xml ./downloaded-artifact.xml
```

---

## 🔍 Déboguer et Surveiller

### Logs en Temps Réel

```powershell
# Suivre les logs de collecte
docker-compose logs -f collecte-depots

# Filtrer les événements importants
docker-compose logs --tail=100 collecte-depots | Select-String -Pattern "Stored|Published|ERROR"
```

### Vérifier Kafka

```powershell
# Se connecter au conteneur Kafka
docker exec -it prioritest-kafka bash

# Lister les topics
kafka-topics --list --bootstrap-server localhost:9092

# Consommer les messages du topic commits
kafka-console-consumer --bootstrap-server localhost:9092 --topic repository.commits --from-beginning --max-messages 5
```

---

## 🎯 Scénario de Test Complet

### Scénario: Collecter Spring PetClinic Complet

```powershell
# 1. Collecter les commits
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/collect" `
    -Method POST `
    -ContentType "application/json" `
    -Body (@{
        repository_url = "https://github.com/spring-projects/spring-petclinic"
        collect_type = "commits"
        date_range = @{
            start = "2024-01-01"
            end = "2025-12-13"
        }
    } | ConvertTo-Json)

# 2. Attendre 30 secondes
Start-Sleep -Seconds 30

# 3. Vérifier les données
docker exec -it prioritest-postgres psql -U collecte_user -d collecte_db -c "
SELECT 
    r.name as repository,
    COUNT(c.id) as total_commits,
    MIN(c.timestamp) as first_commit,
    MAX(c.timestamp) as last_commit,
    COUNT(DISTINCT c.author_email) as unique_authors
FROM repositories r
LEFT JOIN commits c ON r.id = c.repository_id
WHERE r.name LIKE '%petclinic%'
GROUP BY r.name;"

# 4. Voir les auteurs les plus actifs
docker exec -it prioritest-postgres psql -U collecte_user -d collecte_db -c "
SELECT 
    author_name,
    author_email,
    COUNT(*) as commit_count
FROM commits
WHERE repository_id IN (SELECT id FROM repositories WHERE name LIKE '%petclinic%')
GROUP BY author_name, author_email
ORDER BY commit_count DESC
LIMIT 10;"
```

---

## 📝 Checklist de Test avec Données Réelles

- [ ] ✅ Test 1: Collecter commits d'un dépôt public GitHub
- [ ] ✅ Test 2: Collecter issues d'un dépôt public GitHub
- [ ] ✅ Test 3: Collecter commits d'un dépôt public GitLab
- [ ] ✅ Test 4: Recevoir un webhook GitHub réel
- [ ] ✅ Test 5: Uploader un rapport JaCoCo réel
- [ ] ✅ Test 6: Collecter un projet Java complet
- [ ] ✅ Test 7: Vérifier les données dans PostgreSQL
- [ ] ✅ Test 8: Vérifier les artefacts dans MinIO
- [ ] ✅ Test 9: Consommer les messages Kafka
- [ ] ✅ Test 10: Analyser les statistiques collectées

---

## 🚨 Problèmes Courants

### 1. Token GitHub Invalide
**Erreur**: `403 Forbidden` ou `401 Unauthorized`
**Solution**: Vérifiez que votre token GitHub est valide et a les bonnes permissions

### 2. Rate Limiting GitHub
**Erreur**: `403 API rate limit exceeded`
**Solution**: 
- Utilisez un token (augmente la limite de 60 à 5000 req/h)
- Attendez 1 heure pour la réinitialisation
- Réduisez la plage de dates

### 3. Dépôt Trop Gros
**Erreur**: Timeout ou mémoire insuffisante
**Solution**: 
- Commencez par un petit dépôt
- Réduisez la plage de dates
- Collectez par étapes (mois par mois)

### 4. Kafka Non Accessible
**Erreur**: `Failed to resolve 'kafka:9092'`
**Solution**: 
- Vérifiez que Kafka est démarré: `docker-compose ps kafka`
- Redémarrez Kafka: `docker-compose restart kafka`

---

**Prêt à collecter des vraies données ! 🚀**

