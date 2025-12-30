#!/usr/bin/env pwsh
# Pipeline Monitoring Script for PRIORITEST
# Monitors all services S1-S7 and shows pipeline progress

param(
    [string]$RepositoryId = "",
    [switch]$Follow = $false,
    [int]$Interval = 5
)

$ErrorActionPreference = "Continue"

# Service definitions
$services = @(
    @{ Name = "S1-CollecteDepots"; Port = 8001; Path = "/health"; Container = "prioritest-collecte-depots" },
    @{ Name = "S2-AnalyseStatique"; Port = 8081; Path = "/actuator/health"; Container = "prioritest-analyse-statique" },
    @{ Name = "S3-HistoriqueTests"; Port = 8082; Path = "/actuator/health"; Container = "prioritest-historique-tests" },
    @{ Name = "S4-PretraitementFeatures"; Port = 8000; Path = "/health"; Container = "prioritest-pretraitement-features" },
    @{ Name = "S5-MLService"; Port = 8001; Path = "/health"; Container = "prioritest-ml-service" },
    @{ Name = "S6-MoteurPriorisation"; Port = 8006; Path = "/health"; Container = "prioritest-moteur-priorisation" },
    @{ Name = "S7-TestScaffolder"; Port = 8007; Path = "/health"; Container = "prioritest-test-scaffolder" }
)

function Check-ServiceHealth {
    param($Service)
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$($Service.Port)$($Service.Path)" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        return @{ Status = "✓ Healthy"; Color = "Green" }
    } catch {
        return @{ Status = "✗ Unhealthy"; Color = "Red" }
    }
}

function Get-ContainerStatus {
    param($ContainerName)
    
    try {
        $container = docker ps --filter "name=$ContainerName" --format "{{.Status}}" 2>$null
        if ($container) {
            return $container
        } else {
            return "Not Running"
        }
    } catch {
        return "Unknown"
    }
}

function Show-PipelineStatus {
    Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║         PRIORITEST Pipeline Status Monitor (S1-S7)          ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Service Health Status:" -ForegroundColor Yellow
    Write-Host "─────────────────────────────────────────────────────────────────" -ForegroundColor Gray
    
    foreach ($service in $services) {
        $health = Check-ServiceHealth -Service $service
        $containerStatus = Get-ContainerStatus -ContainerName $service.Container
        
        Write-Host "$($service.Name.PadRight(30)) " -NoNewline
        Write-Host "$($health.Status.PadRight(15)) " -NoNewline -ForegroundColor $health.Color
        Write-Host "Container: $containerStatus" -ForegroundColor Gray
    }
    
    Write-Host ""
}

function Show-PipelineProgress {
    param($RepoId)
    
    if (-not $RepoId) {
        Write-Host "`n⚠ No repository ID provided. Use -RepositoryId to track specific pipeline." -ForegroundColor Yellow
        return
    }
    
    Write-Host "`nPipeline Progress for Repository: $RepoId" -ForegroundColor Cyan
    Write-Host "─────────────────────────────────────────────────────────────────" -ForegroundColor Gray
    
    # Check S1 - Collection
    Write-Host "S1 (Collection): " -NoNewline
    $s1Logs = docker logs prioritest-collecte-depots --tail=20 2>&1 | Select-String -Pattern "Starting full analysis pipeline|Step 1|Step 2|Step 3|Step 4|Step 5" | Select-Object -Last 1
    if ($s1Logs) {
        Write-Host $s1Logs -ForegroundColor Green
    } else {
        Write-Host "No recent activity" -ForegroundColor Gray
    }
    
    # Check S2 - Static Analysis (via Kafka)
    Write-Host "S2 (Static Analysis): " -NoNewline
    $s2Logs = docker logs prioritest-analyse-statique --tail=10 2>&1 | Select-String -Pattern "Processing commit|Analyzed|Metrics" | Select-Object -Last 1
    if ($s2Logs) {
        Write-Host $s2Logs -ForegroundColor Green
    } else {
        Write-Host "Waiting for Kafka events..." -ForegroundColor Yellow
    }
    
    # Check S4 - Preprocessing
    Write-Host "S4 (Preprocessing): " -NoNewline
    $s4Logs = docker logs prioritest-pretraitement-features --tail=10 2>&1 | Select-String -Pattern "Preprocessing|Features prepared|completed" | Select-Object -Last 1
    if ($s4Logs) {
        Write-Host $s4Logs -ForegroundColor Green
    } else {
        Write-Host "Not started yet" -ForegroundColor Gray
    }
    
    # Check S5 - ML Predictions
    Write-Host "S5 (ML Predictions): " -NoNewline
    $s5Logs = docker logs prioritest-ml-service --tail=10 2>&1 | Select-String -Pattern "Predictions|Batch prediction|completed" | Select-Object -Last 1
    if ($s5Logs) {
        Write-Host $s5Logs -ForegroundColor Green
    } else {
        Write-Host "Not started yet" -ForegroundColor Gray
    }
    
    # Check S6 - Prioritization
    Write-Host "S6 (Prioritization): " -NoNewline
    $s6Logs = docker logs prioritest-moteur-priorisation --tail=10 2>&1 | Select-String -Pattern "Prioritization|prioritized|completed" | Select-Object -Last 1
    if ($s6Logs) {
        Write-Host $s6Logs -ForegroundColor Green
    } else {
        Write-Host "Not started yet" -ForegroundColor Gray
    }
    
    # Check S7 - Test Scaffolding (optional)
    Write-Host "S7 (Test Scaffolding): " -NoNewline
    $s7Logs = docker logs prioritest-test-scaffolder --tail=10 2>&1 | Select-String -Pattern "Generated|Test scaffold" | Select-Object -Last 1
    if ($s7Logs) {
        Write-Host $s7Logs -ForegroundColor Green
    } else {
        Write-Host "Not started (optional step)" -ForegroundColor Gray
    }
    
    Write-Host ""
}

function Show-RecentLogs {
    param($ServiceName, $ContainerName, $Lines = 5)
    
    Write-Host "`nRecent logs for $ServiceName:" -ForegroundColor Cyan
    Write-Host "─────────────────────────────────────────────────────────────────" -ForegroundColor Gray
    docker logs $ContainerName --tail=$Lines 2>&1 | ForEach-Object {
        if ($_ -match "ERROR|WARNING|Step|Starting|completed|failed") {
            if ($_ -match "ERROR|failed") {
                Write-Host $_ -ForegroundColor Red
            } elseif ($_ -match "WARNING") {
                Write-Host $_ -ForegroundColor Yellow
            } elseif ($_ -match "Step|Starting|completed") {
                Write-Host $_ -ForegroundColor Green
            } else {
                Write-Host $_ -ForegroundColor White
            }
        } else {
            Write-Host $_ -ForegroundColor Gray
        }
    }
}

# Main execution
if ($Follow) {
    Write-Host "Following pipeline progress (Press Ctrl+C to stop)..." -ForegroundColor Yellow
    Write-Host ""
    
    while ($true) {
        Clear-Host
        Show-PipelineStatus
        if ($RepositoryId) {
            Show-PipelineProgress -RepoId $RepositoryId
        }
        Write-Host "Refreshing in $Interval seconds... (Press Ctrl+C to stop)" -ForegroundColor Gray
        Start-Sleep -Seconds $Interval
    }
} else {
    Show-PipelineStatus
    if ($RepositoryId) {
        Show-PipelineProgress -RepoId $RepositoryId
    }
    
    Write-Host "`nQuick Commands:" -ForegroundColor Yellow
    Write-Host "  • Monitor specific repo: .\scripts\monitor-pipeline.ps1 -RepositoryId 'github_org_repo' -Follow" -ForegroundColor White
    Write-Host "  • Check all services: .\scripts\monitor-pipeline.ps1" -ForegroundColor White
    Write-Host "  • View S1 logs: docker logs prioritest-collecte-depots --tail=50 -f" -ForegroundColor White
    Write-Host "  • View S2 logs: docker logs prioritest-analyse-statique --tail=50 -f" -ForegroundColor White
    Write-Host "  • View all logs: docker-compose logs -f" -ForegroundColor White
    Write-Host ""
}

