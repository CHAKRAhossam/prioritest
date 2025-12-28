pipeline {
    agent any
    
    // Triggers automatiques
    triggers {
        // Déclenchement sur push vers n'importe quelle branche
        gitlab(triggerOnPush: true, triggerOnMergeRequest: true, branchFilterType: 'All')
        
        // OU déclenchement périodique (optionnel - commenté)
        // cron('H */4 * * *') // Toutes les 4 heures
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 1, unit: 'HOURS')
        retry(3)
    }
    
    environment {
        SONAR_TOKEN = credentials('sonar-token')
        SONARQUBE_URL = 'http://sonarqube:9000'
        DOCKER_REGISTRY = 'your-registry.io'
        DOCKER_CREDENTIALS = credentials('docker-registry-credentials')
        GITLAB_SECRET_TOKEN = credentials('gitlab-secret-token')
        DEPLOY_ENV = "${env.BRANCH_NAME == 'main' ? 'production' : 'staging'}"
        KUBERNETES_NAMESPACE = "${env.BRANCH_NAME == 'main' ? 'prioritest-prod' : 'prioritest-staging'}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    // Affiche les infos du commit
                    def gitCommit = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()
                    def gitBranch = env.BRANCH_NAME
                    def gitAuthor = sh(returnStdout: true, script: 'git log -1 --pretty=format:"%an"').trim()
                    def gitMessage = sh(returnStdout: true, script: 'git log -1 --pretty=format:"%s"').trim()
                    
                    echo """
                        ========================================
                        Build Information:
                        Branch: ${gitBranch}
                        Commit: ${gitCommit}
                        Author: ${gitAuthor}
                        Message: ${gitMessage}
                        ========================================
                    """
                }
            }
        }
        
        stage('Parallel Build & Test') {
            parallel {
                stage('Java Services') {
                    steps {
                        script {
                            def javaServices = [
                                'S0-ApiGateway',
                                'S2-AnalyseStatique',
                                'S3-HistoriqueTests',
                                'S9-Integrations'
                            ]
                            javaServices.each { service ->
                                dir("services/${service}") {
                                    sh './mvnw clean verify'
                                    withSonarQubeEnv('SonarQube') {
                                        sh './mvnw sonar:sonar -Dsonar.qualitygate.wait=true'
                                    }
                                }
                            }
                        }
                    }
                }
                
                stage('Python Services') {
                    steps {
                        script {
                            def pythonServices = [
                                'S1-CollecteDepots',
                                'S4-PretraitementFeatures',
                                'S5-MLService',
                                'S6-MoteurPriorisation',
                                'S7-TestScaffolder'
                            ]
                            pythonServices.each { service ->
                                dir("services/${service}") {
                                    sh """
                                        python -m venv venv
                                        source venv/bin/activate || venv\\Scripts\\activate
                                        pip install -r requirements.txt
                                        pip install pytest pytest-cov coverage sonar-scanner
                                        pytest --cov=. --cov-report=xml --cov-report=html
                                        coverage xml
                                    """
                                    withSonarQubeEnv('SonarQube') {
                                        sh 'source venv/bin/activate && sonar-scanner -Dsonar.qualitygate.wait=true'
                                    }
                                }
                            }
                        }
                    }
                }
                
                stage('Frontend') {
                    steps {
                        dir('services/S8-DashboardQualite/test-priority-hub') {
                            sh """
                                npm ci
                                npm run lint
                                npm run build
                                npm test -- --coverage
                            """
                            withSonarQubeEnv('SonarQube') {
                                sh 'sonar-scanner -Dsonar.qualitygate.wait=true'
                            }
                        }
                    }
                }
            }
        }
        
        stage('Quality Gate Check') {
            steps {
                script {
                    def services = [
                        'prioritest-s0-apigateway',
                        'prioritest-s1-collectedepots',
                        'prioritest-s2-analysestatique',
                        'prioritest-s3-historiquetests',
                        'prioritest-s4-pretraitementfeatures',
                        'prioritest-s5-mlservice',
                        'prioritest-s6-moteurpriorisation',
                        'prioritest-s7-testscaffolder',
                        'prioritest-s8-dashboard',
                        'prioritest-s9-integrations'
                    ]
                    
                    services.each { projectKey ->
                        def qualityGateStatus = sh(
                            script: """
                                curl -s -u ${SONAR_TOKEN}: \
                                "${SONARQUBE_URL}/api/qualitygates/project_status?projectKey=${projectKey}" \
                                | jq -r '.projectStatus.status'
                            """,
                            returnStdout: true
                        ).trim()
                        
                        if (qualityGateStatus != 'OK') {
                            error "Quality Gate failed for ${projectKey}: ${qualityGateStatus}"
                        } else {
                            echo "Quality Gate passed for ${projectKey}"
                        }
                    }
                }
            }
        }
        
        stage('Build Docker Images') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                    branch 'staging'
                }
            }
            steps {
                script {
                    def services = [
                        'S0-ApiGateway', 'S1-CollecteDepots', 'S2-AnalyseStatique',
                        'S3-HistoriqueTests', 'S4-PretraitementFeatures', 'S5-MLService',
                        'S6-MoteurPriorisation', 'S7-TestScaffolder', 'S8-DashboardQualite', 'S9-Integrations'
                    ]
                    
                    services.each { service ->
                        dir("services/${service}") {
                            def imageName = "${DOCKER_REGISTRY}/${service.toLowerCase()}"
                            def imageTag = "${BUILD_NUMBER}"
                            
                            echo "Building Docker image for ${service}..."
                            sh """
                                docker build -t ${imageName}:${imageTag} .
                                docker tag ${imageName}:${imageTag} ${imageName}:latest
                                docker tag ${imageName}:${imageTag} ${imageName}:${env.BRANCH_NAME}
                            """
                        }
                    }
                }
            }
        }
        
        stage('Push Docker Images') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                    branch 'staging'
                }
            }
            steps {
                script {
                    sh "docker login -u ${DOCKER_CREDENTIALS_USR} -p ${DOCKER_CREDENTIALS_PSW} ${DOCKER_REGISTRY}"
                    
                    def services = [
                        'S0-ApiGateway', 'S1-CollecteDepots', 'S2-AnalyseStatique',
                        'S3-HistoriqueTests', 'S4-PretraitementFeatures', 'S5-MLService',
                        'S6-MoteurPriorisation', 'S7-TestScaffolder', 'S8-DashboardQualite', 'S9-Integrations'
                    ]
                    
                    services.each { service ->
                        def imageName = "${DOCKER_REGISTRY}/${service.toLowerCase()}"
                        def imageTag = "${BUILD_NUMBER}"
                        
                        echo "Pushing Docker image for ${service}..."
                        sh """
                            docker push ${imageName}:${imageTag}
                            docker push ${imageName}:latest
                            docker push ${imageName}:${env.BRANCH_NAME}
                        """
                    }
                }
            }
        }
        
        stage('Deploy') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                script {
                    echo "Deploying to ${DEPLOY_ENV} environment..."
                    sh """
                        cd ${WORKSPACE}
                        export COMPOSE_PROJECT_NAME=prioritest
                        export DEPLOY_ENV=${DEPLOY_ENV}
                        export IMAGE_TAG=${BUILD_NUMBER}
                        export DOCKER_REGISTRY=${DOCKER_REGISTRY}
                        
                        docker-compose -f docker-compose.yml -f docker-compose.${DEPLOY_ENV}.yml pull
                        docker-compose -f docker-compose.yml -f docker-compose.${DEPLOY_ENV}.yml up -d
                    """
                }
            }
        }
        
        stage('Health Check') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                script {
                    def services = [
                        [name: 'S0-ApiGateway', port: 8090, path: '/actuator/health'],
                        [name: 'S1-CollecteDepots', port: 8001, path: '/health'],
                        [name: 'S2-AnalyseStatique', port: 8081, path: '/actuator/health'],
                        [name: 'S3-HistoriqueTests', port: 8082, path: '/actuator/health'],
                        [name: 'S4-PretraitementFeatures', port: 8004, path: '/health'],
                        [name: 'S5-MLService', port: 8005, path: '/health'],
                        [name: 'S6-MoteurPriorisation', port: 8006, path: '/health'],
                        [name: 'S7-TestScaffolder', port: 8007, path: '/health'],
                        [name: 'S8-DashboardQualite', port: 3000, path: '/'],
                        [name: 'S9-Integrations', port: 8009, path: '/actuator/health']
                    ]
                    
                    def maxRetries = 30
                    def retryDelay = 10
                    
                    services.each { service ->
                        def healthCheckPassed = false
                        for (int i = 0; i < maxRetries; i++) {
                            try {
                                def response = sh(
                                    script: """
                                        curl -f -s -o /dev/null -w "%{http_code}" \
                                        http://localhost:${service.port}${service.path} || echo "000"
                                    """,
                                    returnStdout: true
                                ).trim()
                                
                                if (response == "200" || response == "204") {
                                    echo "${service.name} is healthy"
                                    healthCheckPassed = true
                                    break
                                } else {
                                    echo "Waiting for ${service.name}... (attempt ${i+1}/${maxRetries})"
                                    sleep(retryDelay)
                                }
                            } catch (Exception e) {
                                sleep(retryDelay)
                            }
                        }
                        
                        if (!healthCheckPassed) {
                            error "Health check failed for ${service.name}"
                        }
                    }
                }
            }
        }
    }
    
    post {
        always {
            junit '**/target/surefire-reports/*.xml'
            publishTestResults testResultsPattern: '**/test-results/**/*.xml'
            publishHTML([
                reportDir: 'coverage',
                reportFiles: 'index.html',
                reportName: 'Coverage Report'
            ])
            archiveArtifacts artifacts: '**/target/*.jar', allowEmptyArchive: true
        }
        success {
            script {
                def gitCommit = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
                def gitAuthor = sh(returnStdout: true, script: 'git log -1 --pretty=format:"%an"').trim()
                
                emailext(
                    subject: "✓ Build Success: ${env.JOB_NAME} #${BUILD_NUMBER}",
                    body: """
                        Build successful!
                        Branch: ${env.BRANCH_NAME}
                        Commit: ${gitCommit}
                        Author: ${gitAuthor}
                        Build: ${BUILD_URL}
                    """,
                    to: "${gitAuthor}@example.com"
                )
            }
        }
        failure {
            script {
                def gitCommit = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
                def gitAuthor = sh(returnStdout: true, script: 'git log -1 --pretty=format:"%an"').trim()
                def qualityGateReport = sh(
                    script: """
                        curl -s -u ${SONAR_TOKEN}: \
                        "${SONARQUBE_URL}/api/qualitygates/project_status?projectKey=prioritest" \
                        | jq '.' || echo "Unable to fetch Quality Gate report"
                    """,
                    returnStdout: true
                )
                
                emailext(
                    subject: "✗ Build Failed: ${env.JOB_NAME} #${BUILD_NUMBER}",
                    body: """
                        Build failed!
                        Branch: ${env.BRANCH_NAME}
                        Commit: ${gitCommit}
                        Author: ${gitAuthor}
                        Build: ${BUILD_URL}
                        Console: ${BUILD_URL}console
                        
                        Quality Gate Report:
                        ${qualityGateReport}
                    """,
                    to: "${gitAuthor}@example.com"
                )
            }
        }
    }
}

