#!/usr/bin/env pwsh
# Quick Pipeline Status Checker
# Shows which services are running and their health

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PRIORITEST Services Status Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker containers
Write-Host "Docker Containers Status:" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

$containers = @(
    "prioritest-collecte-depots",
    "prioritest-analyse-statique",
    "prioritest-historique-tests",
    "prioritest-pretraitement-features",
    "prioritest-ml-service",
    "prioritest-moteur-priorisation",
    "prioritest-test-scaffolder"
)

foreach ($container in $containers) {
    $status = docker ps --filter "name=$container" --format "{{.Status}}" 2>$null
    if ($status) {
        Write-Host "[OK] $($container.PadRight(40)) $status" -ForegroundColor Green
    } else {
        Write-Host "[X]  $($container.PadRight(40)) Not Running" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Health Endpoints:" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

$healthEndpoints = @(
    @{ Service = "S1"; Url = "http://localhost:8001/health" },
    @{ Service = "S2"; Url = "http://localhost:8081/actuator/health" },
    @{ Service = "S3"; Url = "http://localhost:8082/actuator/health" },
    @{ Service = "S4"; Url = "http://localhost:8000/health" },
    @{ Service = "S5"; Url = "http://localhost:8001/health" },
    @{ Service = "S6"; Url = "http://localhost:8006/health" },
    @{ Service = "S7"; Url = "http://localhost:8007/health" }
)

foreach ($endpoint in $healthEndpoints) {
    try {
        $response = Invoke-WebRequest -Uri $endpoint.Url -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        Write-Host "[OK] $($endpoint.Service.PadRight(5)) $($endpoint.Url)" -ForegroundColor Green
    } catch {
        Write-Host "[X]  $($endpoint.Service.PadRight(5)) $($endpoint.Url)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "API Gateway:" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
try {
    $gatewayHealth = Invoke-RestMethod -Uri "http://localhost:8090/actuator/health" -TimeoutSec 2
    Write-Host "[OK] API Gateway: http://localhost:8090" -ForegroundColor Green
    Write-Host "    Status: $($gatewayHealth.status)" -ForegroundColor Gray
} catch {
    Write-Host "[X]  API Gateway: http://localhost:8090" -ForegroundColor Red
}

Write-Host ""
Write-Host "Useful Commands:" -ForegroundColor Yellow
Write-Host "  - Monitor pipeline: .\scripts\monitor-pipeline.ps1 -RepositoryId 'repo_id' -Follow" -ForegroundColor White
Write-Host "  - View all logs: docker-compose logs -f" -ForegroundColor White
Write-Host "  - View S1 logs: docker logs prioritest-collecte-depots -f" -ForegroundColor White
Write-Host "  - Restart services: docker-compose restart" -ForegroundColor White
Write-Host ""
