package com.example.historiquetests.controller;

import com.example.historiquetests.model.TestCoverage;
import com.example.historiquetests.model.MutationResult;
import com.example.historiquetests.service.CoverageService;
import com.example.historiquetests.repository.MutationResultRepository;
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
    private final MutationResultRepository mutationResultRepository;

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
    
    @GetMapping("/history/{repositoryId}/{branch}")
    @Operation(summary = "Get coverage history by repository and branch", description = "Retrieve coverage history for a repository and branch")
    public ResponseEntity<?> getCoverageHistoryByRepositoryAndBranch(
            @PathVariable String repositoryId,
            @PathVariable String branch) {
        try {
            List<TestCoverage> history = coverageService.getCoverageHistoryByRepositoryAndBranch(repositoryId, branch);
            // Transform to frontend format
            List<Map<String, Object>> result = history.stream().map(tc -> {
                Map<String, Object> map = new java.util.HashMap<>();
                map.put("commitSha", tc.getCommitSha());
                map.put("timestamp", tc.getTimestamp() != null ? tc.getTimestamp().toString() : "");
                map.put("lineCoverage", tc.getLineCoverage());
                map.put("branchCoverage", tc.getBranchCoverage());
                map.put("mutationCoverage", tc.getMutationScore() != null ? tc.getMutationScore() : 0.0);
                map.put("className", tc.getClassName() != null ? tc.getClassName() : "");
                map.put("repositoryId", tc.getRepositoryId());
                map.put("branch", tc.getBranch() != null ? tc.getBranch() : branch);
                return map;
            }).collect(java.util.stream.Collectors.toList());
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
        }
    }
    
    @GetMapping("/mutations/{repositoryId}/{className}")
    @Operation(summary = "Get mutations for a class", description = "Retrieve mutation testing results for a specific class")
    public ResponseEntity<?> getMutationsByClass(
            @PathVariable String repositoryId,
            @PathVariable String className,
            @Parameter(description = "Commit SHA (optional, uses latest if not provided)")
            @RequestParam(required = false) String commitSha) {
        try {
            List<MutationResult> mutations;
            if (commitSha != null && !commitSha.isEmpty()) {
                mutations = mutationResultRepository.findByCommitShaAndClassName(commitSha, className);
            } else {
                // Get latest mutations for this class in the repository
                if (repositoryId != null && !repositoryId.isEmpty()) {
                    mutations = mutationResultRepository.findByClassNameAndRepositoryId(className, repositoryId);
                } else {
                    mutations = mutationResultRepository.findByClassName(className);
                }
            }
            
            // Group mutations by mutator type and calculate coverage
            Map<String, Object> result = new java.util.HashMap<>();
            result.put("className", className);
            result.put("repositoryId", repositoryId);
            result.put("totalMutations", mutations.size());
            result.put("killedMutations", mutations.stream().filter(m -> m.getStatus() == MutationResult.MutationStatus.KILLED).count());
            result.put("survivedMutations", mutations.stream().filter(m -> m.getStatus() == MutationResult.MutationStatus.SURVIVED).count());
            
            // Group by mutator type
            Map<String, Map<String, Object>> mutatorGroups = new java.util.HashMap<>();
            for (MutationResult mutation : mutations) {
                String mutator = mutation.getMutator();
                if (mutator == null || mutator.isEmpty()) {
                    mutator = "Unknown";
                }
                
                mutatorGroups.putIfAbsent(mutator, new java.util.HashMap<>());
                Map<String, Object> group = mutatorGroups.get(mutator);
                group.put("mutator", mutator);
                group.putIfAbsent("total", 0);
                group.putIfAbsent("killed", 0);
                group.putIfAbsent("survived", 0);
                
                group.put("total", ((Integer) group.get("total")) + 1);
                if (mutation.getStatus() == MutationResult.MutationStatus.KILLED) {
                    group.put("killed", ((Integer) group.get("killed")) + 1);
                } else if (mutation.getStatus() == MutationResult.MutationStatus.SURVIVED) {
                    group.put("survived", ((Integer) group.get("survived")) + 1);
                }
            }
            
            result.put("mutatorGroups", mutatorGroups.values());
            result.put("mutations", mutations.stream().map(m -> {
                Map<String, Object> mMap = new java.util.HashMap<>();
                mMap.put("id", m.getId());
                mMap.put("mutator", m.getMutator());
                mMap.put("status", m.getStatus().toString());
                mMap.put("methodName", m.getMethodName());
                mMap.put("lineNumber", m.getLineNumber());
                mMap.put("description", m.getMutationDescription());
                mMap.put("killingTest", m.getKillingTest());
                return mMap;
            }).collect(java.util.stream.Collectors.toList()));
            
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
        }
    }
}
