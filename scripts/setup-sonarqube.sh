#!/bin/bash

SONARQUBE_URL="${SONARQUBE_URL:-http://localhost:9000}"
SONAR_TOKEN="${SONAR_TOKEN}"

if [ -z "$SONAR_TOKEN" ]; then
    echo "Error: SONAR_TOKEN environment variable is not set"
    exit 1
fi

echo "Setting up SonarQube Quality Gates and Profiles for PRIORITEST..."

# Create Quality Gate
echo "Creating Quality Gate..."
curl -X POST \
  -u "${SONAR_TOKEN}:" \
  "${SONARQUBE_URL}/api/qualitygates/create" \
  -d "name=PRIORITEST Quality Gate"

# Get Quality Gate ID
QG_ID=$(curl -s -u "${SONAR_TOKEN}:" \
  "${SONARQUBE_URL}/api/qualitygates/show?name=PRIORITEST Quality Gate" \
  | jq -r '.id')

# Add conditions to Quality Gate
echo "Adding conditions to Quality Gate..."
curl -X POST \
  -u "${SONAR_TOKEN}:" \
  "${SONARQUBE_URL}/api/qualitygates/create_condition" \
  -d "gateId=${QG_ID}&metric=coverage&op=LT&error=30"

curl -X POST \
  -u "${SONAR_TOKEN}:" \
  "${SONARQUBE_URL}/api/qualitygates/create_condition" \
  -d "gateId=${QG_ID}&metric=duplicated_lines_density&op=GT&error=5"

curl -X POST \
  -u "${SONAR_TOKEN}:" \
  "${SONARQUBE_URL}/api/qualitygates/create_condition" \
  -d "gateId=${QG_ID}&metric=reliability_rating&op=GT&error=1"

curl -X POST \
  -u "${SONAR_TOKEN}:" \
  "${SONARQUBE_URL}/api/qualitygates/create_condition" \
  -d "gateId=${QG_ID}&metric=security_rating&op=GT&error=1"

curl -X POST \
  -u "${SONAR_TOKEN}:" \
  "${SONARQUBE_URL}/api/qualitygates/create_condition" \
  -d "gateId=${QG_ID}&metric=maintainability_rating&op=GT&error=2"

curl -X POST \
  -u "${SONAR_TOKEN}:" \
  "${SONARQUBE_URL}/api/qualitygates/create_condition" \
  -d "gateId=${QG_ID}&metric=vulnerabilities&op=GT&error=0"

curl -X POST \
  -u "${SONAR_TOKEN}:" \
  "${SONARQUBE_URL}/api/qualitygates/create_condition" \
  -d "gateId=${QG_ID}&metric=bugs&op=GT&error=10"

# Set as default Quality Gate
echo "Setting as default Quality Gate..."
curl -X POST \
  -u "${SONAR_TOKEN}:" \
  "${SONARQUBE_URL}/api/qualitygates/set_as_default" \
  -d "id=${QG_ID}"

# Create Java Quality Profile
echo "Creating Java Quality Profile..."
curl -X POST \
  -u "${SONAR_TOKEN}:" \
  "${SONARQUBE_URL}/api/qualityprofiles/create" \
  -d "language=java&name=PRIORITEST Java Profile"

# Create Python Quality Profile
echo "Creating Python Quality Profile..."
curl -X POST \
  -u "${SONAR_TOKEN}:" \
  "${SONARQUBE_URL}/api/qualityprofiles/create" \
  -d "language=py&name=PRIORITEST Python Profile"

# Create TypeScript Quality Profile
echo "Creating TypeScript Quality Profile..."
curl -X POST \
  -u "${SONAR_TOKEN}:" \
  "${SONARQUBE_URL}/api/qualityprofiles/create" \
  -d "language=ts&name=PRIORITEST TypeScript Profile"

echo "Setup complete!"

