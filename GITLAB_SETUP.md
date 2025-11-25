# Configuration GitLab

## Étape 1 : Créer le projet sur GitLab

1. Allez sur votre GitLab (https://gitlab.com ou votre instance GitLab)
2. Cliquez sur "New project" ou "Nouveau projet"
3. Choisissez "Create blank project"
4. Remplissez :
   - **Project name** : `ML-Test-Prioritization` ou `prioritest`
   - **Project slug** : `ml-test-prioritization`
   - **Visibility Level** : Private (recommandé) ou Internal
5. Cliquez sur "Create project"

## Étape 2 : Connecter le repo local à GitLab

Une fois le projet créé sur GitLab, exécutez ces commandes :

```bash
# Ajouter le remote GitLab (remplacez par votre URL)
git remote add origin https://gitlab.com/votre-username/ml-test-prioritization.git

# Ou si vous utilisez SSH
git remote add origin git@gitlab.com:votre-username/ml-test-prioritization.git

# Vérifier le remote
git remote -v

# Pousser le code
git branch -M main
git push -u origin main
```

## Étape 3 : Configuration GitLab CI/CD

Le fichier `.gitlab-ci.yml` est déjà créé. Il définit :
- Stage `test` : Tests automatiques
- Stage `build` : Build des images Docker
- Stage `deploy` : Déploiement (manuel)

## Étape 4 : Variables d'environnement GitLab (optionnel)

Dans GitLab > Settings > CI/CD > Variables, ajoutez :
- `CI_REGISTRY_USER` : Votre username GitLab
- `CI_REGISTRY_PASSWORD` : Votre token GitLab

## Structure du projet

```
PRIORITEST/
├── services/              # 9 microservices
│   ├── S1-CollecteDepots/
│   ├── S2-AnalyseStatique/
│   ├── S3-HistoriqueTests/
│   ├── S4-PretraitementFeatures/
│   ├── S5-MLService/
│   ├── S6-MoteurPriorisation/
│   ├── S7-TestScaffolder/
│   ├── S8-DashboardQualite/
│   └── S9-Integrations/
├── infrastructure/        # Configurations infrastructure
├── docs/                  # Documentation
├── scripts/               # Scripts utilitaires
├── docker-compose.yml     # Services Docker
├── .gitlab-ci.yml         # Pipeline CI/CD
└── README.md             # Documentation principale
```

## Prochaines étapes

1. Chaque membre de l'équipe peut cloner le repo
2. Créer une branche pour chaque service
3. Développer dans le dossier correspondant
4. Créer des merge requests pour intégrer le code

