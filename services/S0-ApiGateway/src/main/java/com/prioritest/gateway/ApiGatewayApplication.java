package com.prioritest.gateway;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;

/**
 * API Gateway for PRIORITEST Platform.
 * 
 * Routes all requests to the appropriate microservice:
 * 
 * ROUTING TABLE:
 * ┌─────────────────────────────────┬─────────────────────────────────────────────┬──────────┐
 * │ Gateway Path                    │ Target Service                              │ Port     │
 * ├─────────────────────────────────┼─────────────────────────────────────────────┼──────────┤
 * │ /api/s1/**                      │ S1-CollecteDepots (collect, webhooks)       │ 8001     │
 * │ /api/s2/**                      │ S2-AnalyseStatique (CK metrics)             │ 8081     │
 * │ /api/s3/**                      │ S3-HistoriqueTests (coverage, tests)        │ 8082     │
 * │ /api/s4/**                      │ S4-PretraitementFeatures (pipeline)         │ 8004     │
 * │ /api/s5/**                      │ S5-MLService (train, predict)               │ 8005     │
 * │ /api/s6/**                      │ S6-MoteurPriorisation (prioritize)          │ 8006     │
 * │ /api/s7/**                      │ S7-TestScaffolder (generate tests)          │ 8007     │
 * │ /api/s9/**                      │ S9-Integrations (webhooks, training)        │ 8009     │
 * └─────────────────────────────────┴─────────────────────────────────────────────┴──────────┘
 * 
 * Features:
 * - Service Discovery via Eureka
 * - Load Balancing
 * - Circuit Breaker (Resilience4j)
 * - Rate Limiting
 * - CORS Configuration
 * - Request/Response Logging
 * 
 * @author PRIORITEST Team
 */
@SpringBootApplication
@EnableDiscoveryClient
public class ApiGatewayApplication {

    public static void main(String[] args) {
        SpringApplication.run(ApiGatewayApplication.class, args);
    }
}
