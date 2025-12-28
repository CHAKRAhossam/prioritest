# PowerShell script to help configure SonarQube in Jenkins

param(
    [string]$JenkinsUrl = "http://localhost:8080",
    [string]$SonarQubeUrl = "http://localhost:9000",
    [Parameter(Mandatory=$true)]
    [string]$SonarToken
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Jenkins SonarQube Configuration Helper" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Configuration Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Open Jenkins: $JenkinsUrl" -ForegroundColor White
Write-Host "2. Go to: Manage Jenkins → Configure System" -ForegroundColor White
Write-Host "3. Scroll to 'SonarQube servers' section" -ForegroundColor White
Write-Host "4. Click 'Add SonarQube'" -ForegroundColor White
Write-Host "5. Fill in:" -ForegroundColor White
Write-Host "   - Name: SonarQube" -ForegroundColor Gray
Write-Host "   - Server URL: $SonarQubeUrl" -ForegroundColor Gray
Write-Host ""
Write-Host "6. For 'Server authentication token':" -ForegroundColor White
Write-Host "   - Click 'Add' → 'Jenkins'" -ForegroundColor Gray
Write-Host "   - Kind: Secret text" -ForegroundColor Gray
Write-Host "   - Secret: [Paste your token below]" -ForegroundColor Gray
Write-Host "   - ID: sonar-token" -ForegroundColor Gray
Write-Host "   - Description: SonarQube token" -ForegroundColor Gray
Write-Host "   - Click 'Add'" -ForegroundColor Gray
Write-Host ""
Write-Host "7. Select the credential you just created" -ForegroundColor White
Write-Host "8. Click 'Test connection' - should show 'Success'" -ForegroundColor White
Write-Host "9. Click 'Save'" -ForegroundColor White
Write-Host ""

Write-Host "Your SonarQube Token:" -ForegroundColor Yellow
Write-Host "$SonarToken" -ForegroundColor Green
Write-Host ""
Write-Host "Copy this token and paste it in step 6 above!" -ForegroundColor Cyan
Write-Host ""

# Check if Jenkins is accessible
try {
    $response = Invoke-WebRequest -Uri "$JenkinsUrl" -Method Get -TimeoutSec 5 -UseBasicParsing
    Write-Host "✓ Jenkins is accessible at $JenkinsUrl" -ForegroundColor Green
} catch {
    Write-Host "✗ Jenkins is not accessible at $JenkinsUrl" -ForegroundColor Red
    Write-Host "  Make sure Jenkins is running: docker-compose ps" -ForegroundColor Yellow
}

# Check if SonarQube is accessible
try {
    $response = Invoke-WebRequest -Uri "$SonarQubeUrl/api/system/status" -Method Get -TimeoutSec 5 -UseBasicParsing
    Write-Host "✓ SonarQube is accessible at $SonarQubeUrl" -ForegroundColor Green
} catch {
    Write-Host "✗ SonarQube is not accessible at $SonarQubeUrl" -ForegroundColor Red
    Write-Host "  Make sure SonarQube is running: docker-compose ps" -ForegroundColor Yellow
}

Write-Host ""

