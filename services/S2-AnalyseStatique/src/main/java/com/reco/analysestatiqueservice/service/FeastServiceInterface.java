package com.reco.analysestatiqueservice.service;

import com.reco.analysestatiqueservice.dto.CodeMetricsEvent;

/**
 * Interface for Feast service to allow multiple implementations.
 */
public interface FeastServiceInterface {
    void publishToFeast(CodeMetricsEvent event);
}

