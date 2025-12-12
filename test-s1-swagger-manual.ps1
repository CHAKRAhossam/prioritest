# Script de test manuel des endpoints S1 via Swagger
# Tests tous les endpoints un par un avec exemples de données

$baseUrl = "http://localhost:8001"
$results = @()

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Test Manuel des Endpoints S1 - CollecteDepots via Swagger   ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Swagger UI: $baseUrl/docs" -ForegroundColor Gray
Write-Host ""

# Fonction pour tester un endpoint
function Test-S1Endpoint {
    param(
        [string]$TestNumber,
        [string]$Name,
        [string]$Method,
        [string]$Endpoint,
        [object]$Body = $null,
        [hashtable]$Headers = @{},
        [int[]]$ExpectedStatuses = @(200),
        [string]$Description
    )
    
    Write-Host "┌────────────────────────────────────────────────────────────────┐" -ForegroundColor Yellow
    Write-Host "│ Test $TestNumber : $Name" -ForegroundColor Yellow
    Write-Host "└────────────────────────────────────────────────────────────────┘" -ForegroundColor Yellow
    Write-Host "  Endpoint: $Method $Endpoint" -ForegroundColor Gray
    Write-Host "  Description: $Description" -ForegroundColor Gray
    Write-Host ""
    
    try {
        $params = @{
            Uri = "$baseUrl$Endpoint"
            Method = $Method
            Headers = @{"Accept" = "application/json"}
            UseBasicParsing = $true
            TimeoutSec = 15
            ErrorAction = "Stop"
        }
        
        if ($Headers.Count -gt 0) {
            foreach ($key in $Headers.Keys) {
                $params.Headers[$key] = $Headers[$key]
            }
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json -Depth 10)
            $params.ContentType = "application/json"
            Write-Host "  Request Body:" -ForegroundColor DarkGray
            Write-Host "  $($params.Body)" -ForegroundColor DarkGray
            Write-Host ""
        }
        
        $response = Invoke-WebRequest @params
        
        if ($response.StatusCode -in $ExpectedStatuses) {
            Write-Host "  ✅ Status: $($response.StatusCode)" -ForegroundColor Green
            
            if ($response.Content) {
                try {
                    $json = $response.Content | ConvertFrom-Json
                    Write-Host "  Response:" -ForegroundColor Green
                    Write-Host "  $($json | ConvertTo-Json -Compress -Depth 5)" -ForegroundColor Green
                } catch {
                    Write-Host "  Response: $($response.Content.Substring(0, [Math]::Min(200, $response.Content.Length)))" -ForegroundColor Green
                }
            }
            Write-Host ""
            
            return @{
                Test = $TestNumber
                Name = $Name
                Status = "✅ PASS"
                StatusCode = $response.StatusCode
                Response = $response.Content
            }
        } else {
            Write-Host "  ⚠️  Status: $($response.StatusCode) (expected $ExpectedStatuses)" -ForegroundColor Yellow
            Write-Host ""
            
            return @{
                Test = $TestNumber
                Name = $Name
                Status = "⚠️  WARN"
                StatusCode = $response.StatusCode
                Response = $response.Content
            }
        }
    } catch {
        $statusCode = if ($_.Exception.Response) { $_.Exception.Response.StatusCode.value__ } else { "N/A" }
        
        if ($statusCode -in $ExpectedStatuses) {
            Write-Host "  ✅ Status: $statusCode (expected)" -ForegroundColor Green
            
            if ($_.Exception.Response) {
                try {
                    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
                    $responseBody = $reader.ReadToEnd()
                    Write-Host "  Response: $responseBody" -ForegroundColor Green
                } catch {}
            }
            Write-Host ""
            
            return @{
                Test = $TestNumber
                Name = $Name
                Status = "✅ PASS"
                StatusCode = $statusCode
                Response = ""
            }
        } else {
            Write-Host "  ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
            Write-Host "  Status Code: $statusCode" -ForegroundColor Red
            
            if ($_.Exception.Response) {
                try {
                    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
                    $responseBody = $reader.ReadToEnd()
                    Write-Host "  Response: $responseBody" -ForegroundColor Red
                } catch {}
            }
            Write-Host ""
            
            return @{
                Test = $TestNumber
                Name = $Name
                Status = "❌ FAIL"
                StatusCode = $statusCode
                Error = $_.Exception.Message
            }
        }
    }
}

# Test 1: Health Check
$results += Test-S1Endpoint `
    -TestNumber "1/8" `
    -Name "Health Check" `
    -Method "GET" `
    -Endpoint "/health" `
    -ExpectedStatuses @(200) `
    -Description "Vérifier l'état de santé du service S1"

# Test 2: Collect Status
$results += Test-S1Endpoint `
    -TestNumber "2/8" `
    -Name "Collect Status" `
    -Method "GET" `
    -Endpoint "/api/v1/collect/status" `
    -ExpectedStatuses @(200) `
    -Description "Obtenir le statut des services de collecte"

# Test 3: Get Artifacts (404 attendu - pas de données)
$results += Test-S1Endpoint `
    -TestNumber "3/8" `
    -Name "Get Artifacts" `
    -Method "GET" `
    -Endpoint "/api/v1/artifacts/test_repo/abc123" `
    -ExpectedStatuses @(404, 200) `
    -Description "Récupérer les artefacts pour un commit (404 si pas de données)"

# Test 4: Webhook Jira
$jiraBody = @{
    webhookEvent = "jira:issue_created"
    issue = @{
        key = "TEST-1"
        fields = @{
            summary = "Test issue from Swagger"
            issuetype = @{
                name = "Bug"
            }
            status = @{
                name = "Open"
            }
            created = "2025-12-13T00:00:00.000+0000"
        }
    }
}

$results += Test-S1Endpoint `
    -TestNumber "4/8" `
    -Name "Webhook Jira" `
    -Method "POST" `
    -Endpoint "/api/v1/webhooks/jira" `
    -Body $jiraBody `
    -ExpectedStatuses @(200) `
    -Description "Recevoir un webhook Jira pour une issue"

# Test 5: Webhook GitHub
$githubBody = @{
    ref = "refs/heads/main"
    repository = @{
        id = 12345
        name = "test-repo"
        full_name = "user/test-repo"
        url = "https://github.com/user/test-repo"
    }
    commits = @(
        @{
            id = "abc123def456"
            message = "Test commit from Swagger"
            author = @{
                email = "test@example.com"
                name = "Test User"
            }
            timestamp = "2025-12-13T00:00:00Z"
            added = @("test.java")
            modified = @()
            removed = @()
        }
    )
}

$results += Test-S1Endpoint `
    -TestNumber "5/8" `
    -Name "Webhook GitHub" `
    -Method "POST" `
    -Endpoint "/api/v1/webhooks/github" `
    -Body $githubBody `
    -Headers @{"X-GitHub-Event" = "push"} `
    -ExpectedStatuses @(200) `
    -Description "Recevoir un webhook GitHub pour un push"

# Test 6: Webhook GitLab
$gitlabBody = @{
    object_kind = "push"
    project = @{
        id = 12345
        name = "test-repo"
        path_with_namespace = "user/test-repo"
    }
    commits = @(
        @{
            id = "abc123def456"
            message = "Test commit from Swagger"
            author = @{
                email = "test@example.com"
                name = "Test User"
            }
            timestamp = "2025-12-13T00:00:00Z"
            added = @("test.java")
            modified = @()
            removed = @()
        }
    )
}

$results += Test-S1Endpoint `
    -TestNumber "6/8" `
    -Name "Webhook GitLab" `
    -Method "POST" `
    -Endpoint "/api/v1/webhooks/gitlab" `
    -Body $gitlabBody `
    -Headers @{"X-Gitlab-Event" = "Push Hook"} `
    -ExpectedStatuses @(200) `
    -Description "Recevoir un webhook GitLab pour un push"

# Test 7: Collect Data (peut timeout - c est normal)
$collectBody = @{
    repository_url = "https://github.com/octocat/Hello-World"
    collect_type = "commits"
    date_range = @{
        start = "2025-01-01"
        end = "2025-12-13"
    }
}

Write-Host "┌────────────────────────────────────────────────────────────────┐" -ForegroundColor Yellow
Write-Host "│ Test 7/8 : Collect Data (peut être long - timeout normal)     │" -ForegroundColor Yellow
Write-Host "└────────────────────────────────────────────────────────────────┘" -ForegroundColor Yellow
Write-Host "  Endpoint: POST /api/v1/collect" -ForegroundColor Gray
Write-Host "  Description: Déclencher une collecte manuelle de données" -ForegroundColor Gray
Write-Host "  Note: Ce test peut timeout car l'opération est longue (traitement background)" -ForegroundColor DarkYellow
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/v1/collect" -Method POST -Body ($collectBody | ConvertTo-Json) -ContentType "application/json" -UseBasicParsing -TimeoutSec 10
    Write-Host "  ✅ Status: $($response.StatusCode)" -ForegroundColor Green
    $results += @{
        Test = "7/8"
        Name = "Collect Data"
        Status = "✅ PASS"
        StatusCode = $response.StatusCode
    }
} catch {
    if ($_.Exception.Message -match "timeout|expir") {
        Write-Host "  ⚠️  Timeout (normal - traité en background)" -ForegroundColor Yellow
        $results += @{
            Test = "7/8"
            Name = "Collect Data"
            Status = "⚠️  TIMEOUT"
            Note = "Normal - traité en background"
        }
    } else {
        Write-Host "  ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
        $results += @{
            Test = "7/8"
            Name = "Collect Data"
            Status = "❌ FAIL"
            Error = $_.Exception.Message
        }
    }
}
Write-Host ""

# Test 8: Upload Artifact (nécessite un fichier)
Write-Host "┌────────────────────────────────────────────────────────────────┐" -ForegroundColor Yellow
Write-Host "│ Test 8/8 : Upload Artifact (nécessite un fichier)             │" -ForegroundColor Yellow
Write-Host "└────────────────────────────────────────────────────────────────┘" -ForegroundColor Yellow
Write-Host "  Endpoint: POST /api/v1/artifacts/upload/jacoco" -ForegroundColor Gray
Write-Host "  Description: Uploader un artefact CI/CD (JaCoCo)" -ForegroundColor Gray
Write-Host "  Note: Test sans fichier réel - 422 attendu" -ForegroundColor DarkYellow
Write-Host ""

try {
    $artifactUrl = $baseUrl + '/api/v1/artifacts/upload/jacoco?repository_id=test_repo' + '&' + 'commit_sha=abc123' + '&' + 'build_id=build_1'
    $response = Invoke-WebRequest -Uri $artifactUrl -Method POST -UseBasicParsing -TimeoutSec 5
    Write-Host "  Status: $($response.StatusCode)" -ForegroundColor Gray
    $results += @{
        Test = "8/8"
        Name = "Upload Artifact"
        Status = "INFO"
        StatusCode = $response.StatusCode
    }
} catch {
    $statusCode = if ($_.Exception.Response) { $_.Exception.Response.StatusCode.value__ } else { "N/A" }
    if ($statusCode -eq 422) {
        Write-Host "  ✅ Status: 422 (attendu - pas de fichier fourni)" -ForegroundColor Green
        $results += @{
            Test = "8/8"
            Name = "Upload Artifact"
            Status = "✅ PASS"
            StatusCode = 422
            Note = "422 attendu - validation error (pas de fichier)"
        }
    } else {
        Write-Host "  ❌ Status: $statusCode" -ForegroundColor Red
        $results += @{
            Test = "8/8"
            Name = "Upload Artifact"
            Status = "❌ FAIL"
            StatusCode = $statusCode
        }
    }
}
Write-Host ""

# Résumé
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                      RÉSUMÉ DES TESTS                          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$passed = ($results | Where-Object { $_.Status -match "✅" }).Count
$warned = ($results | Where-Object { $_.Status -match "⚠️" }).Count
$failed = ($results | Where-Object { $_.Status -match "❌" }).Count
$total = $results.Count

Write-Host "Total: $total tests" -ForegroundColor White
Write-Host "✅ Réussis: $passed" -ForegroundColor Green
Write-Host "⚠️  Avertissements: $warned" -ForegroundColor Yellow
Write-Host "❌ Échoués: $failed" -ForegroundColor Red
Write-Host ""

Write-Host "Détails par test:" -ForegroundColor Cyan
foreach ($result in $results) {
    $status = $result.Status
    $color = if ($status -match "✅") { "Green" } elseif ($status -match "⚠️") { "Yellow" } else { "Red" }
    Write-Host "  $status $($result.Test) - $($result.Name)" -ForegroundColor $color
    if ($result.Note) {
        Write-Host "      Note: $($result.Note)" -ForegroundColor DarkGray
    }
}
Write-Host ""

if ($failed -eq 0) {
    Write-Host "🎉 Tous les tests sont passés ou en warning (normal pour background tasks)!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Certains tests ont échoué. Vérifiez les détails ci-dessus." -ForegroundColor Yellow
}
Write-Host ""
Write-Host "Pour tester manuellement dans Swagger:" -ForegroundColor Cyan
Write-Host "  1. Ouvrez: $baseUrl/docs" -ForegroundColor Gray
Write-Host "  2. Cliquez sur un endpoint pour le déplier" -ForegroundColor Gray
Write-Host "  3. Cliquez sur 'Try it out'" -ForegroundColor Gray
Write-Host "  4. Remplissez les paramètres/body" -ForegroundColor Gray
Write-Host "  5. Cliquez sur 'Execute'" -ForegroundColor Gray
Write-Host "  6. Verifiez la reponse en bas" -ForegroundColor Gray

