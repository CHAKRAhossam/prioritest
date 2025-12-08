package com.testprioritization.controller;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.reactive.function.client.WebClient;

import com.testprioritization.config.AppProperties;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import reactor.core.publisher.Mono;

/**
 * Health check controller for liveness and readiness probes.
 */
@RestController
@RequestMapping("/v1/health")
@Tag(name = "Health", description = "Health check endpoints")
@RequiredArgsConstructor
@Slf4j
public class HealthController {

    private final AppProperties appProperties;
    private final WebClient trainingWebClient;
    private final WebClient prioritizationWebClient;

    @Value("${spring.application.name}")
    private String applicationName;

    @Value("${spring.profiles.active:default}")
    private String activeProfile;

    private final Instant startTime = Instant.now();

    /**
     * Basic liveness probe.
     */
    @GetMapping("/live")
    @Operation(summary = "Liveness probe", description = "Check if the service is alive")
    public ResponseEntity<Map<String, Object>> liveness() {
        return ResponseEntity.ok(Map.of(
                "status", "UP",
                "timestamp", Instant.now().toString()
        ));
    }

    /**
     * Readiness probe with dependency checks.
     */
    @GetMapping("/ready")
    @Operation(summary = "Readiness probe", description = "Check if the service is ready")
    public Mono<ResponseEntity<Map<String, Object>>> readiness() {
        return checkDependencies()
                .map(dependencies -> {
                    boolean allHealthy = dependencies.values().stream()
                            .allMatch(status -> "UP".equals(status));
                    
                    Map<String, Object> response = new HashMap<>();
                    response.put("status", allHealthy ? "UP" : "DEGRADED");
                    response.put("timestamp", Instant.now().toString());
                    response.put("dependencies", dependencies);
                    
                    return allHealthy ? 
                            ResponseEntity.ok(response) :
                            ResponseEntity.status(503).body(response);
                })
                .onErrorReturn(ResponseEntity.status(503).body(Map.of(
                        "status", "DOWN",
                        "timestamp", Instant.now().toString()
                )));
    }

    /**
     * Detailed health information.
     */
    @GetMapping
    @Operation(summary = "Health details", description = "Get detailed health information")
    public Mono<ResponseEntity<Map<String, Object>>> health() {
        return checkDependencies()
                .map(dependencies -> {
                    Map<String, Object> response = new HashMap<>();
                    response.put("application", applicationName);
                    response.put("profile", activeProfile);
                    response.put("status", "UP");
                    response.put("timestamp", Instant.now().toString());
                    response.put("uptime", calculateUptime());
                    response.put("dependencies", dependencies);
                    response.put("configuration", getConfigurationSummary());
                    
                    return ResponseEntity.ok(response);
                });
    }

    /**
     * Check health of dependent services.
     */
    private Mono<Map<String, String>> checkDependencies() {
        Mono<String> trainingHealth = checkServiceHealth(trainingWebClient, "Training");
        Mono<String> prioritizationHealth = checkServiceHealth(prioritizationWebClient, "Prioritization");

        return Mono.zip(trainingHealth, prioritizationHealth)
                .map(tuple -> Map.of(
                        "training-service", tuple.getT1(),
                        "prioritization-service", tuple.getT2()
                ))
                .onErrorReturn(Map.of(
                        "training-service", "UNKNOWN",
                        "prioritization-service", "UNKNOWN"
                ));
    }

    /**
     * Check health of a single service.
     */
    private Mono<String> checkServiceHealth(WebClient client, String serviceName) {
        return client.get()
                .uri("/health")
                .retrieve()
                .bodyToMono(Map.class)
                .timeout(java.time.Duration.ofSeconds(5))
                .map(response -> {
                    String status = (String) response.get("status");
                    return "UP".equals(status) ? "UP" : "DOWN";
                })
                .doOnError(error -> log.debug("{} service health check failed: {}", 
                        serviceName, error.getMessage()))
                .onErrorReturn("DOWN");
    }

    /**
     * Calculate uptime.
     */
    private String calculateUptime() {
        long seconds = java.time.Duration.between(startTime, Instant.now()).getSeconds();
        long days = seconds / 86400;
        long hours = (seconds % 86400) / 3600;
        long minutes = (seconds % 3600) / 60;
        long secs = seconds % 60;
        
        if (days > 0) {
            return String.format("%dd %dh %dm %ds", days, hours, minutes, secs);
        } else if (hours > 0) {
            return String.format("%dh %dm %ds", hours, minutes, secs);
        } else if (minutes > 0) {
            return String.format("%dm %ds", minutes, secs);
        } else {
            return String.format("%ds", secs);
        }
    }

    /**
     * Get configuration summary (non-sensitive).
     */
    private Map<String, Object> getConfigurationSummary() {
        return Map.of(
                "policyGateEnabled", appProperties.getPolicyGate().isEnabled(),
                "policyGateBlockOnHighRisk", appProperties.getPolicyGate().isBlockOnHighRisk(),
                "trainingEnabled", appProperties.getTraining().isEnabled(),
                "riskThresholdHigh", appProperties.getRisk().getThreshold().getHigh(),
                "riskThresholdMedium", appProperties.getRisk().getThreshold().getMedium()
        );
    }
}

