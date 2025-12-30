# PowerShell script for Windows users

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "PRIORITEST CI/CD Quick Start" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Start infrastructure
Write-Host "STEP 1: Starting Docker infrastructure..." -ForegroundColor Yellow
docker-compose up -d jenkins sonarqube postgres
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30
Write-Host "✓ Infrastructure started" -ForegroundColor Green
Write-Host ""

# Step 2: Get Jenkins password
Write-Host "STEP 2: Getting Jenkins admin password..." -ForegroundColor Yellow
$jenkinsPassword = docker exec prioritest-jenkins cat /var/jenkins_home/secrets/initialAdminPassword 2>$null
if ($jenkinsPassword) {
    Write-Host "Jenkins Admin Password: $jenkinsPassword" -ForegroundColor Green
    Write-Host "Save this password!" -ForegroundColor Yellow
} else {
    Write-Host "⚠ Could not get password. Check: docker logs prioritest-jenkins" -ForegroundColor Red
}
Write-Host ""

# Step 3: Instructions
Write-Host "STEP 3: Next Steps" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow
Write-Host "1. Open SonarQube: http://localhost:9000" -ForegroundColor White
Write-Host "   - Login: admin / admin" -ForegroundColor White
Write-Host "   - Create a token: My Account > Security > Generate Token" -ForegroundColor White
Write-Host ""
Write-Host "2. Open Jenkins: http://localhost:8080" -ForegroundColor White
Write-Host "   - Login: admin / $jenkinsPassword" -ForegroundColor White
Write-Host "   - Install suggested plugins" -ForegroundColor White
Write-Host ""
Write-Host "3. Configure SonarQube in Jenkins:" -ForegroundColor White
Write-Host "   - Manage Jenkins > Configure System" -ForegroundColor White
Write-Host "   - Add SonarQube server: http://sonarqube:9000" -ForegroundColor White
Write-Host ""
Write-Host "4. Create Multibranch Pipeline job:" -ForegroundColor White
Write-Host "   - New Item > PRIORITEST > Multibranch Pipeline" -ForegroundColor White
Write-Host "   - Add GitLab/GitHub as branch source" -ForegroundColor White
Write-Host ""
Write-Host "5. Configure webhook in GitLab/GitHub:" -ForegroundColor White
Write-Host "   - URL: http://localhost:8080/project/PRIORITEST" -ForegroundColor White
Write-Host ""
Write-Host "For detailed instructions, see: SETUP-CICD.md" -ForegroundColor Cyan
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Quick start complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan

