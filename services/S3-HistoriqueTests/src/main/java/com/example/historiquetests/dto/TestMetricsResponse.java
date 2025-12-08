package com.example.historiquetests.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder;

import java.time.LocalDateTime;
import java.util.List;

/**
 * DTO for REST API response matching the specification:
 * 
 * GET /api/v1/test-metrics?class_name=com.example.UserService&repository_id=repo_12345
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
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class TestMetricsResponse {
    
    @JsonProperty("class_name")
    private String className;
    
    @JsonProperty("repository_id")
    private String repositoryId;
    
    @JsonProperty("current_coverage")
    private CoverageMetrics currentCoverage;
    
    @JsonProperty("test_history")
    private List<TestHistoryEntry> testHistory;
    
    @JsonProperty("test_debt")
    private TestDebtInfo testDebt;
    
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class CoverageMetrics {
        @JsonProperty("line_coverage")
        private Double lineCoverage;
        
        @JsonProperty("branch_coverage")
        private Double branchCoverage;
        
        @JsonProperty("instruction_coverage")
        private Double instructionCoverage;
        
        @JsonProperty("method_coverage")
        private Double methodCoverage;
        
        @JsonProperty("mutation_score")
        private Double mutationScore;
    }
    
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class TestHistoryEntry {
        @JsonProperty("commit_sha")
        private String commitSha;
        
        @JsonProperty("timestamp")
        private LocalDateTime timestamp;
        
        @JsonProperty("line_coverage")
        private Double lineCoverage;
        
        @JsonProperty("branch_coverage")
        private Double branchCoverage;
        
        @JsonProperty("tests_passed")
        private Integer testsPassed;
        
        @JsonProperty("tests_failed")
        private Integer testsFailed;
        
        @JsonProperty("tests_total")
        private Integer testsTotal;
        
        @JsonProperty("mutation_score")
        private Double mutationScore;
    }
    
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class TestDebtInfo {
        @JsonProperty("has_tests")
        private Boolean hasTests;
        
        @JsonProperty("coverage_below_threshold")
        private Boolean coverageBelowThreshold;
        
        @JsonProperty("threshold")
        private Double threshold;
        
        @JsonProperty("debt_score")
        private Double debtScore;
        
        @JsonProperty("recommendations")
        private String recommendations;
        
        @JsonProperty("flakiness_score")
        private Double flakinessScore;
    }
}


