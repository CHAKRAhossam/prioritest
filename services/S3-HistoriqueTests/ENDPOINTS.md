# API Endpoints Reference

Quick reference for all available endpoints.

## Coverage API - `/api/coverage`

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| POST | `/jacoco` | Upload JaCoCo report | file, commit, buildId?, branch? |
| POST | `/pit` | Upload PIT report | file, commit |
| GET | `/commit/{sha}` | Get coverage summary | sha (path) |
| GET | `/class/{name}` | Get coverage history | name (path) |
| GET | `/low-coverage` | Find low coverage classes | threshold? (query, default=80) |

## Test Results API - `/api/tests`

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| POST | `/surefire` | Upload Surefire report | file, commit, buildId?, branch? |
| GET | `/commit/{sha}` | Get test summary | sha (path) |
| GET | `/history/{class}/{name}` | Get test history | class, name (path) |
| GET | `/failed/{sha}` | Get failed tests | sha (path) |

## Metrics API - `/api/metrics`

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/commit/{sha}` | Get complete metrics | sha (path) |

## Test Debt API - `/api/debt`

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| POST | `/calculate/{sha}` | Calculate test debt | sha (path) |
| GET | `/commit/{sha}` | Get debt summary | sha (path) |
| GET | `/high-debt` | Get high debt classes | threshold? (query, default=50) |

## Flakiness API - `/api/flakiness`

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| POST | `/calculate` | Calculate flakiness | start, end (query, ISO datetime) |
| GET | `/flaky` | Get flaky tests | threshold? (query, default=0.3) |
| GET | `/most-flaky` | Get most flaky tests | none |
| GET | `/test/{class}/{name}` | Get test flakiness | class, name (path) |

## Health & Management - `/actuator`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/info` | Application info |
| GET | `/metrics` | Application metrics |
| GET | `/prometheus` | Prometheus metrics |

## Documentation

| Endpoint | Description |
|----------|-------------|
| `/swagger-ui.html` | Interactive API documentation (Swagger UI) |
| `/api-docs` | OpenAPI 3.0 JSON specification |

---

## Quick Examples

### Upload Reports
```bash
# JaCoCo
curl -X POST http://localhost:8080/api/coverage/jacoco \
  -F "file=@jacoco.xml" -F "commit=abc123"

# Surefire
curl -X POST http://localhost:8080/api/tests/surefire \
  -F "file=@TEST-MyTest.xml" -F "commit=abc123"

# PIT
curl -X POST http://localhost:8080/api/coverage/pit \
  -F "file=@mutations.xml" -F "commit=abc123"
```

### Query Metrics
```bash
# Complete metrics
curl http://localhost:8080/api/metrics/commit/abc123

# Coverage only
curl http://localhost:8080/api/coverage/commit/abc123

# Tests only
curl http://localhost:8080/api/tests/commit/abc123

# Test debt
curl http://localhost:8080/api/debt/commit/abc123
```

### Calculate & Query
```bash
# Calculate debt
curl -X POST http://localhost:8080/api/debt/calculate/abc123

# Calculate flakiness (last 7 days)
START=$(date -d '7 days ago' --iso-8601=seconds)
END=$(date --iso-8601=seconds)
curl -X POST "http://localhost:8080/api/flakiness/calculate?start=$START&end=$END"

# Get flaky tests
curl http://localhost:8080/api/flakiness/flaky?threshold=0.3

# Get high debt classes
curl http://localhost:8080/api/debt/high-debt?threshold=50
```

---

## Base URL

- **Local**: http://localhost:8080
- **Docker**: http://historique-tests:8080
- **Production**: Configure as needed

## Response Format

All endpoints return JSON:

**Success:**
```json
{
  "message": "Success",
  "data": { ... }
}
```

**Error:**
```json
{
  "error": "Error message"
}
```

## Authentication

Currently **no authentication** required.

For production, implement:
- OAuth2
- JWT tokens
- API keys

## Rate Limiting

Currently **no rate limiting**.

Recommended for production:
- 1000 requests/hour per IP
- 100 requests/minute per endpoint

---

## See Also

- [README.md](README.md) - Full documentation
- [QUICKSTART.md](QUICKSTART.md) - 5-minute setup
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Detailed API docs
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - CI/CD integration


