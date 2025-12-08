package com.example.historiquetests.service;

import com.example.historiquetests.dto.TestMetricsResponse;
import com.example.historiquetests.dto.TestMetricsResponse.*;
import com.example.historiquetests.model.TestCoverage;
import com.example.historiquetests.model.TestDebt;
import com.example.historiquetests.repository.TestCoverageRepository;
import com.example.historiquetests.repository.TestDebtRepository;
import com.example.historiquetests.repository.TestResultRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * Service to generate test metrics response matching the specification format.
 * 
 * Output format:
 * {
 *   "class_name": "com.example.UserService",
 *   "repository_id": "repo_12345",
 *   "current_coverage": {...},
 *   "test_history": [...],
 *   "test_debt": {...}
 * }
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class TestMetricsService {

    private final TestCoverageRepository coverageRepository;
    private final TestDebtRepository debtRepository;
    private final TestResultRepository testResultRepository;
    
    private static final double COVERAGE_THRESHOLD = 0.80;

    /**
     * Get test metrics for a specific class in a repository
     */
    public TestMetricsResponse getTestMetrics(String className, String repositoryId) {
        log.info("Getting test metrics for class: {}, repository: {}", className, repositoryId);
        
        // Get coverage history
        List<TestCoverage> coverageHistory = coverageRepository
            .findCoverageHistoryByClassAndRepository(className, repositoryId);
        
        if (coverageHistory.isEmpty()) {
            log.warn("No coverage data found for class: {} in repository: {}", className, repositoryId);
            return buildEmptyResponse(className, repositoryId);
        }
        
        // Current coverage (most recent)
        TestCoverage current = coverageHistory.get(0);
        
        // Build response
        return TestMetricsResponse.builder()
            .className(className)
            .repositoryId(repositoryId)
            .currentCoverage(buildCurrentCoverage(current))
            .testHistory(buildTestHistory(coverageHistory, repositoryId))
            .testDebt(buildTestDebt(className, repositoryId, current))
            .build();
    }
    
    /**
     * Get test metrics for all classes in a repository
     */
    public List<TestMetricsResponse> getAllTestMetrics(String repositoryId) {
        log.info("Getting all test metrics for repository: {}", repositoryId);
        
        List<TestCoverage> allCoverages = coverageRepository.findByRepositoryId(repositoryId);
        
        // Group by class name and get the latest for each
        Map<String, TestCoverage> latestByClass = allCoverages.stream()
            .collect(Collectors.toMap(
                TestCoverage::getClassName,
                c -> c,
                (c1, c2) -> c1.getTimestamp().isAfter(c2.getTimestamp()) ? c1 : c2
            ));
        
        List<TestMetricsResponse> responses = new ArrayList<>();
        for (TestCoverage coverage : latestByClass.values()) {
            responses.add(getTestMetrics(coverage.getClassName(), repositoryId));
        }
        
        return responses;
    }
    
    private CoverageMetrics buildCurrentCoverage(TestCoverage coverage) {
        return CoverageMetrics.builder()
            .lineCoverage(coverage.getLineCoverage() / 100.0) // Convert to 0-1 range
            .branchCoverage(coverage.getBranchCoverage() / 100.0)
            .instructionCoverage(coverage.getInstructionCoverage() / 100.0)
            .methodCoverage(coverage.getMethodCoverage() / 100.0)
            .mutationScore(coverage.getMutationScore() != null ? coverage.getMutationScore() / 100.0 : null)
            .build();
    }
    
    private List<TestHistoryEntry> buildTestHistory(List<TestCoverage> coverageHistory, String repositoryId) {
        List<TestHistoryEntry> history = new ArrayList<>();
        
        for (TestCoverage coverage : coverageHistory) {
            // Get test results for this commit
            long passed = testResultRepository.countPassedTestsByRepository(
                coverage.getCommitSha(), repositoryId);
            long failed = testResultRepository.countFailedTestsByRepository(
                coverage.getCommitSha(), repositoryId);
            
            TestHistoryEntry entry = TestHistoryEntry.builder()
                .commitSha(coverage.getCommitSha())
                .timestamp(coverage.getTimestamp())
                .lineCoverage(coverage.getLineCoverage() / 100.0)
                .branchCoverage(coverage.getBranchCoverage() / 100.0)
                .testsPassed((int) passed)
                .testsFailed((int) failed)
                .testsTotal((int) (passed + failed))
                .mutationScore(coverage.getMutationScore() != null ? coverage.getMutationScore() / 100.0 : null)
                .build();
            
            history.add(entry);
        }
        
        return history;
    }
    
    private TestDebtInfo buildTestDebt(String className, String repositoryId, TestCoverage coverage) {
        // Get latest debt info
        Optional<TestDebt> debtOpt = debtRepository.findLatestByClassNameAndRepositoryId(className, repositoryId);
        
        boolean hasTests = coverage.getLinesCovered() > 0;
        boolean belowThreshold = (coverage.getLineCoverage() / 100.0) < COVERAGE_THRESHOLD;
        
        TestDebtInfo.TestDebtInfoBuilder builder = TestDebtInfo.builder()
            .hasTests(hasTests)
            .coverageBelowThreshold(belowThreshold)
            .threshold(COVERAGE_THRESHOLD);
        
        if (debtOpt.isPresent()) {
            TestDebt debt = debtOpt.get();
            builder.debtScore(debt.getDebtScore())
                   .recommendations(debt.getRecommendations());
        }
        
        return builder.build();
    }
    
    private TestMetricsResponse buildEmptyResponse(String className, String repositoryId) {
        return TestMetricsResponse.builder()
            .className(className)
            .repositoryId(repositoryId)
            .currentCoverage(CoverageMetrics.builder().build())
            .testHistory(List.of())
            .testDebt(TestDebtInfo.builder()
                .hasTests(false)
                .coverageBelowThreshold(true)
                .threshold(COVERAGE_THRESHOLD)
                .build())
            .build();
    }
}

