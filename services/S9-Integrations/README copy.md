# 🔄 CI/CD Integration Service

> Microservice d'intégration CI/CD pour l'analyse automatique des risques et la priorisation des tests.

## 🎯 Objectif

Analyser automatiquement les Pull Requests/Merge Requests pour :
- Évaluer le risque de chaque fichier modifié via ML
- Alerter si des classes critiques sont modifiées sans tests
- Commenter la PR avec des recommandations
- Créer un Check qui peut bloquer le merge

## ✨ Fonctionnalités

| Fonctionnalité | Description |
|----------------|-------------|
| GitHub Checks API | Check Runs avec statut success/failure/warning |
| GitLab MR API | Commit Status et notes sur MR |
| Commentaires auto | Markdown détaillés sur PR/MR |
| Policy Gate | Blocage optionnel des PR à haut risque |
| Training Triggers | Re-training ML automatique |
| OpenTelemetry | Traces distribuées |
| Keycloak SSO | OAuth2/OIDC |

## 🏗️ Architecture

```
┌─────────────┐     Webhook      ┌──────────────────────────┐
│   GitHub    │ ────────────────▶│  CI/CD Integration       │
│   GitLab    │                  │  Service                 │
└─────────────┘                  │                          │
                                 │  ┌────────────────────┐  │
                                 │  │ Risk Analyzer      │──┼──▶ ML Service
                                 │  └─────────┬──────────┘  │
                                 │            ▼             │
                                 │  ┌────────────────────┐  │
                                 │  │ Policy Gate        │  │
                                 │  └─────────┬──────────┘  │
                                 │            ▼             │
                                 │  ┌────────────────────┐  │
                                 │  │ Comment Generator  │  │
                                 │  └────────────────────┘  │
                                 └──────────────────────────┘
                                            │
                              ┌─────────────┴─────────────┐
                              ▼                           ▼
                      GitHub Checks API           GitLab Status API
```

## 🚀 Démarrage Rapide

### Mode Local (Sans Docker)

```bash
mvn spring-boot:run -Dspring-boot.run.profiles=local -Dspring-boot.run.arguments=--server.port=8081
```

### Avec Docker

```bash
docker-compose -f docker-compose.dev.yml up -d
mvn spring-boot:run
```

## 📡 API Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/v1/webhooks/github` | Webhook GitHub |
| POST | `/api/v1/webhooks/gitlab` | Webhook GitLab |
| GET | `/api/v1/health/live` | Liveness probe |
| GET | `/api/v1/health/ready` | Readiness probe |
| POST | `/api/v1/training/trigger` | Déclencher entraînement ML |

## 🔗 URLs

| Service | URL |
|---------|-----|
| Swagger UI | http://localhost:8081/api/swagger-ui.html |
| Health | http://localhost:8081/api/v1/health/live |
| API Docs | http://localhost:8081/api/api-docs |
| H2 Console | http://localhost:8081/api/h2-console |

## ⚙️ Configuration

### Variables d'Environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `SPRING_PROFILES_ACTIVE` | Profil (local, dev, prod) | `dev` |
| `DATABASE_URL` | URL PostgreSQL | `jdbc:postgresql://localhost:5432/cicd_integration` |
| `GITHUB_APP_ID` | ID GitHub App | - |
| `GITHUB_WEBHOOK_SECRET` | Secret webhook | - |
| `GITLAB_TOKEN` | Token GitLab | - |
| `RISK_THRESHOLD_HIGH` | Seuil risque élevé | `0.7` |

### Profils Spring

| Profil | BDD | Cache | Auth |
|--------|-----|-------|------|
| `local` | H2 mémoire | Simple | Désactivée |
| `dev` | PostgreSQL | Redis | Keycloak |
| `prod` | PostgreSQL | Redis | Keycloak |

## 💬 Exemple de Commentaire Généré

```markdown
## 🔍 Test Prioritization Analysis

### Risk Summary
| Metric | Value |
|--------|-------|
| 🔴 High Risk | 2 |
| 🟡 Medium Risk | 1 |
| Overall Risk | **HIGH** |

### Recommendations
🚨 **ADD_TESTS**: 'UserService' needs tests (risk: 0.75)
```

## 🛠️ Technologies

- **Backend**: Java 21, Spring Boot 3.2.1, WebFlux
- **Database**: PostgreSQL 16 / H2
- **Cache**: Redis 7
- **Auth**: Keycloak 23 (OAuth2)
- **Observability**: OpenTelemetry, Prometheus
- **Docs**: SpringDoc OpenAPI 3

## 📁 Structure

```
cicd-integration-service/
├── src/main/java/com/testprioritization/
│   ├── config/           # Configuration (Security, OpenAPI, WebClient)
│   ├── controller/       # REST Controllers (Webhooks, Training, Health)
│   ├── service/          # Business Logic (Risk, Policy, Comments)
│   └── model/            # DTOs (Webhook, Response)
├── docs/                 # Diagrammes UML et BPMN
├── kubernetes/           # Manifests K8s
├── docker-compose.yml    # Stack Docker complet
└── pom.xml               # Dépendances Maven
```

## 📊 Diagrammes

Tous les diagrammes UML et BPMN sont disponibles dans le dossier `docs/` :

| Diagramme | Description |
|-----------|-------------|
| [Use Case](docs/use-case-diagram.puml) | Cas d'utilisation et acteurs |
| [Class](docs/class-diagram-detailed.puml) | Structure des classes |
| [Sequence](docs/sequence-diagram.puml) | Flux de traitement webhook |
| [Activity](docs/activity-diagram.puml) | Processus d'analyse |
| [Component](docs/component-diagram.puml) | Architecture en composants |
| [Deployment](docs/deployment-diagram.puml) | Déploiement Kubernetes |
| [BPMN](docs/bpmn-webhook-process.bpmn) | Processus métier BPMN 2.0 |

**Visualiser** : Ouvrir les fichiers `.puml` dans VS Code avec l'extension PlantUML ou sur https://www.plantuml.com/plantuml

## 👤 Auteur

**Oussama Boujdig** - Service 9 : Intégrations & Ops

