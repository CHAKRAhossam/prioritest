# Script PowerShell pour générer les diagrammes PNG depuis les fichiers PlantUML

Write-Host "Génération des diagrammes simplifiés S6 et S7..." -ForegroundColor Green

# Vérifier si PlantUML est disponible
$plantumlCmd = Get-Command plantuml -ErrorAction SilentlyContinue
$javaCmd = Get-Command java -ErrorAction SilentlyContinue

if (-not $plantumlCmd -and -not $javaCmd) {
    Write-Host "Erreur: PlantUML ou Java n'est pas installé." -ForegroundColor Red
    Write-Host "Options d'installation:" -ForegroundColor Yellow
    Write-Host "  1. Installer Java puis télécharger plantuml.jar"
    Write-Host "  2. Installer via npm: npm install -g node-plantuml"
    Write-Host "  3. Utiliser l'outil en ligne: https://www.plantuml.com/plantuml/uml/"
    exit 1
}

# Si plantuml.jar existe, utiliser Java
if (Test-Path "plantuml.jar") {
    Write-Host "Utilisation de plantuml.jar..." -ForegroundColor Cyan
    
    Write-Host "Génération use_case_s6_simple.png..." -ForegroundColor Yellow
    java -jar plantuml.jar -tpng use_case_s6_simple.puml
    
    Write-Host "Génération use_case_s7_simple.png..." -ForegroundColor Yellow
    java -jar plantuml.jar -tpng use_case_s7_simple.puml
    
    Write-Host "Génération class_s6_simple.png..." -ForegroundColor Yellow
    java -jar plantuml.jar -tpng class_s6_simple.puml
    
    Write-Host "Génération class_s7_simple.png..." -ForegroundColor Yellow
    java -jar plantuml.jar -tpng class_s7_simple.puml
}
elseif ($plantumlCmd) {
    Write-Host "Utilisation de la commande plantuml..." -ForegroundColor Cyan
    
    plantuml -tpng use_case_s6_simple.puml
    plantuml -tpng use_case_s7_simple.puml
    plantuml -tpng class_s6_simple.puml
    plantuml -tpng class_s7_simple.puml
}
else {
    Write-Host "PlantUML non trouvé. Utilisez l'outil en ligne:" -ForegroundColor Yellow
    Write-Host "https://www.plantuml.com/plantuml/uml/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Ou copiez le contenu des fichiers .puml dans l'éditeur en ligne." -ForegroundColor Yellow
}

Write-Host "Génération terminée !" -ForegroundColor Green
Write-Host "Fichiers générés :" -ForegroundColor Cyan
Get-ChildItem *.png | Select-Object Name, Length





