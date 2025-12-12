# Documentation - ML Test Prioritization Platform

Bienvenue dans la documentation complète de la plateforme de recommandation automatisée des classes logicielles à tester.

## 📚 Navigation Rapide

### Architecture et Design

1. **[ARCHITECTURE_COMPLETE.md](./ARCHITECTURE_COMPLETE.md)** ⭐ **RECOMMANDÉ**
   - Documentation complète de l'architecture avec tous les détails
   - Inputs/outputs JSON pour chaque service (S1-S9)
   - Schémas de base de données
   - Endpoints API principaux
   - Configuration et déploiement
   - **À lire en premier pour comprendre l'architecture complète**

2. **[ARCHITECTURE_SUMMARY.md](./ARCHITECTURE_SUMMARY.md)**
   - Résumé visuel de l'architecture
   - Flux global simplifié
   - Technologies clés par couche
   - Points d'entrée/sortie principaux
   - **Vue d'ensemble rapide**

3. **[COMMUNICATION_MATRIX.md](./COMMUNICATION_MATRIX.md)**
   - Matrice de communication détaillée entre tous les services
   - Protocoles utilisés (Kafka, REST, SQL, etc.)
   - Exemples de messages JSON
   - Configuration des topics Kafka
   - Gestion des erreurs et retry policies
   - **Pour comprendre les interactions entre services**

4. **[diagrams/ARCHITECTURE_GUIDE.md](./diagrams/ARCHITECTURE_GUIDE.md)**
   - Guide d'architecture avec diagrammes
   - Technologies par service
   - Couleurs pour Draw.io
   - **Pour créer des diagrammes visuels**

### Guides Pratiques

5. **[QUICK_START.md](./QUICK_START.md)**
   - Guide de démarrage rapide
   - Installation et configuration
   - **Pour commencer rapidement**

6. **[SETUP_TEAM.md](./SETUP_TEAM.md)**
   - Guide complet d'onboarding
   - Configuration de l'environnement de développement
   - **Pour les nouveaux membres de l'équipe**

7. **[GITLAB_AUTH.md](./GITLAB_AUTH.md)**
   - Guide d'authentification GitLab
   - Configuration des Personal Access Tokens
   - SSO/SAML
   - **Pour l'authentification**

### Documentation par Service

#### S1 - CollecteDepots (Haytam Ta)
- **Service** : `services/S1-CollecteDepots/`
- **README** : `services/S1-CollecteDepots/README.md`
- **Documentation** : Voir [ARCHITECTURE_COMPLETE.md](./ARCHITECTURE_COMPLETE.md#service-1--collectedepots-haytam-ta)

#### S2 - AnalyseStatique (Haytam Ta)
- **Service** : `services/S2-AnalyseStatique/`
- **README** : `services/S2-AnalyseStatique/README.md`
- **Documentation** : Voir [ARCHITECTURE_COMPLETE.md](./ARCHITECTURE_COMPLETE.md#service-2--analysestatique-haytam-ta)

#### S3 - HistoriqueTests (Oussama Boujdig)
- **Service** : `services/S3-HistoriqueTests/`
- **README** : `services/S3-HistoriqueTests/README.md`
- **API Documentation** : `services/S3-HistoriqueTests/API_DOCUMENTATION.md`
- **Documentation** : Voir [ARCHITECTURE_COMPLETE.md](./ARCHITECTURE_COMPLETE.md#service-3--historiquetests-oussama-boujdig)

#### S4 - PretraitementFeatures (Hicham Kaou)
- **Service** : `services/S4-PretraitementFeatures/`
- **README** : `services/S4-PretraitementFeatures/README.md`
- **Documentation** : Voir [ARCHITECTURE_COMPLETE.md](./ARCHITECTURE_COMPLETE.md#service-4--prétraitementfeatures-hicham-kaou)

#### S5 - MLService (Hicham Kaou)
- **Service** : `services/S5-MLService/`
- **README** : `services/S5-MLService/README.md`
- **Documentation** : Voir [ARCHITECTURE_COMPLETE.md](./ARCHITECTURE_COMPLETE.md#service-5--mlservice-hicham-kaou)

#### S6 - MoteurPriorisation (Hossam Chakra)
- **Service** : `services/S6-MoteurPriorisation/`
- **README** : `services/S6-MoteurPriorisation/README.md`
- **Documentation** : Voir [ARCHITECTURE_COMPLETE.md](./ARCHITECTURE_COMPLETE.md#service-6--moteurpriorisation-hossam-chakra)

#### S7 - TestScaffolder (Hossam Chakra)
- **Service** : `services/S7-TestScaffolder/`
- **README** : `services/S7-TestScaffolder/README.md`
- **Documentation** : Voir [ARCHITECTURE_COMPLETE.md](./ARCHITECTURE_COMPLETE.md#service-7--testscaffolder-hossam-chakra)

#### S8 - DashboardQualité (Ilyas Michich)
- **Service** : `services/S8-DashboardQualite/`
- **README** : `services/S8-DashboardQualite/README.md`
- **Documentation** : Voir [ARCHITECTURE_COMPLETE.md](./ARCHITECTURE_COMPLETE.md#service-8--dashboardqualité-ilyas-michich)

#### S9 - Integrations (Oussama Boujdig)
- **Service** : `services/S9-Integrations/`
- **README** : `services/S9-Integrations/README.md`
- **Documentation** : Voir [ARCHITECTURE_COMPLETE.md](./ARCHITECTURE_COMPLETE.md#service-9--intégrations--ops-oussama-boujdig)

## 🗺️ Parcours Recommandé

### Pour les Nouveaux Développeurs
1. Lire [ARCHITECTURE_SUMMARY.md](./ARCHITECTURE_SUMMARY.md) pour une vue d'ensemble
2. Lire [QUICK_START.md](./QUICK_START.md) pour démarrer
3. Consulter [ARCHITECTURE_COMPLETE.md](./ARCHITECTURE_COMPLETE.md) pour les détails de votre service
4. Lire [COMMUNICATION_MATRIX.md](./COMMUNICATION_MATRIX.md) pour comprendre les interactions

### Pour les Architectes
1. Lire [ARCHITECTURE_COMPLETE.md](./ARCHITECTURE_COMPLETE.md) en entier
2. Consulter [COMMUNICATION_MATRIX.md](./COMMUNICATION_MATRIX.md) pour les détails de communication
3. Examiner [diagrams/ARCHITECTURE_GUIDE.md](./diagrams/ARCHITECTURE_GUIDE.md) pour les diagrammes

### Pour les DevOps
1. Lire [ARCHITECTURE_COMPLETE.md](./ARCHITECTURE_COMPLETE.md#configuration-et-déploiement)
2. Consulter [COMMUNICATION_MATRIX.md](./COMMUNICATION_MATRIX.md#configuration-des-topics-kafka)
3. Examiner les configurations Kubernetes dans `services/S9-Integrations/kubernetes/`

## 📋 Structure des Documents

### ARCHITECTURE_COMPLETE.md
Contient :
- Vue d'ensemble et flux global
- Documentation complète de chaque service (S1-S9) :
  - Rôle et responsabilités
  - Inputs (JSON schemas)
  - Outputs (JSON schemas)
  - Envoie vers (destinations)
  - Détails d'implémentation
- Matrice de communication
- Technologies par service
- Schémas de base de données
- Endpoints API principaux
- Configuration et déploiement
- Métriques et observabilité
- Sécurité

### COMMUNICATION_MATRIX.md
Contient :
- Matrice complète de communication
- Détails pour chaque communication (S1→S2, S2→S4, etc.)
- Protocoles utilisés
- Exemples de messages JSON
- Configuration des topics Kafka
- Configuration des endpoints REST
- Gestion des erreurs
- Monitoring et observabilité

### ARCHITECTURE_SUMMARY.md
Contient :
- Vue d'ensemble visuelle
- Flux global simplifié (ASCII art)
- Services par couche
- Technologies clés
- Points d'entrée/sortie
- Flux de données clés
- Métriques et KPIs

## 🔍 Recherche Rapide

### Par Sujet

**Kafka Topics**
- [ARCHITECTURE_COMPLETE.md](./ARCHITECTURE_COMPLETE.md#service-1--collectedepots-haytam-ta) - Topics S1
- [COMMUNICATION_MATRIX.md](./COMMUNICATION_MATRIX.md#configuration-des-topics-kafka) - Configuration

**REST APIs**
- [ARCHITECTURE_COMPLETE.md](./ARCHITECTURE_COMPLETE.md#endpoints-api-principaux) - Liste complète
- [COMMUNICATION_MATRIX.md](./COMMUNICATION_MATRIX.md#configuration-des-endpoints-rest) - Configuration

**Base de Données**
- [ARCHITECTURE_COMPLETE.md](./ARCHITECTURE_COMPLETE.md#schémas-de-base-de-données) - Schémas
- [COMMUNICATION_MATRIX.md](./COMMUNICATION_MATRIX.md) - Utilisation par service

**JSON Schemas**
- [ARCHITECTURE_COMPLETE.md](./ARCHITECTURE_COMPLETE.md) - Tous les schemas par service

**Configuration**
- [ARCHITECTURE_COMPLETE.md](./ARCHITECTURE_COMPLETE.md#configuration-et-déploiement) - Variables d'environnement

## 📝 Mise à Jour de la Documentation

Cette documentation est maintenue à jour avec le code. Si vous modifiez :
- Les inputs/outputs d'un service → Mettre à jour [ARCHITECTURE_COMPLETE.md](./ARCHITECTURE_COMPLETE.md)
- Les communications entre services → Mettre à jour [COMMUNICATION_MATRIX.md](./COMMUNICATION_MATRIX.md)
- L'architecture globale → Mettre à jour [ARCHITECTURE_SUMMARY.md](./ARCHITECTURE_SUMMARY.md)

## 🤝 Contribution

Pour contribuer à la documentation :
1. Lire les documents existants
2. Suivre le format et la structure
3. Inclure des exemples JSON concrets
4. Mettre à jour tous les documents liés
5. Vérifier la cohérence avec le code

## 📞 Support

Pour toute question sur l'architecture :
- Consulter [ARCHITECTURE_COMPLETE.md](./ARCHITECTURE_COMPLETE.md)
- Consulter [COMMUNICATION_MATRIX.md](./COMMUNICATION_MATRIX.md)
- Contacter l'équipe via Jira : https://prioritest.atlassian.net

---

**Dernière mise à jour** : 2025-12-04  
**Version** : 1.0.0

