# Guide de Test Manuel des Endpoints S1 dans Swagger

**URL Swagger**: http://localhost:8001/docs

## Instructions Générales

1. Ouvrez http://localhost:8001/docs dans votre navigateur
2. Cliquez sur un endpoint pour le déplier
3. Cliquez sur le bouton **"Try it out"**
4. Remplissez les paramètres/body requis
5. Cliquez sur **"Execute"**
6. Vérifiez la réponse en bas (Code, Response body)

---

## Test 1/8: GET /health ✅

**Endpoint**: `GET /health`  
**Description**: Vérifier l'état de santé du service

### Étapes:
1. Cliquez sur `GET /health`
2. Cliquez sur "Try it out"
3. Cliquez sur "Execute"

### Résultat attendu:
- **Code**: 200
- **Response**:
```json
{
  "status": "healthy",
  "service": "CollecteDepots",
  "version": "1.0.0"
}
```

---

## Test 2/8: GET /api/v1/collect/status ✅

**Endpoint**: `GET /api/v1/collect/status`  
**Description**: Obtenir le statut des services de collecte

### Étapes:
1. Cliquez sur `GET /api/v1/collect/status`
2. Cliquez sur "Try it out"
3. Cliquez sur "Execute"

### Résultat attendu:
- **Code**: 200
- **Response**:
```json
{
  "status": "operational",
  "services": {
    "github": false,
    "gitlab": false,
    "jira": false,
    "kafka": true,
    "database": true,
    "minio": true
  }
}
```

---

## Test 3/8: GET /api/v1/artifacts/{repository_id}/{commit_sha} ✅

**Endpoint**: `GET /api/v1/artifacts/{repository_id}/{commit_sha}`  
**Description**: Récupérer les artefacts pour un commit

### Étapes:
1. Cliquez sur `GET /api/v1/artifacts/{repository_id}/{commit_sha}`
2. Cliquez sur "Try it out"
3. Remplissez:
   - `repository_id`: `test_repo`
   - `commit_sha`: `abc123`
4. Cliquez sur "Execute"

### Résultat attendu:
- **Code**: 404 (normal - pas de données)
- **Response**:
```json
{
  "detail": "No artifacts found"
}
```

---

## Test 4/8: POST /api/v1/webhooks/jira ✅

**Endpoint**: `POST /api/v1/webhooks/jira`  
**Description**: Recevoir un webhook Jira

### Étapes:
1. Cliquez sur `POST /api/v1/webhooks/jira`
2. Cliquez sur "Try it out"
3. Remplacez le body par:
```json
{
  "webhookEvent": "jira:issue_created",
  "issue": {
    "key": "TEST-1",
    "fields": {
      "summary": "Test issue from Swagger",
      "issuetype": {
        "name": "Bug"
      },
      "status": {
        "name": "Open"
      },
      "created": "2025-12-13T00:00:00.000+0000"
    }
  }
}
```
4. Cliquez sur "Execute"

### Résultat attendu:
- **Code**: 200
- **Response**: `OK`

---

## Test 5/8: POST /api/v1/webhooks/github ✅

**Endpoint**: `POST /api/v1/webhooks/github`  
**Description**: Recevoir un webhook GitHub

### Étapes:
1. Cliquez sur `POST /api/v1/webhooks/github`
2. Cliquez sur "Try it out"
3. Remplissez les headers:
   - `X-GitHub-Event`: `push`
4. Remplacez le body par:
```json
{
  "ref": "refs/heads/main",
  "repository": {
    "id": 12345,
    "name": "test-repo",
    "full_name": "user/test-repo",
    "url": "https://github.com/user/test-repo"
  },
  "commits": [
    {
      "id": "abc123def456",
      "message": "Test commit from Swagger",
      "author": {
        "email": "test@example.com",
        "name": "Test User"
      },
      "timestamp": "2025-12-13T00:00:00Z",
      "added": ["test.java"],
      "modified": [],
      "removed": []
    }
  ]
}
```
5. Cliquez sur "Execute"

### Résultat attendu:
- **Code**: 200
- **Response**: `OK`

---

## Test 6/8: POST /api/v1/webhooks/gitlab ✅

**Endpoint**: `POST /api/v1/webhooks/gitlab`  
**Description**: Recevoir un webhook GitLab

### Étapes:
1. Cliquez sur `POST /api/v1/webhooks/gitlab`
2. Cliquez sur "Try it out"
3. Remplissez les headers:
   - `X-Gitlab-Event`: `Push Hook`
4. Remplacez le body par:
```json
{
  "object_kind": "push",
  "project": {
    "id": 12345,
    "name": "test-repo",
    "path_with_namespace": "user/test-repo"
  },
  "commits": [
    {
      "id": "abc123def456",
      "message": "Test commit from Swagger",
      "author": {
        "email": "test@example.com",
        "name": "Test User"
      },
      "timestamp": "2025-12-13T00:00:00Z",
      "added": ["test.java"],
      "modified": [],
      "removed": []
    }
  ]
}
```
5. Cliquez sur "Execute"

### Résultat attendu:
- **Code**: 200
- **Response**: `OK`

---

## Test 7/8: POST /api/v1/collect ⚠️

**Endpoint**: `POST /api/v1/collect`  
**Description**: Déclencher une collecte manuelle de données

### Étapes:
1. Cliquez sur `POST /api/v1/collect`
2. Cliquez sur "Try it out"
3. Remplacez le body par:
```json
{
  "repository_url": "https://github.com/octocat/Hello-World",
  "collect_type": "commits",
  "date_range": {
    "start": "2025-01-01",
    "end": "2025-12-13"
  }
}
```
4. Cliquez sur "Execute"

### Résultat attendu:
- **Code**: 202 (Accepted)
- **Response**:
```json
{
  "status": "accepted",
  "message": "Collection started in background",
  "repository_url": "https://github.com/octocat/Hello-World",
  "collect_types": ["commits"]
}
```

⚠️ **Note**: Ce test peut prendre du temps ou timeout car l'opération est longue (traitement en background).

---

## Test 8/8: POST /api/v1/artifacts/upload/{artifact_type} ⚠️

**Endpoint**: `POST /api/v1/artifacts/upload/{artifact_type}`  
**Description**: Uploader un artefact CI/CD

### Étapes:
1. Cliquez sur `POST /api/v1/artifacts/upload/{artifact_type}`
2. Cliquez sur "Try it out"
3. Remplissez:
   - `artifact_type`: `jacoco`
   - `repository_id`: `test_repo`
   - `commit_sha`: `abc123`
   - `build_id`: `build_1`
   - `file`: (Sélectionnez un fichier XML de test)
4. Cliquez sur "Execute"

### Résultat attendu:
- **Code**: 200 (si fichier fourni)
- **Code**: 422 (si pas de fichier - validation error)

⚠️ **Note**: Ce test nécessite un fichier réel. Sans fichier, vous obtiendrez une erreur 422 (normal).

---

## Résumé des Tests

| # | Endpoint | Méthode | Status Attendu | Difficulté |
|---|----------|---------|----------------|------------|
| 1 | `/health` | GET | 200 | ✅ Facile |
| 2 | `/api/v1/collect/status` | GET | 200 | ✅ Facile |
| 3 | `/api/v1/artifacts/{repo_id}/{sha}` | GET | 404 | ✅ Facile |
| 4 | `/api/v1/webhooks/jira` | POST | 200 | ✅ Moyen |
| 5 | `/api/v1/webhooks/github` | POST | 200 | ✅ Moyen |
| 6 | `/api/v1/webhooks/gitlab` | POST | 200 | ✅ Moyen |
| 7 | `/api/v1/collect` | POST | 202 | ⚠️ Long |
| 8 | `/api/v1/artifacts/upload/{type}` | POST | 200/422 | ⚠️ Fichier requis |

---

## Conseils

1. **Commencez par les tests faciles** (1-3) pour vous familiariser avec Swagger
2. **Les webhooks** (4-6) nécessitent des JSON valides - copiez-collez les exemples
3. **Le collect** (7) peut timeout - c'est normal, il traite en background
4. **L'upload** (8) nécessite un fichier réel - créez un fichier XML vide pour tester

## Vérification dans les Logs

Pour vérifier que les webhooks sont bien traités:

```powershell
docker-compose logs --tail=20 collecte-depots | Select-String -Pattern "Processed|Published|Stored"
```

Vous devriez voir des messages comme:
- `Published commit event evt_webhook_...`
- `Stored commit abc123`
- `Processed commit event evt_...`

---

## Problèmes Courants

### Timeout sur les webhooks
- **Cause**: Kafka non accessible
- **Solution**: Normal, les webhooks sont traités en background. Vérifiez les logs.

### 422 Validation Error
- **Cause**: JSON invalide ou champs manquants
- **Solution**: Vérifiez que le JSON est bien formaté et contient tous les champs requis.

### 404 Not Found
- **Cause**: Ressource n'existe pas (normal pour le test des artifacts)
- **Solution**: C'est le comportement attendu si aucune donnée n'a été collectée.

---

**Bonne chance avec vos tests ! 🎉**

