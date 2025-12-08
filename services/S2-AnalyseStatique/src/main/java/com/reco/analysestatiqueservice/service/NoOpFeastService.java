package com.reco.analysestatiqueservice.service;

import com.reco.analysestatiqueservice.dto.CodeMetricsEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

/**
 * No-op implementation of FeastService when Feast is disabled.
 */
@Service
@ConditionalOnProperty(name = "feast.enabled", havingValue = "false", matchIfMissing = true)
public class NoOpFeastService implements FeastServiceInterface {
    
    private static final Logger logger = LoggerFactory.getLogger(NoOpFeastService.class);
    
    @Override
    public void publishToFeast(CodeMetricsEvent event) {
        logger.debug("Feast is disabled, skipping publication of metrics for: {}", event.getClassName());
    }
}

