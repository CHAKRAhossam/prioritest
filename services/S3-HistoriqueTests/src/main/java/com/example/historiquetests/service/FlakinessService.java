package com.example.historiquetests.service;

import com.example.historiquetests.model.TestFlakiness;
import com.example.historiquetests.model.TestResult;
import com.example.historiquetests.repository.TestFlakinessRepository;
import com.example.historiquetests.repository.TestResultRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
@Slf4j
public class FlakinessService {

    private final TestFlakinessRepository flakinessRepository;
    private final TestResultRepository testResultRepository;
    
    /**
     * Calculate flakiness for all tests in a given time window
     */
    public List<TestFlakiness> calculateFlakiness(LocalDateTime windowStart, LocalDateTime windowEnd) {
        log.info("Calculating test flakiness from {} to {}", windowStart, windowEnd);
        
        List<TestResult> results = testResultRepository.findByTimestampBetween(windowStart, windowEnd);
        
        // Group results by test
        Map<String, List<TestResult>> resultsByTest = new HashMap<>();
        for (TestResult result : results) {
            String key = result.getTestClass() + "#" + result.getTestName();
            resultsByTest.computeIfAbsent(key, k -> new ArrayList<>()).add(result);
        }
        
        List<TestFlakiness> flakinessRecords = new ArrayList<>();
        
        // Calculate flakiness for each test
        for (Map.Entry<String, List<TestResult>> entry : resultsByTest.entrySet()) {
            String[] parts = entry.getKey().split("#");
            String testClass = parts[0];
            String testName = parts[1];
            List<TestResult> testResults = entry.getValue();
            
            TestFlakiness flakiness = calculateTestFlakiness(testClass, testName, testResults, windowStart, windowEnd);
            flakinessRecords.add(flakiness);
        }
        
        // Save or update flakiness records
        for (TestFlakiness flakiness : flakinessRecords) {
            Optional<TestFlakiness> existing = flakinessRepository.findByTestClassAndTestName(
                flakiness.getTestClass(), 
                flakiness.getTestName()
            );
            
            if (existing.isPresent()) {
                TestFlakiness existingFlakiness = existing.get();
                existingFlakiness.setTotalRuns(flakiness.getTotalRuns());
                existingFlakiness.setFailedRuns(flakiness.getFailedRuns());
                existingFlakiness.setPassedRuns(flakiness.getPassedRuns());
                existingFlakiness.setConsecutiveFailures(flakiness.getConsecutiveFailures());
                existingFlakiness.setFlakinessScore(flakiness.getFlakinessScore());
                existingFlakiness.setWindowStart(flakiness.getWindowStart());
                existingFlakiness.setWindowEnd(flakiness.getWindowEnd());
                existingFlakiness.setLastFailure(flakiness.getLastFailure());
                existingFlakiness.setLastSuccess(flakiness.getLastSuccess());
                existingFlakiness.setCalculatedAt(LocalDateTime.now());
                flakinessRepository.save(existingFlakiness);
            } else {
                flakinessRepository.save(flakiness);
            }
        }
        
        log.info("Calculated flakiness for {} tests", flakinessRecords.size());
        return flakinessRecords;
    }
    
    private TestFlakiness calculateTestFlakiness(String testClass, String testName, 
                                                 List<TestResult> results, 
                                                 LocalDateTime windowStart, 
                                                 LocalDateTime windowEnd) {
        TestFlakiness flakiness = new TestFlakiness();
        flakiness.setTestClass(testClass);
        flakiness.setTestName(testName);
        flakiness.setWindowStart(windowStart);
        flakiness.setWindowEnd(windowEnd);
        
        // Sort by timestamp
        results.sort(Comparator.comparing(TestResult::getTimestamp));
        
        int totalRuns = results.size();
        int passed = 0;
        int failed = 0;
        int consecutiveFailures = 0;
        int maxConsecutiveFailures = 0;
        int transitions = 0; // Status changes indicate flakiness
        
        TestResult.TestStatus previousStatus = null;
        LocalDateTime lastFailure = null;
        LocalDateTime lastSuccess = null;
        
        for (TestResult result : results) {
            if (result.getStatus() == TestResult.TestStatus.PASSED) {
                passed++;
                consecutiveFailures = 0;
                lastSuccess = result.getTimestamp();
            } else if (result.getStatus() == TestResult.TestStatus.FAILED || 
                      result.getStatus() == TestResult.TestStatus.ERROR) {
                failed++;
                consecutiveFailures++;
                maxConsecutiveFailures = Math.max(maxConsecutiveFailures, consecutiveFailures);
                lastFailure = result.getTimestamp();
            }
            
            // Count transitions (sign of flakiness)
            if (previousStatus != null && previousStatus != result.getStatus()) {
                transitions++;
            }
            previousStatus = result.getStatus();
        }
        
        flakiness.setTotalRuns(totalRuns);
        flakiness.setPassedRuns(passed);
        flakiness.setFailedRuns(failed);
        flakiness.setConsecutiveFailures(maxConsecutiveFailures);
        flakiness.setLastFailure(lastFailure);
        flakiness.setLastSuccess(lastSuccess);
        
        // Calculate flakiness score (0.0 = stable, 1.0 = very flaky)
        // Score considers: failure rate, transitions, and pattern
        double failureRate = totalRuns > 0 ? (double) failed / totalRuns : 0.0;
        double transitionRate = totalRuns > 1 ? (double) transitions / (totalRuns - 1) : 0.0;
        
        // A test is flaky if it sometimes passes and sometimes fails
        double flakinessScore = 0.0;
        if (passed > 0 && failed > 0) {
            // Has both passes and failures - definitely shows flakiness
            flakinessScore = (transitionRate * 0.7) + (Math.min(failureRate, 1 - failureRate) * 0.3);
        }
        
        flakiness.setFlakinessScore(flakinessScore);
        
        return flakiness;
    }
    
    /**
     * Get all flaky tests above a threshold
     */
    public List<TestFlakiness> getFlakyTests(double threshold) {
        return flakinessRepository.findFlakyTestsAboveThreshold(threshold);
    }
    
    /**
     * Get most flaky tests
     */
    public List<TestFlakiness> getMostFlakyTests() {
        return flakinessRepository.findMostFlakyTests();
    }
    
    /**
     * Check if a specific test is flaky
     */
    public Optional<TestFlakiness> getTestFlakiness(String testClass, String testName) {
        return flakinessRepository.findByTestClassAndTestName(testClass, testName);
    }
}


