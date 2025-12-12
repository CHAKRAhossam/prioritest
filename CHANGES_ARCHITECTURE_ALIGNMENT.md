# Changements pour Alignement avec l'Architecture

## Branche
`feature/apply-architecture-specs`

## Objectif
Aligner le code existant avec les spécifications d'architecture définies dans `docs/ARCHITECTURE_COMPLETE.md`.

## Modifications par Service

### S1 - CollecteDepots ✅

#### Modèles d'événements créés
- **Fichier créé** : `services/S1-CollecteDepots/src/models/events.py`
  - `CommitEvent` : Modèle aligné avec la spécification Kafka topic `repository.commits`
  - `IssueEvent` : Modèle aligné avec la spécification Kafka topic `repository.issues`
  - `CIArtifactEvent` : Modèle aligné avec la spécification Kafka topic `ci.artifacts`
  - `FileChange` : Modèle pour les changements de fichiers
  - `Metadata` : Modèle pour les métadonnées

#### API REST alignée
- **Fichier modifié** : `services/S1-CollecteDepots/src/api/collect.py`
  - Ajout de `DateRange` model pour validation
  - Documentation mise à jour avec format JSON selon spécifications
  - Correction du parsing de `date_range`

#### Webhooks documentés
- **Fichier modifié** : `services/S1-CollecteDepots/src/api/webhooks.py`
  - Documentation ajoutée avec format JSON d'entrée selon spécifications

#### Format JSON Kafka
Les événements publiés dans Kafka correspondent maintenant exactement aux spécifications :
- `repository.commits` : Format conforme
- `repository.issues` : Format conforme
- `ci.artifacts` : Format conforme

### S2 - AnalyseStatique ✅
- [x] Format Kafka topic `code.metrics` - Ajout du champ `timestamp`
- [x] Format Feast Feature Store - Aligné avec spécifications
- [x] Extraction métriques (CK, complexité, smells) - Déjà conforme

### S3 - HistoriqueTests ✅
- [x] Format REST API - Déjà bien documenté et conforme
- [x] Format TimescaleDB - Hypertables configurées
- [x] Parsers JaCoCo/Surefire/PIT - Implémentés et fonctionnels

### S4 - PretraitementFeatures (À faire)
- [ ] Vérifier format Feast features
- [ ] Aligner features dérivées (churn, bug-fix proximity)
- [ ] Vérifier split temporel train/val/test

### S5 - MLService (À faire)
- [ ] Vérifier format API `/api/v1/predict`
- [ ] Aligner format MLflow
- [ ] Vérifier SHAP values dans réponse

### S6 - MoteurPriorisation (À faire)
- [ ] Vérifier format API `/api/v1/prioritize`
- [ ] Aligner format PostgreSQL
- [ ] Vérifier stratégies d'optimisation

### S7 - TestScaffolder (À faire)
- [ ] Vérifier format API `/api/v1/test-scaffold`
- [ ] Aligner format Git repository
- [ ] Vérifier génération de tests

### S8 - DashboardQualité (À faire)
- [ ] Vérifier format WebSocket
- [ ] Aligner format REST API
- [ ] Vérifier intégration React

### S9 - Integrations (À faire)
- [ ] Vérifier format webhooks GitHub/GitLab
- [ ] Aligner format CI/CD comments
- [ ] Vérifier format checks/status

## Prochaines Étapes

1. Continuer l'alignement des services S2-S9
2. Vérifier les communications entre services
3. Tester les formats JSON
4. Mettre à jour les tests unitaires
5. Documenter les changements

## Notes

- Tous les modèles Pydantic utilisent maintenant les formats exacts des spécifications
- Les docstrings incluent les exemples JSON des spécifications
- Les validations sont renforcées pour correspondre aux schémas

