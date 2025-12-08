package com.example.historiquetests.controller;

import com.example.historiquetests.service.MetricsAggregationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/metrics")
@RequiredArgsConstructor
@Tag(name = "Metrics", description = "Aggregated metrics and reports")
public class MetricsController {

    private final MetricsAggregationService metricsService;

    @GetMapping("/commit/{commitSha}")
    @Operation(summary = "Get complete metrics for commit", 
               description = "Retrieve comprehensive metrics including coverage, tests, and debt for a commit")
    public ResponseEntity<?> getCommitMetrics(@PathVariable String commitSha) {
        try {
            MetricsAggregationService.CommitMetrics metrics = metricsService.generateCommitMetrics(commitSha);
            return ResponseEntity.ok(metrics);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
        }
    }
}


