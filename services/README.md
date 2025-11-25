# Services

Chaque service est un microservice indépendant avec sa propre structure.

## Structure recommandée par service

```
SX-ServiceName/
├── src/              # Code source
├── tests/            # Tests unitaires et d'intégration
├── requirements.txt  # Dépendances Python
├── Dockerfile       # Image Docker
├── README.md        # Documentation du service
└── .env.example     # Variables d'environnement
```

## Services

- **S1-CollecteDepots** : Ingestion des dépôts Git/GitHub/GitLab, issues Jira, rapports CI/CD
- **S2-AnalyseStatique** : Extraction de métriques de code (LOC, complexité, CK, dépendances)
- **S3-HistoriqueTests** : Agréger couverture et résultats de tests (JaCoCo, Surefire, PIT)
- **S4-PretraitementFeatures** : Nettoyage, imputation, features dérivées (churn, auteurs, bug-fix proximity)
- **S5-MLService** : Modèles ML pour prédiction de risque de défaut (XGBoost, LightGBM, SHAP)
- **S6-MoteurPriorisation** : Transformation des scores en liste priorisée (effort-aware, OR-Tools)
- **S7-TestScaffolder** : Génération de squelettes de tests JUnit avec suggestions
- **S8-DashboardQualite** : Interface React.js pour visualiser recommandations, couverture, risques
- **S9-Integrations** : Intégration CI/CD, Docker/Kubernetes, observabilité, auth SSO

