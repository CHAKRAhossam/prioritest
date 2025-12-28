#!/bin/bash

set -e

ENVIRONMENT=${1:-staging}
IMAGE_TAG=${2:-latest}
DOCKER_REGISTRY=${DOCKER_REGISTRY:-your-registry.io}

echo "=========================================="
echo "Deploying PRIORITEST"
echo "Environment: ${ENVIRONMENT}"
echo "Image Tag: ${IMAGE_TAG}"
echo "Registry: ${DOCKER_REGISTRY}"
echo "=========================================="

export COMPOSE_PROJECT_NAME=prioritest
export DEPLOY_ENV=${ENVIRONMENT}
export IMAGE_TAG=${IMAGE_TAG}
export DOCKER_REGISTRY=${DOCKER_REGISTRY}

# Pull latest images
echo "Pulling latest images..."
docker-compose -f docker-compose.yml -f docker-compose.${ENVIRONMENT}.yml pull

# Deploy
echo "Deploying services..."
docker-compose -f docker-compose.yml -f docker-compose.${ENVIRONMENT}.yml up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 30

# Health check
echo "Running health checks..."
./scripts/health-check.sh

echo "=========================================="
echo "Deployment completed successfully!"
echo "=========================================="

