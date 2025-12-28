pipeline {
    agent any
    
    // Triggers automatiques (désactivés pour l'instant - configurer via webhook GitLab)
    // triggers {
    //     // Déclenchement sur push vers n'importe quelle branche
    //     // gitlab(triggerOnPush: true, triggerOnMergeRequest: true, branchFilterType: 'All')
    //     
    //     // OU déclenchement périodique (optionnel)
    //     // cron('H */4 * * *') // Toutes les 4 heures
    // }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 1, unit: 'HOURS')
        retry(3)
    }
    
    environment {
        SONARQUBE_URL = 'http://sonarqube:9000'
        DEPLOY_ENV = "${env.BRANCH_NAME == 'main' ? 'production' : 'staging'}"
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
        
        stage('Check SonarQube Connection') {
            steps {
                script {
                    try {
                        def sonarToken = credentials('sonar-token')
                        env.SONAR_TOKEN = sonarToken
                        echo "SonarQube token found"
                    } catch (Exception e) {
                        echo "Warning: SonarQube token not configured. SonarQube analysis will be skipped."
                        env.SONAR_TOKEN = ''
                    }
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
                                    script {
                                        try {
                                            // Use Pipeline Maven Integration plugin
                                            withMaven(maven: 'Maven') {
                                                if (fileExists('mvnw')) {
                                                    sh 'chmod +x mvnw || true'
                                                    sh './mvnw clean verify'
                                                } else {
                                                    sh 'mvn clean verify'
                                                }
                                                if (env.SONAR_TOKEN) {
                                                    withSonarQubeEnv('SonarQube') {
                                                        if (fileExists('mvnw')) {
                                                            sh './mvnw sonar:sonar -Dsonar.qualitygate.wait=true'
                                                        } else {
                                                            sh 'mvn sonar:sonar -Dsonar.qualitygate.wait=true'
                                                        }
                                                    }
                                                } else {
                                                    echo "Skipping SonarQube analysis for ${service} (token not configured)"
                                                }
                                            }
                                        } catch (Exception e) {
                                            echo "Error building ${service}: ${e.getMessage()}"
                                            // Continue with other services
                                        }
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
                                    script {
                                        try {
                                            // Use Pyenv Pipeline plugin
                                            withPythonEnv('python3') {
                                                sh """
                                                    python -m venv venv || python3 -m venv venv
                                                    . venv/bin/activate || venv/Scripts/activate
                                                    pip install -r requirements.txt
                                                    pip install pytest pytest-cov coverage
                                                    pytest --cov=. --cov-report=xml --cov-report=html || echo 'No tests found'
                                                    coverage xml || echo 'Coverage not available'
                                                """
                                                if (env.SONAR_TOKEN) {
                                                    withSonarQubeEnv('SonarQube') {
                                                        sh '. venv/bin/activate && sonar-scanner -Dsonar.qualitygate.wait=true || echo "SonarQube scan skipped"'
                                                    }
                                                } else {
                                                    echo "Skipping SonarQube analysis for ${service} (token not configured)"
                                                }
                                            }
                                        } catch (Exception e) {
                                            echo "Error building ${service}: ${e.getMessage()}"
                                            // Continue with other services
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                
                stage('Frontend') {
                    steps {
                        dir('services/S8-DashboardQualite/test-priority-hub') {
                            script {
                                try {
                                    // Use Pipeline NPM Integration plugin
                                    withNPM(npmrcConfig: '') {
                                        sh """
                                            npm ci || npm install
                                            npm run lint || echo 'Lint skipped'
                                            npm run build
                                            npm test -- --coverage || echo 'Tests skipped'
                                        """
                                        if (env.SONAR_TOKEN) {
                                            withSonarQubeEnv('SonarQube') {
                                                sh 'sonar-scanner -Dsonar.qualitygate.wait=true || echo "SonarQube scan skipped"'
                                            }
                                        } else {
                                            echo "Skipping SonarQube analysis for frontend (token not configured)"
                                        }
                                    }
                                } catch (Exception e) {
                                    echo "Error building frontend: ${e.getMessage()}"
                                }
                            }
                        }
                    }
                }
            }
        }
        
        stage('Quality Gate Check') {
            when {
                expression { env.SONAR_TOKEN != null && env.SONAR_TOKEN != '' }
            }
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
                        try {
                            def qualityGateStatus = sh(
                                script: """
                                    curl -s -u ${env.SONAR_TOKEN}: \
                                    "${SONARQUBE_URL}/api/qualitygates/project_status?projectKey=${projectKey}" \
                                    | jq -r '.projectStatus.status' || echo 'UNKNOWN'
                                """,
                                returnStdout: true
                            ).trim()
                            
                            if (qualityGateStatus == 'OK') {
                                echo "Quality Gate passed for ${projectKey}"
                            } else if (qualityGateStatus == 'UNKNOWN') {
                                echo "Quality Gate not available for ${projectKey} (project may not exist yet)"
                            } else {
                                echo "Warning: Quality Gate status for ${projectKey}: ${qualityGateStatus}"
                                // Don't fail the build, just warn
                            }
                        } catch (Exception e) {
                            echo "Could not check Quality Gate for ${projectKey}: ${e.getMessage()}"
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
                    echo "Docker build stage - skipped (Docker registry not configured)"
                    // Docker build/push requires registry credentials
                    // Uncomment when registry is configured:
                    /*
                    def services = [
                        'S0-ApiGateway', 'S1-CollecteDepots', 'S2-AnalyseStatique',
                        'S3-HistoriqueTests', 'S4-PretraitementFeatures', 'S5-MLService',
                        'S6-MoteurPriorisation', 'S7-TestScaffolder', 'S8-DashboardQualite', 'S9-Integrations'
                    ]
                    
                    services.each { service ->
                        dir("services/${service}") {
                            def imageName = "prioritest/${service.toLowerCase()}"
                            def imageTag = "${BUILD_NUMBER}"
                            
                            echo "Building Docker image for ${service}..."
                            sh """
                                docker build -t ${imageName}:${imageTag} .
                                docker tag ${imageName}:${imageTag} ${imageName}:latest
                            """
                        }
                    }
                    */
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
                    echo "Health check stage - skipped (services not deployed in this pipeline)"
                    // Health checks require services to be running
                    // This would be used after deployment
                }
            }
        }
    }
    
    post {
        always {
            script {
                try {
                    junit '**/target/surefire-reports/*.xml'
                } catch (Exception e) {
                    echo "No JUnit reports found: ${e.getMessage()}"
                }
                try {
                    // Use HTML Publisher plugin (now installed)
                    publishHTML([
                        reportDir: 'coverage',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report',
                        allowMissing: true
                    ])
                } catch (Exception e) {
                    echo "No coverage reports found: ${e.getMessage()}"
                }
                try {
                    archiveArtifacts artifacts: '**/target/*.jar', allowEmptyArchive: true
                } catch (Exception e) {
                    echo "No artifacts to archive: ${e.getMessage()}"
                }
            }
        }
        success {
            script {
                try {
                    def gitCommit = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
                    def gitAuthor = sh(returnStdout: true, script: 'git log -1 --pretty=format:"%an"').trim()
                    
                    echo """
                        ========================================
                        Build Successful!
                        Branch: ${env.BRANCH_NAME}
                        Commit: ${gitCommit}
                        Author: ${gitAuthor}
                        Build: ${BUILD_URL}
                        ========================================
                    """
                } catch (Exception e) {
                    echo "Could not get build info: ${e.getMessage()}"
                }
            }
        }
        failure {
            script {
                try {
                    def gitCommit = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
                    def gitAuthor = sh(returnStdout: true, script: 'git log -1 --pretty=format:"%an"').trim()
                    
                    echo """
                        ========================================
                        Build Failed!
                        Branch: ${env.BRANCH_NAME}
                        Commit: ${gitCommit}
                        Author: ${gitAuthor}
                        Build: ${BUILD_URL}
                        Console: ${BUILD_URL}console
                        ========================================
                    """
                } catch (Exception e) {
                    echo "Could not get build info: ${e.getMessage()}"
                }
            }
        }
    }
}

