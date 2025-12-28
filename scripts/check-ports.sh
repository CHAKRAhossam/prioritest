#!/bin/bash

echo "=========================================="
echo "Vérification des Ports PRIORITEST"
echo "=========================================="
echo ""

# Liste des ports utilisés
declare -A ports=(
    ["8080"]="Jenkins"
    ["8090"]="API Gateway"
    ["9000"]="SonarQube"
    ["9100"]="MinIO API"
    ["9101"]="MinIO Console"
    ["8761"]="Eureka Discovery"
    ["5432"]="PostgreSQL PRIORITEST"
    ["5433"]="PostgreSQL SonarQube"
    ["5000"]="MLflow"
    ["50000"]="Jenkins Agent"
    ["2181"]="Zookeeper"
    ["9092"]="Kafka (interne)"
    ["9093"]="Kafka (externe)"
    ["8001"]="S1 - CollecteDepots"
    ["8081"]="S2 - AnalyseStatique"
    ["8082"]="S3 - HistoriqueTests"
    ["8004"]="S4 - PretraitementFeatures"
    ["8005"]="S5 - MLService"
    ["8006"]="S6 - MoteurPriorisation"
    ["8007"]="S7 - TestScaffolder"
    ["8009"]="S9 - Integrations"
    ["3000"]="S8 - DashboardQualite"
)

echo "Ports configurés:"
echo "-----------------"
for port in "${!ports[@]}"; do
    printf "%-6s %s\n" "$port:" "${ports[$port]}"
done | sort -n

echo ""
echo "Vérification des conflits..."
echo "----------------------------"

# Vérifier les ports en conflit dans docker-compose.yml
conflicts=0

# Vérifier port 8080
if grep -q "8080:8080" docker-compose.yml 2>/dev/null; then
    count=$(grep -c "8080:8080" docker-compose.yml)
    if [ "$count" -gt 1 ]; then
        echo "⚠️  Conflit détecté: Port 8080 utilisé $count fois"
        conflicts=$((conflicts + 1))
    fi
fi

# Vérifier port 9000
if grep -q "9000:9000" docker-compose.yml 2>/dev/null; then
    count=$(grep -c "9000:9000" docker-compose.yml)
    if [ "$count" -gt 1 ]; then
        echo "⚠️  Conflit détecté: Port 9000 utilisé $count fois"
        conflicts=$((conflicts + 1))
    fi
fi

if [ "$conflicts" -eq 0 ]; then
    echo "✅ Aucun conflit de ports détecté!"
else
    echo "❌ $conflicts conflit(s) détecté(s)"
    exit 1
fi

echo ""
echo "Ports actuellement utilisés sur le système:"
echo "-------------------------------------------"
if command -v netstat &> /dev/null; then
    netstat -tuln 2>/dev/null | grep LISTEN | awk '{print $4}' | cut -d: -f2 | sort -n | uniq
elif command -v ss &> /dev/null; then
    ss -tuln | grep LISTEN | awk '{print $4}' | cut -d: -f2 | sort -n | uniq
else
    echo "netstat ou ss non disponible"
fi

echo ""
echo "=========================================="
echo "Vérification terminée"
echo "=========================================="

