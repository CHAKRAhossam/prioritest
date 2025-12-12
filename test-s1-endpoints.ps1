# Script de test des endpoints S1-CollecteDepots
# Teste tous les endpoints disponibles du service

$ErrorActionPreference = "Continue"
$baseUrl = "http://localhost:8001"

Write-Host "=== Test des Endpoints S1-CollecteDepots ===" -ForegroundColor Cyan
Write-Host "Base URL: $baseUrl" -ForegroundColor Gray
Write-Host ""

# Fonction pour tester un endpoint
function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Url,
        [hashtable]$Headers = @{},
        [object]$Body = $null,
        [int]$ExpectedStatus = 200
    )
    
    Write-Host "Testing: $Name" -ForegroundColor Yellow
    Write-Host "  $Method $Url" -ForegroundColor Gray
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            Headers = $Headers
            TimeoutSec = 30
            UseBasicParsing = $true
            ErrorAction = "Stop"
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json -Depth 10)
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-WebRequest @params
        
        if ($response.StatusCode -eq $ExpectedStatus) {
            Write-Host "  ✅ Status: $($response.StatusCode)" -ForegroundColor Green
            
            if ($response.Content) {
                try {
                    $json = $response.Content | ConvertFrom-Json
                    Write-Host "  Response: $($json | ConvertTo-Json -Compress -Depth 3)" -ForegroundColor DarkGray
                } catch {
                    Write-Host "  Response: $($response.Content.Substring(0, [Math]::Min(200, $response.Content.Length)))" -ForegroundColor DarkGray
                }
            }
            Write-Host ""
            return $true
        } else {
            Write-Host "  ⚠️  Status: $($response.StatusCode) (expected $ExpectedStatus)" -ForegroundColor Yellow
            Write-Host ""
            return $false
        }
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode -eq $ExpectedStatus) {
            Write-Host "  ✅ Status: $statusCode (expected)" -ForegroundColor Green
            Write-Host ""
            return $true
        } else {
            Write-Host "  ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
            if ($_.Exception.Response) {
                $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
                $responseBody = $reader.ReadToEnd()
                Write-Host "  Response: $responseBody" -ForegroundColor Red
            }
            Write-Host ""
            return $false
        }
    }
}

# Vérifier que le service est accessible
Write-Host "--- Vérification de l'accessibilité du service ---" -ForegroundColor Magenta
try {
    $healthCheck = Invoke-WebRequest -Uri "$baseUrl/health" -Method GET -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Service accessible (Status: $($healthCheck.StatusCode))" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ Service non accessible: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Vérifiez que le service S1 est démarré avec: docker-compose up -d collecte-depots" -ForegroundColor Yellow
    exit 1
}

# Tests des endpoints
$results = @{}

Write-Host "=== Tests des Endpoints ===" -ForegroundColor Cyan
Write-Host ""

# 1. Health Check
Write-Host "--- 1. Health Check ---" -ForegroundColor Magenta
$results["health"] = Test-Endpoint -Name "Health Check" -Method "GET" -Url "$baseUrl/health"

# 2. API Documentation
Write-Host "--- 2. Documentation API ---" -ForegroundColor Magenta
$results["docs"] = Test-Endpoint -Name "Swagger UI" -Method "GET" -Url "$baseUrl/docs" -ExpectedStatus 200
$results["openapi"] = Test-Endpoint -Name "OpenAPI JSON" -Method "GET" -Url "$baseUrl/openapi.json" -ExpectedStatus 200

# 3. Collect Endpoint
Write-Host "--- 3. Collect Endpoint ---" -ForegroundColor Magenta
$collectBody = @{
    repository_url = "https://github.com/octocat/Hello-World"
    collect_type = "commits"
    date_range = @{
        start = "2025-01-01"
        end = "2025-12-04"
    }
}
$results["collect"] = Test-Endpoint -Name "POST /api/v1/collect" -Method "POST" -Url "$baseUrl/api/v1/collect" -Body $collectBody -ExpectedStatus 202

# 4. Webhooks GitHub
Write-Host "--- 4. Webhooks GitHub ---" -ForegroundColor Magenta
$githubWebhookBody = @{
    ref = "refs/heads/main"
    repository = @{
        id = 12345
        name = "Hello-World"
        full_name = "octocat/Hello-World"
        url = "https://github.com/octocat/Hello-World"
    }
    commits = @(
        @{
            id = "abc123"
            message = "Test commit"
            author = @{
                email = "test@example.com"
                name = "Test User"
            }
            timestamp = "2025-12-04T10:30:00Z"
            added = @("file1.java")
            modified = @()
            removed = @()
        }
    )
}
$results["webhook_github"] = Test-Endpoint -Name "POST /api/v1/webhooks/github" -Method "POST" -Url "$baseUrl/api/v1/webhooks/github" -Body $githubWebhookBody -Headers @{"X-GitHub-Event" = "push"} -ExpectedStatus 200

# 5. Webhooks GitLab
Write-Host "--- 5. Webhooks GitLab ---" -ForegroundColor Magenta
$gitlabWebhookBody = @{
    object_kind = "push"
    project = @{
        id = 12345
        name = "Hello-World"
        path_with_namespace = "octocat/Hello-World"
    }
    commits = @(
        @{
            id = "abc123"
            message = "Test commit"
            author = @{
                email = "test@example.com"
                name = "Test User"
            }
            timestamp = "2025-12-04T10:30:00Z"
            added = @("file1.java")
            modified = @()
            removed = @()
        }
    )
}
$results["webhook_gitlab"] = Test-Endpoint -Name "POST /api/v1/webhooks/gitlab" -Method "POST" -Url "$baseUrl/api/v1/webhooks/gitlab" -Body $gitlabWebhookBody -Headers @{"X-Gitlab-Event" = "Push Hook"} -ExpectedStatus 200

# 6. Webhooks Jira
Write-Host "--- 6. Webhooks Jira ---" -ForegroundColor Magenta
$jiraWebhookBody = @{
    webhookEvent = "jira:issue_created"
    issue = @{
        key = "MTP-77"
        fields = @{
            summary = "Test issue"
            issuetype = @{
                name = "Bug"
            }
            status = @{
                name = "Open"
            }
            created = "2025-12-04T10:30:00.000+0000"
        }
    }
}
$results["webhook_jira"] = Test-Endpoint -Name "POST /api/v1/webhooks/jira" -Method "POST" -Url "$baseUrl/api/v1/webhooks/jira" -Body $jiraWebhookBody -ExpectedStatus 200

# 7. Artifacts Upload (JaCoCo)
Write-Host "--- 7. Artifacts Upload ---" -ForegroundColor Magenta
# Note: Ce test nécessite un fichier réel, on teste juste que l'endpoint existe
$results["artifacts_jacoco"] = Test-Endpoint -Name "POST /api/v1/artifacts/upload/jacoco" -Method "POST" -Url "$baseUrl/api/v1/artifacts/upload/jacoco" -Body @{} -ExpectedStatus 422

# 8. Get Artifacts
Write-Host "--- 8. Get Artifacts ---" -ForegroundColor Magenta
$results["artifacts_get"] = Test-Endpoint -Name "GET /api/v1/artifacts" -Method "GET" -Url "$baseUrl/api/v1/artifacts?repository_id=test_repo&commit_sha=abc123" -ExpectedStatus 200

# Résumé
Write-Host ""
Write-Host "=== Résumé des Tests ===" -ForegroundColor Cyan
$total = $results.Count
$passed = ($results.Values | Where-Object { $_ -eq $true }).Count
$failed = $total - $passed

Write-Host "Total: $total" -ForegroundColor White
Write-Host "✅ Réussis: $passed" -ForegroundColor Green
Write-Host "❌ Échoués: $failed" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Green" })

Write-Host ""
Write-Host "Détails:" -ForegroundColor Cyan
foreach ($key in $results.Keys) {
    $status = if ($results[$key]) { "✅" } else { "❌" }
    Write-Host "  $status $key" -ForegroundColor $(if ($results[$key]) { "Green" } else { "Red" })
}

Write-Host ""
if ($failed -eq 0) {
    Write-Host "🎉 Tous les tests sont passés!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Certains tests ont échoué. Vérifiez les logs ci-dessus." -ForegroundColor Yellow
}

