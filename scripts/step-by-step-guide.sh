#!/bin/bash

echo "=========================================="
echo "PRIORITEST CI/CD Setup - Step by Step Guide"
echo "=========================================="
echo ""

# Step 1: Start infrastructure
echo "STEP 1: Starting Docker infrastructure..."
echo "----------------------------------------"
echo "Starting Jenkins, SonarQube, and all services..."
docker-compose up -d jenkins sonarqube postgres
echo "Waiting for services to be ready..."
sleep 30
echo "✓ Infrastructure started"
echo ""

# Step 2: Get Jenkins password
echo "STEP 2: Getting Jenkins admin password..."
echo "----------------------------------------"
JENKINS_PASSWORD=$(docker exec prioritest-jenkins cat /var/jenkins_home/secrets/initialAdminPassword 2>/dev/null || echo "NOT_AVAILABLE")
if [ "$JENKINS_PASSWORD" != "NOT_AVAILABLE" ]; then
    echo "Jenkins Admin Password: $JENKINS_PASSWORD"
    echo "Save this password!"
else
    echo "⚠ Could not get password. Check: docker logs prioritest-jenkins"
fi
echo ""

# Step 3: Setup SonarQube
echo "STEP 3: Setting up SonarQube..."
echo "----------------------------------------"
echo "1. Open SonarQube: http://localhost:9000"
echo "2. Default login: admin / admin"
echo "3. Create a project token:"
echo "   - Go to: My Account > Security > Generate Token"
echo "   - Name: prioritest-token"
echo "   - Copy the token"
echo ""
read -p "Enter your SonarQube token: " SONAR_TOKEN
export SONAR_TOKEN=$SONAR_TOKEN
export SONARQUBE_URL=http://localhost:9000
./scripts/setup-sonarqube.sh
echo "✓ SonarQube configured"
echo ""

# Step 4: Setup Jenkins
echo "STEP 4: Setting up Jenkins..."
echo "----------------------------------------"
export JENKINS_URL=http://localhost:8080
export JENKINS_USER=admin
export JENKINS_PASSWORD=$JENKINS_PASSWORD
./scripts/setup-jenkins.sh
echo "✓ Jenkins configured"
echo ""

# Step 5: Create Jenkins job
echo "STEP 5: Creating Jenkins job..."
echo "----------------------------------------"
echo "Manual steps required:"
echo "1. Open Jenkins: http://localhost:8080"
echo "2. Login with admin / $JENKINS_PASSWORD"
echo "3. Click 'New Item'"
echo "4. Enter name: PRIORITEST"
echo "5. Select 'Multibranch Pipeline'"
echo "6. Click OK"
echo "7. In Branch Sources:"
echo "   - Add source: GitLab or GitHub"
echo "   - Project: your-username/prioritest"
echo "   - Credentials: Add your GitLab/GitHub token"
echo "8. Save"
echo ""

# Step 6: Configure webhook
echo "STEP 6: Configuring GitLab/GitHub webhook..."
echo "----------------------------------------"
echo "In your GitLab/GitHub repository:"
echo "1. Go to Settings > Webhooks"
echo "2. Add webhook:"
echo "   - URL: http://your-jenkins-ip:8080/project/PRIORITEST"
echo "   - Secret Token: [generate a token]"
echo "   - Trigger: Push events, Merge request events"
echo "3. Save webhook"
echo ""

# Step 7: Test pipeline
echo "STEP 7: Testing the pipeline..."
echo "----------------------------------------"
echo "To test the pipeline:"
echo "1. Make a small change to your code"
echo "2. Commit and push:"
echo "   git add ."
echo "   git commit -m 'test: trigger pipeline'"
echo "   git push origin main"
echo "3. Check Jenkins: http://localhost:8080"
echo "4. The pipeline should start automatically!"
echo ""

echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Access URLs:"
echo "- Jenkins: http://localhost:8080"
echo "- SonarQube: http://localhost:9000"
echo "- API Gateway: http://localhost:8080 (after deployment)"
echo ""

