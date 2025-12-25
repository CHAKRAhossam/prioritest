# S0 - API Gateway

**Spring Cloud Gateway** for the PRIORITEST Platform.

## Description

Central API Gateway that routes all requests to the appropriate microservices. Provides:
- **Service Discovery** integration with Eureka
- **Load Balancing** across service instances
- **Circuit Breaker** with Resilience4j for fault tolerance
- **Rate Limiting** to prevent abuse
- **CORS Configuration** for frontend access
- **Request/Response Logging** with correlation IDs

## Architecture

```
                                    ┌─────────────────────┐
                                    │  Discovery Server   │
                                    │    (Eureka:8761)    │
                                    └──────────┬──────────┘
                                               │ registers
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
┌───────────┐      │     ┌─────────────────────▼─────────────────────┐   │
│  Frontend │──────┼────►│           API Gateway (8080)              │   │
│   (3000)  │      │     │                                           │   │
└───────────┘      │     │  /api/s1/** → S1-CollecteDepots:8001     │   │
                   │     │  /api/s2/** → S2-AnalyseStatique:8081    │   │
                   │     │  /api/s3/** → S3-HistoriqueTests:8082    │   │
                   │     │  /api/s4/** → S4-PretraitementFeatures:8004 │
                   │     │  /api/s5/** → S5-MLService:8005          │   │
                   │     │  /api/s6/** → S6-MoteurPriorisation:8006 │   │
                   │     │  /api/s7/** → S7-TestScaffolder:8007     │   │
                   │     │  /api/s9/** → S9-Integrations:8009       │   │
                   │     └───────────────────────────────────────────┘   │
                   │                          │                          │
                   │     routes to ───────────┼──────────────────────    │
                   │                          ▼                          │
                   │     ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
                   │     │ S1  │ S2  │ S3  │ S4  │ S5  │ S6  │ S7  │ S9  │
                   │     └─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
                   └──────────────────────────────────────────────────────┘
```

## Routing Table

| Gateway Path | Target Service | Port | Description |
|--------------|----------------|------|-------------|
| `/api/s1/**` | S1-CollecteDepots | 8001 | Repository collection, webhooks |
| `/api/s2/**` | S2-AnalyseStatique | 8081 | CK metrics analysis |
| `/api/s3/**` | S3-HistoriqueTests | 8082 | Test coverage, results, flakiness |
| `/api/s4/**` | S4-PretraitementFeatures | 8004 | Feature engineering pipeline |
| `/api/s5/**` | S5-MLService | 8005 | ML training and predictions |
| `/api/s6/**` | S6-MoteurPriorisation | 8006 | Test prioritization |
| `/api/s7/**` | S7-TestScaffolder | 8007 | JUnit test generation |
| `/api/s9/**` | S9-Integrations | 8009 | External integrations |

## API Endpoints

### Health & Status

```bash
# Gateway health
GET http://localhost:8080/api/health

# All services health (aggregated)
GET http://localhost:8080/api/health/all

# Available routes
GET http://localhost:8080/api/health/routes

# Individual service health
GET http://localhost:8080/health/s1
GET http://localhost:8080/health/s2
GET http://localhost:8080/health/s3
...
```

### Service Routes Examples

```bash
# S1 - Collect repository
POST http://localhost:8080/api/s1/api/v1/collect
{
  "repository_url": "https://github.com/org/repo",
  "collect_type": "commits|issues"
}

# S2 - Analyze metrics
POST http://localhost:8080/api/s2/metrics/analyze
Content-Type: multipart/form-data
file: <java-project.zip>

# S3 - Upload coverage
POST http://localhost:8080/api/s3/coverage/jacoco
Content-Type: multipart/form-data
file: <jacoco.xml>

# S5 - Train model
POST http://localhost:8080/api/s5/train

# S5 - Predict risk
POST http://localhost:8080/api/s5/predict
{
  "class_name": "com.example.UserService",
  "features": {...}
}

# S6 - Prioritize tests
POST http://localhost:8080/api/s6/prioritize?strategy=maximize_popt20
{
  "repository_id": "github_org_repo"
}

# S7 - Generate test
POST http://localhost:8080/api/s7/generate
{
  "java_code": "public class UserService {...}"
}
```

## Configuration

### application.yml

Key configurations:
- **Server Port**: 8080
- **Eureka**: Connects to discovery-server:8761
- **Circuit Breaker**: 50% failure threshold, 10s open state
- **Timeout**: 30 seconds per request

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_PORT` | 8080 | Gateway port |
| `EUREKA_URI` | http://discovery-server:8761/eureka/ | Eureka server URL |
| `EUREKA_USER` | eureka | Eureka username |
| `EUREKA_PASSWORD` | eureka123 | Eureka password |

## Build & Run

### Local Development

```bash
cd services/S0-ApiGateway
./mvnw spring-boot:run
```

### Docker

```bash
docker build -t prioritest-api-gateway .
docker run -p 8080:8080 prioritest-api-gateway
```

### Docker Compose

The gateway is included in the main `docker-compose.yml`:

```bash
docker-compose up -d api-gateway
```

## Features

### Circuit Breaker

Each service route has a dedicated circuit breaker:
- Opens after 50% failure rate in 10 requests
- Stays open for 10 seconds
- Half-open state allows 5 test calls

### CORS

Configured for frontend origins:
- `http://localhost:3000` (React)
- `http://localhost:5173` (Vite)
- `http://prioritest-dashboard:3000` (Docker)

### Logging

All requests include:
- `X-Correlation-Id`: For tracing across services
- `X-Request-Id`: Unique per request
- Duration logging in milliseconds

## Monitoring

### Actuator Endpoints

```bash
# Health
GET http://localhost:8080/actuator/health

# Metrics
GET http://localhost:8080/actuator/metrics

# Circuit breakers status
GET http://localhost:8080/actuator/circuitbreakers

# Gateway routes
GET http://localhost:8080/actuator/gateway/routes
```

### Prometheus Metrics

Available at `/actuator/prometheus` for Grafana dashboards.

## Tech Stack

- **Spring Boot 3.2.0**
- **Spring Cloud Gateway 2023.0.0**
- **Spring Cloud Netflix Eureka Client**
- **Resilience4j** for circuit breaker
- **Micrometer** for metrics
- **Java 17**
