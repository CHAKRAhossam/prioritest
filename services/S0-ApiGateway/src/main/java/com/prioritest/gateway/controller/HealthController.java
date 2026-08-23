package com.prioritest.gateway.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

/**
 * Health controller for aggregated health checks.
 * Provides a single endpoint to check all service health statuses.
 */
@RestController
@RequestMapping("/api/health")
public class HealthController {

    private final WebClient webClient = WebClient.builder().build();

    /**
     * Gateway health check.
     */
    @GetMapping
    public Mono<ResponseEntity<Map<String, Object>>> gatewayHealth() {
        Map<String, Object> health = new HashMap<>();
        health.put("status", "UP");
        health.put("service", "api-gateway");
        health.put("timestamp", LocalDateTime.now().toString());
        health.put("version", "1.0.0");
        
        return Mono.just(ResponseEntity.ok(health));
    }

    /**
     * Aggregated health check for all services.
     */
    @GetMapping("/all")
    public Mono<ResponseEntity<Map<String, Object>>> allServicesHealth() {
        Map<String, Object> response = new HashMap<>();
        response.put("gateway", "UP");
        response.put("timestamp", LocalDateTime.now().toString());
        
        Map<String, String> services = new HashMap<>();
        services.put("s1-collecte", "http://prioritest-s1-collecte:8001/health");
        services.put("s2-analyse", "http://prioritest-s2-analyse:8081/actuator/health");
        services.put("s3-historique", "http://prioritest-s3-historique:8082/actuator/health");
        services.put("s4-features", "http://prioritest-s4-features:8004/health");
        services.put("s5-ml", "http://prioritest-s5-ml:8005/health");
        services.put("s6-prioritization", "http://prioritest-s6-prioritization:8006/health");
        services.put("s7-scaffolder", "http://prioritest-s7-scaffolder:8007/health");
        services.put("s9-integrations", "http://prioritest-s9-integrations:8009/v1/health");

        Map<String, Object> serviceStatuses = new HashMap<>();
        
        for (Map.Entry<String, String> entry : services.entrySet()) {
            try {
                serviceStatuses.put(entry.getKey(), checkServiceHealth(entry.getValue()));
            } catch (Exception e) {
                serviceStatuses.put(entry.getKey(), "DOWN");
            }
        }
        
        response.put("services", serviceStatuses);
        
        return Mono.just(ResponseEntity.ok(response));
    }

    private String checkServiceHealth(String url) {
        try {
            webClient.get()
                .uri(url)
                .retrieve()
                .bodyToMono(String.class)
                .block();
            return "UP";
        } catch (Exception e) {
            return "DOWN";
        }
    }

    /**
     * Get routing information.
     */
    @GetMapping("/routes")
    public Mono<ResponseEntity<Map<String, Object>>> getRoutes() {
        Map<String, Object> routes = new HashMap<>();
        
        routes.put("s1", Map.of(
            "path", "/api/s1/**",
            "service", "S1-CollecteDepots",
            "port", 8001,
            "endpoints", new String[]{
                "POST /api/s1/api/v1/collect",
                "GET /api/s1/api/v1/collect/status",
                "POST /api/s1/api/v1/webhooks/github",
                "POST /api/s1/api/v1/webhooks/gitlab",
                "POST /api/s1/api/v1/webhooks/jira",
                "POST /api/s1/api/v1/artifacts/upload/{type}",
                "GET /api/s1/api/v1/artifacts/{repo_id}/{commit}"
            }
        ));
        
        routes.put("s2", Map.of(
            "path", "/api/s2/**",
            "service", "S2-AnalyseStatique",
            "port", 8081,
            "endpoints", new String[]{
                "POST /api/s2/metrics/analyze",
                "GET /api/s2/health"
            }
        ));
        
        routes.put("s3", Map.of(
            "path", "/api/s3/**",
            "service", "S3-HistoriqueTests",
            "port", 8082,
            "endpoints", new String[]{
                "POST /api/s3/coverage/jacoco",
                "POST /api/s3/coverage/pit",
                "GET /api/s3/coverage/commit/{sha}",
                "POST /api/s3/tests/surefire",
                "GET /api/s3/tests/commit/{sha}",
                "GET /api/s3/flakiness/flaky",
                "POST /api/s3/flakiness/calculate",
                "GET /api/s3/debt/commit/{sha}"
            }
        ));
        
        routes.put("s4", Map.of(
            "path", "/api/s4/**",
            "service", "S4-PretraitementFeatures",
            "port", 8004,
            "endpoints", new String[]{
                "POST /api/s4/run-pipeline",
                "GET /api/s4/health"
            }
        ));
        
        routes.put("s5", Map.of(
            "path", "/api/s5/**",
            "service", "S5-MLService",
            "port", 8005,
            "endpoints", new String[]{
                "POST /api/s5/train",
                "POST /api/s5/predict",
                "POST /api/s5/predict/batch",
                "GET /api/s5/features"
            }
        ));
        
        routes.put("s6", Map.of(
            "path", "/api/s6/**",
            "service", "S6-MoteurPriorisation",
            "port", 8006,
            "endpoints", new String[]{
                "POST /api/s6/prioritize",
                "GET /api/s6/prioritize/{repository_id}"
            }
        ));
        
        routes.put("s7", Map.of(
            "path", "/api/s7/**",
            "service", "S7-TestScaffolder",
            "port", 8007,
            "endpoints", new String[]{
                "GET /api/s7/test-scaffold",
                "POST /api/s7/test-scaffold/batch",
                "POST /api/s7/analyze",
                "POST /api/s7/generate",
                "POST /api/s7/generate-complete"
            }
        ));
        
        routes.put("s9", Map.of(
            "path", "/api/s9/**",
            "service", "S9-Integrations",
            "port", 8009,
            "endpoints", new String[]{
                "POST /api/s9/webhooks/github",
                "POST /api/s9/webhooks/gitlab",
                "POST /api/s9/training/trigger",
                "GET /api/s9/training/status/{jobId}"
            }
        ));
        
        return Mono.just(ResponseEntity.ok(routes));
    }
}
