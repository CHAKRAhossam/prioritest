package com.example.historiquetests.controller;

import com.example.historiquetests.dto.TestMetricsResponse;
import com.example.historiquetests.service.TestMetricsService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * REST Controller for test metrics API matching the specification:
 * 
 * GET /api/v1/test-metrics?class_name=com.example.UserService&repository_id=repo_12345
 * 
 * Response:
 * {
 *   "class_name": "com.example.UserService",
 *   "repository_id": "repo_12345",
 *   "current_coverage": {
 *     "line_coverage": 0.85,
 *     "branch_coverage": 0.78
 *   },
 *   "test_history": [...],
 *   "test_debt": {...}
 * }
 */
@RestController
@RequestMapping("/api/v1/test-metrics")
@RequiredArgsConstructor
@Tag(name = "Test Metrics API v1", description = "Test metrics API conforming to microservice specification")
public class TestMetricsController {

    private final TestMetricsService testMetricsService;

    @GetMapping
    @Operation(
        summary = "Get test metrics for a class",
        description = "Retrieve comprehensive test metrics including coverage, history, and debt for a specific class in a repository",
        responses = {
            @ApiResponse(
                responseCode = "200",
                description = "Test metrics retrieved successfully",
                content = @Content(schema = @Schema(implementation = TestMetricsResponse.class))
            ),
            @ApiResponse(responseCode = "400", description = "Missing required parameters"),
            @ApiResponse(responseCode = "500", description = "Internal server error")
        }
    )
    public ResponseEntity<?> getTestMetrics(
            @Parameter(description = "Fully qualified class name (e.g., com.example.UserService)", required = true)
            @RequestParam("class_name") String className,
            
            @Parameter(description = "Repository identifier", required = true)
            @RequestParam("repository_id") String repositoryId) {
        
        try {
            if (className == null || className.isEmpty()) {
                return ResponseEntity.badRequest().body(Map.of("error", "class_name is required"));
            }
            if (repositoryId == null || repositoryId.isEmpty()) {
                return ResponseEntity.badRequest().body(Map.of("error", "repository_id is required"));
            }
            
            TestMetricsResponse response = testMetricsService.getTestMetrics(className, repositoryId);
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
        }
    }
    
    @GetMapping("/repository/{repositoryId}")
    @Operation(
        summary = "Get all test metrics for a repository",
        description = "Retrieve test metrics for all classes in a repository"
    )
    public ResponseEntity<?> getAllTestMetrics(
            @Parameter(description = "Repository identifier", required = true)
            @PathVariable String repositoryId) {
        
        try {
            List<TestMetricsResponse> responses = testMetricsService.getAllTestMetrics(repositoryId);
            return ResponseEntity.ok(responses);
            
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
        }
    }
    
    @GetMapping("/class/{className}")
    @Operation(
        summary = "Get test metrics by class name across all repositories",
        description = "Retrieve test metrics for a specific class name (may return multiple if class exists in multiple repositories)"
    )
    public ResponseEntity<?> getTestMetricsByClass(
            @Parameter(description = "Fully qualified class name", required = true)
            @PathVariable String className,
            
            @Parameter(description = "Optional repository filter")
            @RequestParam(value = "repository_id", required = false) String repositoryId) {
        
        try {
            if (repositoryId != null && !repositoryId.isEmpty()) {
                TestMetricsResponse response = testMetricsService.getTestMetrics(className, repositoryId);
                return ResponseEntity.ok(response);
            } else {
                // Return 400 if no repository_id provided
                return ResponseEntity.badRequest().body(Map.of(
                    "error", "repository_id is required",
                    "hint", "Use /api/v1/test-metrics?class_name=...&repository_id=..."
                ));
            }
            
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
        }
    }
}


