# Docker pour S2-AnalyseStatique

## Construction de l'image

```bash
cd prioritest/services/S2-AnalyseStatique
docker build -t analyse-statique-service:latest .
```

## Exécution avec Docker

```bash
docker run -p 8081:8081 \
  -e KAFKA_ENABLED=false \
  -e FEAST_ENABLED=false \
  analyse-statique-service:latest
```

## Exécution avec Docker Compose

Le service est déjà configuré dans `prioritest/docker-compose.yml`.

### Démarrer tous les services

```bash
cd prioritest
docker-compose up -d
```

### Démarrer uniquement le service S2

```bash
cd prioritest
docker-compose up -d analyse-statique
```

### Voir les logs

```bash
docker-compose logs -f analyse-statique
```

### Arrêter le service

```bash
docker-compose stop analyse-statique
```

## Configuration

Les variables d'environnement peuvent être modifiées dans `docker-compose.yml` :

- `KAFKA_ENABLED`: Activer/désactiver Kafka (default: false)
- `FEAST_ENABLED`: Activer/désactiver Feast (default: false)
- `SPRING_DATASOURCE_URL`: URL de la base de données PostgreSQL (optionnel)
- `GIT_TEMP_DIR`: Répertoire temporaire pour les dépôts Git clonés

## Healthcheck

Le service expose un endpoint de healthcheck à `/actuator/health` (nécessite Spring Boot Actuator).

Pour activer Actuator, ajoutez dans `pom.xml` :

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

Et dans `application.properties` :

```properties
management.endpoints.web.exposure.include=health
management.endpoint.health.show-details=when-authorized
```

## Volumes

Le service utilise un volume nommé `analyse_statique_temp` pour stocker les dépôts Git clonés temporairement.

## Réseau

Le service fait partie du réseau Docker `prioritest-network` et peut communiquer avec :
- `postgres:5432` (PostgreSQL)
- `kafka:9092` (Kafka)
- `zookeeper:2181` (Zookeeper)

