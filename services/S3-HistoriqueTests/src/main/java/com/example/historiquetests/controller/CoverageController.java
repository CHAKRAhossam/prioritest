package com.example.historiquetests.controller;

import com.example.historiquetests.model.TestCoverage;
import com.example.historiquetests.service.CoverageService;
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
@RequestMapping("/api/coverage")
@RequiredArgsConstructor
@Tag(name = "Coverage", description = "Test coverage management endpoints")
public class CoverageController {

    private final CoverageService coverageService;

    @PostMapping(value = "/jacoco", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    @Operation(summary = "Upload JaCoCo XML report", description = "Process and store JaCoCo coverage report")
    public ResponseEntity<?> uploadJaCoCoReport(
            @Parameter(description = "JaCoCo XML report file", required = true, 
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
            List<TestCoverage> saved = coverageService.processJaCoCoReport(file, commit, buildId, branch, repositoryId);
            return ResponseEntity.ok(Map.of(
                "message", "JaCoCo report processed successfully",
                "classesProcessed", saved.size(),
                "commit", commit,
                "repository_id", repositoryId
            ));
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
        }
    }
    
    @PostMapping(value = "/pit", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    @Operation(summary = "Upload PIT mutation report", description = "Process and store PIT mutation testing report")
    public ResponseEntity<?> uploadPITReport(
            @Parameter(description = "PIT mutations XML file", required = true,
                       content = @Content(mediaType = MediaType.MULTIPART_FORM_DATA_VALUE))
            @RequestPart("file") MultipartFile file,
            @Parameter(description = "Git commit SHA", required = true)
            @RequestPart("commit") String commit,
            @Parameter(description = "Repository ID", required = true)
            @RequestPart("repository_id") String repositoryId) {
        try {
            coverageService.processPITReport(file, commit, repositoryId);
            return ResponseEntity.ok(Map.of(
                "message", "PIT report processed successfully",
                "commit", commit,
                "repository_id", repositoryId
            ));
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
        }
    }

    @GetMapping("/commit/{commitSha}")
    @Operation(summary = "Get coverage for commit", description = "Retrieve all coverage data for a specific commit")
    public ResponseEntity<?> getCoverageByCommit(@PathVariable String commitSha) {
        try {
            CoverageService.CoverageSummary summary = coverageService.getCoverageSummary(commitSha);
            return ResponseEntity.ok(summary);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
        }
    }
    
    @GetMapping("/class/{className}")
    @Operation(summary = "Get coverage history for class", description = "Retrieve coverage history for a specific class")
    public ResponseEntity<?> getCoverageHistory(@PathVariable String className) {
        try {
            List<TestCoverage> history = coverageService.getCoverageHistory(className);
            return ResponseEntity.ok(history);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
        }
    }
}
