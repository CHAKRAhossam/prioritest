package com.reco.analysestatiqueservice.kafka;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.reco.analysestatiqueservice.dto.CommitEvent;
import com.reco.analysestatiqueservice.service.MetricsService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.kafka.support.KafkaHeaders;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.stereotype.Component;

/**
 * Kafka consumer for repository.commits topic.
 * Consumes commit events and triggers code analysis.
 * Only active if kafka.enabled=true in application.properties
 */
@Component
@ConditionalOnProperty(name = "kafka.enabled", havingValue = "true", matchIfMissing = false)
public class CommitEventConsumer {
    
    private static final Logger logger = LoggerFactory.getLogger(CommitEventConsumer.class);
    
    private final ObjectMapper objectMapper;
    private final MetricsService metricsService;
    
    public CommitEventConsumer(ObjectMapper objectMapper, MetricsService metricsService) {
        this.objectMapper = objectMapper;
        this.metricsService = metricsService;
    }
    
    @KafkaListener(
            topics = "${kafka.topic.repository-commits:repository.commits}",
            groupId = "${kafka.consumer.group-id:analyse-statique-service}",
            containerFactory = "kafkaListenerContainerFactory"
    )
    public void consumeCommitEvent(
            @Payload String message,
            @Header(KafkaHeaders.RECEIVED_TOPIC) String topic,
            @Header(KafkaHeaders.RECEIVED_PARTITION) int partition,
            @Header(KafkaHeaders.OFFSET) long offset,
            Acknowledgment acknowledgment) {
        
        logger.info("Received commit event from topic: {}, partition: {}, offset: {}", 
                topic, partition, offset);
        
        try {
            CommitEvent event = objectMapper.readValue(message, CommitEvent.class);
            logger.info("Processing commit event: {} for repository: {} at commit: {}", 
                    event.getEventId(), event.getRepositoryId(), event.getCommitSha());
            
            // Process the commit event
            metricsService.processCommitEvent(event);
            
            // Acknowledge message
            if (acknowledgment != null) {
                acknowledgment.acknowledge();
            }
            
        } catch (Exception e) {
            logger.error("Error processing commit event", e);
            // In production, implement retry logic or dead letter queue
        }
    }
}

