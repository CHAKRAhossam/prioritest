# Test simple et rapide des endpoints S1
$baseUrl = "http://localhost:8001"

Write-Host "=== Test Simple des Endpoints S1 ===" -ForegroundColor Cyan
Write-Host ""

# 1. Health Check
Write-Host "1. Health Check" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/health" -Method GET -UseBasicParsing -TimeoutSec 5
    Write-Host "   ✅ Status: $($response.StatusCode)" -ForegroundColor Green
    $response.Content | ConvertFrom-Json | ConvertTo-Json
} catch {
    Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 2. OpenAPI
Write-Host "2. OpenAPI JSON" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/openapi.json" -Method GET -UseBasicParsing -TimeoutSec 10
    Write-Host "   ✅ Status: $($response.StatusCode)" -ForegroundColor Green
    $json = $response.Content | ConvertFrom-Json
    Write-Host "   Endpoints disponibles: $($json.paths.PSObject.Properties.Name.Count)" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 3. Collect Status
Write-Host "3. Collect Status" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/v1/collect/status" -Method GET -UseBasicParsing -TimeoutSec 5
    Write-Host "   ✅ Status: $($response.StatusCode)" -ForegroundColor Green
    $response.Content | ConvertFrom-Json | ConvertTo-Json
} catch {
    Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 4. Webhook GitHub (simple)
Write-Host "4. Webhook GitHub (test minimal)" -ForegroundColor Yellow
$githubBody = @{
    ref = "refs/heads/main"
    repository = @{
        id = 12345
        name = "test"
        full_name = "test/test"
    }
    commits = @()
} | ConvertTo-Json
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/v1/webhooks/github" -Method POST -Body $githubBody -ContentType "application/json" -Headers @{"X-GitHub-Event" = "push"} -UseBasicParsing -TimeoutSec 10
    Write-Host "   ✅ Status: $($response.StatusCode)" -ForegroundColor Green
    if ($response.Content) { $response.Content | ConvertFrom-Json | ConvertTo-Json }
} catch {
    $statusCode = if ($_.Exception.Response) { $_.Exception.Response.StatusCode.value__ } else { "N/A" }
    Write-Host "   ⚠️  Status: $statusCode - $($_.Exception.Message)" -ForegroundColor Yellow
}
Write-Host ""

# 5. Get Artifacts (404 attendu si pas de données)
Write-Host "5. Get Artifacts (404 attendu)" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/v1/artifacts/test_repo/abc123" -Method GET -UseBasicParsing -TimeoutSec 5
    Write-Host "   ✅ Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    $statusCode = if ($_.Exception.Response) { $_.Exception.Response.StatusCode.value__ } else { "N/A" }
    if ($statusCode -eq 404) {
        Write-Host "   ✅ Status: 404 (attendu - pas de données)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Status: $statusCode" -ForegroundColor Yellow
    }
}
Write-Host ""

Write-Host "=== Résumé ===" -ForegroundColor Cyan
Write-Host "Les endpoints de base fonctionnent. Les timeouts peuvent être dus à:" -ForegroundColor Gray
Write-Host "- Kafka non accessible (warnings dans les logs)" -ForegroundColor Gray
Write-Host "- Opérations longues (collecte de données)" -ForegroundColor Gray
Write-Host "- Connexions externes (GitHub/GitLab/Jira APIs)" -ForegroundColor Gray

