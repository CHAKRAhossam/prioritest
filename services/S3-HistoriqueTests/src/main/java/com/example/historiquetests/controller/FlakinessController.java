package com.example.historiquetests.controller;

import com.example.historiquetests.model.TestFlakiness;
import com.example.historiquetests.service.FlakinessService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/flakiness")
@RequiredArgsConstructor
@Tag(name = "Flakiness", description = "Test flakiness detection and tracking")
public class FlakinessController {

    private final FlakinessService flakinessService;

    @PostMapping("/calculate")
    @Operation(summary = "Calculate flakiness", 
               description = "Analyze test results in a time window to detect flaky tests")
    public ResponseEntity<?> calculateFlakiness(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime start,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime end) {
        try {
            List<TestFlakiness> flakiness = flakinessService.calculateFlakiness(start, end);
            return ResponseEntity.ok(Map.of(
                "message", "Flakiness calculated successfully",
                "testsAnalyzed", flakiness.size(),
                "windowStart", start,
                "windowEnd", end
            ));
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
        }
    }
    
    @GetMapping("/flaky")
    @Operation(summary = "Get flaky tests", 
               description = "Retrieve tests with flakiness score above threshold")
    public ResponseEntity<?> getFlakyTests(
            @RequestParam(value = "threshold", defaultValue = "0.3") double threshold) {
        try {
            List<TestFlakiness> flakyTests = flakinessService.getFlakyTests(threshold);
            return ResponseEntity.ok(flakyTests);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
        }
    }
    
    @GetMapping("/most-flaky")
    @Operation(summary = "Get most flaky tests", 
               description = "Retrieve tests ordered by flakiness score")
    public ResponseEntity<?> getMostFlakyTests() {
        try {
            List<TestFlakiness> flakyTests = flakinessService.getMostFlakyTests();
            return ResponseEntity.ok(flakyTests);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
        }
    }
    
    @GetMapping("/test/{testClass}/{testName}")
    @Operation(summary = "Get test flakiness", 
               description = "Retrieve flakiness information for a specific test")
    public ResponseEntity<?> getTestFlakiness(
            @PathVariable String testClass,
            @PathVariable String testName) {
        try {
            return flakinessService.getTestFlakiness(testClass, testName)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
        }
    }
}


