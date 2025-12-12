# Script de test des services Prioritest
# Teste tous les endpoints principaux après démarrage Docker

Write-Host "=== Test des Services Prioritest ===" -ForegroundColor Cyan
Write-Host ""

# Fonction pour tester un endpoint
function Test-Endpoint {
    param(
        [string]$ServiceName,
        [string]$Url,
        [string]$Method = "GET",
        [string]$Body = $null
    )
    
    Write-Host "Testing $ServiceName : $Url" -ForegroundColor Yellow
    
    try {
        if ($Method -eq "GET") {
            $response = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        } else {
            $response = Invoke-WebRequest -Uri $Url -Method POST -Body $Body -ContentType "application/json" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        }
        
        if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 202) {
            Write-Host "  ✅ $ServiceName - Status: $($response.StatusCode)" -ForegroundColor Green
            if ($response.Content) {
                $json = $response.Content | ConvertFrom-Json
                Write-Host "  Response: $($json | ConvertTo-Json -Compress)" -ForegroundColor Gray
            }
            return $true
        } else {
            Write-Host "  ⚠️  $ServiceName - Status: $($response.StatusCode)" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "  ❌ $ServiceName - Error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    Write-Host ""
}

# Attendre que les services soient prêts
Write-Host "Waiting for services to be ready..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# Test Infrastructure
Write-Host "=== Infrastructure Services ===" -ForegroundColor Cyan
Test-Endpoint "PostgreSQL" "http://localhost:5432" -ErrorAction SilentlyContinue
Test-Endpoint "MinIO" "http://localhost:9000/minio/health/live"
Test-Endpoint "MLflow" "http://localhost:5000/health"

Write-Host ""
Write-Host "=== Microservices ===" -ForegroundColor Cyan

# S1 - CollecteDepots
Write-Host ""
Write-Host "--- S1: CollecteDepots ---" -ForegroundColor Magenta
Test-Endpoint "S1 Health" "http://localhost:8001/health"

# Test API collect
$collectBody = @{
    repository_url = "https://github.com/octocat/Hello-World"
    collect_type = "commits"
    date_range = @{
        start = "2025-01-01"
        end = "2025-12-04"
    }
} | ConvertTo-Json

Test-Endpoint "S1 Collect" "http://localhost:8001/api/v1/collect" "POST" $collectBody

# S2 - AnalyseStatique
Write-Host ""
Write-Host "--- S2: AnalyseStatique ---" -ForegroundColor Magenta
Test-Endpoint "S2 Health" "http://localhost:8081/health"

# S3 - HistoriqueTests
Write-Host ""
Write-Host "--- S3: HistoriqueTests ---" -ForegroundColor Magenta
Test-Endpoint "S3 Health" "http://localhost:8003/actuator/health"
Test-Endpoint "S3 Test Metrics" "http://localhost:8003/api/v1/test-metrics?class_name=com.example.UserService&repository_id=repo_12345"

# S5 - MLService
Write-Host ""
Write-Host "--- S5: MLService ---" -ForegroundColor Magenta
Test-Endpoint "S5 Health" "http://localhost:8005/health"

# Test prediction
$predictBody = @{
    class_name = "com.example.UserService"
    repository_id = "repo_12345"
    lines_modified = 150.0
    complexity = 12.0
    churn = 0.15
    num_authors = 3.0
    bug_fix_proximity = 0.8
} | ConvertTo-Json

Test-Endpoint "S5 Predict" "http://localhost:8005/api/v1/predict" "POST" $predictBody

# S6 - MoteurPriorisation
Write-Host ""
Write-Host "--- S6: MoteurPriorisation ---" -ForegroundColor Magenta
Test-Endpoint "S6 Health" "http://localhost:8006/health"

# S7 - TestScaffolder
Write-Host ""
Write-Host "--- S7: TestScaffolder ---" -ForegroundColor Magenta
Test-Endpoint "S7 Health" "http://localhost:8007/health"
Test-Endpoint "S7 Test Scaffold" "http://localhost:8007/api/v1/test-scaffold?class_name=com.example.UserService&priority=1"

# S8 - DashboardQualite
Write-Host ""
Write-Host "--- S8: DashboardQualite ---" -ForegroundColor Magenta
Test-Endpoint "S8 Health" "http://localhost:8008/health"
Test-Endpoint "S8 Overview" "http://localhost:8008/api/v1/dashboard/overview?repository_id=repo_12345"

# S9 - Integrations
Write-Host ""
Write-Host "--- S9: Integrations ---" -ForegroundColor Magenta
Test-Endpoint "S9 Health" "http://localhost:8009/api/v1/health/live"

Write-Host ""
Write-Host "=== Test Summary ===" -ForegroundColor Cyan
Write-Host "Tests completed. Check results above." -ForegroundColor Green

