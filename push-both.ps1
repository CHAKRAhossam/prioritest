# Script PowerShell pour pousser vers GitHub et GitLab
# Continue même si l'un des deux échoue

Write-Host "🚀 Pushing to both repositories..." -ForegroundColor Cyan
Write-Host ""

# Pousser vers GitHub
Write-Host "📤 Pushing to GitHub..." -ForegroundColor Yellow
git push github main

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ GitHub push successful" -ForegroundColor Green
} else {
    Write-Host "❌ GitHub push failed" -ForegroundColor Red
}

Write-Host ""

# Pousser vers GitLab
Write-Host "📤 Pushing to GitLab..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ GitLab push successful" -ForegroundColor Green
} else {
    Write-Host "⚠️ GitLab push failed (this is OK if you have connection issues)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✨ Push process completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Repositories:" -ForegroundColor Cyan
Write-Host "  - GitHub: https://github.com/CHAKRAhossam/prioritest"
Write-Host "  - GitLab: https://gitlab.com/chakrahossam-group/prioritest"

