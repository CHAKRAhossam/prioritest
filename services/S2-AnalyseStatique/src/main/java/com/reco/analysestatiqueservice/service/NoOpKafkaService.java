package com.reco.analysestatiqueservice.service;

import com.reco.analysestatiqueservice.dto.CodeMetricsEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

/**
 * No-op implementation of KafkaService when Kafka is disabled.
 */
@Service
@ConditionalOnProperty(name = "kafka.enabled", havingValue = "false", matchIfMissing = true)
public class NoOpKafkaService implements KafkaServiceInterface {
    
    private static final Logger logger = LoggerFactory.getLogger(NoOpKafkaService.class);
    
    @Override
    public void publishCodeMetrics(CodeMetricsEvent event) {
        logger.debug("Kafka is disabled, skipping publication of metrics for: {}", event.getClassName());
    }
}

