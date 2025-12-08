# Fonctionnalités Ajoutées au Service S2 - AnalyseStatique

## 📋 Résumé

Ce document liste toutes les fonctionnalités ajoutées pour compléter le Service 2 selon le cahier des charges.

## ✅ Fonctionnalités Implémentées

### 1. Intégration Kafka ✅

- **Consumer Kafka** : `CommitEventConsumer` qui consomme les messages du topic `repository.commits`
- **Producer Kafka** : `KafkaService` qui publie les métriques vers le topic `code.metrics`
- **Configuration Kafka** : `KafkaConfig` avec support pour producers et consumers
- **DTOs** : 
  - `CommitEvent` : Structure pour les messages entrants depuis `repository.commits`
  - `CodeMetricsEvent` : Structure pour les messages sortants vers `code.metrics`

### 2. Intégration Git (JGit) ✅

- **GitService** : Service pour cloner des dépôts Git et checkout un commit spécifique
- Support pour :
  - Clonage de dépôts Git
  - Checkout d'un commit spécifique
  - Gestion des répertoires temporaires
  - Nettoyage automatique

### 3. Calcul des Métriques Globales ✅

- **GlobalMetricsService** : Service pour calculer les métriques nécessitant une vue globale du projet
- **NOC (Number of Children)** : Calcul du nombre d'enfants pour chaque classe (nécessite analyse de l'héritage)
- **In/Out Degree** : Calcul des degrés d'entrée et de sortie dans le graphe de dépendances avec JGraphT
- Utilisation de **JGraphT** pour construire et analyser le graphe de dépendances

### 4. Intégration Feast Feature Store ✅

- **FeastService** : Service pour publier les métriques vers Feast Feature Store
- Format des données conforme au schéma Feast
- Publication asynchrone via WebClient (reactive)

### 5. Configuration PostgreSQL/TimescaleDB ✅

- Configuration dans `application.properties` pour PostgreSQL
- Support TimescaleDB (compatible PostgreSQL)
- Configuration JPA/Hibernate pour la persistance

### 6. Amélioration du MetricsService ✅

- Nouvelle méthode `processCommitEvent()` pour traiter les événements depuis Kafka
- Intégration complète du pipeline :
  1. Réception événement commit depuis Kafka
  2. Clonage du dépôt au commit donné
  3. Analyse des fichiers modifiés
  4. Calcul des métriques (CK, dépendances, smells)
  5. Calcul des métriques globales (NOC, in/out degree)
  6. Publication vers Kafka et Feast

### 7. Configuration et Infrastructure ✅

- **KafkaConfig** : Configuration complète pour Kafka (producers/consumers)
- **WebClientConfig** : Configuration pour WebClient (Feast)
- **JacksonConfig** : Configuration pour ObjectMapper (JSON)
- **application.properties** : Toutes les configurations nécessaires

## 📦 Dépendances Ajoutées

Les dépendances suivantes ont été ajoutées au `pom.xml` :

- `spring-kafka` : Intégration Kafka
- `org.jgrapht:jgrapht-core` : Graphe de dépendances
- `org.eclipse.jgit:org.eclipse.jgit` : Opérations Git
- `spring-boot-starter-webflux` : Client HTTP réactif (Feast)
- `postgresql` : Driver PostgreSQL
- `jackson-datatype-jsr310` : Support dates/temps

## 🔄 Flux de Traitement

```
Kafka (repository.commits)
    ↓
CommitEventConsumer
    ↓
MetricsService.processCommitEvent()
    ↓
GitService.cloneAndCheckout()
    ↓
Analyse fichiers modifiés
    ↓
Extraction métriques (CK, dépendances, smells)
    ↓
GlobalMetricsService (NOC, in/out degree)
    ↓
Publication vers Kafka (code.metrics) + Feast
```

## ⚠️ Fonctionnalités Restantes (Optionnelles)

### 1. Support Python (radon) ⏳

- Actuellement, seul Java est supporté
- Pour ajouter le support Python, il faudrait :
  - Créer un service Python séparé (recommandé)
  - Ou intégrer radon via Jython (complexe)
  - Ou utiliser un appel système vers un script Python

### 2. Normalisation par Module/Langage ⏳

- La normalisation n'est pas encore implémentée
- Pourrait être ajoutée dans `GlobalMetricsService` ou un service dédié

### 3. Amélioration du calcul NOC ⏳

- Le calcul actuel de NOC est simplifié
- Pour une version complète, il faudrait parser l'héritage depuis les fichiers sources

## 🚀 Utilisation

### Démarrer le service

1. Démarrer les services requis (Kafka, PostgreSQL, Feast) via docker-compose
2. Configurer `application.properties` avec les bonnes URLs
3. Lancer l'application Spring Boot

### Tester avec Kafka

Envoyer un message au topic `repository.commits` :

```json
{
  "event_id": "evt_123",
  "repository_id": "repo_12345",
  "commit_sha": "abc123",
  "files_changed": [
    {
      "path": "src/UserService.java",
      "status": "modified"
    }
  ]
}
```

Le service va automatiquement :
1. Cloner le dépôt
2. Analyser les fichiers
3. Publier les métriques vers `code.metrics` et Feast

## 📝 Notes

- Le service assume que `repository_id` correspond à un dépôt GitHub (format `owner/repo`)
- Pour d'autres sources Git, il faudrait un service de mapping `repository_id` → URL Git
- Le nettoyage des dépôts clonés est optionnel (peut être gardé pour cache)

