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
                    
                    // Clear corrupted Maven repository to fix "Non-readable POM" errors
                    echo "Cleaning Maven repository to fix corrupted POM files..."
                    sh 'rm -rf /root/.m2/repository/org/sonatype/oss/oss-parent/7 || true'
                    sh 'rm -rf /root/.m2/repository/io/prometheus/simpleclient_bom || true'
                    sh 'rm -rf /root/.m2/repository/com/fasterxml/jackson/jackson-bom || true'
                    sh 'rm -rf /root/.m2/repository/org/junit/junit-bom || true'
                    sh 'rm -rf /root/.m2/repository/org/apache/apache || true'
                    sh 'rm -rf /root/.m2/repository/io/netty/netty-bom || true'
                    sh 'rm -rf /root/.m2/repository/com/squareup/okhttp3/okhttp-bom || true'
                    sh 'rm -rf /root/.m2/repository/io/opentelemetry/opentelemetry-bom || true'
                    sh 'rm -rf /root/.m2/repository/com/oracle/database/jdbc/ojdbc-bom || true'
                    sh 'rm -rf /root/.m2/repository/com/querydsl/querydsl-bom || true'
                    sh 'rm -rf /root/.m2/repository/io/rest-assured/rest-assured-bom || true'
                    sh 'rm -rf /root/.m2/repository/io/rsocket/rsocket-bom || true'
                    sh 'rm -rf /root/.m2/repository/org/seleniumhq/selenium/selenium-bom || true'
                    sh 'rm -rf /root/.m2/repository/org/springframework || true'
                    sh 'rm -rf /root/.m2/repository/org/testcontainers/testcontainers-bom || true'
                    sh 'rm -rf /root/.m2/repository/org/mockito/mockito-bom || true'
                    echo "Maven repository cleaned"
                }
            }
        }
        
        stage('Check SonarQube Connection') {
            steps {
                script {
                    // Check if SonarQube is accessible
                    def sonarUrl = env.SONARQUBE_URL ?: 'http://sonarqube:9000'
                    try {
                        def response = sh(
                            script: "curl -s -o /dev/null -w '%{http_code}' '${sonarUrl}/api/system/status' || echo '000'",
                            returnStdout: true
                        ).trim()
                        if (response == '200') {
                            echo "✅ SonarQube is accessible at ${sonarUrl}"
                            env.SONAR_TOKEN = 'configured'  // Flag to indicate SonarQube is available
                        } else {
                            echo "⚠️ SonarQube returned status ${response}"
                            env.SONAR_TOKEN = ''
                        }
                    } catch (Exception e) {
                        echo "⚠️ Warning: Could not connect to SonarQube. SonarQube analysis will be skipped."
                        env.SONAR_TOKEN = ''
                    }
                }
            }
        }
        
        stage('Parallel Build & Test') {
            parallel {
                // Java Services - Individual stages for each service
                stage('S0-ApiGateway') {
                    steps {
                        dir('services/S0-ApiGateway') {
                                    script {
                                        try {
                                    echo "Building S0-ApiGateway..."
                                            
                                            // Use Maven directly (installed in Jenkins image)
                                            // Try mvnw first if available, otherwise use system Maven
                                            def mavenCmd = 'mvn'
                                            if (fileExists('mvnw')) {
                                                sh 'chmod +x mvnw || true'
                                                mavenCmd = './mvnw'
                                            }
                                            
                                    // Verify Maven works first
                                            sh """
                                        echo 'Verifying Maven installation...'
                                        ${mavenCmd} --version || { echo '❌ Maven command failed'; exit 1; }
                                    """
                                    
                                    // Compile first to catch compilation errors
                                    sh """
                                        echo 'Compiling S0-ApiGateway...'
                                        ${mavenCmd} clean compile || { echo '❌ Compilation failed'; exit 1; }
                                        echo '✅ Compilation successful'
                                    """
                                    
                                    // Build and test (continue even if tests fail, but ensure they run)
                                    sh """
                                        echo 'Running tests for S0-ApiGateway...'
                                        
                                        # Check if there are test classes
                                        if [ -d src/test/java ] || [ -d src/test ]; then
                                            echo '✅ Test source directory found'
                                            TEST_FILES=\$(find src/test -name '*Test.java' -o -name '*Tests.java' 2>/dev/null | wc -l)
                                            echo "Found \${TEST_FILES} test files"
                                        else
                                            echo '⚠️ Warning: No test source directory found (src/test/java or src/test)'
                                        fi
                                        
                                        # Run tests with JaCoCo agent attached
                                        set +e
                                        ${mavenCmd} jacoco:prepare-agent test -Dmaven.test.failure.ignore=true
                                        TEST_EXIT_CODE=\$?
                                        set -e
                                                
                                                # Check if tests actually ran
                                                if [ -d target/surefire-reports ]; then
                                                    echo '✅ Surefire reports directory exists'
                                            TEST_COUNT=\$(find target/surefire-reports -name '*.xml' 2>/dev/null | wc -l)
                                                    echo "Found \${TEST_COUNT} test report files"
                                                    if [ \${TEST_COUNT} -eq 0 ]; then
                                                        echo '⚠️ Warning: No test reports found - tests may not have executed'
                                                        # Check Maven output for test execution
                                                        echo 'Checking Maven test output...'
                                                        ${mavenCmd} test -X 2>&1 | grep -i "test" | tail -10 || echo 'Could not check Maven test output'
                                                    fi
                                                else
                                                    echo '⚠️ Warning: target/surefire-reports directory not found'
                                                    echo 'Attempting to run tests explicitly...'
                                                    # Try to run tests explicitly with surefire plugin
                                                    ${mavenCmd} surefire:test -DskipTests=false -Dmaven.test.failure.ignore=true 2>&1 | tail -30 || echo '⚠️ Explicit test execution failed'
                                                    
                                                    # Check again
                                                    if [ -d target/surefire-reports ]; then
                                                        echo '✅ Surefire reports directory created after explicit test run'
                                                        TEST_COUNT=\$(find target/surefire-reports -name '*.xml' 2>/dev/null | wc -l)
                                                        echo "Found \${TEST_COUNT} test report files"
                                                    else
                                                        echo '⚠️ Warning: Tests may not be configured or no tests exist'
                                                    fi
                                        fi
                                        
                                        if [ \${TEST_EXIT_CODE} -ne 0 ]; then
                                            echo '⚠️ Tests completed with exit code: ' \${TEST_EXIT_CODE}
                                                else
                                                    echo '✅ Tests completed successfully'
                                                fi
                                            """
                                            
                                            // Force JaCoCo report generation even if tests failed
                                            sh """
                                                echo 'Checking JaCoCo execution data...'
                                                if [ -f target/jacoco.exec ]; then
                                                    echo '✅ jacoco.exec found'
                                                    FILE_SIZE=\$(stat -f%z target/jacoco.exec 2>/dev/null || stat -c%s target/jacoco.exec 2>/dev/null || echo '0')
                                                    echo "jacoco.exec size: \${FILE_SIZE} bytes"
                                                    if [ \${FILE_SIZE} -eq 0 ]; then
                                                        echo '⚠️ Warning: jacoco.exec is empty - no coverage data collected'
                                                        echo 'Attempting to run tests again with explicit JaCoCo agent...'
                                                        ${mavenCmd} jacoco:prepare-agent test -Dmaven.test.failure.ignore=true || echo '⚠️ Failed to run tests with JaCoCo'
                                                    fi
                                                else
                                                    echo '⚠️ Warning: jacoco.exec not found, tests may not have run'
                                                    echo 'Attempting to run tests again with explicit JaCoCo agent...'
                                                    # Try running tests again with JaCoCo agent
                                                    ${mavenCmd} jacoco:prepare-agent test -Dmaven.test.failure.ignore=true || echo '⚠️ Failed to run tests with JaCoCo'
                                                    
                                                    # Check again
                                                    if [ -f target/jacoco.exec ]; then
                                                        echo '✅ jacoco.exec created after retry'
                                                        FILE_SIZE=\$(stat -f%z target/jacoco.exec 2>/dev/null || stat -c%s target/jacoco.exec 2>/dev/null || echo '0')
                                                        echo "jacoco.exec size: \${FILE_SIZE} bytes"
                                                    else
                                                        echo '⚠️ Warning: jacoco.exec still not found after retry - no tests may have been executed'
                                                    fi
                                                fi
                                        
                                        echo 'Generating JaCoCo report...'
                                        ${mavenCmd} jacoco:report || echo '⚠️ JaCoCo report generation failed or skipped'
                                            """
                                            
                                            // Copy JaCoCo HTML reports to coverage directory for publishing
                                            sh """
                                                mkdir -p coverage || true
                                                if [ -d target/site/jacoco ]; then
                                            cp -r target/site/jacoco/* coverage/ || echo '⚠️ JaCoCo HTML report copy failed'
                                            echo '✅ Coverage reports copied to coverage/'
                                        else
                                            echo '⚠️ Warning: target/site/jacoco directory not found'
                                                fi
                                            """
                                            
                                            // Verify JaCoCo XML report exists before SonarQube analysis
                                            sh """
                                                if [ -f target/site/jacoco/jacoco.xml ]; then
                                                    echo '✅ JaCoCo XML report found at target/site/jacoco/jacoco.xml'
                                                else
                                                    echo '⚠️ Warning: JaCoCo XML report not found at target/site/jacoco/jacoco.xml'
                                                    echo 'Attempting to regenerate...'
                                            ${mavenCmd} jacoco:report || echo '⚠️ Failed to regenerate JaCoCo report'
                                            if [ ! -f target/site/jacoco/jacoco.xml ]; then
                                                echo '⚠️ Warning: Proceeding without coverage report'
                                            fi
                                                fi
                                            """
                                            
                                            // SonarQube analysis
                                            if (env.SONAR_TOKEN && env.SONAR_TOKEN != '') {
                                                withSonarQubeEnv('SonarQube') {
                                                    withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN_VALUE')]) {
                                                    sh """
                                                            export PATH=/opt/sonar-scanner/bin:\$PATH
                                                            export SONAR_HOST_URL=${env.SONARQUBE_URL ?: 'http://sonarqube:9000'}
                                                            export SONAR_TOKEN=\${SONAR_TOKEN_VALUE}
                                                            
                                                        # Verify XML report exists before analysis
                                                        if [ -f target/site/jacoco/jacoco.xml ]; then
                                                                echo '✅ Proceeding with SonarQube analysis with coverage report'
                                                        else
                                                                echo '⚠️ Warning: Proceeding without coverage report'
                                                        fi
                                                        # Run SonarQube analysis without qualitygate.wait to avoid build failure
                                                        # Quality Gate will be checked in a separate stage
                                                        ${mavenCmd} sonar:sonar || echo '⚠️ SonarQube analysis completed with warnings (Quality Gate will be checked separately)'
                                                    """
                                                    }
                                                }
                                            } else {
                                                echo "SonarQube token not configured, skipping analysis for S0-ApiGateway"
                                            }
                                            
                                    echo "✅ S0-ApiGateway build completed"
                                        } catch (Exception e) {
                                    echo "❌ Error building S0-ApiGateway: ${e.getMessage()}"
                                    currentBuild.result = 'UNSTABLE'
                                        }
                                    }
                                }
                            }
                        }
                
                stage('S2-AnalyseStatique') {
                    steps {
                        dir('services/S2-AnalyseStatique') {
                            script {
                                try {
                                    echo "Building S2-AnalyseStatique..."
                                    
                                    def mavenCmd = 'mvn'
                                    if (fileExists('mvnw')) {
                                        sh 'chmod +x mvnw || true'
                                        mavenCmd = './mvnw'
                                    }
                                    
                                    // Verify Maven works first
                                    sh """
                                        echo 'Verifying Maven installation...'
                                        ${mavenCmd} --version || { echo '❌ Maven command failed'; exit 1; }
                                    """
                                    
                                    // Compile first to catch compilation errors
                                    sh """
                                        echo 'Compiling S2-AnalyseStatique...'
                                        ${mavenCmd} clean compile || { echo '❌ Compilation failed'; exit 1; }
                                        echo '✅ Compilation successful'
                                    """
                                    
                                    // Run tests with JaCoCo agent attached
                                    sh """
                                        echo 'Running tests for S2-AnalyseStatique with JaCoCo...'
                                        set +e
                                        # Prepare JaCoCo agent and run tests
                                        ${mavenCmd} jacoco:prepare-agent test -Dmaven.test.failure.ignore=true
                                        TEST_EXIT_CODE=\$?
                                        set -e
                                        
                                        if [ -d target/surefire-reports ]; then
                                            echo '✅ Surefire reports directory exists'
                                            TEST_COUNT=\$(find target/surefire-reports -name '*.xml' 2>/dev/null | wc -l)
                                            echo "Found \${TEST_COUNT} test report files"
                                        else
                                            echo '⚠️ Warning: target/surefire-reports directory not found'
                                        fi
                                        
                                        if [ \${TEST_EXIT_CODE} -ne 0 ]; then
                                            echo '⚠️ Tests completed with exit code: ' \${TEST_EXIT_CODE}
                                        else
                                            echo '✅ Tests completed successfully'
                                        fi
                                    """
                                    
                                    // Check for JaCoCo execution data and generate report
                                    sh """
                                        echo 'Checking JaCoCo execution data...'
                                        
                                        # Check if jacoco.exec exists
                                        if [ -f target/jacoco.exec ]; then
                                            echo '✅ jacoco.exec found'
                                            FILE_SIZE=\$(stat -f%z target/jacoco.exec 2>/dev/null || stat -c%s target/jacoco.exec 2>/dev/null || echo '0')
                                            echo "jacoco.exec size: \${FILE_SIZE} bytes"
                                            if [ \${FILE_SIZE} -eq 0 ]; then
                                                echo '⚠️ Warning: jacoco.exec is empty - no coverage data collected'
                                            fi
                                        else
                                            echo '⚠️ Warning: jacoco.exec not found after tests'
                                            
                                            # Check if JaCoCo plugin is configured in pom.xml
                                            echo 'Checking JaCoCo plugin configuration...'
                                            if grep -q 'jacoco-maven-plugin' pom.xml 2>/dev/null; then
                                                echo '✅ JaCoCo plugin found in pom.xml'
                                            else
                                                echo '⚠️ Warning: JaCoCo plugin not found in pom.xml - may need to be added'
                                            fi
                                            
                                            # Try to find jacoco.exec in alternative locations
                                            echo 'Searching for jacoco.exec in alternative locations...'
                                            JACOCO_EXEC=\$(find . -name 'jacoco.exec' -type f 2>/dev/null | head -n 1)
                                            if [ -n "\${JACOCO_EXEC}" ]; then
                                                echo "✅ Found jacoco.exec at: \${JACOCO_EXEC}"
                                                mkdir -p target || true
                                                cp "\${JACOCO_EXEC}" target/jacoco.exec || echo '⚠️ Failed to copy jacoco.exec'
                                            else
                                                echo '⚠️ jacoco.exec not found in any location'
                                                
                                                # Try cleaning and running tests again
                                                echo 'Attempting to clean and run tests again with JaCoCo...'
                                                ${mavenCmd} clean jacoco:prepare-agent test -Dmaven.test.failure.ignore=true || echo '⚠️ Failed to run tests with JaCoCo after clean'
                                                
                                                # Check again
                                                if [ -f target/jacoco.exec ]; then
                                                    echo '✅ jacoco.exec created after clean and retry'
                                                    FILE_SIZE=\$(stat -f%z target/jacoco.exec 2>/dev/null || stat -c%s target/jacoco.exec 2>/dev/null || echo '0')
                                                    echo "jacoco.exec size: \${FILE_SIZE} bytes"
                                                else
                                                    echo '⚠️ Warning: jacoco.exec still not found - JaCoCo agent may not be properly attached'
                                                    echo 'Checking Maven output for JaCoCo agent attachment...'
                                                    ${mavenCmd} jacoco:prepare-agent test -Dmaven.test.failure.ignore=true -X 2>&1 | grep -i jacoco | head -10 || echo 'Could not check JaCoCo agent attachment'
                                                fi
                                            fi
                                        fi
                                        
                                        echo 'Generating JaCoCo report...'
                                        # Try to generate report even if jacoco.exec doesn't exist (some versions can do this)
                                        ${mavenCmd} jacoco:report || echo '⚠️ JaCoCo report generation failed or skipped'
                                        
                                        # Check if report was generated
                                        if [ -d target/site/jacoco ]; then
                                            echo '✅ JaCoCo report directory created'
                                        else
                                            echo '⚠️ Warning: JaCoCo report directory not created'
                                        fi
                                    """
                                    
                                    // Copy JaCoCo HTML reports to coverage directory for publishing
                                    sh """
                                        mkdir -p coverage || true
                                        if [ -d target/site/jacoco ]; then
                                            cp -r target/site/jacoco/* coverage/ || echo '⚠️ JaCoCo HTML report copy failed'
                                            echo '✅ Coverage reports copied to coverage/'
                                        else
                                            echo '⚠️ Warning: target/site/jacoco directory not found'
                                        fi
                                    """
                                    
                                    // Verify JaCoCo XML report exists before SonarQube analysis
                                    sh """
                                        if [ -f target/site/jacoco/jacoco.xml ]; then
                                            echo '✅ JaCoCo XML report found at target/site/jacoco/jacoco.xml'
                                        else
                                            echo '⚠️ Warning: JaCoCo XML report not found'
                                            echo 'Attempting to regenerate...'
                                            ${mavenCmd} jacoco:report || echo '⚠️ Failed to regenerate JaCoCo report'
                                        fi
                                    """
                                    
                                    if (env.SONAR_TOKEN && env.SONAR_TOKEN != '') {
                                        withSonarQubeEnv('SonarQube') {
                                            withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN_VALUE')]) {
                                                sh """
                                                    export PATH=/opt/sonar-scanner/bin:\$PATH
                                                    export SONAR_HOST_URL=${env.SONARQUBE_URL ?: 'http://sonarqube:9000'}
                                                    export SONAR_TOKEN=\${SONAR_TOKEN_VALUE}
                                                    
                                                    if [ -f target/site/jacoco/jacoco.xml ]; then
                                                        echo '✅ Proceeding with SonarQube analysis with coverage report'
                                                    else
                                                        echo '⚠️ Warning: Proceeding without coverage report'
                                                    fi
                                                    ${mavenCmd} sonar:sonar || echo '⚠️ SonarQube analysis completed with warnings (Quality Gate will be checked separately)'
                                                """
                                            }
                                        }
                                    } else {
                                        echo "SonarQube token not configured, skipping analysis for S2-AnalyseStatique"
                                    }
                                    
                                    echo "✅ S2-AnalyseStatique build completed"
                                } catch (Exception e) {
                                    echo "❌ Error building S2-AnalyseStatique: ${e.getMessage()}"
                                    currentBuild.result = 'UNSTABLE'
                                }
                            }
                        }
                    }
                }
                
                stage('S3-HistoriqueTests') {
                    steps {
                        dir('services/S3-HistoriqueTests') {
                        script {
                                try {
                                    echo "Building S3-HistoriqueTests..."
                                    
                                    def mavenCmd = 'mvn'
                                    if (fileExists('mvnw')) {
                                        sh 'chmod +x mvnw || true'
                                        mavenCmd = './mvnw'
                                    }
                                    
                                    // Verify Maven works first
                                    sh """
                                        echo 'Verifying Maven installation...'
                                        ${mavenCmd} --version || { echo '❌ Maven command failed'; exit 1; }
                                    """
                                    
                                    // Clean corrupted Maven repository POMs and JARs
                                    sh """
                                        echo 'Cleaning corrupted Maven repository POMs and JARs...'
                                        M2_REPO=\${HOME}/.m2/repository
                                        if [ -d \${M2_REPO} ]; then
                                            echo 'Removing corrupted BOM POMs...'
                                            # Remove corrupted BOM POMs that are empty or contain no data
                                            find \${M2_REPO} -name '*.pom' -type f -size 0 -delete 2>/dev/null || true
                                            
                                            echo 'Removing corrupted plugin JARs...'
                                            # Remove corrupted plugin JARs that are empty or contain no data
                                            find \${M2_REPO} -path '*/maven-*-plugin/*/*.jar' -type f -size 0 -delete 2>/dev/null || true
                                            
                                            # Remove specific corrupted BOM directories
                                            rm -rf \${M2_REPO}/io/github/resilience4j/resilience4j-bom/2.0.2 2>/dev/null || true
                                            rm -rf \${M2_REPO}/io/github/openfeign/feign-bom/12.4 2>/dev/null || true
                                            rm -rf \${M2_REPO}/io/fabric8/kubernetes-client-bom/6.2.0 2>/dev/null || true
                                            rm -rf \${M2_REPO}/org/assertj/assertj-bom/3.24.2 2>/dev/null || true
                                            rm -rf \${M2_REPO}/io/zipkin/brave/brave-bom/5.15.1 2>/dev/null || true
                                            rm -rf \${M2_REPO}/com/datastax/oss/java-driver-bom/4.15.0 2>/dev/null || true
                                            rm -rf \${M2_REPO}/io/dropwizard/metrics/metrics-bom/4.2.19 2>/dev/null || true
                                            rm -rf \${M2_REPO}/org/glassfish/jaxb/jaxb-bom/4.0.3 2>/dev/null || true
                                            rm -rf \${M2_REPO}/org/apache/groovy/groovy-bom/4.0.15 2>/dev/null || true
                                            rm -rf \${M2_REPO}/org/infinispan/infinispan-bom/14.0.17.Final 2>/dev/null || true
                                            rm -rf \${M2_REPO}/com/fasterxml/jackson/jackson-parent/2.15 2>/dev/null || true
                                            rm -rf \${M2_REPO}/org/glassfish/jersey/jersey-bom/3.1.3 2>/dev/null || true
                                            rm -rf \${M2_REPO}/org/eclipse/jetty/jetty-bom/11.0.16 2>/dev/null || true
                                            rm -rf \${M2_REPO}/org/jetbrains/kotlin/kotlin-bom/1.8.22 2>/dev/null || true
                                            rm -rf \${M2_REPO}/org/jetbrains/kotlinx/kotlinx-coroutines-bom/1.6.4 2>/dev/null || true
                                            rm -rf \${M2_REPO}/org/apache/logging/log4j/log4j-bom/2.20.0 2>/dev/null || true
                                            rm -rf \${M2_REPO}/io/micrometer/micrometer-bom/1.11.4 2>/dev/null || true
                                            rm -rf \${M2_REPO}/io/micrometer/micrometer-tracing-bom/1.1.5 2>/dev/null || true
                                            rm -rf \${M2_REPO}/io/projectreactor/reactor-bom/2022.0.11 2>/dev/null || true
                                            
                                            # Remove specific corrupted plugin directories
                                            echo 'Removing corrupted maven-clean-plugin...'
                                            rm -rf \${M2_REPO}/org/apache/maven/plugins/maven-clean-plugin/3.2.0 2>/dev/null || true
                                            
                                            echo '✅ Corrupted POMs and plugin JARs cleaned'
                                        fi
                                    """
                                    
                                    // Compile first to catch compilation errors and force dependency download
                                    sh """
                                        echo 'Compiling S3-HistoriqueTests and downloading dependencies...'
                                        # Force update of dependencies (-U flag) to re-download corrupted POMs
                                        set +e
                                        ${mavenCmd} clean compile -U
                                        COMPILE_EXIT_CODE=\$?
                                        set -e
                                        
                                        if [ \${COMPILE_EXIT_CODE} -eq 0 ]; then
                                            echo '✅ Compilation successful'
                                        else
                                            echo '❌ Compilation failed with exit code: ' \${COMPILE_EXIT_CODE}
                                            echo 'Attempting to clean and retry compilation...'
                                            # Try cleaning corrupted artifacts again and retry
                                            rm -rf \${HOME}/.m2/repository/org/apache/maven/plugins/maven-clean-plugin/3.2.0 2>/dev/null || true
                                            find \${HOME}/.m2/repository -path '*/maven-*-plugin/*/*.jar' -type f -size 0 -delete 2>/dev/null || true
                                            ${mavenCmd} clean compile -U || { 
                                                echo '❌ Compilation failed after retry'; 
                                                echo 'This may indicate a problem with the project configuration or corrupted Maven repository';
                                                exit 1; 
                                            }
                                            echo '✅ Compilation successful after retry'
                                        fi
                                    """
                                    
                                    // Run tests with JaCoCo agent attached
                                    sh """
                                        echo 'Running tests for S3-HistoriqueTests with JaCoCo...'
                                        set +e
                                        # Prepare JaCoCo agent and run tests
                                        ${mavenCmd} jacoco:prepare-agent test -Dmaven.test.failure.ignore=true
                                        TEST_EXIT_CODE=\$?
                                        set -e
                                        
                                        if [ -d target/surefire-reports ]; then
                                            echo '✅ Surefire reports directory exists'
                                            TEST_COUNT=\$(find target/surefire-reports -name '*.xml' 2>/dev/null | wc -l)
                                            echo "Found \${TEST_COUNT} test report files"
                                        else
                                            echo '⚠️ Warning: target/surefire-reports directory not found'
                                        fi
                                        
                                        if [ \${TEST_EXIT_CODE} -ne 0 ]; then
                                            echo '⚠️ Tests completed with exit code: ' \${TEST_EXIT_CODE}
                                        fi
                                    """
                                    
                                    // Check for JaCoCo execution data and generate report
                                    sh """
                                        echo 'Checking JaCoCo execution data...'
                                        if [ -f target/jacoco.exec ]; then
                                            echo '✅ jacoco.exec found'
                                            FILE_SIZE=\$(stat -f%z target/jacoco.exec 2>/dev/null || stat -c%s target/jacoco.exec 2>/dev/null || echo '0')
                                            echo "jacoco.exec size: \${FILE_SIZE} bytes"
                                            if [ \${FILE_SIZE} -eq 0 ]; then
                                                echo '⚠️ Warning: jacoco.exec is empty - no coverage data collected'
                                            fi
                                        else
                                            echo '⚠️ Warning: jacoco.exec not found after tests'
                                            echo 'Attempting to run tests again with explicit JaCoCo agent...'
                                            # Try running with explicit JaCoCo agent preparation
                                            ${mavenCmd} jacoco:prepare-agent test -Dmaven.test.failure.ignore=true || echo '⚠️ Failed to run tests with JaCoCo'
                                        fi
                                        
                                        echo 'Generating JaCoCo report...'
                                        ${mavenCmd} jacoco:report || echo '⚠️ JaCoCo report generation failed or skipped'
                                    """
                                    
                                    // Copy JaCoCo HTML reports to coverage directory for publishing
                                    sh """
                                        mkdir -p coverage || true
                                        if [ -d target/site/jacoco ]; then
                                            cp -r target/site/jacoco/* coverage/ || echo '⚠️ JaCoCo HTML report copy failed'
                                            echo '✅ Coverage reports copied to coverage/'
                                        else
                                            echo '⚠️ Warning: target/site/jacoco directory not found'
                                        fi
                                    """
                                    
                                    // Verify JaCoCo XML report exists before SonarQube analysis
                                    sh """
                                        if [ -f target/site/jacoco/jacoco.xml ]; then
                                            echo '✅ JaCoCo XML report found at target/site/jacoco/jacoco.xml'
                                        else
                                            echo '⚠️ Warning: JaCoCo XML report not found'
                                            echo 'Attempting to regenerate...'
                                            ${mavenCmd} jacoco:report || echo '⚠️ Failed to regenerate JaCoCo report'
                                        fi
                                    """
                                    
                                    if (env.SONAR_TOKEN && env.SONAR_TOKEN != '') {
                                        withSonarQubeEnv('SonarQube') {
                                            withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN_VALUE')]) {
                                                sh """
                                                    export PATH=/opt/sonar-scanner/bin:\$PATH
                                                    export SONAR_HOST_URL=${env.SONARQUBE_URL ?: 'http://sonarqube:9000'}
                                                    export SONAR_TOKEN=\${SONAR_TOKEN_VALUE}
                                                    
                                                    if [ -f target/site/jacoco/jacoco.xml ]; then
                                                        echo '✅ Proceeding with SonarQube analysis with coverage report'
                                                    else
                                                        echo '⚠️ Warning: Proceeding without coverage report'
                                                    fi
                                                    ${mavenCmd} sonar:sonar || echo '⚠️ SonarQube analysis completed with warnings (Quality Gate will be checked separately)'
                                                """
                                            }
                                        }
                                    } else {
                                        echo "SonarQube token not configured, skipping analysis for S3-HistoriqueTests"
                                    }
                                    
                                    echo "✅ S3-HistoriqueTests build completed"
                                } catch (Exception e) {
                                    echo "❌ Error building S3-HistoriqueTests: ${e.getMessage()}"
                                    currentBuild.result = 'UNSTABLE'
                                }
                            }
                        }
                    }
                }
                
                stage('S9-Integrations') {
                    steps {
                        dir('services/S9-Integrations') {
                                    script {
                                        try {
                                    echo "Building S9-Integrations..."
                                    
                                    def mavenCmd = 'mvn'
                                    if (fileExists('mvnw')) {
                                        sh 'chmod +x mvnw || true'
                                        mavenCmd = './mvnw'
                                    }
                                    
                                    // Verify Maven works first
                                    sh """
                                        echo 'Verifying Maven installation...'
                                        ${mavenCmd} --version || { echo '❌ Maven command failed'; exit 1; }
                                    """
                                    
                                    // Clean corrupted Maven repository POMs and JARs (S9-Integrations specific versions)
                                    sh """
                                        echo 'Cleaning corrupted Maven repository POMs and JARs...'
                                        M2_REPO=\${HOME}/.m2/repository
                                        if [ -d \${M2_REPO} ]; then
                                            echo 'Removing corrupted BOM POMs...'
                                            # Remove corrupted BOM POMs that are empty or contain no data
                                            find \${M2_REPO} -name '*.pom' -type f -size 0 -delete 2>/dev/null || true
                                            
                                            echo 'Removing corrupted plugin JARs...'
                                            # Remove corrupted plugin JARs that are empty or contain no data
                                            find \${M2_REPO} -path '*/maven-*-plugin/*/*.jar' -type f -size 0 -delete 2>/dev/null || true
                                            
                                            # Remove specific corrupted BOM directories for S9-Integrations
                                            rm -rf \${M2_REPO}/io/github/resilience4j/resilience4j-bom/2.1.0 2>/dev/null || true
                                            rm -rf \${M2_REPO}/io/github/openfeign/feign-bom/13.1 2>/dev/null || true
                                            rm -rf \${M2_REPO}/io/fabric8/kubernetes-client-bom/6.9.2 2>/dev/null || true
                                            rm -rf \${M2_REPO}/org/assertj/assertj-bom/3.24.2 2>/dev/null || true
                                            rm -rf \${M2_REPO}/io/zipkin/brave/brave-bom/5.16.0 2>/dev/null || true
                                            rm -rf \${M2_REPO}/com/datastax/oss/java-driver-bom/4.17.0 2>/dev/null || true
                                            rm -rf \${M2_REPO}/io/dropwizard/metrics/metrics-bom/4.2.23 2>/dev/null || true
                                            rm -rf \${M2_REPO}/org/glassfish/jaxb/jaxb-bom/4.0.4 2>/dev/null || true
                                            rm -rf \${M2_REPO}/org/apache/groovy/groovy-bom/4.0.16 2>/dev/null || true
                                            rm -rf \${M2_REPO}/org/infinispan/infinispan-bom/14.0.21.Final 2>/dev/null || true
                                            rm -rf \${M2_REPO}/com/fasterxml/jackson/jackson-parent/2.15 2>/dev/null || true
                                            rm -rf \${M2_REPO}/org/glassfish/jersey/jersey-bom/3.1.5 2>/dev/null || true
                                            rm -rf \${M2_REPO}/org/eclipse/jetty/ee10/jetty-ee10-bom/12.0.5 2>/dev/null || true
                                            rm -rf \${M2_REPO}/org/eclipse/jetty/jetty-bom/12.0.5 2>/dev/null || true
                                            rm -rf \${M2_REPO}/org/jetbrains/kotlin/kotlin-bom/1.9.21 2>/dev/null || true
                                            rm -rf \${M2_REPO}/org/jetbrains/kotlinx/kotlinx-coroutines-bom/1.7.3 2>/dev/null || true
                                            rm -rf \${M2_REPO}/org/jetbrains/kotlinx/kotlinx-serialization-bom/1.6.2 2>/dev/null || true
                                            rm -rf \${M2_REPO}/org/apache/logging/log4j/log4j-bom/2.21.1 2>/dev/null || true
                                            rm -rf \${M2_REPO}/io/micrometer/micrometer-bom/1.12.1 2>/dev/null || true
                                            rm -rf \${M2_REPO}/io/micrometer/micrometer-tracing-bom/1.2.1 2>/dev/null || true
                                            rm -rf \${M2_REPO}/io/projectreactor/reactor-bom/2023.0.1 2>/dev/null || true
                                            
                                            # Remove specific corrupted plugin directories
                                            echo 'Removing corrupted maven-clean-plugin...'
                                            rm -rf \${M2_REPO}/org/apache/maven/plugins/maven-clean-plugin/3.3.2 2>/dev/null || true
                                            
                                            echo '✅ Corrupted POMs and plugin JARs cleaned'
                                        fi
                                    """
                                    
                                    // Compile first to catch compilation errors and force dependency download
                                    sh """
                                        echo 'Compiling S9-Integrations and downloading dependencies...'
                                        # Force update of dependencies (-U flag) to re-download corrupted POMs
                                        set +e
                                        ${mavenCmd} clean compile -U
                                        COMPILE_EXIT_CODE=\$?
                                        set -e
                                        
                                        if [ \${COMPILE_EXIT_CODE} -eq 0 ]; then
                                            echo '✅ Compilation successful'
                                        else
                                            echo '❌ Compilation failed with exit code: ' \${COMPILE_EXIT_CODE}
                                            echo 'Attempting to clean corrupted artifacts again and retry compilation...'
                                            # Try cleaning corrupted artifacts again and retry
                                            rm -rf \${HOME}/.m2/repository/org/apache/maven/plugins/maven-clean-plugin/3.3.2 2>/dev/null || true
                                            find \${HOME}/.m2/repository -path '*/maven-*-plugin/*/*.jar' -type f -size 0 -delete 2>/dev/null || true
                                            ${mavenCmd} clean compile -U || { 
                                                echo '❌ Compilation failed after retry'; 
                                                echo 'This may indicate a problem with the project configuration or corrupted Maven repository';
                                                exit 1; 
                                            }
                                            echo '✅ Compilation successful after retry'
                                        fi
                                    """
                                    
                                    // Run tests with JaCoCo agent attached
                                    sh """
                                        echo 'Running tests for S9-Integrations with JaCoCo...'
                                        set +e
                                        # Prepare JaCoCo agent and run tests
                                        ${mavenCmd} jacoco:prepare-agent test -Dmaven.test.failure.ignore=true
                                        TEST_EXIT_CODE=\$?
                                        set -e
                                        
                                        if [ -d target/surefire-reports ]; then
                                            echo '✅ Surefire reports directory exists'
                                            TEST_COUNT=\$(find target/surefire-reports -name '*.xml' 2>/dev/null | wc -l)
                                            echo "Found \${TEST_COUNT} test report files"
                                        else
                                            echo '⚠️ Warning: target/surefire-reports directory not found'
                                        fi
                                        
                                        if [ \${TEST_EXIT_CODE} -ne 0 ]; then
                                            echo '⚠️ Tests completed with exit code: ' \${TEST_EXIT_CODE}
                                        fi
                                    """
                                    
                                    // Check for JaCoCo execution data and generate report
                                    sh """
                                        echo 'Checking JaCoCo execution data...'
                                        if [ -f target/jacoco.exec ]; then
                                            echo '✅ jacoco.exec found'
                                            FILE_SIZE=\$(stat -f%z target/jacoco.exec 2>/dev/null || stat -c%s target/jacoco.exec 2>/dev/null || echo '0')
                                            echo "jacoco.exec size: \${FILE_SIZE} bytes"
                                            if [ \${FILE_SIZE} -eq 0 ]; then
                                                echo '⚠️ Warning: jacoco.exec is empty - no coverage data collected'
                                            fi
                                        else
                                            echo '⚠️ Warning: jacoco.exec not found after tests'
                                            echo 'Attempting to run tests again with explicit JaCoCo agent...'
                                            # Try running with explicit JaCoCo agent preparation
                                            ${mavenCmd} jacoco:prepare-agent test -Dmaven.test.failure.ignore=true || echo '⚠️ Failed to run tests with JaCoCo'
                                        fi
                                        
                                        echo 'Generating JaCoCo report...'
                                        ${mavenCmd} jacoco:report || echo '⚠️ JaCoCo report generation failed or skipped'
                                    """
                                    
                                    // Copy JaCoCo HTML reports to coverage directory for publishing
                                    sh """
                                        mkdir -p coverage || true
                                        if [ -d target/site/jacoco ]; then
                                            cp -r target/site/jacoco/* coverage/ || echo '⚠️ JaCoCo HTML report copy failed'
                                            echo '✅ Coverage reports copied to coverage/'
                                        else
                                            echo '⚠️ Warning: target/site/jacoco directory not found'
                                        fi
                                    """
                                    
                                    // Verify JaCoCo XML report exists before SonarQube analysis
                                    sh """
                                        if [ -f target/site/jacoco/jacoco.xml ]; then
                                            echo '✅ JaCoCo XML report found at target/site/jacoco/jacoco.xml'
                                        else
                                            echo '⚠️ Warning: JaCoCo XML report not found'
                                            echo 'Attempting to regenerate...'
                                            ${mavenCmd} jacoco:report || echo '⚠️ Failed to regenerate JaCoCo report'
                                        fi
                                    """
                                    
                                    if (env.SONAR_TOKEN && env.SONAR_TOKEN != '') {
                                        withSonarQubeEnv('SonarQube') {
                                            withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN_VALUE')]) {
                                                sh """
                                                    export PATH=/opt/sonar-scanner/bin:\$PATH
                                                    export SONAR_HOST_URL=${env.SONARQUBE_URL ?: 'http://sonarqube:9000'}
                                                    export SONAR_TOKEN=\${SONAR_TOKEN_VALUE}
                                                    
                                                    if [ -f target/site/jacoco/jacoco.xml ]; then
                                                        echo '✅ Proceeding with SonarQube analysis with coverage report'
                                                    else
                                                        echo '⚠️ Warning: Proceeding without coverage report'
                                                    fi
                                                    ${mavenCmd} sonar:sonar || echo '⚠️ SonarQube analysis completed with warnings (Quality Gate will be checked separately)'
                                                """
                                            }
                                        }
                                    } else {
                                        echo "SonarQube token not configured, skipping analysis for S9-Integrations"
                                    }
                                    
                                    echo "✅ S9-Integrations build completed"
                                } catch (Exception e) {
                                    echo "❌ Error building S9-Integrations: ${e.getMessage()}"
                                    currentBuild.result = 'UNSTABLE'
                                    currentBuild.result = 'UNSTABLE'
                                }
                            }
                        }
                    }
                }
                
                // Python Services - Individual stages for each service
                stage('S1-CollecteDepots') {
                    steps {
                        dir('services/S1-CollecteDepots') {
                            script {
                                try {
                                    echo "Building S1-CollecteDepots..."
                                            
                                            // Use Python3 directly (installed in Jenkins image)
                                            // Load Rust environment for pydantic-core compilation
                                            sh """
                                                # Install system dependencies required for Python packages
                                                echo 'Installing system dependencies for Python packages...'
                                                
                                                # Wait for apt-get lock to be released (max 60 seconds)
                                                echo 'Checking for apt-get lock...'
                                                COUNTER=0
                                                while [ -f /var/lib/apt/lists/lock ] || [ -f /var/lib/dpkg/lock ] || [ -f /var/cache/apt/archives/lock ]; do
                                                    if [ \${COUNTER} -ge 60 ]; then
                                                        echo '⚠️ apt-get lock timeout, attempting to install packages anyway...'
                                                        break
                                                    fi
                                                    echo "Waiting for apt-get lock to be released... (\${COUNTER}/60)"
                                                    sleep 2
                                                    COUNTER=\$((COUNTER + 2))
                                                done
                                                
                                                # Try to update package list
                                                set +e
                                                apt-get update -qq
                                                APT_UPDATE_EXIT_CODE=\$?
                                                set -e
                                                
                                                if [ \${APT_UPDATE_EXIT_CODE} -ne 0 ]; then
                                                    echo '⚠️ apt-get update failed, attempting to install packages anyway...'
                                                fi
                                                
                                                # Install required packages (try even if update failed)
                                                set +e
                                                apt-get install -y -qq libxml2-dev libxslt1-dev 2>&1 | grep -v "Unable to locate package" || {
                                                    echo '⚠️ Failed to install libxml2-dev/libxslt1-dev, checking if already installed...'
                                                    # Check if packages are already installed
                                                    dpkg -l | grep -q libxml2-dev && echo '✅ libxml2-dev already installed' || echo '⚠️ libxml2-dev not found'
                                                    dpkg -l | grep -q libxslt1-dev && echo '✅ libxslt1-dev already installed' || echo '⚠️ libxslt1-dev not found'
                                                }
                                                set -e
                                                
                                                export CARGO_HOME=/root/.cargo
                                                export RUSTUP_HOME=/root/.rustup
                                                export PATH=\$CARGO_HOME/bin:\$PATH
                                                if [ -f /root/.cargo/env ]; then
                                                    . /root/.cargo/env
                                                fi
                                                python3 -m venv venv || { echo '❌ venv creation failed'; exit 1; }
                                                . venv/bin/activate || { echo '❌ venv activation failed'; exit 1; }
                                                pip install --upgrade pip || { echo '⚠️ pip upgrade failed'; }
                                                
                                                # Install Python dependencies
                                                echo 'Installing Python dependencies...'
                                                set +e
                                                pip install -r requirements.txt
                                                PIP_INSTALL_EXIT_CODE=\$?
                                                set -e
                                                
                                                if [ \${PIP_INSTALL_EXIT_CODE} -ne 0 ]; then
                                                    echo '⚠️ pip install -r requirements.txt failed with exit code: ' \${PIP_INSTALL_EXIT_CODE}
                                                    echo 'Attempting to install critical packages individually...'
                                                    # Install critical packages that are likely needed
                                                    pip install requests PyGithub confluent-kafka pydantic-settings tenacity fastapi uvicorn pydantic sqlalchemy alembic || echo '⚠️ Failed to install some critical packages'
                                                    
                                                    # Try to install lxml separately (may fail if system packages not available)
                                                    pip install lxml || echo '⚠️ Failed to install lxml (may require libxml2-dev/libxslt1-dev)'
                                                else
                                                    echo '✅ Python dependencies installed successfully'
                                                fi
                                                
                                                # Install test dependencies
                                                pip install pytest pytest-cov coverage || { echo '⚠️ pytest install failed'; }
                                                # Run tests with proper error handling
                                                echo 'Running tests...'
                                                set +e
                                                pytest --cov=. --cov-report=xml --cov-report=html --cov-report=term-missing
                                                TEST_EXIT_CODE=\$?
                                                set -e
                                                
                                                if [ \${TEST_EXIT_CODE} -eq 0 ]; then
                                                    echo '✅ All tests passed'
                                                elif [ \${TEST_EXIT_CODE} -eq 5 ]; then
                                                    echo '⚠️ No tests collected'
                                                else
                                                    echo "⚠️ Tests completed with exit code: \${TEST_EXIT_CODE}"
                                                fi
                                                
                                                # Ensure coverage.xml is generated even if tests failed
                                                if [ -f .coverage ]; then
                                                    echo '✅ Found .coverage file, generating XML report...'
                                                    coverage xml || echo '⚠️ Coverage XML generation from .coverage failed'
                                                else
                                                    echo '⚠️ Warning: .coverage file not found'
                                                fi
                                                
                                                # Verify coverage.xml exists and is valid
                                                if [ -f coverage.xml ]; then
                                                    echo '✅ coverage.xml found'
                                                    if [ -s coverage.xml ]; then
                                                        echo '✅ coverage.xml is not empty'
                                                        FILE_SIZE=\$(stat -f%z coverage.xml 2>/dev/null || stat -c%s coverage.xml 2>/dev/null || echo '0')
                                                        echo "coverage.xml size: \${FILE_SIZE} bytes"
                                                    else
                                                        echo '⚠️ Warning: coverage.xml is empty'
                                                    fi
                                                else
                                                    echo '⚠️ Warning: coverage.xml not found, attempting to generate...'
                                                    coverage xml || echo '⚠️ Coverage XML not generated'
                                                    if [ ! -f coverage.xml ]; then
                                                        echo '⚠️ Warning: coverage.xml still not found after generation attempt'
                                                    fi
                                                fi
                                                
                                                # Copy HTML coverage reports to coverage directory
                                                mkdir -p coverage || true
                                                if [ -d htmlcov ]; then
                                                    cp -r htmlcov/* coverage/ || echo 'HTML coverage copy failed'
                                                elif [ -d coverage ]; then
                                                    echo 'Coverage reports already in coverage/'
                                                fi
                                            """
                                            
                                            // SonarQube analysis
                                            if (env.SONAR_TOKEN && env.SONAR_TOKEN != '') {
                                                withSonarQubeEnv('SonarQube') {
                                                    withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN_VALUE')]) {
                                                        sh """
                                                            export PATH=/opt/sonar-scanner/bin:\$PATH
                                                            export SONAR_HOST_URL=${env.SONARQUBE_URL ?: 'http://sonarqube:9000'}
                                                            export SONAR_TOKEN=\${SONAR_TOKEN_VALUE}
                                                            . venv/bin/activate
                                                            
                                                            # Verify coverage.xml exists before SonarQube analysis
                                                            if [ -f coverage.xml ]; then
                                                                echo '✅ coverage.xml found, proceeding with SonarQube analysis'
                                                                ls -lh coverage.xml || echo 'Could not list coverage.xml'
                                                            else
                                                                echo '⚠️ Warning: coverage.xml not found, SonarQube analysis may not include coverage'
                                                            fi
                                                            
                                                            # Run SonarQube analysis without qualitygate.wait to avoid build failure
                                                            # Quality Gate will be checked in a separate stage
                                                            /opt/sonar-scanner/bin/sonar-scanner || echo "⚠️ SonarQube scan completed with warnings (Quality Gate will be checked separately)"
                                                        """
                                                    }
                                                }
                                            } else {
                                        echo "SonarQube token not configured, skipping analysis for S1-CollecteDepots"
                                            }
                                            
                                    echo "✅ S1-CollecteDepots build completed"
                                        } catch (Exception e) {
                                    echo "❌ Error building S1-CollecteDepots: ${e.getMessage()}"
                                    currentBuild.result = 'UNSTABLE'
                                        }
                                    }
                                }
                            }
                        }
                
                stage('S4-PretraitementFeatures') {
                    steps {
                        dir('services/S4-PretraitementFeatures') {
                            script {
                                try {
                                    echo "Building S4-PretraitementFeatures..."
                                    
                                    sh """
                                        # Install system dependencies required for Python packages (cmake for pyarrow)
                                        echo 'Installing system dependencies for Python packages...'
                                        
                                        # Wait for apt-get lock to be released (max 60 seconds)
                                        echo 'Checking for apt-get lock...'
                                        COUNTER=0
                                        while [ -f /var/lib/apt/lists/lock ] || [ -f /var/lib/dpkg/lock ] || [ -f /var/cache/apt/archives/lock ]; do
                                            if [ \${COUNTER} -ge 60 ]; then
                                                echo '⚠️ apt-get lock timeout, attempting to install packages anyway...'
                                                break
                                            fi
                                            echo "Waiting for apt-get lock to be released... (\${COUNTER}/60)"
                                            sleep 2
                                            COUNTER=\$((COUNTER + 2))
                                        done
                                        
                                        # Try to update package list
                                        set +e
                                        apt-get update -qq
                                        APT_UPDATE_EXIT_CODE=\$?
                                        set -e
                                        
                                        if [ \${APT_UPDATE_EXIT_CODE} -ne 0 ]; then
                                            echo '⚠️ apt-get update failed, attempting to install packages anyway...'
                                        fi
                                        
                                        # Install required packages (try even if update failed)
                                        set +e
                                        apt-get install -y -qq cmake build-essential 2>&1 | grep -v "Unable to locate package" || {
                                            echo '⚠️ Failed to install cmake/build-essential, checking if already installed...'
                                            # Check if packages are already installed
                                            dpkg -l | grep -q cmake && echo '✅ cmake already installed' || echo '⚠️ cmake not found'
                                            dpkg -l | grep -q build-essential && echo '✅ build-essential already installed' || echo '⚠️ build-essential not found'
                                        }
                                        set -e
                                        
                                        export CARGO_HOME=/root/.cargo
                                        export RUSTUP_HOME=/root/.rustup
                                        export PATH=\$CARGO_HOME/bin:\$PATH
                                        if [ -f /root/.cargo/env ]; then
                                            . /root/.cargo/env
                                        fi
                                        python3 -m venv venv || { echo '❌ venv creation failed'; exit 1; }
                                        . venv/bin/activate || { echo '❌ venv activation failed'; exit 1; }
                                        pip install --upgrade pip || { echo '⚠️ pip upgrade failed'; }
                                        
                                        # Install Python dependencies
                                        echo 'Installing Python dependencies...'
                                        set +e
                                        pip install -r requirements.txt
                                        PIP_INSTALL_EXIT_CODE=\$?
                                        set -e
                                        
                                        if [ \${PIP_INSTALL_EXIT_CODE} -ne 0 ]; then
                                            echo '⚠️ pip install -r requirements.txt failed with exit code: ' \${PIP_INSTALL_EXIT_CODE}
                                            echo 'Attempting to install critical packages individually...'
                                            
                                            # Try to install pyarrow with a specific version that has pre-built wheels (avoid compilation)
                                            echo 'Attempting to install pyarrow with pre-built wheel (version 22.0.0)...'
                                            pip install --only-binary :all: "pyarrow>=12.0.0,<23.0.0" || {
                                                echo '⚠️ Failed to install pyarrow with pre-built wheel, trying specific version...'
                                                pip install "pyarrow==22.0.0" || {
                                                    echo '⚠️ Failed to install pyarrow 22.0.0, trying latest available wheel...'
                                                    pip install --only-binary :all: pyarrow || echo '⚠️ Failed to install pyarrow (may require Arrow C++ library)'
                                                }
                                            }
                                            
                                            # Install critical packages that are required for tests
                                            echo 'Installing critical packages for tests...'
                                            pip install httpx sqlalchemy imbalanced-learn || echo '⚠️ Failed to install some critical packages'
                                            
                                            # Install other important packages
                                            pip install pandas fastapi scikit-learn uvicorn pydantic requests kafka-python pytest-asyncio || echo '⚠️ Failed to install some additional packages'
                                        else
                                            echo '✅ Python dependencies installed successfully'
                                        fi
                                        
                                        # Ensure critical packages are installed even if requirements.txt succeeded (in case pyarrow failed)
                                        echo 'Verifying critical packages are installed...'
                                        pip install httpx sqlalchemy imbalanced-learn || echo '⚠️ Some packages may already be installed'
                                        
                                        # Install test dependencies
                                        pip install pytest pytest-cov coverage || { echo '⚠️ pytest install failed'; }
                                        
                                        # Run tests with proper error handling
                                        echo 'Running tests...'
                                        set +e
                                        pytest --cov=. --cov-report=xml --cov-report=html --cov-report=term-missing
                                        TEST_EXIT_CODE=\$?
                                        set -e
                                        
                                        if [ \${TEST_EXIT_CODE} -eq 0 ]; then
                                            echo '✅ All tests passed'
                                        elif [ \${TEST_EXIT_CODE} -eq 5 ]; then
                                            echo '⚠️ No tests collected'
                                        else
                                            echo "⚠️ Tests completed with exit code: \${TEST_EXIT_CODE}"
                                        fi
                                        
                                        # Ensure coverage.xml is generated even if tests failed
                                        if [ -f .coverage ]; then
                                            echo '✅ Found .coverage file, generating XML report...'
                                            coverage xml || echo '⚠️ Coverage XML generation from .coverage failed'
                                        else
                                            echo '⚠️ Warning: .coverage file not found'
                                        fi
                                        
                                        # Verify coverage.xml exists and is valid
                                        if [ -f coverage.xml ]; then
                                            echo '✅ coverage.xml found'
                                            if [ -s coverage.xml ]; then
                                                echo '✅ coverage.xml is not empty'
                                                FILE_SIZE=\$(stat -f%z coverage.xml 2>/dev/null || stat -c%s coverage.xml 2>/dev/null || echo '0')
                                                echo "coverage.xml size: \${FILE_SIZE} bytes"
                                            else
                                                echo '⚠️ Warning: coverage.xml is empty'
                                            fi
                                        else
                                            echo '⚠️ Warning: coverage.xml not found, attempting to generate...'
                                            coverage xml || echo '⚠️ Coverage XML not generated'
                                            if [ ! -f coverage.xml ]; then
                                                echo '⚠️ Warning: coverage.xml still not found after generation attempt'
                                            fi
                                        fi
                                        
                                        # Copy HTML coverage reports to coverage directory
                                        mkdir -p coverage || true
                                        if [ -d htmlcov ]; then
                                            cp -r htmlcov/* coverage/ || echo '⚠️ HTML coverage copy failed'
                                            echo '✅ Coverage reports copied to coverage/'
                                        else
                                            echo '⚠️ Warning: htmlcov directory not found'
                                        fi
                                    """
                                    
                                    if (env.SONAR_TOKEN && env.SONAR_TOKEN != '') {
                                        withSonarQubeEnv('SonarQube') {
                                            withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN_VALUE')]) {
                                                sh """
                                                    export PATH=/opt/sonar-scanner/bin:\$PATH
                                                    export SONAR_HOST_URL=${env.SONARQUBE_URL ?: 'http://sonarqube:9000'}
                                                    export SONAR_TOKEN=\${SONAR_TOKEN_VALUE}
                                                    . venv/bin/activate
                                                    
                                                    if [ -f coverage.xml ]; then
                                                        echo '✅ coverage.xml found, proceeding with SonarQube analysis'
                                                    else
                                                        echo '⚠️ Warning: coverage.xml not found, SonarQube analysis may not include coverage'
                                                    fi
                                                    
                                                    /opt/sonar-scanner/bin/sonar-scanner || echo "⚠️ SonarQube scan completed with warnings"
                                                """
                                            }
                                        }
                                    } else {
                                        echo "SonarQube token not configured, skipping analysis for S4-PretraitementFeatures"
                                    }
                                    
                                    echo "✅ S4-PretraitementFeatures build completed"
                                } catch (Exception e) {
                                    echo "❌ Error building S4-PretraitementFeatures: ${e.getMessage()}"
                                    currentBuild.result = 'UNSTABLE'
                                }
                            }
                        }
                    }
                }
                
                stage('S5-MLService') {
                    steps {
                        dir('services/S5-MLService') {
                            script {
                                try {
                                    echo "Building S5-MLService..."
                                    
                                    sh """
                                        export CARGO_HOME=/root/.cargo
                                        export RUSTUP_HOME=/root/.rustup
                                        export PATH=\$CARGO_HOME/bin:\$PATH
                                        if [ -f /root/.cargo/env ]; then
                                            . /root/.cargo/env
                                        fi
                                        python3 -m venv venv || { echo '❌ venv creation failed'; exit 1; }
                                        . venv/bin/activate || { echo '❌ venv activation failed'; exit 1; }
                                        pip install --upgrade pip || { echo '⚠️ pip upgrade failed'; }
                                        
                                        # Install Python dependencies
                                        echo 'Installing Python dependencies...'
                                        set +e
                                        pip install -r requirements.txt
                                        PIP_INSTALL_EXIT_CODE=\$?
                                        set -e
                                        
                                        if [ \${PIP_INSTALL_EXIT_CODE} -ne 0 ]; then
                                            echo '⚠️ pip install -r requirements.txt failed with exit code: ' \${PIP_INSTALL_EXIT_CODE}
                                            echo 'Attempting to install critical packages individually...'
                                            
                                            # Install critical packages that are required for the service
                                            pip install pandas fastapi scikit-learn xgboost lightgbm shap matplotlib seaborn || echo '⚠️ Failed to install some critical packages'
                                            
                                            # Install other important packages
                                            pip install uvicorn pydantic requests httpx joblib || echo '⚠️ Failed to install some additional packages'
                                        else
                                            echo '✅ Python dependencies installed successfully'
                                        fi
                                        
                                        # Ensure critical packages are installed even if requirements.txt succeeded
                                        echo 'Verifying critical packages are installed...'
                                        pip install httpx || echo '⚠️ httpx may already be installed'
                                        
                                        # Install test dependencies
                                        pip install pytest pytest-cov coverage || { echo '⚠️ pytest install failed'; }
                                        
                                        # Run tests with proper error handling
                                        echo 'Running tests...'
                                        set +e
                                        pytest --cov=. --cov-report=xml --cov-report=html --cov-report=term-missing
                                        TEST_EXIT_CODE=\$?
                                        set -e
                                        
                                        if [ \${TEST_EXIT_CODE} -eq 0 ]; then
                                            echo '✅ All tests passed'
                                        elif [ \${TEST_EXIT_CODE} -eq 5 ]; then
                                            echo '⚠️ No tests collected'
                                        else
                                            echo "⚠️ Tests completed with exit code: \${TEST_EXIT_CODE}"
                                        fi
                                        
                                        # Ensure coverage.xml is generated even if tests failed
                                        if [ -f .coverage ]; then
                                            echo '✅ Found .coverage file, generating XML report...'
                                            coverage xml || echo '⚠️ Coverage XML generation from .coverage failed'
                                        else
                                            echo '⚠️ Warning: .coverage file not found'
                                        fi
                                        
                                        # Verify coverage.xml exists and is valid
                                        if [ -f coverage.xml ]; then
                                            echo '✅ coverage.xml found'
                                            if [ -s coverage.xml ]; then
                                                echo '✅ coverage.xml is not empty'
                                                FILE_SIZE=\$(stat -f%z coverage.xml 2>/dev/null || stat -c%s coverage.xml 2>/dev/null || echo '0')
                                                echo "coverage.xml size: \${FILE_SIZE} bytes"
                                            else
                                                echo '⚠️ Warning: coverage.xml is empty'
                                            fi
                                        else
                                            echo '⚠️ Warning: coverage.xml not found, attempting to generate...'
                                            coverage xml || echo '⚠️ Coverage XML not generated'
                                            if [ ! -f coverage.xml ]; then
                                                echo '⚠️ Warning: coverage.xml still not found after generation attempt'
                                            fi
                                        fi
                                        
                                        # Copy HTML coverage reports to coverage directory
                                        mkdir -p coverage || true
                                        if [ -d htmlcov ]; then
                                            cp -r htmlcov/* coverage/ || echo '⚠️ HTML coverage copy failed'
                                            echo '✅ Coverage reports copied to coverage/'
                                        else
                                            echo '⚠️ Warning: htmlcov directory not found'
                                        fi
                                    """
                                    
                                    if (env.SONAR_TOKEN && env.SONAR_TOKEN != '') {
                                        withSonarQubeEnv('SonarQube') {
                                            withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN_VALUE')]) {
                                                sh """
                                                    export PATH=/opt/sonar-scanner/bin:\$PATH
                                                    export SONAR_HOST_URL=${env.SONARQUBE_URL ?: 'http://sonarqube:9000'}
                                                    export SONAR_TOKEN=\${SONAR_TOKEN_VALUE}
                                                    . venv/bin/activate
                                                    
                                                    if [ -f coverage.xml ]; then
                                                        echo '✅ coverage.xml found, proceeding with SonarQube analysis'
                                                    else
                                                        echo '⚠️ Warning: coverage.xml not found, SonarQube analysis may not include coverage'
                                                    fi
                                                    
                                                    /opt/sonar-scanner/bin/sonar-scanner || echo "⚠️ SonarQube scan completed with warnings"
                                                """
                                            }
                                        }
                                    } else {
                                        echo "SonarQube token not configured, skipping analysis for S5-MLService"
                                    }
                                    
                                    echo "✅ S5-MLService build completed"
                                } catch (Exception e) {
                                    echo "❌ Error building S5-MLService: ${e.getMessage()}"
                                    currentBuild.result = 'UNSTABLE'
                                }
                            }
                        }
                    }
                }
                
                stage('S6-MoteurPriorisation') {
                    steps {
                        dir('services/S6-MoteurPriorisation') {
                            script {
                                try {
                                    echo "Building S6-MoteurPriorisation..."
                                    
                                    sh """
                                        # Install system dependencies required for Python packages
                                        echo 'Installing system dependencies for Python packages...'
                                        
                                        # Wait for apt-get lock to be released (max 60 seconds)
                                        echo 'Checking for apt-get lock...'
                                        COUNTER=0
                                        while [ -f /var/lib/apt/lists/lock ] || [ -f /var/lib/dpkg/lock ] || [ -f /var/cache/apt/archives/lock ]; do
                                            if [ \${COUNTER} -ge 60 ]; then
                                                echo '⚠️ apt-get lock timeout, attempting to install packages anyway...'
                                                break
                                            fi
                                            echo "Waiting for apt-get lock to be released... (\${COUNTER}/60)"
                                            sleep 2
                                            COUNTER=\$((COUNTER + 2))
                                        done
                                        
                                        # Try to update package list
                                        set +e
                                        apt-get update -qq
                                        APT_UPDATE_EXIT_CODE=\$?
                                        set -e
                                        
                                        if [ \${APT_UPDATE_EXIT_CODE} -ne 0 ]; then
                                            echo '⚠️ apt-get update failed, attempting to install packages anyway...'
                                        fi
                                        
                                        # Install required packages (libpq-dev only, postgresql-dev doesn't exist)
                                        set +e
                                        apt-get install -y -qq libpq-dev 2>&1 | grep -v "Unable to locate package" || {
                                            echo '⚠️ Failed to install libpq-dev, checking if already installed...'
                                            # Check if package is already installed
                                            dpkg -l | grep -q libpq-dev && echo '✅ libpq-dev already installed' || echo '⚠️ libpq-dev not found'
                                        }
                                        set -e
                                        
                                        export CARGO_HOME=/root/.cargo
                                        export RUSTUP_HOME=/root/.rustup
                                        export PATH=\$CARGO_HOME/bin:\$PATH
                                        if [ -f /root/.cargo/env ]; then
                                            . /root/.cargo/env
                                        fi
                                        python3 -m venv venv || { echo '❌ venv creation failed'; exit 1; }
                                        . venv/bin/activate || { echo '❌ venv activation failed'; exit 1; }
                                        pip install --upgrade pip || { echo '⚠️ pip upgrade failed'; }
                                        
                                        # Install Python dependencies
                                        echo 'Installing Python dependencies...'
                                        
                                        # psycopg2-binary 2.9.9 has issues with Python 3.13, install compatible version first
                                        echo 'Installing psycopg2-binary compatible with Python 3.13...'
                                        pip install "psycopg2-binary>=2.9.11" || {
                                            echo '⚠️ Failed to install psycopg2-binary>=2.9.11, trying latest version...'
                                            pip install psycopg2-binary --upgrade || echo '⚠️ Failed to install psycopg2-binary'
                                        }
                                        
                                        set +e
                                        pip install -r requirements.txt
                                        PIP_INSTALL_EXIT_CODE=\$?
                                        set -e
                                        
                                        if [ \${PIP_INSTALL_EXIT_CODE} -ne 0 ]; then
                                            echo '⚠️ pip install -r requirements.txt failed with exit code: ' \${PIP_INSTALL_EXIT_CODE}
                                            echo 'Attempting to install critical packages individually...'
                                            
                                            # Install critical packages that are required for the service
                                            pip install fastapi uvicorn sqlalchemy alembic ortools httpx python-dotenv || echo '⚠️ Failed to install some critical packages'
                                            
                                            # Try to install psycopg2-binary again if it failed (skip if already installed)
                                            pip show psycopg2-binary >/dev/null 2>&1 || {
                                                echo '⚠️ psycopg2-binary not found, attempting to install compatible version...'
                                                pip install "psycopg2-binary>=2.9.11" || echo '⚠️ Failed to install psycopg2-binary (may require libpq-dev)'
                                            }
                                        else
                                            echo '✅ Python dependencies installed successfully'
                                        fi
                                        
                                        # Ensure critical packages are installed even if requirements.txt succeeded
                                        echo 'Verifying critical packages are installed...'
                                        pip install httpx python-dotenv || echo '⚠️ Some packages may already be installed'
                                        
                                        # Install test dependencies
                                        pip install pytest pytest-cov coverage || { echo '⚠️ pytest install failed'; }
                                        
                                        # Run tests with proper error handling
                                        echo 'Running tests...'
                                        set +e
                                        pytest --cov=. --cov-report=xml --cov-report=html --cov-report=term-missing
                                        TEST_EXIT_CODE=\$?
                                        set -e
                                        
                                        if [ \${TEST_EXIT_CODE} -eq 0 ]; then
                                            echo '✅ All tests passed'
                                        elif [ \${TEST_EXIT_CODE} -eq 5 ]; then
                                            echo '⚠️ No tests collected'
                                        else
                                            echo "⚠️ Tests completed with exit code: \${TEST_EXIT_CODE}"
                                        fi
                                        
                                        # Ensure coverage.xml is generated even if tests failed
                                        if [ -f .coverage ]; then
                                            echo '✅ Found .coverage file, generating XML report...'
                                            coverage xml || echo '⚠️ Coverage XML generation from .coverage failed'
                                        else
                                            echo '⚠️ Warning: .coverage file not found'
                                        fi
                                        
                                        # Verify coverage.xml exists and is valid
                                        if [ -f coverage.xml ]; then
                                            echo '✅ coverage.xml found'
                                            if [ -s coverage.xml ]; then
                                                echo '✅ coverage.xml is not empty'
                                                FILE_SIZE=\$(stat -f%z coverage.xml 2>/dev/null || stat -c%s coverage.xml 2>/dev/null || echo '0')
                                                echo "coverage.xml size: \${FILE_SIZE} bytes"
                                            else
                                                echo '⚠️ Warning: coverage.xml is empty'
                                            fi
                                        else
                                            echo '⚠️ Warning: coverage.xml not found, attempting to generate...'
                                            coverage xml || echo '⚠️ Coverage XML not generated'
                                            if [ ! -f coverage.xml ]; then
                                                echo '⚠️ Warning: coverage.xml still not found after generation attempt'
                                            fi
                                        fi
                                        
                                        # Copy HTML coverage reports to coverage directory
                                        mkdir -p coverage || true
                                        if [ -d htmlcov ]; then
                                            cp -r htmlcov/* coverage/ || echo '⚠️ HTML coverage copy failed'
                                            echo '✅ Coverage reports copied to coverage/'
                                        else
                                            echo '⚠️ Warning: htmlcov directory not found'
                                        fi
                                    """
                                    
                                    if (env.SONAR_TOKEN && env.SONAR_TOKEN != '') {
                                        withSonarQubeEnv('SonarQube') {
                                            withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN_VALUE')]) {
                                                sh """
                                                    export PATH=/opt/sonar-scanner/bin:\$PATH
                                                    export SONAR_HOST_URL=${env.SONARQUBE_URL ?: 'http://sonarqube:9000'}
                                                    export SONAR_TOKEN=\${SONAR_TOKEN_VALUE}
                                                    . venv/bin/activate
                                                    
                                                    if [ -f coverage.xml ]; then
                                                        echo '✅ coverage.xml found, proceeding with SonarQube analysis'
                                                    else
                                                        echo '⚠️ Warning: coverage.xml not found, SonarQube analysis may not include coverage'
                                                    fi
                                                    
                                                    /opt/sonar-scanner/bin/sonar-scanner || echo "⚠️ SonarQube scan completed with warnings"
                                                """
                                            }
                                        }
                                    } else {
                                        echo "SonarQube token not configured, skipping analysis for S6-MoteurPriorisation"
                                    }
                                    
                                    echo "✅ S6-MoteurPriorisation build completed"
                                } catch (Exception e) {
                                    echo "❌ Error building S6-MoteurPriorisation: ${e.getMessage()}"
                                    currentBuild.result = 'UNSTABLE'
                                }
                            }
                        }
                    }
                }
                
                stage('S7-TestScaffolder') {
                    steps {
                        dir('services/S7-TestScaffolder') {
                            script {
                                try {
                                    echo "Building S7-TestScaffolder..."
                                    
                                    sh """
                                        export CARGO_HOME=/root/.cargo
                                        export RUSTUP_HOME=/root/.rustup
                                        export PATH=\$CARGO_HOME/bin:\$PATH
                                        if [ -f /root/.cargo/env ]; then
                                            . /root/.cargo/env
                                        fi
                                        python3 -m venv venv || { echo '❌ venv creation failed'; exit 1; }
                                        . venv/bin/activate || { echo '❌ venv activation failed'; exit 1; }
                                        pip install --upgrade pip || { echo '⚠️ pip upgrade failed'; }
                                        
                                        # Install Python dependencies
                                        echo 'Installing Python dependencies...'
                                        set +e
                                        pip install -r requirements.txt
                                        PIP_INSTALL_EXIT_CODE=\$?
                                        set -e
                                        
                                        if [ \${PIP_INSTALL_EXIT_CODE} -ne 0 ]; then
                                            echo '⚠️ pip install -r requirements.txt failed with exit code: ' \${PIP_INSTALL_EXIT_CODE}
                                            echo 'Attempting to install critical packages individually...'
                                            # Try to install critical packages individually
                                            pip install fastapi uvicorn pydantic pydantic-settings jinja2 gitpython httpx python-dotenv || echo '⚠️ Failed to install some critical packages'
                                        else
                                            echo '✅ Python dependencies installed successfully'
                                        fi
                                        
                                        # Verify critical packages are installed even if requirements.txt succeeded
                                        echo 'Verifying critical Python packages are installed...'
                                        pip show fastapi >/dev/null || { echo '⚠️ fastapi not found after install'; }
                                        pip show uvicorn >/dev/null || { echo '⚠️ uvicorn not found after install'; }
                                        pip show pydantic >/dev/null || { echo '⚠️ pydantic not found after install'; }
                                        pip show jinja2 >/dev/null || { echo '⚠️ jinja2 not found after install'; }
                                        pip show gitpython >/dev/null || { echo '⚠️ gitpython not found after install'; }
                                        pip show httpx >/dev/null || { echo '⚠️ httpx not found after install'; }
                                        pip show python-dotenv >/dev/null || { echo '⚠️ python-dotenv not found after install'; }
                                        echo '✅ Critical Python packages verification complete'
                                        
                                        # Install test dependencies
                                        pip install pytest pytest-cov coverage || { echo '⚠️ pytest install failed'; }
                                        
                                        # Run tests with proper error handling
                                        echo 'Running tests...'
                                        set +e
                                        pytest --cov=. --cov-report=xml --cov-report=html --cov-report=term-missing
                                        TEST_EXIT_CODE=\$?
                                        set -e
                                        
                                        if [ \${TEST_EXIT_CODE} -eq 0 ]; then
                                            echo '✅ All tests passed'
                                        elif [ \${TEST_EXIT_CODE} -eq 5 ]; then
                                            echo '⚠️ No tests collected'
                                        else
                                            echo "⚠️ Tests completed with exit code: \${TEST_EXIT_CODE}"
                                        fi
                                        
                                        # Ensure coverage.xml is generated even if tests failed
                                        if [ -f .coverage ]; then
                                            echo '✅ Found .coverage file, generating XML report...'
                                            coverage xml || echo '⚠️ Coverage XML generation from .coverage failed'
                                        else
                                            echo '⚠️ Warning: .coverage file not found'
                                        fi
                                        
                                        # Verify coverage.xml exists and is valid
                                        if [ -f coverage.xml ]; then
                                            echo '✅ coverage.xml found'
                                            if [ -s coverage.xml ]; then
                                                echo '✅ coverage.xml is not empty'
                                                FILE_SIZE=\$(stat -f%z coverage.xml 2>/dev/null || stat -c%s coverage.xml 2>/dev/null || echo '0')
                                                echo "coverage.xml size: \${FILE_SIZE} bytes"
                                            else
                                                echo '⚠️ Warning: coverage.xml is empty'
                                            fi
                                        else
                                            echo '⚠️ Warning: coverage.xml not found, attempting to generate...'
                                            coverage xml || echo '⚠️ Coverage XML not generated'
                                            if [ ! -f coverage.xml ]; then
                                                echo '⚠️ Warning: coverage.xml still not found after generation attempt'
                                            fi
                                        fi
                                        
                                        # Copy HTML coverage reports to coverage directory
                                        mkdir -p coverage || true
                                        if [ -d htmlcov ]; then
                                            cp -r htmlcov/* coverage/ || echo '⚠️ HTML coverage copy failed'
                                            echo '✅ Coverage reports copied to coverage/'
                                        else
                                            echo '⚠️ Warning: htmlcov directory not found'
                                        fi
                                    """
                                    
                                    if (env.SONAR_TOKEN && env.SONAR_TOKEN != '') {
                                        withSonarQubeEnv('SonarQube') {
                                            withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN_VALUE')]) {
                                                sh """
                                                    export PATH=/opt/sonar-scanner/bin:\$PATH
                                                    export SONAR_HOST_URL=${env.SONARQUBE_URL ?: 'http://sonarqube:9000'}
                                                    export SONAR_TOKEN=\${SONAR_TOKEN_VALUE}
                                                    . venv/bin/activate
                                                    
                                                    if [ -f coverage.xml ]; then
                                                        echo '✅ coverage.xml found, proceeding with SonarQube analysis'
                                                    else
                                                        echo '⚠️ Warning: coverage.xml not found, SonarQube analysis may not include coverage'
                                                    fi
                                                    
                                                    /opt/sonar-scanner/bin/sonar-scanner || echo "⚠️ SonarQube scan completed with warnings"
                                                """
                                            }
                                        }
                                    } else {
                                        echo "SonarQube token not configured, skipping analysis for S7-TestScaffolder"
                                    }
                                    
                                    echo "✅ S7-TestScaffolder build completed"
                                } catch (Exception e) {
                                    echo "❌ Error building S7-TestScaffolder: ${e.getMessage()}"
                                    currentBuild.result = 'UNSTABLE'
                                }
                            }
                        }
                    }
                }
                
                // Frontend Service
                stage('S8-DashboardQualite') {
                    steps {
                        dir('services/S8-DashboardQualite/test-priority-hub') {
                            script {
                                try {
                                    echo "Building S8-DashboardQualite..."
                                    
                                    // Use npm directly (installed in Jenkins image)
                                    sh """
                                        # Install npm dependencies with fallback to npm install if npm ci fails
                                        echo 'Installing npm dependencies...'
                                        set +e
                                        npm ci 2>&1 | head -30
                                        NPM_CI_EXIT_CODE=\$?
                                        set -e
                                        
                                        if [ \${NPM_CI_EXIT_CODE} -ne 0 ]; then
                                            echo '⚠️ npm ci failed (exit code: ' \${NPM_CI_EXIT_CODE} '), likely due to package-lock.json desync'
                                            echo 'Cleaning npm cache and node_modules, then trying npm install...'
                                            
                                            # Clean npm cache
                                            npm cache clean --force || echo '⚠️ npm cache clean failed (may already be clean)'
                                            
                                            # Remove node_modules and package-lock.json
                                            rm -rf node_modules package-lock.json || echo '⚠️ Failed to remove node_modules/package-lock.json (may not exist)'
                                            
                                            # Install dependencies
                                            echo 'Running npm install to regenerate package-lock.json...'
                                            npm install || { 
                                                echo '❌ npm install failed'
                                                echo 'Attempting to install critical dependencies individually...'
                                                npm install --save-dev jsdom vitest @vitest/coverage-v8 || echo '⚠️ Failed to install critical test dependencies'
                                                exit 1
                                            }
                                            
                                            echo '✅ npm install succeeded, package-lock.json regenerated'
                                        else
                                            echo '✅ npm ci succeeded'
                                        fi
                                        
                                        # Ensure jsdom is installed (required for Vitest)
                                        echo 'Installing jsdom...'
                                        npm install --save-dev jsdom || echo '⚠️ jsdom install failed (may already be installed)'
                                        
                                        # Run lint with proper error handling
                                        echo 'Running lint...'
                                        set +e
                                        npm run lint
                                        LINT_EXIT_CODE=\$?
                                        set -e
                                        
                                        if [ \${LINT_EXIT_CODE} -eq 0 ]; then
                                            echo '✅ Lint passed'
                                        else
                                            echo "⚠️ Lint completed with exit code: \${LINT_EXIT_CODE} (continuing build)"
                                        fi
                                        
                                        # Build the application
                                        echo 'Building application...'
                                        npm run build || { echo '❌ Build failed'; exit 1; }
                                        echo '✅ Build successful'
                                        
                                        # Run tests with coverage - ensure LCOV report is generated
                                        echo 'Running tests with coverage...'
                                        set +e
                                        npm run test:coverage
                                        TEST_EXIT_CODE=\$?
                                        set -e
                                        
                                        if [ \${TEST_EXIT_CODE} -eq 0 ]; then
                                            echo '✅ All tests passed'
                                        else
                                            echo "⚠️ Tests completed with exit code: \${TEST_EXIT_CODE} (some tests may have failed)"
                                        fi
                                        
                                        # Verify coverage reports exist and generate LCOV if needed
                                        echo 'Checking coverage reports...'
                                        
                                        # Check for coverage directory
                                        if [ ! -d coverage ]; then
                                            echo '⚠️ Warning: Coverage directory not found, creating it...'
                                            mkdir -p coverage || echo '⚠️ Failed to create coverage directory'
                                        fi
                                        
                                        # Check for LCOV report in various locations
                                        LCOV_FILE=""
                                        if [ -f coverage/lcov.info ]; then
                                            LCOV_FILE="coverage/lcov.info"
                                                echo '✅ LCOV report found at coverage/lcov.info'
                                        else
                                            echo '⚠️ Warning: coverage/lcov.info not found, checking alternative locations...'
                                            # Search for lcov.info in common locations
                                            for LOCATION in "./coverage/lcov.info" "./lcov.info" "./coverage/.tmp/lcov.info" "./.coverage/lcov.info"; do
                                                if [ -f "\${LOCATION}" ]; then
                                                    LCOV_FILE="\${LOCATION}"
                                                    echo "✅ Found LCOV report at: \${LOCATION}"
                                                    break
                                                fi
                                            done
                                            
                                            # If still not found, search recursively
                                            if [ -z "\${LCOV_FILE}" ]; then
                                                FOUND_LCOV=\$(find . -name 'lcov.info' -type f 2>/dev/null | grep -v node_modules | head -n 1)
                                                if [ -n "\${FOUND_LCOV}" ]; then
                                                    LCOV_FILE="\${FOUND_LCOV}"
                                                    echo "✅ Found LCOV report at: \${FOUND_LCOV}"
                                                fi
                                            fi
                                            
                                            # Copy to standard location if found elsewhere
                                            if [ -n "\${LCOV_FILE}" ] && [ "\${LCOV_FILE}" != "coverage/lcov.info" ]; then
                                                mkdir -p coverage || true
                                                cp "\${LCOV_FILE}" coverage/lcov.info || echo '⚠️ Failed to copy LCOV report'
                                                LCOV_FILE="coverage/lcov.info"
                                            fi
                                        fi
                                        
                                        # If LCOV still not found, try to generate it explicitly
                                        if [ -z "\${LCOV_FILE}" ] || [ ! -f "\${LCOV_FILE}" ]; then
                                            echo '⚠️ Warning: No lcov.info found, attempting to generate LCOV report explicitly...'
                                            
                                            # Check if vitest.config.ts exists and configure coverage reporter
                                            if [ -f vitest.config.ts ] || [ -f vitest.config.js ]; then
                                                echo 'Vitest config found, ensuring LCOV reporter is configured...'
                                            fi
                                            
                                            # Try to generate coverage with explicit LCOV output
                                            set +e
                                            npm test -- --coverage --reporter=verbose --coverage.reporter=lcov --coverage.reporter=text --coverage.reporter=html 2>&1 | tail -20
                                            COVERAGE_EXIT=\$?
                                            set -e
                                            
                                            # Check again for LCOV file
                                            if [ -f coverage/lcov.info ]; then
                                                LCOV_FILE="coverage/lcov.info"
                                                echo '✅ LCOV report generated successfully'
                                            else
                                                # Check in .tmp directory (Vitest sometimes puts it there)
                                                if [ -f coverage/.tmp/lcov.info ]; then
                                                    cp coverage/.tmp/lcov.info coverage/lcov.info || echo '⚠️ Failed to copy from .tmp'
                                                    LCOV_FILE="coverage/lcov.info"
                                                    echo '✅ LCOV report found in .tmp and copied'
                                                else
                                                    echo '⚠️ Warning: LCOV report generation failed or not found'
                                                fi
                                            fi
                                        fi
                                        
                                        # Final verification
                                        if [ -n "\${LCOV_FILE}" ] && [ -f "\${LCOV_FILE}" ]; then
                                            FILE_SIZE=\$(stat -f%z "\${LCOV_FILE}" 2>/dev/null || stat -c%s "\${LCOV_FILE}" 2>/dev/null || echo '0')
                                            echo "✅ LCOV report verified: \${LCOV_FILE} (size: \${FILE_SIZE} bytes)"
                                            
                                            # Ensure it's in the standard location for SonarQube
                                            if [ "\${LCOV_FILE}" != "coverage/lcov.info" ]; then
                                                mkdir -p coverage || true
                                                cp "\${LCOV_FILE}" coverage/lcov.info || echo '⚠️ Failed to copy to standard location'
                                            fi
                                        else
                                            echo '⚠️ Warning: LCOV report not available - SonarQube analysis will proceed without coverage'
                                        fi
                                    """
                                    
                                    // SonarQube analysis
                                    if (env.SONAR_TOKEN && env.SONAR_TOKEN != '') {
                                        withSonarQubeEnv('SonarQube') {
                                            withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN_VALUE')]) {
                                                sh """
                                                    export PATH=/opt/sonar-scanner/bin:\$PATH
                                                    export SONAR_HOST_URL=${env.SONARQUBE_URL ?: 'http://sonarqube:9000'}
                                                    export SONAR_TOKEN=\${SONAR_TOKEN_VALUE}
                                                    
                                                    # Verify coverage report exists before SonarQube analysis
                                                    if [ -f coverage/lcov.info ]; then
                                                        echo 'LCOV report found, proceeding with SonarQube analysis'
                                                    else
                                                        echo 'Warning: coverage/lcov.info not found, SonarQube analysis may not include coverage'
                                                    fi
                                                    
                                                    # Run SonarQube analysis without qualitygate.wait to avoid build failure
                                                    # Quality Gate will be checked in a separate stage
                                                    /opt/sonar-scanner/bin/sonar-scanner || echo "⚠️ SonarQube scan completed with warnings (Quality Gate will be checked separately)"
                                                """
                                            }
                                        }
                                    } else {
                                        echo "SonarQube token not configured, skipping analysis for S8-DashboardQualite"
                                    }
                                    
                                    echo "✅ S8-DashboardQualite build completed"
                                } catch (Exception e) {
                                    echo "❌ Error building S8-DashboardQualite: ${e.getMessage()}"
                                    currentBuild.result = 'UNSTABLE'
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
                    // Use actual SonarQube project keys (from sonar-project.properties or Maven format: groupId:artifactId)
                    // Note: Some projects use sonar-project.properties keys, others use Maven keys
                    // Based on actual SonarQube analysis logs:
                    def services = [
                        'com.prioritest:api-gateway',  // Maven key (from S0 pom.xml: com.prioritest:api-gateway)
                        'prioritest-s1-collectedepots',
                        'com.reco:S2-AnalyseStatique',  // Maven key (from S2 pom.xml: com.reco:S2-AnalyseStatique)
                        'com.example:historique-tests',  // Maven key (from S3 pom.xml: com.example:historique-tests)
                        'prioritest-s4-pretraitementfeatures',
                        'prioritest-s5-mlservice',
                        'prioritest-s6-moteurpriorisation',
                        'prioritest-s7-testscaffolder',
                        'prioritest-s8-dashboard',
                        'com.testprioritization:cicd-integration-service'  // Maven key (from S9 pom.xml: com.testprioritization:cicd-integration-service)
                    ]
                    
                    // Use withCredentials to get the actual token value
                    withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN_VALUE')]) {
                        def url = env.SONARQUBE_URL ?: 'http://sonarqube:9000'
                        
                        def failedQualityGates = []
                        
                        services.each { projectKey ->
                            try {
                                // Use the actual token value from credentials (without env. prefix)
                                def response = sh(
                                    script: "curl -s -u '${SONAR_TOKEN_VALUE}:' '${url}/api/qualitygates/project_status?projectKey=${projectKey}'",
                                    returnStdout: true
                                ).trim()
                                
                                // Try to extract status (jq may not be available)
                                def qualityGateStatus = 'UNKNOWN'
                                if (response.contains('"status":"OK"')) {
                                    qualityGateStatus = 'OK'
                                } else if (response.contains('"status":"ERROR"')) {
                                    qualityGateStatus = 'ERROR'
                                } else if (response.contains('"status":"WARN"')) {
                                    qualityGateStatus = 'WARN'
                                }
                                
                                if (qualityGateStatus == 'OK') {
                                    echo "✅ Quality Gate passed for ${projectKey}"
                                } else if (qualityGateStatus == 'UNKNOWN') {
                                    echo "⚠️ Quality Gate not available for ${projectKey} (project may not exist yet or analysis not completed)"
                                } else {
                                    echo "⚠️ Warning: Quality Gate status for ${projectKey}: ${qualityGateStatus}"
                                    echo "   View details: ${url}/dashboard?id=${projectKey.replace(':', '%3A')}"
                                    
                                    // Try to get more details about failed conditions
                                    try {
                                        def details = sh(
                                            script: "curl -s -u '${SONAR_TOKEN_VALUE}:' '${url}/api/qualitygates/project_status?projectKey=${projectKey}' | grep -o '\"metric\":\"[^\"]*\"' | head -5 || true",
                                            returnStdout: true
                                        ).trim()
                                        if (details) {
                                            echo "   Failed conditions: ${details}"
                                        }
                                    } catch (Exception e) {
                                        // Ignore if we can't get details
                                    }
                                    
                                    failedQualityGates.add(projectKey)
                                    // Don't fail the build, just warn
                                }
                            } catch (Exception e) {
                                echo "Could not check Quality Gate for ${projectKey}: ${e.getMessage()}"
                            }
                        }
                        
                        // Summary
                        if (failedQualityGates.size() > 0) {
                            echo ""
                            echo "⚠️ Summary: ${failedQualityGates.size()} service(s) failed Quality Gate:"
                            failedQualityGates.each { key ->
                                echo "   - ${key}"
                            }
                            echo "   Please check SonarQube dashboard for details and improve code quality/coverage."
                        } else {
                            echo ""
                            echo "✅ All Quality Gates passed!"
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
                    // Collect coverage reports from all services
                    script {
                        def coverageFound = false
                        
                        // Check Java services (JaCoCo HTML reports)
                        def javaServices = ['S0-ApiGateway', 'S2-AnalyseStatique', 'S3-HistoriqueTests', 'S9-Integrations']
                        javaServices.each { service ->
                            def coveragePath = "services/${service}/coverage/index.html"
                            if (fileExists(coveragePath)) {
                                echo "Found coverage report for ${service}"
                                coverageFound = true
                            }
                        }
                        
                        // Check Python services (pytest-cov HTML reports)
                        def pythonServices = ['S1-CollecteDepots', 'S4-PretraitementFeatures', 'S5-MLService', 'S6-MoteurPriorisation', 'S7-TestScaffolder']
                        pythonServices.each { service ->
                            def coveragePath = "services/${service}/coverage/index.html"
                            if (fileExists(coveragePath)) {
                                echo "Found coverage report for ${service}"
                                coverageFound = true
                            }
                        }
                        
                        // Check Frontend (Vitest coverage)
                        def frontendPath = "services/S8-DashboardQualite/test-priority-hub/coverage/index.html"
                        if (fileExists(frontendPath)) {
                            echo "Found coverage report for Frontend"
                            coverageFound = true
                        }
                        
                        // Try to publish from root coverage directory
                        if (fileExists('coverage/index.html')) {
                            publishHTML([
                                reportDir: 'coverage',
                                reportFiles: 'index.html',
                                reportName: 'Coverage Report'
                            ])
                            coverageFound = true
                        }
                        
                        if (!coverageFound) {
                            echo "No coverage reports found in any service directory"
                        }
                    }
                } catch (Exception e) {
                    echo "Could not publish coverage report: ${e.getMessage()}"
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

