package com.testprioritization.service;

import java.time.Instant;
import java.util.Map;
import java.util.UUID;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import com.testprioritization.config.AppProperties;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Scope;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import reactor.core.publisher.Mono;

/**
 * Training Trigger Service - Triggers ML model retraining.
 * 
 * Supports:
 * - Automatic scheduled retraining (configurable cron)
 * - Manual trigger via API
 * - Event-based triggers (e.g., after X commits)
 */
@Service
@Slf4j
@SuppressWarnings({"null", "unchecked"})
public class TrainingTriggerService {

    private final WebClient trainingWebClient;
    private final AppProperties appProperties;
    private final Tracer tracer;
    private final Counter trainingTriggersCounter;
    private final Counter trainingSuccessCounter;
    private final Counter trainingFailureCounter;

    public TrainingTriggerService(WebClient trainingWebClient, AppProperties appProperties,
            Tracer tracer, MeterRegistry meterRegistry) {
        this.trainingWebClient = trainingWebClient;
        this.appProperties = appProperties;
        this.tracer = tracer;
        
        this.trainingTriggersCounter = Counter.builder("training.triggers.total")
                .description("Total training triggers")
                .register(meterRegistry);
        
        this.trainingSuccessCounter = Counter.builder("training.success.total")
                .description("Successful training runs")
                .register(meterRegistry);
        
        this.trainingFailureCounter = Counter.builder("training.failure.total")
                .description("Failed training runs")
                .register(meterRegistry);
    }

    /**
     * Trigger model training manually.
     */
    public Mono<TrainingResponse> triggerTraining(TrainingRequest request) {
        if (!appProperties.getTraining().isEnabled()) {
            log.info("Training trigger is disabled");
            return Mono.just(TrainingResponse.builder()
                    .status("DISABLED")
                    .message("Training triggers are disabled")
                    .build());
        }

        Span span = tracer.spanBuilder("training.trigger")
                .setAttribute("trigger_type", request.getTriggerType())
                .setAttribute("repository", request.getRepository())
                .startSpan();

        trainingTriggersCounter.increment();

        try (Scope scope = span.makeCurrent()) {
            Map<String, Object> body = Map.of(
                    "job_id", UUID.randomUUID().toString(),
                    "repository", request.getRepository() != null ? request.getRepository() : "all",
                    "trigger_type", request.getTriggerType(),
                    "parameters", Map.of(
                            "incremental", request.isIncremental(),
                            "include_recent_commits", true,
                            "min_samples", 100
                    )
            );

            return trainingWebClient.post()
                    .uri("/trigger")
                    .bodyValue(body)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .map(response -> {
                        trainingSuccessCounter.increment();
                        span.setAttribute("job_id", (String) response.get("job_id"));
                        
                        return TrainingResponse.builder()
                                .jobId((String) response.get("job_id"))
                                .status("TRIGGERED")
                                .message("Training job started successfully")
                                .startedAt(Instant.now())
                                .build();
                    })
                    .doOnSuccess(resp -> log.info("Training triggered: {}", resp.getJobId()))
                    .doOnError(error -> {
                        log.error("Failed to trigger training: {}", error.getMessage());
                        trainingFailureCounter.increment();
                        span.recordException(error);
                    })
                    .doFinally(signalType -> span.end())
                    .onErrorReturn(TrainingResponse.builder()
                            .status("FAILED")
                            .message("Failed to trigger training")
                            .build());
        }
    }

    /**
     * Check training job status.
     */
    public Mono<TrainingResponse> getTrainingStatus(String jobId) {
        Span span = tracer.spanBuilder("training.status")
                .setAttribute("job_id", jobId)
                .startSpan();

        try (Scope scope = span.makeCurrent()) {
            return trainingWebClient.get()
                    .uri("/status/{jobId}", jobId)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .map(response -> TrainingResponse.builder()
                            .jobId(jobId)
                            .status((String) response.get("status"))
                            .message((String) response.get("message"))
                            .metrics((Map<String, Object>) response.get("metrics"))
                            .build())
                    .doOnError(error -> {
                        log.error("Failed to get training status: {}", error.getMessage());
                        span.recordException(error);
                    })
                    .doFinally(signalType -> span.end())
                    .onErrorReturn(TrainingResponse.builder()
                            .jobId(jobId)
                            .status("UNKNOWN")
                            .message("Failed to get status")
                            .build());
        }
    }

    /**
     * Scheduled automatic training trigger.
     * Runs based on configured cron expression (default: 2 AM daily).
     */
    @Scheduled(cron = "${app.training.cron:0 0 2 * * ?}")
    public void scheduledTraining() {
        if (!appProperties.getTraining().isEnabled()) {
            return;
        }

        log.info("Starting scheduled training trigger");
        
        TrainingRequest request = TrainingRequest.builder()
                .triggerType("SCHEDULED")
                .incremental(true)
                .build();

        triggerTraining(request)
                .subscribe(
                        response -> log.info("Scheduled training completed: {}", response),
                        error -> log.error("Scheduled training failed: {}", error.getMessage())
                );
    }

    /**
     * Trigger training after threshold commits.
     */
    public Mono<TrainingResponse> triggerOnCommitThreshold(String repository, 
            int commitCount) {
        
        if (commitCount < appProperties.getTraining().getMinCommitsThreshold()) {
            return Mono.just(TrainingResponse.builder()
                    .status("SKIPPED")
                    .message(String.format("Commit count %d below threshold %d",
                            commitCount, appProperties.getTraining().getMinCommitsThreshold()))
                    .build());
        }

        log.info("Triggering training for {} after {} commits", repository, commitCount);

        TrainingRequest request = TrainingRequest.builder()
                .repository(repository)
                .triggerType("COMMIT_THRESHOLD")
                .incremental(true)
                .build();

        return triggerTraining(request);
    }

    /**
     * Training request model.
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TrainingRequest {
        private String repository;
        private String triggerType;
        private boolean incremental;
        private Map<String, Object> parameters;
    }

    /**
     * Training response model.
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TrainingResponse {
        private String jobId;
        private String status;
        private String message;
        private Instant startedAt;
        private Instant completedAt;
        private Map<String, Object> metrics;
    }
}

