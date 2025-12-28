#!/bin/bash

set -e

services=(
    "S0-ApiGateway:8090:/actuator/health"
    "S1-CollecteDepots:8001:/health"
    "S2-AnalyseStatique:8081:/actuator/health"
    "S3-HistoriqueTests:8082:/actuator/health"
    "S4-PretraitementFeatures:8004:/health"
    "S5-MLService:8005:/health"
    "S6-MoteurPriorisation:8006:/health"
    "S7-TestScaffolder:8007:/health"
    "S8-DashboardQualite:3000:/"
    "S9-Integrations:8009:/actuator/health"
)

echo "Starting health checks for all services..."
echo "=========================================="

for service in "${services[@]}"; do
    IFS=':' read -r name port path <<< "$service"
    echo -n "Checking ${name} on port ${port}... "
    
    max_retries=30
    retry_delay=2
    success=false
    
    for i in $(seq 1 $max_retries); do
        if curl -f -s "http://localhost:${port}${path}" > /dev/null 2>&1; then
            echo "✓ Healthy"
            success=true
            break
        else
            if [ $i -lt $max_retries ]; then
                sleep $retry_delay
            fi
        fi
    done
    
    if [ "$success" = false ]; then
        echo "✗ Failed (after ${max_retries} attempts)"
        exit 1
    fi
done

echo "=========================================="
echo "All services are healthy!"

