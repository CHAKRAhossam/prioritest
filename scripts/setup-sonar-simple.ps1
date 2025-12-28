$token = "sqa_597e49e8cd6b775f26d69b9b83ea2660afdb714e"
$url = "http://localhost:9000"

Write-Host "Configuring SonarQube..." -ForegroundColor Cyan

# Create Quality Gate
Write-Host "Creating Quality Gate..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$url/api/qualitygates/create" `
        -Method Post `
        -Headers @{Authorization = "Basic $([Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${token}:")))"} `
        -Body @{name = "PRIORITEST Quality Gate"} `
        -ContentType "application/x-www-form-urlencoded"
    Write-Host "  Quality Gate created" -ForegroundColor Green
} catch {
    Write-Host "  Quality Gate may already exist" -ForegroundColor Yellow
}

# Get Quality Gate ID
Write-Host "Getting Quality Gate ID..." -ForegroundColor Yellow
$gateInfo = Invoke-RestMethod -Uri "$url/api/qualitygates/show?name=PRIORITEST Quality Gate" `
    -Method Get `
    -Headers @{Authorization = "Basic $([Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${token}:")))"}

$qgId = $gateInfo.id
Write-Host "  Quality Gate ID: $qgId" -ForegroundColor Green

# Add conditions
Write-Host "Adding conditions..." -ForegroundColor Yellow
$conditions = @(
    @{metric = "coverage"; op = "LT"; error = "30"},
    @{metric = "duplicated_lines_density"; op = "GT"; error = "5"},
    @{metric = "reliability_rating"; op = "GT"; error = "1"},
    @{metric = "security_rating"; op = "GT"; error = "1"},
    @{metric = "maintainability_rating"; op = "GT"; error = "2"},
    @{metric = "vulnerabilities"; op = "GT"; error = "0"},
    @{metric = "bugs"; op = "GT"; error = "10"}
)

foreach ($c in $conditions) {
    try {
        $body = @{
            gateId = $qgId
            metric = $c.metric
            op = $c.op
            error = $c.error
        }
        Invoke-RestMethod -Uri "$url/api/qualitygates/create_condition" `
            -Method Post `
            -Headers @{Authorization = "Basic $([Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${token}:")))"} `
            -Body $body `
            -ContentType "application/x-www-form-urlencoded"
        Write-Host "  Added: $($c.metric)" -ForegroundColor Green
    } catch {
        Write-Host "  Condition may exist: $($c.metric)" -ForegroundColor Yellow
    }
}

# Set as default
Write-Host "Setting as default..." -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "$url/api/qualitygates/set_as_default" `
        -Method Post `
        -Headers @{Authorization = "Basic $([Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${token}:")))"} `
        -Body @{id = $qgId} `
        -ContentType "application/x-www-form-urlencoded"
    Write-Host "  Set as default" -ForegroundColor Green
} catch {
    Write-Host "  Error setting default" -ForegroundColor Red
}

# Create Profiles
Write-Host "Creating Quality Profiles..." -ForegroundColor Yellow
$profiles = @(
    @{lang = "java"; name = "PRIORITEST Java Profile"},
    @{lang = "py"; name = "PRIORITEST Python Profile"},
    @{lang = "ts"; name = "PRIORITEST TypeScript Profile"}
)

foreach ($p in $profiles) {
    try {
        Invoke-RestMethod -Uri "$url/api/qualityprofiles/create" `
            -Method Post `
            -Headers @{Authorization = "Basic $([Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${token}:")))"} `
            -Body @{language = $p.lang; name = $p.name} `
            -ContentType "application/x-www-form-urlencoded"
        Write-Host "  Created: $($p.name)" -ForegroundColor Green
    } catch {
        Write-Host "  Profile may exist: $($p.name)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green

