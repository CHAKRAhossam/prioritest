#!/bin/bash
# Script to generate Maven wrapper (mvnw) for services that don't have it

set -e

SERVICES=(
    "services/S0-ApiGateway"
    "services/S2-AnalyseStatique"
    "services/S3-HistoriqueTests"
    "services/S9-Integrations"
)

for service in "${SERVICES[@]}"; do
    if [ -d "$service" ] && [ -f "$service/pom.xml" ]; then
        if [ ! -f "$service/mvnw" ]; then
            echo "Generating Maven wrapper for $service..."
            cd "$service"
            mvn wrapper:wrapper -Dmaven=3.9.6 || echo "Failed to generate wrapper for $service"
            chmod +x mvnw || true
            cd - > /dev/null
        else
            echo "Maven wrapper already exists for $service"
        fi
    fi
done

echo "Maven wrapper generation complete"


