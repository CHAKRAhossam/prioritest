package com.example.historiquetests.service;

import com.example.historiquetests.model.TestResult;
import com.example.historiquetests.parser.SurefireParser;
import com.example.historiquetests.repository.TestResultRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class TestResultService {

    private final TestResultRepository testResultRepository;
    private final MinioService minioService;
    private final SurefireParser surefireParser;

    /**
     * Process Surefire XML test report
     */
    public List<TestResult> processSurefireReport(MultipartFile xmlFile, String commitSha, String buildId, String branch) throws Exception {
        return processSurefireReport(xmlFile, commitSha, buildId, branch, "default");
    }
    
    /**
     * Process Surefire XML test report with repositoryId
     */
    public List<TestResult> processSurefireReport(MultipartFile xmlFile, String commitSha, String buildId, String branch, String repositoryId) throws Exception {
        log.info("Processing Surefire report for commit: {}, repository: {}", commitSha, repositoryId);
        
        // Upload raw file
        minioService.upload(repositoryId + "/" + commitSha + "/surefire-" + xmlFile.getOriginalFilename(), xmlFile);
        
        // Parse the report
        List<TestResult> results = surefireParser.parseSurefireReport(
            xmlFile.getInputStream(), 
            commitSha, 
            buildId, 
            branch,
            repositoryId
        );
        
        // Save all results
        List<TestResult> saved = testResultRepository.saveAll(results);
        
        log.info("Saved {} test results for commit {} in repository {}", saved.size(), commitSha, repositoryId);
        return saved;
    }
    
    /**
     * Get test results summary for a commit
     */
    public TestSummary getTestSummary(String commitSha) {
        TestSummary summary = new TestSummary();
        summary.commitSha = commitSha;
        summary.passed = testResultRepository.countPassedTests(commitSha);
        summary.failed = testResultRepository.countFailedTests(commitSha);
        summary.skipped = testResultRepository.countSkippedTests(commitSha);
        summary.total = summary.passed + summary.failed + summary.skipped;
        summary.totalExecutionTime = testResultRepository.sumExecutionTimeForCommit(commitSha);
        
        if (summary.total > 0) {
            summary.passRate = (double) summary.passed / summary.total * 100.0;
        }
        
        return summary;
    }
    
    /**
     * Get test execution history
     */
    public List<TestResult> getTestHistory(String testClass, String testName) {
        return testResultRepository.findTestHistory(testClass, testName);
    }
    
    /**
     * Get all failed tests for a commit
     */
    public List<TestResult> getFailedTests(String commitSha) {
        return testResultRepository.findByCommitSha(commitSha).stream()
            .filter(tr -> tr.getStatus() == TestResult.TestStatus.FAILED || 
                         tr.getStatus() == TestResult.TestStatus.ERROR)
            .toList();
    }
    
    public static class TestSummary {
        public String commitSha;
        public long total;
        public long passed;
        public long failed;
        public long skipped;
        public double passRate;
        public Double totalExecutionTime;
    }
}
