# Test simple et rapide des endpoints principaux
# Usage: .\test-simple.ps1

$BASE_URL = "http://localhost:8080"
$COMMIT = "test-$(Get-Date -Format 'yyyyMMddHHmmss')"

Write-Host "🧪 Test rapide de l'API" -ForegroundColor Cyan
Write-Host "=======================" -ForegroundColor Cyan
Write-Host ""

# 1. Upload JaCoCo
Write-Host "1️⃣  Upload JaCoCo report..." -ForegroundColor Yellow
$response = curl.exe -X POST "$BASE_URL/api/coverage/jacoco" `
  -F "file=@jacoco-sample.xml" `
  -F "commit=$COMMIT" `
  -F "buildId=build001" `
  -F "branch=main"
Write-Host $response
Write-Host ""

# 2. Upload Surefire
Write-Host "2️⃣  Upload Surefire report..." -ForegroundColor Yellow
$response = curl.exe -X POST "$BASE_URL/api/tests/surefire" `
  -F "file=@surefire-sample.xml" `
  -F "commit=$COMMIT" `
  -F "buildId=build001" `
  -F "branch=main"
Write-Host $response
Write-Host ""

# 3. Upload PIT
Write-Host "3️⃣  Upload PIT report..." -ForegroundColor Yellow
$response = curl.exe -X POST "$BASE_URL/api/coverage/pit" `
  -F "file=@pit-sample.xml" `
  -F "commit=$COMMIT"
Write-Host $response
Write-Host ""

# 4. Get coverage summary
Write-Host "4️⃣  Get coverage summary..." -ForegroundColor Yellow
$response = curl.exe -X GET "$BASE_URL/api/coverage/commit/$COMMIT"
Write-Host $response
Write-Host ""

# 5. Get test summary
Write-Host "5️⃣  Get test summary..." -ForegroundColor Yellow
$response = curl.exe -X GET "$BASE_URL/api/tests/commit/$COMMIT"
Write-Host $response
Write-Host ""

# 6. Get aggregated metrics
Write-Host "6️⃣  Get aggregated metrics..." -ForegroundColor Yellow
$response = curl.exe -X GET "$BASE_URL/api/metrics/commit/$COMMIT"
Write-Host $response
Write-Host ""

# 7. Calculate test debt
Write-Host "7️⃣  Calculate test debt..." -ForegroundColor Yellow
$response = curl.exe -X POST "$BASE_URL/api/debt/calculate/$COMMIT"
Write-Host $response
Write-Host ""

# 8. Get debt summary
Write-Host "8️⃣  Get debt summary..." -ForegroundColor Yellow
$response = curl.exe -X GET "$BASE_URL/api/debt/commit/$COMMIT"
Write-Host $response
Write-Host ""

Write-Host "✅ Tests terminés pour commit: $COMMIT" -ForegroundColor Green

