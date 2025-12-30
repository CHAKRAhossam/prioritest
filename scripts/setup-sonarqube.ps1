# PowerShell script to setup SonarQube Quality Gates and Profiles

param(
    [string]$SonarQubeUrl = "http://localhost:9000",
    [Parameter(Mandatory=$true)]
    [string]$SonarToken
)

Write-Host "Setting up SonarQube Quality Gates and Profiles for PRIORITEST..." -ForegroundColor Cyan

# Create Quality Gate
Write-Host "Creating Quality Gate..." -ForegroundColor Yellow
$createGateResponse = Invoke-RestMethod -Uri "$SonarQubeUrl/api/qualitygates/create" `
    -Method Post `
    -Headers @{Authorization = "Basic $([Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${SonarToken}:")))"} `
    -Body @{name = "PRIORITEST Quality Gate"} `
    -ContentType "application/x-www-form-urlencoded"

# Get Quality Gate ID
Write-Host "Getting Quality Gate ID..." -ForegroundColor Yellow
$gateInfo = Invoke-RestMethod -Uri "$SonarQubeUrl/api/qualitygates/show?name=PRIORITEST Quality Gate" `
    -Method Get `
    -Headers @{Authorization = "Basic $([Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${SonarToken}:")))"}

$qgId = $gateInfo.id
Write-Host "Quality Gate ID: $qgId" -ForegroundColor Green

# Add conditions to Quality Gate
Write-Host "Adding conditions to Quality Gate..." -ForegroundColor Yellow

$conditions = @(
    @{metric = "coverage"; op = "LT"; error = "30"},
    @{metric = "duplicated_lines_density"; op = "GT"; error = "5"},
    @{metric = "reliability_rating"; op = "GT"; error = "1"},
    @{metric = "security_rating"; op = "GT"; error = "1"},
    @{metric = "maintainability_rating"; op = "GT"; error = "2"},
    @{metric = "vulnerabilities"; op = "GT"; error = "0"},
    @{metric = "bugs"; op = "GT"; error = "10"}
)

foreach ($condition in $conditions) {
    try {
        $body = @{
            gateId = $qgId
            metric = $condition.metric
            op = $condition.op
            error = $condition.error
        }
        
        Invoke-RestMethod -Uri "$SonarQubeUrl/api/qualitygates/create_condition" `
            -Method Post `
            -Headers @{Authorization = "Basic $([Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${SonarToken}:")))"} `
            -Body $body `
            -ContentType "application/x-www-form-urlencoded"
        
        Write-Host "  ✓ Added condition: $($condition.metric)" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Failed to add condition: $($condition.metric) - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Set as default Quality Gate
Write-Host "Setting as default Quality Gate..." -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "$SonarQubeUrl/api/qualitygates/set_as_default" `
        -Method Post `
        -Headers @{Authorization = "Basic $([Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${SonarToken}:")))"} `
        -Body @{id = $qgId} `
        -ContentType "application/x-www-form-urlencoded"
    
    Write-Host "  ✓ Quality Gate set as default" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Failed to set as default: $($_.Exception.Message)" -ForegroundColor Red
}

# Create Quality Profiles
Write-Host "Creating Quality Profiles..." -ForegroundColor Yellow

$profiles = @(
    @{language = "java"; name = "PRIORITEST Java Profile"},
    @{language = "py"; name = "PRIORITEST Python Profile"},
    @{language = "ts"; name = "PRIORITEST TypeScript Profile"}
)

foreach ($profile in $profiles) {
    try {
        Invoke-RestMethod -Uri "$SonarQubeUrl/api/qualityprofiles/create" `
            -Method Post `
            -Headers @{Authorization = "Basic $([Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${SonarToken}:")))"} `
            -Body @{language = $profile.language; name = $profile.name} `
            -ContentType "application/x-www-form-urlencoded"
        
        Write-Host "  ✓ Created profile: $($profile.name)" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Failed to create profile: $($profile.name) - $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "Quality Gate: PRIORITEST Quality Gate (ID: $qgId)" -ForegroundColor Cyan
Write-Host 'Profiles created for: Java, Python, TypeScript' -ForegroundColor Cyan
