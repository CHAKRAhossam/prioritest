package com.reco.analysestatiqueservice.service;

import com.reco.analysestatiqueservice.dto.CodeMetricsEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

/**
 * Service for publishing code metrics to Feast Feature Store.
 * Uses HTTP API to push features to Feast.
 */
@Service
@ConditionalOnProperty(name = "feast.enabled", havingValue = "true", matchIfMissing = false)
public class FeastService implements FeastServiceInterface {
    
    private static final Logger logger = LoggerFactory.getLogger(FeastService.class);
    
    private final WebClient webClient;
    
    @Value("${feast.url:http://localhost:6566}")
    private String feastUrl;
    
    @Value("${feast.feature-service:code-metrics-service}")
    private String featureService;
    
    public FeastService(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder.baseUrl(feastUrl).build();
    }
    
    /**
     * Publishes code metrics to Feast Feature Store.
     * 
     * @param event The code metrics event
     */
    public void publishToFeast(CodeMetricsEvent event) {
        try {
            Map<String, Object> feastRequest = buildFeastRequest(event);
            
            webClient.post()
                    .uri("/api/v1/features/online")
                    .contentType(MediaType.APPLICATION_JSON)
                    .bodyValue(feastRequest)
                    .retrieve()
                    .bodyToMono(String.class)
                    .doOnSuccess(response -> logger.debug("Published to Feast: {}", event.getClassName()))
                    .doOnError(error -> logger.error("Failed to publish to Feast: {}", event.getClassName(), error))
                    .subscribe();
                    
        } catch (Exception e) {
            logger.error("Error publishing to Feast", e);
        }
    }
    
    /**
     * Builds Feast request payload.
     */
    private Map<String, Object> buildFeastRequest(CodeMetricsEvent event) {
        Map<String, Object> request = new HashMap<>();
        request.put("feature_service", featureService);
        
        // Entity
        Map<String, Object> entity = new HashMap<>();
        entity.put("class_name", event.getClassName());
        entity.put("repository_id", event.getRepositoryId());
        request.put("entity", entity);
        
        // Features
        Map<String, Object> features = new HashMap<>();
        CodeMetricsEvent.Metrics metrics = event.getMetrics();
        
        features.put("loc", metrics.getLoc());
        features.put("cyclomatic_complexity", metrics.getCyclomaticComplexity());
        
        if (metrics.getCkMetrics() != null) {
            CodeMetricsEvent.CKMetrics ck = metrics.getCkMetrics();
            features.put("wmc", ck.getWmc());
            features.put("dit", ck.getDit());
            features.put("noc", ck.getNoc());
            features.put("cbo", ck.getCbo());
            features.put("rfc", ck.getRfc());
            features.put("lcom", ck.getLcom());
        }
        
        if (metrics.getDependencies() != null) {
            CodeMetricsEvent.Dependencies deps = metrics.getDependencies();
            features.put("in_degree", deps.getInDegree());
            features.put("out_degree", deps.getOutDegree());
        }
        
        request.put("features", features);
        request.put("timestamp", Instant.now().toString());
        
        return request;
    }
}

