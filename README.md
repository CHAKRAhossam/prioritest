# ML Test Prioritization

Plateforme de recommandation automatisée des classes logicielles à tester en priorité, utilisant le Machine Learning pour améliorer la couverture unitaire.

## 📋 Structure du Projet

Le projet est organisé en 9 microservices :

```
PRIORITEST/
├── services/
│   ├── S1-CollecteDepots/          # Haytam Ta
│   ├── S2-AnalyseStatique/          # Haytam Ta
│   ├── S3-HistoriqueTests/          # Oussama Boujdig
│   ├── S4-PretraitementFeatures/    # Hicham Kaou
│   ├── S5-MLService/                # Hicham Kaou
│   ├── S6-MoteurPriorisation/       # Hossam Chakra
│   ├── S7-TestScaffolder/           # Hossam Chakra
│   ├── S8-DashboardQualite/         # Ilyas Michich
│   └── S9-Integrations/             # Oussama Boujdig
├── infrastructure/
├── docs/
└── scripts/
```

## 🚀 Démarrage Rapide

### Prérequis

- Python 3.8+
- Docker & Docker Compose
- PostgreSQL
- Kafka (optionnel, via Docker)

### Installation

```bash
# Cloner le repository
git clone https://gitlab.com/chakrahossam-group/prioritest.git
cd prioritest

# Installer les dépendances
pip install -r requirements.txt

# Démarrer les services avec Docker Compose
docker-compose up -d
```

## 👥 Équipe

- **Haytam Ta** : Services 1 & 2 (CollecteDepots, AnalyseStatique)
- **Hicham Kaou** : Services 4 & 5 (PretraitementFeatures, MLService)
- **Hossam Chakra** : Services 6 & 7 (MoteurPriorisation, TestScaffolder)
- **Ilyas Michich** : Service 8 (DashboardQualite)
- **Oussama Boujdig** : Services 3 & 9 (HistoriqueTests, Integrations)

## 📚 Documentation

- `STRUCTURE_PROJET.md` : Structure détaillée du projet

## 🔗 Liens

- **GitLab** : https://gitlab.com/chakrahossam-group/prioritest
- **GitHub** : https://github.com/CHAKRAhossam/prioritest
- **Jira** : https://prioritest.atlassian.net/browse/MTP
- **Board Scrum** : https://prioritest.atlassian.net/jira/software/projects/MTP/boards/134

## 📝 License

[À définir]
