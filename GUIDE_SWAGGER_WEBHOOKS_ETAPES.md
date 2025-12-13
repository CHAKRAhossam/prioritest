# 📖 Guide Étape par Étape - Tester les Webhooks dans Swagger

## ✅ Service S1 Mis à Jour !

**Bonne nouvelle**: J'ai ajouté les modèles Pydantic aux webhooks. Maintenant le **Request body** s'affiche dans Swagger ! 🎉

---

## 🚀 Étapes Détaillées pour Tester

### 📍 Étape 0: Ouvrir Swagger

1. **Ouvrez votre navigateur**
2. **Allez sur**: http://localhost:8001/docs
3. Vous verrez la page Swagger UI

---

## 🔵 TEST 1: GitHub Webhook

### Étapes:

**1. Trouvez la section "Webhooks"** (au milieu de la page)

**2. Cliquez sur** `POST /api/v1/webhooks/github` (la ligne entière)
   - La section va s'ouvrir et afficher les détails

**3. Cliquez sur le bouton bleu** `Try it out` (en haut à droite)
   - Les champs deviennent éditables

**4. Remplissez le header:**
   - Dans le champ `x-github-event`, tapez: **`push`**
   - Laissez `X-Hub-Signature-256` vide

**5. Scrollez vers le bas jusqu'à "Request body"**
   - Vous devriez voir une grande zone de texte avec un exemple JSON

**6. Supprimez tout le JSON et copiez-collez ceci:**

```json
{
  "ref": "refs/heads/main",
  "before": "0000000000000000000000000000000000000000",
  "after": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
  "repository": {
    "id": 123456789,
    "name": "mon-projet-java",
    "full_name": "monequipe/mon-projet-java",
    "url": "https://github.com/monequipe/mon-projet-java",
    "description": "Application Spring Boot"
  },
  "pusher": {
    "name": "jean-dupont",
    "email": "jean.dupont@example.com"
  },
  "commits": [
    {
      "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
      "tree_id": "b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1",
      "message": "feat: Ajout authentification OAuth2",
      "timestamp": "2025-12-13T14:30:00+01:00",
      "url": "https://github.com/monequipe/mon-projet-java/commit/a1b2c3d4",
      "author": {
        "name": "Jean Dupont",
        "email": "jean.dupont@example.com",
        "username": "jean-dupont"
      },
      "committer": {
        "name": "Jean Dupont",
        "email": "jean.dupont@example.com"
      },
      "added": [
        "src/main/java/com/example/auth/OAuth2Service.java",
        "src/main/java/com/example/auth/OAuth2Controller.java"
      ],
      "removed": [],
      "modified": [
        "pom.xml",
        "src/main/resources/application.properties"
      ]
    }
  ]
}
```

**7. Scrollez tout en bas et cliquez sur le gros bouton bleu** `Execute`

**8. Attendez 2-5 secondes**

**9. Scrollez vers le bas pour voir la réponse**

### ✅ Résultat Attendu:

```
Server response
Code: 200
Response body: "OK"
```

---

## 📊 Vérification des Données

**Dans PowerShell, copiez-collez:**

```powershell
docker exec prioritest-postgres psql -U prioritest -d prioritest -c "SELECT commit_sha, LEFT(commit_message, 50) as message, author_name FROM commits ORDER BY created_at DESC LIMIT 3;"
```

Vous devriez voir votre nouveau commit avec le message **"feat: Ajout authentification OAuth2"** ! 🎉

---

## 🟠 TEST 2: GitLab Webhook

### Étapes:

**1. Cliquez sur** `POST /api/v1/webhooks/gitlab`

**2. Cliquez sur** `Try it out`

**3. Remplissez le header:**
   - `X-Gitlab-Event`: **`Push Hook`**

**4. Dans Request body, collez:**

```json
{
  "object_kind": "push",
  "event_name": "push",
  "before": "0000000000000000000000000000000000000000",
  "after": "c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3",
  "ref": "refs/heads/develop",
  "checkout_sha": "c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3",
  "project": {
    "id": 987654321,
    "name": "app-mobile",
    "description": "Application mobile React Native",
    "web_url": "https://gitlab.com/monentreprise/app-mobile",
    "path_with_namespace": "monentreprise/app-mobile"
  },
  "commits": [
    {
      "id": "c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3",
      "message": "refactor: Optimisation performances écran accueil",
      "title": "refactor: Optimisation",
      "timestamp": "2025-12-13T15:00:00+01:00",
      "url": "https://gitlab.com/monentreprise/app-mobile/-/commit/c4d5e6f7",
      "author": {
        "name": "Marie Martin",
        "email": "marie.martin@example.com"
      },
      "added": ["src/components/HomeScreen/OptimizedList.tsx"],
      "modified": ["src/components/HomeScreen/index.tsx", "package.json"],
      "removed": []
    }
  ],
  "total_commits_count": 1
}
```

**5. Cliquez sur** `Execute`

### ✅ Résultat Attendu:
```
Code: 200
Response body: "OK"
```

---

## 🟣 TEST 3: Jira Webhook

### Étapes:

**1. Cliquez sur** `POST /api/v1/webhooks/jira`

**2. Cliquez sur** `Try it out`

**3. Dans Request body, collez:**

```json
{
  "timestamp": 1702472400000,
  "webhookEvent": "jira:issue_created",
  "issue_event_type_name": "issue_created",
  "user": {
    "accountId": "123abc456def",
    "emailAddress": "product.owner@example.com",
    "displayName": "Sophie Durand"
  },
  "issue": {
    "id": "10001",
    "key": "MOBILE-456",
    "fields": {
      "summary": "Bug critique: Crash application Android 14",
      "description": "L'application crash au démarrage sur Android 14",
      "issuetype": {
        "id": "1",
        "name": "Bug",
        "subtask": false
      },
      "project": {
        "id": "10000",
        "key": "MOBILE",
        "name": "Application Mobile"
      },
      "priority": {
        "name": "Critical",
        "id": "1"
      },
      "status": {
        "name": "Open",
        "id": "1"
      },
      "created": "2025-12-13T15:30:00.000+0100",
      "updated": "2025-12-13T15:30:00.000+0100",
      "reporter": {
        "displayName": "Sophie Durand",
        "emailAddress": "product.owner@example.com"
      },
      "assignee": {
        "displayName": "Marie Martin",
        "emailAddress": "marie.martin@example.com"
      },
      "labels": ["urgent", "android", "crash"]
    }
  }
}
```

**4. Cliquez sur** `Execute`

### ✅ Résultat Attendu:
```
Code: 200
Response body: "OK"
```

### Vérification:

```powershell
docker exec prioritest-postgres psql -U prioritest -d prioritest -c "SELECT issue_key, LEFT(summary, 50), status FROM issues ORDER BY created_at DESC LIMIT 3;"
```

---

## 📊 Résumé Final

Après les 3 tests, vérifiez tout:

```powershell
# Statistiques complètes
docker exec prioritest-postgres psql -U prioritest -d prioritest -c "
SELECT 
    'Repositories' as type, COUNT(*) as count FROM repositories
UNION ALL
SELECT 
    'Commits' as type, COUNT(*) as count FROM commits
UNION ALL
SELECT 
    'Issues' as type, COUNT(*) as count FROM issues;
"
```

Vous devriez avoir:
- **Repositories**: 2-3
- **Commits**: 3-5 (1 initial + vos tests)
- **Issues**: 1-2

---

## 🎯 Points Clés à Retenir

### ✅ Ce qui a été corrigé:
1. **Request body maintenant visible** dans Swagger
2. **Exemples JSON automatiques** dans chaque endpoint
3. **Validation automatique** des données
4. **Documentation enrichie** avec descriptions

### 📝 Comment utiliser:
1. **Cliquez** sur l'endpoint → il s'ouvre
2. **Cliquez** sur "Try it out" → devient éditable
3. **Remplissez** headers et body
4. **Cliquez** sur "Execute" → envoie la requête
5. **Scrollez** vers le bas → voir la réponse

### 🎉 Avantage:
- Plus besoin de chercher les exemples JSON
- Swagger génère automatiquement un exemple
- Vous pouvez le modifier selon vos besoins

---

**Prêt à tester ! Ouvrez http://localhost:8001/docs et suivez ce guide ! 🚀**

