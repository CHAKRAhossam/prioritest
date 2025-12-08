# API Documentation - Historique Tests

## Base URL
```
http://localhost:8080/api
```

## Authentication
Currently, the API does not require authentication. For production deployment, implement OAuth2 or JWT authentication.

## Content Types
- **Request**: `multipart/form-data` (for file uploads), `application/json`
- **Response**: `application/json`

---

## Coverage API

### Upload JaCoCo Report

**POST** `/api/coverage/jacoco`

Upload and process a JaCoCo XML coverage report.

**Parameters:**
- `file` (multipart) - JaCoCo XML file (required)
- `commit` (string) - Git commit SHA (required)
- `buildId` (string) - CI build ID (optional)
- `branch` (string) - Git branch name (optional, default: "main")

**Example Request:**
```bash
curl -X POST "http://localhost:8080/api/coverage/jacoco" \
  -F "file=@jacoco.xml" \
  -F "commit=abc123" \
  -F "buildId=build-001" \
  -F "branch=main"
```

**Success Response (200 OK):**
```json
{
  "message": "JaCoCo report processed successfully",
  "classesProcessed": 45,
  "commit": "abc123"
}
```

---

### Upload PIT Mutation Report

**POST** `/api/coverage/pit`

Upload and process a PIT mutation testing XML report.

**Parameters:**
- `file` (multipart) - PIT mutations XML file (required)
- `commit` (string) - Git commit SHA (required)

**Example Request:**
```bash
curl -X POST "http://localhost:8080/api/coverage/pit" \
  -F "file=@mutations.xml" \
  -F "commit=abc123"
```

**Success Response (200 OK):**
```json
{
  "message": "PIT report processed successfully",
  "commit": "abc123"
}
```

---

### Get Coverage Summary

**GET** `/api/coverage/commit/{commitSha}`

Get aggregated coverage metrics for a commit.

**Example Request:**
```bash
curl http://localhost:8080/api/coverage/commit/abc123
```

**Success Response (200 OK):**
```json
{
  "commitSha": "abc123",
  "totalClasses": 45,
  "averageLineCoverage": 78.5,
  "averageBranchCoverage": 65.2,
  "averageMutationScore": 72.0,
  "totalLines": 2500,
  "coveredLines": 1962
}
```

---

### Get Coverage History

**GET** `/api/coverage/class/{className}`

Get historical coverage data for a specific class.

**Example Request:**
```bash
curl http://localhost:8080/api/coverage/class/com.example.MyService
```

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "commitSha": "abc123",
    "className": "com.example.MyService",
    "lineCoverage": 78.5,
    "branchCoverage": 65.2,
    "mutationScore": 72.0,
    "timestamp": "2024-01-15T10:30:00"
  },
  {
    "id": 2,
    "commitSha": "def456",
    "className": "com.example.MyService",
    "lineCoverage": 82.3,
    "branchCoverage": 70.1,
    "mutationScore": 75.5,
    "timestamp": "2024-01-16T14:20:00"
  }
]
```

---

### Get Low Coverage Classes

**GET** `/api/coverage/low-coverage?threshold={threshold}`

Find classes with line coverage below the threshold.

**Parameters:**
- `threshold` (double) - Coverage threshold percentage (default: 80.0)

**Example Request:**
```bash
curl "http://localhost:8080/api/coverage/low-coverage?threshold=80"
```

**Success Response (200 OK):**
```json
[
  {
    "className": "com.example.PoorlyTested",
    "lineCoverage": 45.2,
    "branchCoverage": 30.5,
    "uncoveredLines": 120,
    "commitSha": "abc123"
  }
]
```

---

## Test Results API

### Upload Surefire Report

**POST** `/api/tests/surefire`

Upload and process Surefire/Failsafe test results.

**Parameters:**
- `file` (multipart) - Surefire XML file (TEST-*.xml) (required)
- `commit` (string) - Git commit SHA (required)
- `buildId` (string) - CI build ID (optional)
- `branch` (string) - Git branch name (optional)

**Example Request:**
```bash
curl -X POST "http://localhost:8080/api/tests/surefire" \
  -F "file=@TEST-MyServiceTest.xml" \
  -F "commit=abc123" \
  -F "buildId=build-001" \
  -F "branch=main"
```

**Success Response (200 OK):**
```json
{
  "message": "Surefire report processed successfully",
  "testsProcessed": 125,
  "commit": "abc123"
}
```

---

### Get Test Summary

**GET** `/api/tests/commit/{commitSha}`

Get aggregated test results for a commit.

**Example Request:**
```bash
curl http://localhost:8080/api/tests/commit/abc123
```

**Success Response (200 OK):**
```json
{
  "commitSha": "abc123",
  "total": 125,
  "passed": 120,
  "failed": 3,
  "skipped": 2,
  "passRate": 96.0,
  "totalExecutionTime": 45.3
}
```

---

### Get Test History

**GET** `/api/tests/history/{testClass}/{testName}`

Get execution history for a specific test.

**Example Request:**
```bash
curl http://localhost:8080/api/tests/history/com.example.MyServiceTest/shouldCalculateTotal
```

**Success Response (200 OK):**
```json
[
  {
    "testClass": "com.example.MyServiceTest",
    "testName": "shouldCalculateTotal",
    "status": "PASSED",
    "executionTime": 0.125,
    "timestamp": "2024-01-15T10:30:00",
    "commitSha": "abc123"
  },
  {
    "testClass": "com.example.MyServiceTest",
    "testName": "shouldCalculateTotal",
    "status": "FAILED",
    "executionTime": 0.135,
    "errorMessage": "Expected 10 but was 9",
    "timestamp": "2024-01-14T15:20:00",
    "commitSha": "xyz789"
  }
]
```

---

### Get Failed Tests

**GET** `/api/tests/failed/{commitSha}`

Get all failed tests for a commit.

**Example Request:**
```bash
curl http://localhost:8080/api/tests/failed/abc123
```

**Success Response (200 OK):**
```json
[
  {
    "testClass": "com.example.BrokenTest",
    "testName": "shouldWork",
    "status": "FAILED",
    "executionTime": 0.05,
    "errorMessage": "NullPointerException",
    "stackTrace": "java.lang.NullPointerException\n\tat com.example...",
    "timestamp": "2024-01-15T10:30:00"
  }
]
```

---

## Metrics API

### Get Complete Metrics

**GET** `/api/metrics/commit/{commitSha}`

Get comprehensive quality metrics dashboard for a commit.

**Example Request:**
```bash
curl http://localhost:8080/api/metrics/commit/abc123
```

**Success Response (200 OK):**
```json
{
  "commitSha": "abc123",
  "generatedAt": "2024-01-15T10:35:00",
  "coverage": {
    "totalClasses": 45,
    "averageLineCoverage": "78.50%",
    "averageBranchCoverage": "65.20%",
    "averageMutationScore": "72.00%",
    "coveredLines": 1962,
    "totalLines": 2500
  },
  "tests": {
    "total": 125,
    "passed": 120,
    "failed": 3,
    "skipped": 2,
    "passRate": "96.00%",
    "executionTime": "45.30s"
  },
  "debt": {
    "averageDebtScore": "25.50",
    "highDebtClasses": 5,
    "totalUncoveredLines": 538,
    "totalSurvivedMutants": 28
  },
  "qualityScore": 75.3
}
```

---

## Test Debt API

### Calculate Test Debt

**POST** `/api/debt/calculate/{commitSha}`

Calculate test debt for all classes in a commit.

**Example Request:**
```bash
curl -X POST http://localhost:8080/api/debt/calculate/abc123
```

**Success Response (200 OK):**
```json
{
  "message": "Test debt calculated successfully",
  "classesAnalyzed": 45,
  "commit": "abc123"
}
```

---

### Get Debt Summary

**GET** `/api/debt/commit/{commitSha}`

Get test debt summary for a commit.

**Example Request:**
```bash
curl http://localhost:8080/api/debt/commit/abc123
```

**Success Response (200 OK):**
```json
{
  "commitSha": "abc123",
  "totalClasses": 45,
  "averageDebtScore": 25.5,
  "highDebtClasses": 5,
  "totalUncoveredLines": 538,
  "totalSurvivedMutants": 28
}
```

---

### Get High Debt Classes

**GET** `/api/debt/high-debt?threshold={threshold}`

Find classes with debt score above threshold.

**Parameters:**
- `threshold` (double) - Debt score threshold (default: 50.0)

**Example Request:**
```bash
curl "http://localhost:8080/api/debt/high-debt?threshold=50"
```

**Success Response (200 OK):**
```json
[
  {
    "className": "com.example.LegacyService",
    "debtScore": 75.5,
    "coverageDeficit": 45.0,
    "uncoveredLines": 250,
    "survivedMutants": 15,
    "recommendations": "Add tests to improve line coverage from 35.0% to 80.0% (add 250 line(s)); Add tests for conditional logic - branch coverage is 20.0%, target is 75.0%; Strengthen test assertions - 15 mutants survived (mutation score: 45.0%)"
  }
]
```

---

## Flakiness API

### Calculate Flakiness

**POST** `/api/flakiness/calculate?start={start}&end={end}`

Analyze test results in a time window to detect flaky tests.

**Parameters:**
- `start` (ISO DateTime) - Window start time (required)
- `end` (ISO DateTime) - Window end time (required)

**Example Request:**
```bash
curl -X POST "http://localhost:8080/api/flakiness/calculate?start=2024-01-01T00:00:00&end=2024-01-08T00:00:00"
```

**Success Response (200 OK):**
```json
{
  "message": "Flakiness calculated successfully",
  "testsAnalyzed": 125,
  "windowStart": "2024-01-01T00:00:00",
  "windowEnd": "2024-01-08T00:00:00"
}
```

---

### Get Flaky Tests

**GET** `/api/flakiness/flaky?threshold={threshold}`

Get tests with flakiness score above threshold.

**Parameters:**
- `threshold` (double) - Flakiness threshold (0.0-1.0, default: 0.3)

**Example Request:**
```bash
curl "http://localhost:8080/api/flakiness/flaky?threshold=0.3"
```

**Success Response (200 OK):**
```json
[
  {
    "testClass": "com.example.FlakyTest",
    "testName": "sometimesWorks",
    "flakinessScore": 0.65,
    "totalRuns": 20,
    "passedRuns": 12,
    "failedRuns": 8,
    "consecutiveFailures": 3,
    "lastFailure": "2024-01-15T10:30:00",
    "lastSuccess": "2024-01-15T11:00:00"
  }
]
```

---

### Get Most Flaky Tests

**GET** `/api/flakiness/most-flaky`

Get all tests ordered by flakiness score (descending).

**Example Request:**
```bash
curl http://localhost:8080/api/flakiness/most-flaky
```

---

### Get Test Flakiness

**GET** `/api/flakiness/test/{testClass}/{testName}`

Get flakiness information for a specific test.

**Example Request:**
```bash
curl http://localhost:8080/api/flakiness/test/com.example.FlakyTest/sometimesWorks
```

**Success Response (200 OK):**
```json
{
  "testClass": "com.example.FlakyTest",
  "testName": "sometimesWorks",
  "flakinessScore": 0.65,
  "totalRuns": 20,
  "passedRuns": 12,
  "failedRuns": 8,
  "windowStart": "2024-01-01T00:00:00",
  "windowEnd": "2024-01-08T00:00:00"
}
```

**Not Found Response (404):**
```json
{
  "error": "Test flakiness data not found"
}
```

---

## Error Responses

All endpoints may return error responses in the following format:

**Error Response (500 Internal Server Error):**
```json
{
  "error": "Detailed error message"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Invalid request parameters"
}
```

---

## Rate Limiting

Currently, there is no rate limiting. Consider implementing rate limiting for production use.

## Pagination

For endpoints returning large datasets, consider implementing pagination using:
- `?page=0&size=20` query parameters
- Spring Data's `Pageable` interface

## Filtering and Sorting

Consider adding query parameters for filtering and sorting:
- `?sort=timestamp,desc`
- `?filter=status:FAILED`

---

## Interactive Documentation

For interactive API testing, visit the Swagger UI:
```
http://localhost:8080/swagger-ui.html
```

## OpenAPI Specification

Get the OpenAPI 3.0 specification in JSON format:
```
http://localhost:8080/api-docs
```


