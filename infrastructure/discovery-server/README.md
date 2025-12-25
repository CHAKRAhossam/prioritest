# Discovery Server (Eureka)

**Netflix Eureka Server** for service discovery in the PRIORITEST Platform.

## Description

Central service registry where all microservices register themselves. Enables:
- **Service Discovery**: Services find each other by name instead of hardcoded URLs
- **Load Balancing**: API Gateway can distribute load across multiple instances
- **Health Monitoring**: Tracks which services are UP or DOWN
- **Self-Healing**: Automatically removes unhealthy instances

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Discovery Server (8761)                          │
│                                                                         │
│   ┌───────────────────────────────────────────────────────────────┐    │
│   │                     Service Registry                          │    │
│   │                                                               │    │
│   │   api-gateway ─────────────► http://api-gateway:8080         │    │
│   │   s1-collecte ─────────────► http://s1-collecte:8001         │    │
│   │   s2-analyse ──────────────► http://s2-analyse:8081          │    │
│   │   s3-historique ───────────► http://s3-historique:8082       │    │
│   │   s4-features ─────────────► http://s4-features:8004         │    │
│   │   s5-ml ───────────────────► http://s5-ml:8005               │    │
│   │   s6-prioritization ───────► http://s6-prioritization:8006   │    │
│   │   s7-scaffolder ───────────► http://s7-scaffolder:8007       │    │
│   │   s9-integrations ─────────► http://s9-integrations:8009     │    │
│   │                                                               │    │
│   └───────────────────────────────────────────────────────────────┘    │
│                                                                         │
│   Dashboard: http://localhost:8761                                      │
│   Credentials: eureka / eureka123                                       │
└─────────────────────────────────────────────────────────────────────────┘
```

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `http://localhost:8761` | Eureka Dashboard (web UI) |
| `http://localhost:8761/eureka/apps` | All registered services (XML) |
| `http://localhost:8761/eureka/apps/{appName}` | Specific service info |
| `http://localhost:8761/actuator/health` | Health check |

## Configuration

### Default Credentials

- **Username**: `eureka`
- **Password**: `eureka123`

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_PORT` | 8761 | Eureka server port |
| `EUREKA_USER` | eureka | Dashboard username |
| `EUREKA_PASSWORD` | eureka123 | Dashboard password |

## Build & Run

### Local Development

```bash
cd infrastructure/discovery-server
./mvnw spring-boot:run
```

Access the dashboard at: http://localhost:8761

### Docker

```bash
docker build -t prioritest-discovery-server .
docker run -p 8761:8761 prioritest-discovery-server
```

### Docker Compose

```bash
docker-compose up -d discovery-server
```

## Service Registration

### For Java/Spring Services

Add to `pom.xml`:
```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-netflix-eureka-client</artifactId>
</dependency>
```

Add to `application.yml`:
```yaml
eureka:
  client:
    service-url:
      defaultZone: http://eureka:eureka123@discovery-server:8761/eureka/
  instance:
    prefer-ip-address: true
```

### For Python/FastAPI Services

Use `py-eureka-client`:
```python
import py_eureka_client.eureka_client as eureka_client

eureka_client.init(
    eureka_server="http://eureka:eureka123@discovery-server:8761/eureka",
    app_name="s1-collecte",
    instance_port=8001
)
```

## Tech Stack

- **Spring Boot 3.2.0**
- **Spring Cloud Netflix Eureka Server 2023.0.0**
- **Spring Security** for dashboard protection
- **Java 17**
