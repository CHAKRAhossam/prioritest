package com.reco.analysestatiqueservice.service;

import com.reco.analysestatiqueservice.dto.CodeMetricsEvent;

/**
 * Interface for Kafka service to allow multiple implementations.
 */
public interface KafkaServiceInterface {
    void publishCodeMetrics(CodeMetricsEvent event);
}

