#!/bin/bash

set -e

echo "=========================================="
echo "Setting up Jenkins for PRIORITEST"
echo "=========================================="

JENKINS_URL="${JENKINS_URL:-http://localhost:8080}"
JENKINS_USER="${JENKINS_USER:-admin}"
JENKINS_PASSWORD="${JENKINS_PASSWORD}"

if [ -z "$JENKINS_PASSWORD" ]; then
    echo "Getting initial Jenkins admin password..."
    JENKINS_PASSWORD=$(docker exec prioritest-jenkins cat /var/jenkins_home/secrets/initialAdminPassword 2>/dev/null || echo "")
    
    if [ -z "$JENKINS_PASSWORD" ]; then
        echo "Error: Could not get Jenkins password. Please provide JENKINS_PASSWORD environment variable"
        echo "Or check the Jenkins container logs: docker logs prioritest-jenkins"
        exit 1
    fi
fi

echo "Jenkins URL: $JENKINS_URL"
echo "Jenkins User: $JENKINS_USER"
echo ""

# Wait for Jenkins to be ready
echo "Waiting for Jenkins to be ready..."
for i in {1..30}; do
    if curl -s -f "$JENKINS_URL/login" > /dev/null; then
        echo "Jenkins is ready!"
        break
    fi
    echo "Attempt $i/30: Waiting for Jenkins..."
    sleep 5
done

# Install required plugins
echo "Installing required Jenkins plugins..."
PLUGINS="gitlab-plugin workflow-aggregator sonar pipeline-stage-view docker-workflow docker-plugin"

for plugin in $PLUGINS; do
    echo "Installing $plugin..."
    curl -X POST \
        -u "$JENKINS_USER:$JENKINS_PASSWORD" \
        "$JENKINS_URL/pluginManager/installNecessaryPlugins" \
        -d "<install plugin='$plugin@latest' />" \
        -H "Content-Type: text/xml" || true
done

echo ""
echo "Waiting for plugins to install..."
sleep 30

# Create credentials for SonarQube
echo "Creating SonarQube credentials..."
SONAR_TOKEN="${SONAR_TOKEN:-your-sonar-token}"

curl -X POST \
    -u "$JENKINS_USER:$JENKINS_PASSWORD" \
    "$JENKINS_URL/credentials/store/system/domain/_/createCredentials" \
    --data-urlencode "json={
        \"\": \"0\",
        \"credentials\": {
            \"scope\": \"GLOBAL\",
            \"id\": \"sonar-token\",
            \"username\": \"\",
            \"password\": \"$SONAR_TOKEN\",
            \"secret\": \"$SONAR_TOKEN\",
            \"description\": \"SonarQube token\",
            \"\$class\": \"com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl\"
        }
    }" || echo "Note: Credentials may already exist"

# Configure SonarQube server
echo "Configuring SonarQube server..."
SONARQUBE_URL="${SONARQUBE_URL:-http://sonarqube:9000}"

curl -X POST \
    -u "$JENKINS_USER:$JENKINS_PASSWORD" \
    "$JENKINS_URL/configure" \
    --data-urlencode "json={
        \"sonar\": {
            \"installations\": [{
                \"name\": \"SonarQube\",
                \"serverUrl\": \"$SONARQUBE_URL\",
                \"serverAuthenticationToken\": {
                    \"value\": \"$SONAR_TOKEN\",
                    \"\$class\": \"org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl\"
                }
            }]
        }
    }" || echo "Note: SonarQube may already be configured"

echo ""
echo "=========================================="
echo "Jenkins setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Open Jenkins: $JENKINS_URL"
echo "2. Login with: $JENKINS_USER / [password from container]"
echo "3. Create a new Multibranch Pipeline job named 'PRIORITEST'"
echo "4. Configure GitLab/GitHub as branch source"
echo "5. Run the pipeline!"
echo ""

