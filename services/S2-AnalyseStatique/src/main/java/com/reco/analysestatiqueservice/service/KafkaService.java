package com.reco.analysestatiqueservice.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.reco.analysestatiqueservice.dto.CodeMetricsEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

/**
 * Service for publishing code metrics to Kafka topic.
 * Only active if kafka.enabled=true in application.properties
 */
@Service
@ConditionalOnProperty(name = "kafka.enabled", havingValue = "true", matchIfMissing = false)
public class KafkaService implements KafkaServiceInterface {
    
    private static final Logger logger = LoggerFactory.getLogger(KafkaService.class);
    
    private final KafkaTemplate<String, String> kafkaTemplate;
    private final ObjectMapper objectMapper;
    
    @Value("${kafka.topic.code-metrics:code.metrics}")
    private String codeMetricsTopic;
    
    public KafkaService(KafkaTemplate<String, String> kafkaTemplate, ObjectMapper objectMapper) {
        this.kafkaTemplate = kafkaTemplate;
        this.objectMapper = objectMapper;
    }
    
    /**
     * Publishes a code metrics event to Kafka.
     * 
     * @param event The code metrics event
     */
    public void publishCodeMetrics(CodeMetricsEvent event) {
        try {
            String json = objectMapper.writeValueAsString(event);
            String key = event.getRepositoryId() + ":" + event.getClassName();
            
            kafkaTemplate.send(codeMetricsTopic, key, json)
                    .whenComplete((result, ex) -> {
                        if (ex == null) {
                            logger.debug("Published code metrics to Kafka: {} - {}", 
                                    event.getRepositoryId(), event.getClassName());
                        } else {
                            logger.error("Failed to publish code metrics to Kafka: {} - {}", 
                                    event.getRepositoryId(), event.getClassName(), ex);
                        }
                    });
            
        } catch (Exception e) {
            logger.error("Error serializing code metrics event", e);
        }
    }
}

