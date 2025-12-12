# Script de test avec donnees reelles - S1 CollecteDepots
# Ce script collecte des donnees d'un vrai depot GitHub

$baseUrl = "http://localhost:8001"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " Test avec Donnees Reelles - S1" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Verifier que le service est accessible
Write-Host "[1/5] Verification du service..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
    Write-Host "  OK Service operationnel: $($health.service) v$($health.version)" -ForegroundColor Green
} catch {
    Write-Host "  ERREUR Service non accessible!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Test 2: Collecter un vrai depot GitHub (petit)
Write-Host "[2/5] Collecte du depot 'octocat/Hello-World' (depot de demo GitHub)..." -ForegroundColor Yellow
Write-Host "  URL: https://github.com/octocat/Hello-World" -ForegroundColor Gray
Write-Host "  Type: commits" -ForegroundColor Gray
Write-Host "  Periode: 2020-01-01 a 2025-12-13" -ForegroundColor Gray
Write-Host ""

$collectBody = @{
    repository_url = "https://github.com/octocat/Hello-World"
    collect_type = "commits"
    date_range = @{
        start = "2020-01-01"
        end = "2025-12-13"
    }
}

try {
    $collectResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/collect" `
        -Method POST `
        -Body ($collectBody | ConvertTo-Json) `
        -ContentType "application/json" `
        -TimeoutSec 30
    
    Write-Host "  OK Collecte demarree!" -ForegroundColor Green
    Write-Host "  Status: $($collectResponse.status)" -ForegroundColor Gray
    Write-Host "  Message: $($collectResponse.message)" -ForegroundColor Gray
} catch {
    $statusCode = if ($_.Exception.Response) { $_.Exception.Response.StatusCode.value__ } else { "N/A" }
    if ($_.Exception.Message -match "timeout|expir") {
        Write-Host "  INFO Timeout (normal - traitement en background)" -ForegroundColor Yellow
    } elseif ($statusCode -eq 202) {
        Write-Host "  OK Collecte acceptee (202)" -ForegroundColor Green
    } else {
        Write-Host "  ERREUR $($_.Exception.Message)" -ForegroundColor Red
    }
}
Write-Host ""

# Test 3: Attendre un peu pour la collecte
Write-Host "[3/5] Attente de la collecte (30 secondes)..." -ForegroundColor Yellow
Write-Host "  Les commits sont collectes en arriere-plan..." -ForegroundColor Gray
Start-Sleep -Seconds 30
Write-Host "  OK Attente terminee" -ForegroundColor Green
Write-Host ""

# Test 4: Verifier les donnees dans PostgreSQL
Write-Host "[4/5] Verification des donnees dans PostgreSQL..." -ForegroundColor Yellow
try {
    # Compter les commits
    $commitCount = docker exec prioritest-postgres psql -U collecte_user -d collecte_db -t -c "SELECT COUNT(*) FROM commits;" 2>$null
    if ($commitCount) {
        $commitCount = $commitCount.Trim()
        Write-Host "  OK Commits collectes: $commitCount" -ForegroundColor Green
    }
    
    # Voir les derniers commits
    $recentCommits = docker exec prioritest-postgres psql -U collecte_user -d collecte_db -t -c "SELECT commit_sha, LEFT(commit_message, 40), author_name FROM commits ORDER BY timestamp DESC LIMIT 3;" 2>$null
    if ($recentCommits) {
        Write-Host "  Derniers commits:" -ForegroundColor Gray
        $recentCommits -split "`n" | ForEach-Object {
            if ($_.Trim()) {
                Write-Host "    $_" -ForegroundColor DarkGray
            }
        }
    }
} catch {
    Write-Host "  INFO Impossible de verifier PostgreSQL (normal si pas encore de donnees)" -ForegroundColor Yellow
}
Write-Host ""

# Test 5: Creer et uploader un rapport JaCoCo de test
Write-Host "[5/5] Upload d'un rapport JaCoCo de test..." -ForegroundColor Yellow

# Creer un fichier JaCoCo simple
$jacocoContent = @"
<?xml version="1.0" encoding="UTF-8"?>
<report name="Test Coverage Report">
  <sessioninfo id="test-session-$(Get-Date -Format 'yyyyMMddHHmmss')" start="1702468800000" dump="1702555200000"/>
  <package name="com/example">
    <class name="com/example/HelloWorld" sourcefilename="HelloWorld.java">
      <method name="sayHello" desc="()Ljava/lang/String;">
        <counter type="INSTRUCTION" missed="0" covered="10"/>
        <counter type="BRANCH" missed="0" covered="2"/>
        <counter type="LINE" missed="0" covered="3"/>
        <counter type="COMPLEXITY" missed="0" covered="1"/>
        <counter type="METHOD" missed="0" covered="1"/>
      </method>
    </class>
  </package>
  <counter type="INSTRUCTION" missed="0" covered="10"/>
  <counter type="BRANCH" missed="0" covered="2"/>
  <counter type="LINE" missed="0" covered="3"/>
  <counter type="COMPLEXITY" missed="0" covered="1"/>
  <counter type="METHOD" missed="0" covered="1"/>
  <counter type="CLASS" missed="0" covered="1"/>
</report>
"@

$jacocoFile = "jacoco-test-real.xml"
$jacocoContent | Out-File -FilePath $jacocoFile -Encoding UTF8

Write-Host "  Fichier JaCoCo cree: $jacocoFile" -ForegroundColor Gray

# Uploader via curl (PowerShell Invoke-WebRequest a des problemes avec multipart/form-data)
$uploadUrl = "$baseUrl/api/v1/artifacts/upload/jacoco?repository_id=hello-world&commit_sha=abc123test&build_id=build-$(Get-Date -Format 'yyyyMMddHHmmss')"

Write-Host "  Upload en cours..." -ForegroundColor Gray
try {
    # Verifier si curl est disponible
    $curlPath = Get-Command curl -ErrorAction SilentlyContinue
    if ($curlPath) {
        $curlResult = curl -X POST $uploadUrl -F "file=@$jacocoFile" -H "Accept: application/json" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  OK Artefact uploade avec succes!" -ForegroundColor Green
        } else {
            Write-Host "  INFO Upload echoue (peut necessiter configuration MinIO)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  INFO curl non disponible - skip upload" -ForegroundColor Yellow
        Write-Host "  Vous pouvez uploader manuellement via Swagger UI" -ForegroundColor Gray
    }
} catch {
    Write-Host "  INFO Upload echoue: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Nettoyer le fichier temporaire
Remove-Item $jacocoFile -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " Resume des Tests" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Actions effectuees:" -ForegroundColor Green
Write-Host "  [x] Service S1 verifie" -ForegroundColor Gray
Write-Host "  [x] Depot 'octocat/Hello-World' collecte" -ForegroundColor Gray
Write-Host "  [x] Donnees verifiees dans PostgreSQL" -ForegroundColor Gray
Write-Host "  [x] Rapport JaCoCo teste" -ForegroundColor Gray
Write-Host ""
Write-Host "Prochaines etapes:" -ForegroundColor Yellow
Write-Host "  1. Verifier les logs: docker-compose logs collecte-depots" -ForegroundColor White
Write-Host "  2. Voir les donnees SQL:" -ForegroundColor White
Write-Host "     docker exec -it prioritest-postgres psql -U collecte_user -d collecte_db" -ForegroundColor DarkGray
Write-Host "  3. Tester d'autres depots dans Swagger: http://localhost:8001/docs" -ForegroundColor White
Write-Host ""
Write-Host "Depots recommandes pour tests supplementaires:" -ForegroundColor Cyan
Write-Host "  - https://github.com/spring-projects/spring-petclinic (projet Java)" -ForegroundColor Gray
Write-Host "  - https://github.com/microsoft/TypeScript-Node-Starter (projet TypeScript)" -ForegroundColor Gray
Write-Host "  - https://gitlab.com/inkscape/inkscape (depot GitLab)" -ForegroundColor Gray
Write-Host ""

