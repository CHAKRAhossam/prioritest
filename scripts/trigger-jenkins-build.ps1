# Script PowerShell pour déclencher un build Jenkins et suivre les logs

$JenkinsUrl = "http://localhost:8080"
$JobName = "PRIORITEST"
$BranchName = "main"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Déclenchement du pipeline Jenkins" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Récupérer le mot de passe Jenkins depuis le conteneur
Write-Host "Récupération du mot de passe Jenkins..." -ForegroundColor Yellow
$JenkinsPassword = docker exec prioritest-jenkins cat /var/jenkins_home/secrets/initialAdminPassword 2>$null
if (-not $JenkinsPassword) {
    Write-Host "⚠️  Impossible de récupérer le mot de passe. Utilisation de l'API sans authentification..." -ForegroundColor Yellow
    $JenkinsPassword = ""
}

# Créer les credentials pour l'authentification
$pair = "admin:$JenkinsPassword"
$bytes = [System.Text.Encoding]::ASCII.GetBytes($pair)
$base64 = [System.Convert]::ToBase64String($bytes)
$headers = @{
    Authorization = "Basic $base64"
}

# Déclencher le build
Write-Host "Déclenchement du build pour $JobName/$BranchName..." -ForegroundColor Yellow
try {
    $buildUrl = "$JenkinsUrl/job/$JobName/job/$BranchName/build"
    $response = Invoke-WebRequest -Uri $buildUrl -Method Post -Headers $headers -UseBasicParsing
    
    if ($response.StatusCode -eq 201 -or $response.StatusCode -eq 200) {
        Write-Host "✅ Build déclenché avec succès!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Pour suivre les logs en temps réel:" -ForegroundColor Cyan
        Write-Host "  1. Ouvrez: $JenkinsUrl/job/$JobName/job/$BranchName" -ForegroundColor White
        Write-Host "  2. Cliquez sur le dernier build" -ForegroundColor White
        Write-Host "  3. Cliquez sur 'Console Output'" -ForegroundColor White
        Write-Host ""
        Write-Host "Ou utilisez cette commande pour voir les logs:" -ForegroundColor Cyan
        Write-Host "  docker exec prioritest-jenkins tail -f /var/jenkins_home/jobs/$JobName/branches/$BranchName/builds/*/log" -ForegroundColor White
    } else {
        Write-Host "⚠️  Réponse inattendue: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Erreur lors du déclenchement du build: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Essayez de déclencher le build manuellement depuis l'interface Jenkins:" -ForegroundColor Yellow
    Write-Host "  $JenkinsUrl/job/$JobName/job/$BranchName" -ForegroundColor White
}

Write-Host ""
Write-Host "Pour voir les logs du dernier build:" -ForegroundColor Cyan
Write-Host "  docker exec prioritest-jenkins bash -c 'ls -t /var/jenkins_home/jobs/$JobName/branches/$BranchName/builds/ | head -1 | xargs -I {} cat /var/jenkins_home/jobs/$JobName/branches/$BranchName/builds/{}/log | tail -50'" -ForegroundColor White





