package com.example.historiquetests.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

/**
 * Aggregates all metrics for a commit into a comprehensive report
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class MetricsAggregationService {

    private final CoverageService coverageService;
    private final TestResultService testResultService;
    private final TestDebtService testDebtService;
    private final FlakinessService flakinessService;
    
    /**
     * Generate complete metrics report for a commit
     */
    public CommitMetrics generateCommitMetrics(String commitSha) {
        log.info("Generating complete metrics for commit: {}", commitSha);
        
        CommitMetrics metrics = new CommitMetrics();
        metrics.commitSha = commitSha;
        metrics.generatedAt = LocalDateTime.now();
        
        // Coverage metrics
        try {
            CoverageService.CoverageSummary coverage = coverageService.getCoverageSummary(commitSha);
            metrics.coverage = Map.of(
                "totalClasses", coverage.totalClasses,
                "averageLineCoverage", String.format("%.2f%%", coverage.averageLineCoverage),
                "averageBranchCoverage", String.format("%.2f%%", coverage.averageBranchCoverage),
                "averageMutationScore", String.format("%.2f%%", coverage.averageMutationScore),
                "coveredLines", coverage.coveredLines,
                "totalLines", coverage.totalLines
            );
        } catch (Exception e) {
            log.error("Error getting coverage summary", e);
            metrics.coverage = Map.of("error", "Coverage data not available");
        }
        
        // Test results metrics
        try {
            TestResultService.TestSummary testSummary = testResultService.getTestSummary(commitSha);
            metrics.tests = Map.of(
                "total", testSummary.total,
                "passed", testSummary.passed,
                "failed", testSummary.failed,
                "skipped", testSummary.skipped,
                "passRate", String.format("%.2f%%", testSummary.passRate),
                "executionTime", testSummary.totalExecutionTime != null ? 
                    String.format("%.2fs", testSummary.totalExecutionTime) : "N/A"
            );
        } catch (Exception e) {
            log.error("Error getting test summary", e);
            metrics.tests = Map.of("error", "Test data not available");
        }
        
        // Test debt metrics
        try {
            TestDebtService.DebtSummary debtSummary = testDebtService.getDebtSummary(commitSha);
            metrics.debt = Map.of(
                "averageDebtScore", String.format("%.2f", debtSummary.averageDebtScore),
                "highDebtClasses", debtSummary.highDebtClasses,
                "totalUncoveredLines", debtSummary.totalUncoveredLines,
                "totalSurvivedMutants", debtSummary.totalSurvivedMutants
            );
        } catch (Exception e) {
            log.error("Error getting debt summary", e);
            metrics.debt = Map.of("error", "Debt data not available");
        }
        
        // Flakiness metrics
        try {
            var flakyTests = flakinessService.getFlakyTests(0.3);
            metrics.flakiness = Map.of(
                "flakyTestsCount", flakyTests.size(),
                "mostFlakyTests", flakinessService.getMostFlakyTests().stream()
                    .limit(5)
                    .map(f -> f.getTestClass() + "#" + f.getTestName())
                    .toList()
            );
        } catch (Exception e) {
            log.error("Error getting flakiness summary", e);
            metrics.flakiness = Map.of("error", "Flakiness data not available");
        }
        
        // Quality score (0-100)
        metrics.qualityScore = calculateQualityScore(metrics);
        
        return metrics;
    }
    
    /**
     * Calculate overall quality score based on all metrics
     */
    private double calculateQualityScore(CommitMetrics metrics) {
        double score = 100.0;
        
        try {
            // Coverage contribution (40 points)
            if (metrics.coverage.containsKey("averageLineCoverage")) {
                String coverageStr = metrics.coverage.get("averageLineCoverage").toString().replace("%", "");
                double coverage = Double.parseDouble(coverageStr);
                score = Math.min(40, coverage / 2); // Max 40 points for 80%+ coverage
            }
            
            // Test pass rate contribution (30 points)
            if (metrics.tests.containsKey("passRate")) {
                String passRateStr = metrics.tests.get("passRate").toString().replace("%", "");
                double passRate = Double.parseDouble(passRateStr);
                score += Math.min(30, passRate * 0.3); // Max 30 points for 100% pass rate
            }
            
            // Debt penalty (up to -30 points)
            if (metrics.debt.containsKey("averageDebtScore")) {
                String debtStr = metrics.debt.get("averageDebtScore").toString();
                double debtScore = Double.parseDouble(debtStr);
                score -= (debtScore * 0.3); // Subtract debt score (max 30 points penalty)
            }
            
        } catch (Exception e) {
            log.error("Error calculating quality score", e);
        }
        
        return Math.max(0, Math.min(100, score));
    }
    
    public static class CommitMetrics {
        public String commitSha;
        public LocalDateTime generatedAt;
        public Map<String, Object> coverage = new HashMap<>();
        public Map<String, Object> tests = new HashMap<>();
        public Map<String, Object> debt = new HashMap<>();
        public Map<String, Object> flakiness = new HashMap<>();
        public double qualityScore;
    }
}


