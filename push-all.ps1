# Script PowerShell pour pousser vers GitLab et GitHub simultanément

Write-Host "Pushing to GitLab and GitHub..." -ForegroundColor Cyan
git push origin main

Write-Host ""
Write-Host "✅ Push completed to both repositories:" -ForegroundColor Green
Write-Host "   - GitLab: https://gitlab.com/chakrahossam-group/prioritest"
Write-Host "   - GitHub: https://github.com/CHAKRAhossam/prioritest"

