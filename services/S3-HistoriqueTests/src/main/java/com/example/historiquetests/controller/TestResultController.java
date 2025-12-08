package com.example.historiquetests.controller;

import com.example.historiquetests.model.TestResult;
import com.example.historiquetests.service.TestResultService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/tests")
@RequiredArgsConstructor
@Tag(name = "Test Results", description = "Test execution results management")
public class TestResultController {

    private final TestResultService testResultService;

    @PostMapping(value = "/surefire", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    @Operation(summary = "Upload Surefire report", description = "Process and store Surefire/Failsafe test results")
    public ResponseEntity<?> uploadSurefireReport(
            @Parameter(description = "Surefire TEST-*.xml file", required = true,
                       content = @Content(mediaType = MediaType.MULTIPART_FORM_DATA_VALUE))
            @RequestPart("file") MultipartFile file,
            @Parameter(description = "Git commit SHA", required = true)
            @RequestPart("commit") String commit,
            @Parameter(description = "Repository ID", required = true)
            @RequestPart("repository_id") String repositoryId,
            @Parameter(description = "Build ID (optional)")
            @RequestPart(value = "buildId", required = false) String buildId,
            @Parameter(description = "Git branch name")
            @RequestPart(value = "branch", required = false) String branch) {
        try {
            List<TestResult> saved = testResultService.processSurefireReport(file, commit, buildId, branch, repositoryId);
            return ResponseEntity.ok(Map.of(
                "message", "Surefire report processed successfully",
                "testsProcessed", saved.size(),
                "commit", commit,
                "repository_id", repositoryId
            ));
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
        }
    }
    
    @GetMapping("/commit/{commitSha}")
    @Operation(summary = "Get test summary for commit", description = "Retrieve test execution summary for a specific commit")
    public ResponseEntity<?> getTestSummary(@PathVariable String commitSha) {
        try {
            TestResultService.TestSummary summary = testResultService.getTestSummary(commitSha);
            return ResponseEntity.ok(summary);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
        }
    }
    
    @GetMapping("/history/{testClass}/{testName}")
    @Operation(summary = "Get test history", description = "Retrieve execution history for a specific test")
    public ResponseEntity<?> getTestHistory(
            @PathVariable String testClass,
            @PathVariable String testName) {
        try {
            List<TestResult> history = testResultService.getTestHistory(testClass, testName);
            return ResponseEntity.ok(history);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
        }
    }
    
    @GetMapping("/failed/{commitSha}")
    @Operation(summary = "Get failed tests", description = "Retrieve all failed tests for a specific commit")
    public ResponseEntity<?> getFailedTests(@PathVariable String commitSha) {
        try {
            List<TestResult> failedTests = testResultService.getFailedTests(commitSha);
            return ResponseEntity.ok(failedTests);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
        }
    }
}
