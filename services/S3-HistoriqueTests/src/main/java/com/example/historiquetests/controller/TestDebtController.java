package com.example.historiquetests.controller;

import com.example.historiquetests.model.TestDebt;
import com.example.historiquetests.service.TestDebtService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/debt")
@RequiredArgsConstructor
@Tag(name = "Test Debt", description = "Test debt calculation and tracking")
public class TestDebtController {

    private final TestDebtService testDebtService;

    @PostMapping("/calculate/{commitSha}")
    @Operation(summary = "Calculate test debt", 
               description = "Calculate test debt for all classes in a commit")
    public ResponseEntity<?> calculateTestDebt(@PathVariable String commitSha) {
        try {
            List<TestDebt> debts = testDebtService.calculateTestDebt(commitSha);
            return ResponseEntity.ok(Map.of(
                "message", "Test debt calculated successfully",
                "classesAnalyzed", debts.size(),
                "commit", commitSha
            ));
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
        }
    }
    
    @GetMapping("/commit/{commitSha}")
    @Operation(summary = "Get debt summary", 
               description = "Retrieve test debt summary for a commit")
    public ResponseEntity<?> getDebtSummary(@PathVariable String commitSha) {
        try {
            TestDebtService.DebtSummary summary = testDebtService.getDebtSummary(commitSha);
            return ResponseEntity.ok(summary);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
        }
    }
    
    @GetMapping("/high-debt")
    @Operation(summary = "Get high debt classes", 
               description = "Retrieve classes with debt score above threshold")
    public ResponseEntity<?> getHighDebtClasses(
            @RequestParam(value = "threshold", defaultValue = "50.0") double threshold) {
        try {
            List<TestDebt> highDebt = testDebtService.getHighDebtClasses(threshold);
            return ResponseEntity.ok(highDebt);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
        }
    }
}


