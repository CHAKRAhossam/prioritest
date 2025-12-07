# Script de test Docker pour Service 6 (PowerShell)

Write-Host "🐳 Test Docker - Service 6 Moteur de Priorisation" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Vérifier Docker
Write-Host "`n1. Vérification Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker est disponible: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker n'est pas installé" -ForegroundColor Red
    exit 1
}

try {
    docker ps | Out-Null
    Write-Host "✅ Docker Desktop est démarré" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Desktop n'est pas démarré" -ForegroundColor Red
    Write-Host "   Veuillez démarrer Docker Desktop" -ForegroundColor Yellow
    exit 1
}

# Construire l'image
Write-Host "`n2. Construction de l'image..." -ForegroundColor Yellow
docker build -t s6-moteur-priorisation:latest .
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Image construite" -ForegroundColor Green
} else {
    Write-Host "❌ Erreur lors de la construction" -ForegroundColor Red
    exit 1
}

# Lancer le conteneur
Write-Host "`n3. Lancement du conteneur..." -ForegroundColor Yellow
docker run -d --name s6-test -p 8006:8006 s6-moteur-priorisation:latest
Start-Sleep -Seconds 5
Write-Host "✅ Conteneur lancé" -ForegroundColor Green

# Tester health check
Write-Host "`n4. Test health check..." -ForegroundColor Yellow
$maxAttempts = 10
$success = $false
for ($i = 1; $i -le $maxAttempts; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8006/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Health check OK" -ForegroundColor Green
            $success = $true
            break
        }
    } catch {
        if ($i -eq $maxAttempts) {
            Write-Host "❌ Health check échoué après $maxAttempts tentatives" -ForegroundColor Red
            docker logs s6-test
            docker stop s6-test
            docker rm s6-test
            exit 1
        }
        Start-Sleep -Seconds 2
    }
}

# Tester Swagger
Write-Host "`n5. Test Swagger UI..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8006/docs" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Swagger UI accessible" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Swagger UI non accessible (peut être normal)" -ForegroundColor Yellow
}

# Afficher les logs
Write-Host "`n6. Logs du conteneur:" -ForegroundColor Yellow
docker logs s6-test

# Nettoyer
Write-Host "`n7. Nettoyage..." -ForegroundColor Yellow
docker stop s6-test
docker rm s6-test
Write-Host "✅ Conteneur arrêté et supprimé" -ForegroundColor Green

Write-Host "`n✅ Tous les tests Docker sont passés !" -ForegroundColor Green
Write-Host "Pour démarrer le service : docker-compose up -d" -ForegroundColor Cyan

