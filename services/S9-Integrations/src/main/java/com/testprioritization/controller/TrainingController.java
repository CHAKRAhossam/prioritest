package com.testprioritization.controller;

import java.util.Map;

import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.testprioritization.service.TrainingTriggerService;
import com.testprioritization.service.TrainingTriggerService.TrainingRequest;
import com.testprioritization.service.TrainingTriggerService.TrainingResponse;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import reactor.core.publisher.Mono;

/**
 * Controller for managing ML model training.
 */
@RestController
@RequestMapping("/v1/training")
@Tag(name = "Training", description = "ML model training management endpoints")
@SecurityRequirement(name = "bearer-jwt")
@RequiredArgsConstructor
@Slf4j
public class TrainingController {

    private final TrainingTriggerService trainingTriggerService;

    /**
     * Trigger model training manually.
     */
    @PostMapping("/trigger")
    @PreAuthorize("hasAnyRole('ADMIN', 'TRAINING_MANAGER')")
    @Operation(summary = "Trigger training",
            description = "Manually trigger ML model training")
    public Mono<ResponseEntity<TrainingResponse>> triggerTraining(
            @RequestBody TrainingRequest request) {
        
        log.info("Manual training trigger requested: {}", request);
        
        if (request.getTriggerType() == null) {
            request.setTriggerType("MANUAL");
        }

        return trainingTriggerService.triggerTraining(request)
                .map(response -> {
                    if ("FAILED".equals(response.getStatus()) || 
                            "DISABLED".equals(response.getStatus())) {
                        return ResponseEntity.badRequest().body(response);
                    }
                    return ResponseEntity.ok(response);
                });
    }

    /**
     * Get training job status.
     */
    @GetMapping("/status/{jobId}")
    @PreAuthorize("hasAnyRole('ADMIN', 'TRAINING_MANAGER', 'USER')")
    @Operation(summary = "Get training status",
            description = "Get the status of a training job")
    public Mono<ResponseEntity<TrainingResponse>> getTrainingStatus(
            @PathVariable String jobId) {
        
        log.debug("Getting training status for job: {}", jobId);

        return trainingTriggerService.getTrainingStatus(jobId)
                .map(ResponseEntity::ok);
    }

    /**
     * Trigger training for a specific repository.
     */
    @PostMapping("/trigger/{repository}")
    @PreAuthorize("hasAnyRole('ADMIN', 'TRAINING_MANAGER')")
    @Operation(summary = "Trigger repository training",
            description = "Trigger ML model training for a specific repository")
    public Mono<ResponseEntity<TrainingResponse>> triggerRepositoryTraining(
            @PathVariable String repository,
            @RequestBody(required = false) Map<String, Object> options) {
        
        log.info("Training trigger for repository: {}", repository);

        TrainingRequest request = TrainingRequest.builder()
                .repository(repository)
                .triggerType("REPOSITORY_SPECIFIC")
                .incremental(options != null && 
                        Boolean.TRUE.equals(options.get("incremental")))
                .build();

        return trainingTriggerService.triggerTraining(request)
                .map(ResponseEntity::ok);
    }

    /**
     * Trigger incremental training.
     */
    @PostMapping("/trigger/incremental")
    @PreAuthorize("hasAnyRole('ADMIN', 'TRAINING_MANAGER')")
    @Operation(summary = "Trigger incremental training",
            description = "Trigger incremental model training with recent data")
    public Mono<ResponseEntity<TrainingResponse>> triggerIncrementalTraining() {
        log.info("Incremental training trigger requested");

        TrainingRequest request = TrainingRequest.builder()
                .triggerType("INCREMENTAL")
                .incremental(true)
                .build();

        return trainingTriggerService.triggerTraining(request)
                .map(ResponseEntity::ok);
    }

    /**
     * Trigger full retraining.
     */
    @PostMapping("/trigger/full")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Trigger full retraining",
            description = "Trigger full model retraining (admin only)")
    public Mono<ResponseEntity<TrainingResponse>> triggerFullRetraining() {
        log.info("Full retraining trigger requested");

        TrainingRequest request = TrainingRequest.builder()
                .triggerType("FULL_RETRAIN")
                .incremental(false)
                .build();

        return trainingTriggerService.triggerTraining(request)
                .map(ResponseEntity::ok);
    }
}

