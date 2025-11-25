# Structure du Projet ML Test Prioritization

## 📁 Organisation des dossiers

```
PRIORITEST/
│
├── services/                          # Microservices (9 services)
│   ├── S1-CollecteDepots/            # Haytam Ta
│   │   ├── src/
│   │   ├── tests/
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── README.md
│   │
│   ├── S2-AnalyseStatique/           # Haytam Ta
│   ├── S3-HistoriqueTests/           # Oussama Boujdig
│   ├── S4-PretraitementFeatures/     # Hicham Kaou
│   ├── S5-MLService/                  # Hicham Kaou
│   ├── S6-MoteurPriorisation/        # Hossam Chakra
│   ├── S7-TestScaffolder/            # Hossam Chakra
│   ├── S8-DashboardQualite/          # Ilyas Michich
│   └── S9-Integrations/              # Oussama Boujdig
│
├── infrastructure/                    # Configurations infrastructure
│   ├── docker/
│   │   ├── init-scripts/
│   │   └── prometheus.yml
│   └── kubernetes/
│
├── docs/                              # Documentation
│   ├── architecture/
│   ├── api/
│   └── deployment/
│
├── scripts/                           # Scripts utilitaires
│   ├── setup.sh
│   └── deploy.sh
│
├── docker-compose.yml                 # Services Docker locaux
├── .gitlab-ci.yml                     # Pipeline CI/CD GitLab
├── .gitignore
├── requirements.txt                   # Dépendances Python globales
└── README.md                          # Documentation principale
```

## 🎯 Structure recommandée par service

Chaque service devrait avoir cette structure :

```
SX-ServiceName/
├── src/                    # Code source
│   ├── main.py            # Point d'entrée
│   ├── api/               # Endpoints API
│   ├── models/            # Modèles de données
│   ├── services/          # Logique métier
│   └── utils/             # Utilitaires
│
├── tests/                  # Tests
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── requirements.txt        # Dépendances Python du service
├── Dockerfile             # Image Docker
├── .env.example           # Exemple de variables d'environnement
├── README.md              # Documentation du service
└── .gitignore            # Fichiers à ignorer
```

## 🚀 Commandes utiles

### Initialiser un nouveau service

```bash
cd services/SX-ServiceName
mkdir -p src tests
touch src/main.py requirements.txt Dockerfile README.md
```

### Démarrer l'infrastructure

```bash
docker-compose up -d
```

### Vérifier les services

```bash
docker-compose ps
```

## 📝 Prochaines étapes

1. Chaque membre crée sa branche GitLab
2. Développe son service dans le dossier correspondant
3. Crée des merge requests pour intégrer le code

