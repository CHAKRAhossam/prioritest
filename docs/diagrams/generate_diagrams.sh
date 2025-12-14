#!/bin/bash

# Script pour générer les diagrammes PNG depuis les fichiers PlantUML

echo "Génération des diagrammes simplifiés S6 et S7..."

# Vérifier si PlantUML est installé
if ! command -v plantuml &> /dev/null; then
    echo "Erreur: PlantUML n'est pas installé."
    echo "Installation:"
    echo "  - Java doit être installé"
    echo "  - Télécharger plantuml.jar depuis https://plantuml.com/download"
    echo "  - Ou installer via: npm install -g node-plantuml"
    exit 1
fi

# Générer les diagrammes
echo "Génération use_case_s6_simple.png..."
plantuml -tpng use_case_s6_simple.puml

echo "Génération use_case_s7_simple.png..."
plantuml -tpng use_case_s7_simple.puml

echo "Génération class_s6_simple.png..."
plantuml -tpng class_s6_simple.puml

echo "Génération class_s7_simple.png..."
plantuml -tpng class_s7_simple.puml

echo "Génération terminée !"
echo "Fichiers générés :"
ls -lh *.png





