#!/bin/bash
# Script de test Docker pour Service 6

set -e

echo "🐳 Test Docker - Service 6 Moteur de Priorisation"
echo "=================================================="

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Vérifier Docker
echo -e "${YELLOW}1. Vérification Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker n'est pas installé${NC}"
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo -e "${RED}❌ Docker Desktop n'est pas démarré${NC}"
    echo "   Veuillez démarrer Docker Desktop"
    exit 1
fi
echo -e "${GREEN}✅ Docker est disponible${NC}"

# Construire l'image
echo -e "\n${YELLOW}2. Construction de l'image...${NC}"
docker build -t s6-moteur-priorisation:latest .
echo -e "${GREEN}✅ Image construite${NC}"

# Lancer le conteneur
echo -e "\n${YELLOW}3. Lancement du conteneur...${NC}"
docker run -d --name s6-test -p 8006:8006 s6-moteur-priorisation:latest
sleep 5
echo -e "${GREEN}✅ Conteneur lancé${NC}"

# Tester health check
echo -e "\n${YELLOW}4. Test health check...${NC}"
for i in {1..10}; do
    if curl -f http://localhost:8006/health &> /dev/null; then
        echo -e "${GREEN}✅ Health check OK${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}❌ Health check échoué après 10 tentatives${NC}"
        docker logs s6-test
        docker stop s6-test
        docker rm s6-test
        exit 1
    fi
    sleep 2
done

# Tester Swagger
echo -e "\n${YELLOW}5. Test Swagger UI...${NC}"
if curl -f http://localhost:8006/docs &> /dev/null; then
    echo -e "${GREEN}✅ Swagger UI accessible${NC}"
else
    echo -e "${YELLOW}⚠️  Swagger UI non accessible (peut être normal)${NC}"
fi

# Afficher les logs
echo -e "\n${YELLOW}6. Logs du conteneur:${NC}"
docker logs s6-test

# Nettoyer
echo -e "\n${YELLOW}7. Nettoyage...${NC}"
docker stop s6-test
docker rm s6-test
echo -e "${GREEN}✅ Conteneur arrêté et supprimé${NC}"

echo -e "\n${GREEN}✅ Tous les tests Docker sont passés !${NC}"
echo "Pour démarrer le service : docker-compose up -d"

