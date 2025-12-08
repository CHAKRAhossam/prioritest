# 🧪 Guide de Test de l'API Historique Tests

Ce dossier contient des fichiers de test et des scripts pour valider tous les endpoints de l'API.

## 📁 Fichiers inclus

### Fichiers de données XML :
- `jacoco-sample.xml` - Rapport de couverture JaCoCo
- `surefire-sample.xml` - Rapport de tests Surefire
- `pit-sample.xml` - Rapport de mutations PIT

### Scripts de test :
- `test-simple.sh` - Test rapide des endpoints principaux (⚡ recommandé pour débuter)
- `test-all-endpoints.sh` - Test complet de tous les endpoints

## 🚀 Utilisation

### Option 1 : Test Rapide (Recommandé)

```bash
cd test-data
chmod +x test-simple.sh
./test-simple.sh
```

### Option 2 : Test Complet

```bash
cd test-data
chmod +x test-all-endpoints.sh
./test-all-endpoints.sh
```

### Option 3 : Tests manuels avec curl

#### 1. Upload JaCoCo Report

```bash
curl -X POST 'http://localhost:8080/api/coverage/jacoco' \
  -F 'file=@jacoco-sample.xml' \
  -F 'commit=abc123' \
  -F 'buildId=build001' \
  -F 'branch=main'
```

#### 2. Upload Surefire Report

```bash
curl -X POST 'http://localhost:8080/api/tests/surefire' \
  -F 'file=@surefire-sample.xml' \
  -F 'commit=abc123' \
  -F 'buildId=build001' \
  -F 'branch=main'
```

#### 3. Upload PIT Mutations Report

```bash
curl -X POST 'http://localhost:8080/api/coverage/pit' \
  -F 'file=@pit-sample.xml' \
  -F 'commit=abc123'
```

#### 4. Get Coverage Summary

```bash
curl -X GET 'http://localhost:8080/api/coverage/commit/abc123'
```

#### 5. Get Test Summary

```bash
curl -X GET 'http://localhost:8080/api/tests/commit/abc123'
```

#### 6. Get Aggregated Metrics

```bash
curl -X GET 'http://localhost:8080/api/metrics/commit/abc123'
```

#### 7. Get Low Coverage Classes

```bash
curl -X GET 'http://localhost:8080/api/coverage/low-coverage?threshold=80'
```

#### 8. Get Failed Tests

```bash
curl -X GET 'http://localhost:8080/api/tests/failed/abc123'
```

#### 9. Calculate Flakiness

```bash
curl -X POST 'http://localhost:8080/api/flakiness/calculate'
```

#### 10. Get Most Flaky Tests

```bash
curl -X GET 'http://localhost:8080/api/flakiness/most-flaky?limit=10'
```

#### 11. Calculate Test Debt

```bash
curl -X POST 'http://localhost:8080/api/debt/calculate/abc123'
```

#### 12. Get High Debt Classes

```bash
curl -X GET 'http://localhost:8080/api/debt/high-debt?threshold=5.0'
```

## 🌐 Alternative : Test avec Swagger UI

Ouvre ton navigateur et va sur :
```
http://localhost:8080/swagger-ui.html
```

1. Clique sur un endpoint (ex: `POST /api/coverage/jacoco`)
2. Clique sur **"Try it out"**
3. Upload le fichier XML correspondant
4. Remplis les paramètres requis
5. Clique sur **"Execute"**

## 📊 Workflow de Test Complet

Pour tester un cycle complet de CI/CD :

```bash
# 1. Définir un commit SHA
COMMIT="test-$(date +%s)"

# 2. Upload tous les rapports
curl -X POST 'http://localhost:8080/api/coverage/jacoco' \
  -F "file=@jacoco-sample.xml" \
  -F "commit=$COMMIT" \
  -F "branch=main"

curl -X POST 'http://localhost:8080/api/tests/surefire' \
  -F "file=@surefire-sample.xml" \
  -F "commit=$COMMIT" \
  -F "branch=main"

curl -X POST 'http://localhost:8080/api/coverage/pit' \
  -F "file=@pit-sample.xml" \
  -F "commit=$COMMIT"

# 3. Consulter les métriques agrégées
curl "http://localhost:8080/api/metrics/commit/$COMMIT" | jq .

# 4. Calculer la dette de test
curl -X POST "http://localhost:8080/api/debt/calculate/$COMMIT"

# 5. Consulter la dette
curl "http://localhost:8080/api/debt/commit/$COMMIT" | jq .

# 6. Calculer le flakiness
curl -X POST "http://localhost:8080/api/flakiness/calculate"

# 7. Consulter les tests flaky
curl "http://localhost:8080/api/flakiness/flaky" | jq .
```

## 🔍 Vérification dans PostgreSQL

Pour vérifier les données en base :

```bash
# Se connecter à PostgreSQL
docker exec -it historique-tests-db psql -U admin -d historique_tests

# Requêtes utiles
SELECT COUNT(*) FROM test_coverage;
SELECT COUNT(*) FROM test_results;
SELECT COUNT(*) FROM mutation_results;
SELECT * FROM test_coverage WHERE commit_sha = 'abc123';
SELECT * FROM test_results WHERE commit_sha = 'abc123';
```

## 📦 Vérification dans MinIO

Pour vérifier les fichiers archivés :

1. Ouvre http://localhost:9001
2. Login : `minioadmin` / `minioadmin`
3. Browse bucket : `coverage-reports`
4. Tu devrais voir les fichiers uploadés organisés par commit

## ⚠️ Prérequis

- Docker Compose en cours d'exécution
- `jq` installé (pour formatter le JSON) : `sudo apt install jq` ou `brew install jq`
- `curl` installé

## 🐛 Troubleshooting

### Erreur "Connection refused"
```bash
# Vérifie que les services sont démarrés
docker-compose ps

# Vérifie les logs
docker-compose logs app
```

### Erreur "No such file"
```bash
# Assure-toi d'être dans le dossier test-data
cd test-data
pwd  # Doit afficher: .../historique-tests/test-data
```

### Erreur 500 lors de l'upload
```bash
# Vérifie les logs de l'application
docker-compose logs app --tail 50
```

## 📈 Résultats Attendus

Après avoir exécuté les tests, tu devrais voir :

- **Coverage** : 3 classes avec leurs métriques de couverture
- **Test Results** : 5 tests dont 1 en échec
- **Mutations** : 3 mutations (2 killed, 1 survived)
- **Mutation Score** : ~66% (2 killed sur 3 mutations)
- **Test Debt** : Calculé selon les classes non couvertes
- **Flakiness** : 0 pour l'instant (nécessite plusieurs runs)

## 🎯 Prochaines Étapes

1. **Intégrer dans ton CI/CD** : Upload automatique des rapports après chaque build
2. **Créer des dashboards** : Visualiser l'évolution des métriques
3. **Définir des seuils** : Alerter si la couverture descend sous 80%
4. **Tracker le flakiness** : Identifier les tests instables
5. **Monitor la dette** : Suivre l'évolution de la dette de test

