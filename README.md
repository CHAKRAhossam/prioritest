# PRIORITEST - Plateforme de Priorisation Intelligente des Tests

<div align="center">

![PRIORITEST](https://img.shields.io/badge/PRIORITEST-v1.0.0-blue)
![Microservices](https://img.shields.io/badge/Architecture-Microservices-green)
![Docker](https://img.shields.io/badge/Deployment-Docker-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Une plateforme intelligente pour prioriser les tests basée sur l'analyse statique, le machine learning et l'historique des tests**

[🚀 Démarrage Rapide](#-démarrage-rapide) • [📋 Documentation](#-documentation) • [🏗️ Architecture](#️-architecture) • [🎥 Démo Vidéo](#-démo-vidéo)

</div>

---

## 📖 À Propos

PRIORITEST est une plateforme microservices avancée qui automatise la priorisation des tests logiciels en combinant :
- **Analyse statique du code** (métriques CK, complexité cyclomatique)
- **Machine Learning** (prédiction des risques de défauts)
- **Historique des tests** (couverture, flakiness, résultats passés)
- **Optimisation multi-objectifs** (effort, couverture, risque)

La plateforme analyse automatiquement vos dépôts Git, génère des prédictions ML, et crée un plan de tests priorisé optimisé pour maximiser la détection de défauts avec un budget d'effort limité.

---

## 🎥 Démo Vidéo

<div align="center">

### 🎬 Vidéo de Démonstration Complète

<div align="center">

[![Vidéo de Démonstration PRIORITEST](https://img.shields.io/badge/▶️-Regarder_la_Démo-red?style=for-the-badge&logo=youtube)](https://youtube.com/watch?v=VIDEO_ID)

📹 **Vidéo de démonstration disponible sur YouTube**

*Cliquez sur le badge ci-dessus pour regarder la démonstration complète*

**Langue :** Français | **Durée :** ~15 minutes

> 💡 **Note :** Pour ajouter la vidéo, uploader `docs/DEMO.mp4` sur YouTube et remplacer `VIDEO_ID` ci-dessus par l'ID de votre vidéo YouTube.

</div>

**Contenu de la démo :**
- 🚀 Démarrage et configuration
- 📦 Ajout d'un dépôt GitHub
- 🔄 Exécution du pipeline complet (S1 → S2 → S4 → S5 → S6)
- 📊 Visualisation des résultats de priorisation
- 🎯 Utilisation des différentes stratégies de priorisation
- 📈 Analyse des métriques et rapports

> 💡 **Note :** Si la vidéo ne s'affiche pas directement, vous pouvez [la télécharger ici](docs/DEMO.mp4)

</div>

---

## ✨ Fonctionnalités Principales

### 🔍 Collecte et Analyse
- **Collecte automatique** : Commits, issues, artefacts CI/CD depuis GitHub/GitLab
- **Analyse statique** : Métriques CK, complexité, dépendances
- **Historique des tests** : Suivi de la couverture, flakiness, résultats

### 🤖 Machine Learning
- **Prédiction de risques** : Modèles ML pour identifier les classes à haut risque
- **Feature engineering** : Préparation automatique des features
- **Entraînement continu** : Amélioration des modèles avec nouvelles données

### 🎯 Priorisation Intelligente
- **Stratégies multiples** : POPT@20, Top-K, Optimisation budgétaire
- **Effort-aware** : Prise en compte du temps de test estimé
- **Criticité des modules** : Pondération par importance métier

### 📊 Dashboard Interactif
- **Visualisation en temps réel** : Graphiques, métriques, recommandations
- **Gestion des dépôts** : Ajout, suivi, historique
- **Rapports détaillés** : Export CSV, analyse de tendances

---

## 🏗️ Architecture

PRIORITEST suit une architecture microservices avec 9 services principaux :

```
┌─────────────────────────────────────────────────────────────┐
│                    S0 - API Gateway                         │
│              (Spring Cloud Gateway - Port 8090)             │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                     │
┌───────▼──────┐  ┌────────▼────────┐  ┌─────────▼─────────┐
│ S1 - Collecte │  │ S2 - Analyse   │  │ S3 - Historique    │
│   Depots      │  │  Statique      │  │    Tests           │
│  (FastAPI)    │  │  (Spring Boot) │  │  (Spring Boot)     │
│   Port 8001   │  │   Port 8081    │  │   Port 8082        │
└───────┬───────┘  └────────┬───────┘  └─────────┬─────────┘
        │                   │                     │
        │         ┌─────────▼─────────┐           │
        │         │     Kafka         │           │
        │         │  (Event Streaming)│           │
        │         └─────────┬─────────┘           │
        │                   │                     │
┌───────▼──────┐  ┌─────────▼─────────┐  ┌───────▼──────────┐
│ S4 - Features│  │ S5 - ML Service   │  │ S6 - Priorisation│
│ Preprocessing│  │   (FastAPI)       │  │    (FastAPI)     │
│  Port 8000   │  │   Port 8001       │  │   Port 8006      │
└───────┬───────┘  └─────────┬─────────┘  └───────┬─────────┘
        │                   │                     │
        └───────────────────┼─────────────────────┘
                            │
                    ┌───────▼────────┐
                    │ S7 - Test      │
                    │  Scaffolder    │
                    │  (FastAPI)     │
                    │  Port 8007     │
                    └────────────────┘
```

### Services Détaillés

| Service | Technologie | Port | Description |
|---------|------------|------|-------------|
| **S0 - API Gateway** | Spring Cloud Gateway | 8090 | Point d'entrée unique, routage, CORS |
| **S1 - CollecteDepots** | FastAPI (Python) | 8001 | Collecte Git/GitHub/GitLab, webhooks |
| **S2 - AnalyseStatique** | Spring Boot (Java) | 8081 | Métriques CK, complexité, dépendances |
| **S3 - HistoriqueTests** | Spring Boot (Java) | 8082 | Couverture, flakiness, résultats tests |
| **S4 - PretraitementFeatures** | FastAPI (Python) | 8000 | Feature engineering, préparation données |
| **S5 - MLService** | FastAPI (Python) | 8001 | Modèles ML, prédictions de risques |
| **S6 - MoteurPriorisation** | FastAPI (Python) | 8006 | Optimisation, stratégies de priorisation |
| **S7 - TestScaffolder** | FastAPI (Python) | 8007 | Génération automatique de tests JUnit |
| **S8 - DashboardQualite** | React + Vite | 3000 | Interface utilisateur, visualisations |
| **S9 - Integrations** | Spring Boot (Java) | 8009 | Intégrations externes (Jira, etc.) |

### Infrastructure

- **PostgreSQL + TimescaleDB** : Base de données principale (métriques temporelles)
- **Kafka + Zookeeper** : Streaming d'événements entre services
- **MinIO** : Stockage d'artefacts CI/CD (compatible S3)
- **Redis** : Cache et sessions
- **Eureka** : Service discovery
- **MLflow** : Gestion des modèles ML et expérimentations
- **SonarQube** : Analyse de qualité de code
- **Jenkins** : CI/CD

---

## 🚀 Démarrage Rapide

### Prérequis

- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Git**
- **8 GB RAM minimum** (recommandé: 16 GB)
- **Ports disponibles** : 3000, 8000-8009, 8080-8083, 8090, 8761, 9000, 9092

### Installation

1. **Cloner le dépôt**
   ```bash
   # Depuis GitLab
   git clone https://gitlab.com/chakrahossam-group/prioritest.git
   
   # Ou depuis GitHub
   git clone https://github.com/CHAKRAhossam/prioritest.git
   
   cd prioritest
   ```

2. **Configurer les variables d'environnement** (optionnel)
   ```bash
   cp .env.example .env
   # Éditer .env avec vos tokens GitHub/GitLab/Jira
   ```

3. **Lancer tous les services**
   ```bash
   docker-compose up -d --build
   ```

4. **Vérifier le statut des services**
   ```bash
   # Windows PowerShell
   .\scripts\check-pipeline-status.ps1
   
   # Linux/Mac
   ./scripts/health-check.sh
   ```

5. **Accéder au dashboard**
   ```
   http://localhost:3000
   ```

### Vérification de l'Installation

```bash
# Vérifier que tous les conteneurs sont en cours d'exécution
docker ps --filter "name=prioritest"

# Vérifier les health checks
curl http://localhost:8090/actuator/health
curl http://localhost:8001/health
curl http://localhost:8006/health
```

---

## 📋 Utilisation

### 1. Ajouter un Dépôt

1. Ouvrir le dashboard : `http://localhost:3000`
2. Cliquer sur **"Add Repository"**
3. Entrer l'URL du dépôt GitHub/GitLab
4. Le pipeline complet démarre automatiquement

### 2. Pipeline d'Analyse

Le pipeline s'exécute automatiquement dans cet ordre :

```
S1 (Collecte)
  ↓ Collecte commits/issues → Publie sur Kafka
S2 (Analyse Statique)
  ↓ Traite les événements Kafka → Calcule métriques
S4 (Prétraitement)
  ↓ Prépare les features
S5 (ML)
  ↓ Génère prédictions de risques
S6 (Priorisation)
  ↓ Crée plan de tests priorisé
```

**Durée estimée** : 2-5 minutes selon la taille du dépôt

### 3. Visualiser les Résultats

- **Recommandations** : Liste priorisée des classes à tester
- **Métriques** : POPT@20, couverture estimée, effort total
- **Graphiques** : Tendances, distribution des risques
- **Export** : Télécharger en CSV

### 4. Stratégies de Priorisation

- **maximize_popt20** : Optimise POPT@20 (détection max de défauts)
- **top_k_coverage** : Top K classes avec meilleur ratio effort/couverture
- **budget_optimization** : Maximise couverture dans un budget d'heures
- **coverage_optimization** : Atteint un objectif de couverture
- **multi_objective** : Optimise plusieurs objectifs simultanément

---

## 🔧 Configuration

### Variables d'Environnement

Créer un fichier `.env` à la racine :

```env
# GitHub
GITHUB_TOKEN=your_github_token_here

# GitLab
GITLAB_TOKEN=your_gitlab_token_here

# Jira
JIRA_URL=https://your-jira.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your_jira_token

# Database
DATABASE_URL=postgresql://prioritest:prioritest@postgres:5432/prioritest

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

### Ports Personnalisés

Modifier `docker-compose.yml` pour changer les ports :

```yaml
ports:
  - "3000:8080"  # Dashboard (host:container)
```

---

## 📡 API Documentation

### Endpoints Principaux

#### S1 - Collecte de Dépôts

```bash
# Ajouter un dépôt et lancer l'analyse complète
POST /api/s1/collect/analyze-full
{
  "repository_url": "https://github.com/org/repo",
  "collect_type": "commits|issues|ci_reports"
}

# Lister les dépôts
GET /api/s1/collect/repositories

# Obtenir les branches
GET /api/s1/collect/branches?repository_url=https://github.com/org/repo
```

#### S6 - Priorisation

```bash
# Créer une priorisation
POST /api/s6/prioritize?strategy=maximize_popt20
{
  "repository_id": "github_org_repo",
  "branch": "main",
  "constraints": {
    "budget_hours": 40,
    "target_coverage": 0.85
  }
}

# Obtenir une priorisation existante
GET /api/s6/prioritize/{repository_id}?strategy=maximize_popt20
```

### Documentation Swagger

- **API Gateway** : http://localhost:8090/swagger-ui.html
- **S1** : http://localhost:8001/docs
- **S4** : http://localhost:8000/docs
- **S5** : http://localhost:8001/docs
- **S6** : http://localhost:8006/docs
- **S7** : http://localhost:8007/docs

---

## 📊 Monitoring

### Vérifier le Statut des Services

```bash
# Script PowerShell (Windows)
.\scripts\check-pipeline-status.ps1

# Script Bash (Linux/Mac)
./scripts/health-check.sh
```

### Surveiller le Pipeline

```bash
# Suivre les logs de S1 (orchestration)
docker logs prioritest-collecte-depots -f

# Suivre tous les services
docker-compose logs -f

# Surveiller un dépôt spécifique
.\scripts\monitor-pipeline.ps1 -RepositoryId 'github_org_repo' -Follow
```

### Health Checks

- **API Gateway** : http://localhost:8090/actuator/health
- **S1** : http://localhost:8001/health
- **S2** : http://localhost:8081/actuator/health
- **S3** : http://localhost:8082/actuator/health
- **S4** : http://localhost:8000/health
- **S5** : http://localhost:8001/health
- **S6** : http://localhost:8006/health
- **S7** : http://localhost:8007/health

### Logs

```bash
# Logs d'un service spécifique
docker logs prioritest-collecte-depots --tail=100 -f

# Logs de tous les services
docker-compose logs -f

# Logs filtrés par pattern
docker logs prioritest-collecte-depots | grep "Starting full analysis"
```

---

## 🛠️ Développement

### Structure du Projet

```
prioritest/
├── services/              # Services microservices
│   ├── S0-ApiGateway/     # API Gateway
│   ├── S1-CollecteDepots/ # Collecte
│   ├── S2-AnalyseStatique/# Analyse statique
│   ├── S3-HistoriqueTests/# Historique
│   ├── S4-PretraitementFeatures/ # Features
│   ├── S5-MLService/      # ML
│   ├── S6-MoteurPriorisation/ # Priorisation
│   ├── S7-TestScaffolder/ # Génération tests
│   └── S8-DashboardQualite/ # Frontend
├── infrastructure/        # Services infrastructure
│   ├── discovery-server/  # Eureka
│   ├── mlflow/           # MLflow
│   └── jenkins/          # Jenkins
├── scripts/              # Scripts utilitaires
├── docker-compose.yml    # Configuration Docker
└── README.md            # Ce fichier
```

### Lancer en Mode Développement

```bash
# Rebuild et restart un service spécifique
docker-compose up -d --build s1-collecte-depots

# Voir les logs en temps réel
docker-compose logs -f s1-collecte-depots

# Accéder au shell d'un conteneur
docker exec -it prioritest-collecte-depots /bin/bash
```

### Tests

```bash
# Tests Python (S1, S4, S5, S6, S7)
cd services/S1-CollecteDepots
pytest

# Tests Java (S0, S2, S3, S9)
cd services/S0-ApiGateway
mvn test
```

---

## 🐛 Dépannage

### Services Ne Démarrant Pas

```bash
# Vérifier les logs
docker-compose logs service-name

# Redémarrer un service
docker-compose restart service-name

# Rebuild un service
docker-compose up -d --build service-name
```

### Problèmes de Connexion

- **Vérifier les ports** : `netstat -an | findstr "8001 8090"`
- **Vérifier les conteneurs** : `docker ps`
- **Vérifier les réseaux** : `docker network ls`

### Erreurs Kafka

```bash
# Redémarrer Kafka
docker-compose restart kafka zookeeper

# Vérifier les topics
docker exec -it prioritest-kafka kafka-topics --list --bootstrap-server localhost:9092
```

### Erreurs de Base de Données

```bash
# Vérifier la connexion
docker exec -it prioritest-postgres psql -U prioritest -d prioritest

# Réinitialiser la base (ATTENTION: supprime les données)
docker-compose down -v
docker-compose up -d postgres
```

---

## 📚 Documentation Complémentaire

- [Guide de Monitoring](PIPELINE-MONITORING.md) : Comment surveiller le pipeline
- [Architecture Détaillée](docs/ARCHITECTURE.md) : Détails techniques
- [Guide API](docs/API.md) : Documentation complète de l'API
- [Guide de Contribution](CONTRIBUTING.md) : Comment contribuer

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour plus de détails.

---

## 📄 Licence

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus d'informations.

---

## 👥 Équipe

- **Hossam Chakra**
- **Haytam Ta**
- **Hicham Kaou**
- **Ilyas Michich**
- **Oussama Boujdig**

### Liens du Projet

- **GitLab** : https://gitlab.com/chakrahossam-group/prioritest
- **GitHub** : https://github.com/CHAKRAhossam/prioritest
- **Jira** : https://prioritest.atlassian.net/browse/MTP
- **Board Scrum** : https://prioritest.atlassian.net/jira/software/projects/MTP/boards/134

---

## 🙏 Remerciements

- Spring Cloud pour l'infrastructure microservices
- FastAPI pour les APIs Python
- React pour le frontend
- Tous les contributeurs open-source

---

<div align="center">

**Fait avec ❤️ par l'équipe PRIORITEST**

[⭐ Star sur GitHub](https://github.com/CHAKRAhossam/prioritest) • [🔗 GitLab](https://gitlab.com/chakrahossam-group/prioritest) • [📋 Jira](https://prioritest.atlassian.net/browse/MTP)

</div>
