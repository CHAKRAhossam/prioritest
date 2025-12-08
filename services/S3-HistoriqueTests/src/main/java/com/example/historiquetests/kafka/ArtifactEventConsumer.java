package com.example.historiquetests.kafka;

import com.example.historiquetests.dto.ArtifactEvent;
import com.example.historiquetests.service.ArtifactProcessingService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

/**
 * Kafka Consumer for CI/CD artifact events.
 * Listens to topic: ci.artifacts
 * 
 * Processes incoming artifact notifications and triggers report parsing.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class ArtifactEventConsumer {

    private final ArtifactProcessingService artifactProcessingService;

    /**
     * Consume artifact events from Kafka topic ci.artifacts
     * 
     * Expected message format:
     * {
     *   "event_id": "evt_125",
     *   "repository_id": "repo_12345",
     *   "build_id": "build_789",
     *   "commit_sha": "abc123",
     *   "artifact_type": "jacoco",
     *   "artifact_url": "s3://minio/artifacts/jacoco_abc123.xml"
     * }
     */
    @KafkaListener(
        topics = "${kafka.topic.artifacts:ci.artifacts}",
        groupId = "${spring.kafka.consumer.group-id:historique-tests-group}",
        containerFactory = "kafkaListenerContainerFactory"
    )
    public void consumeArtifactEvent(ArtifactEvent event) {
        log.info("Received artifact event: eventId={}, type={}, repository={}, commit={}",
                event.getEventId(), event.getArtifactType(), 
                event.getRepositoryId(), event.getCommitSha());
        
        try {
            // Validate the event
            if (!event.isValid()) {
                log.warn("Invalid artifact event received: {}", event);
                return;
            }
            
            // Process the artifact based on type
            artifactProcessingService.processArtifact(event);
            
            log.info("Successfully processed artifact event: {}", event.getEventId());
            
        } catch (Exception e) {
            log.error("Error processing artifact event: {}", event.getEventId(), e);
            // In production, you might want to send to a DLQ (Dead Letter Queue)
        }
    }
}


