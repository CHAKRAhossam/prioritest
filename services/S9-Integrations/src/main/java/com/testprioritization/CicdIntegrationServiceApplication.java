package com.testprioritization;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.annotation.EnableScheduling;

import com.testprioritization.config.AppProperties;

/**
 * CI/CD Integration Service - Main Application
 * 
 * This microservice provides:
 * - GitHub Checks API integration
 * - GitLab MR API integration
 * - Automatic PR/MR comments with risk analysis
 * - Policy gate for high-risk class modifications
 * - Training triggers for ML model updates
 * - OpenTelemetry observability
 * - Keycloak SSO authentication
 */
@SpringBootApplication
@EnableConfigurationProperties(AppProperties.class)
@EnableCaching
@EnableAsync
@EnableScheduling
public class CicdIntegrationServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(CicdIntegrationServiceApplication.class, args);
    }
}

