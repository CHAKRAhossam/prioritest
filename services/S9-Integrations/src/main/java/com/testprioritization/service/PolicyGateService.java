package com.testprioritization.service;

import java.util.ArrayList;
import java.util.List;

import org.springframework.stereotype.Service;

import com.testprioritization.config.AppProperties;
import com.testprioritization.model.response.CheckStatus;
import com.testprioritization.model.response.RiskAnalysisResult;
import com.testprioritization.model.response.RiskAnalysisResult.ClassRiskInfo;
import com.testprioritization.model.response.RiskAnalysisResult.PolicyViolation;
import com.testprioritization.model.response.RiskAnalysisResult.RiskLevel;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Scope;
import lombok.extern.slf4j.Slf4j;

/**
 * Policy Gate Service - Enforces test requirements for high-risk modifications.
 * 
 * Provides optional "gate" policy that alerts or blocks when:
 * - High-risk classes are modified without corresponding tests
 * - Test coverage drops below threshold
 * - Critical components are modified
 */
@Service
@Slf4j
public class PolicyGateService {

    private final AppProperties appProperties;
    private final Tracer tracer;
    private final Counter policyViolationsCounter;
    private final Counter policyPassCounter;
    private final Counter policyBlockCounter;

    public PolicyGateService(AppProperties appProperties, Tracer tracer, 
            MeterRegistry meterRegistry) {
        this.appProperties = appProperties;
        this.tracer = tracer;
        
        this.policyViolationsCounter = Counter.builder("policy.violations.total")
                .description("Total number of policy violations detected")
                .register(meterRegistry);
        
        this.policyPassCounter = Counter.builder("policy.pass.total")
                .description("Total number of policy checks passed")
                .register(meterRegistry);
        
        this.policyBlockCounter = Counter.builder("policy.block.total")
                .description("Total number of policy blocks")
                .register(meterRegistry);
    }

    /**
     * Evaluate policy gate for a risk analysis result.
     * 
     * @param riskAnalysis The risk analysis result to evaluate
     * @return PolicyGateResult with pass/fail status and violations
     */
    public PolicyGateResult evaluatePolicy(RiskAnalysisResult riskAnalysis) {
        Span span = tracer.spanBuilder("policyGate.evaluate")
                .setAttribute("analysis.id", riskAnalysis.getAnalysisId())
                .startSpan();

        try (Scope scope = span.makeCurrent()) {
            if (!appProperties.getPolicyGate().isEnabled()) {
                log.debug("Policy gate is disabled, skipping evaluation");
                return PolicyGateResult.builder()
                        .passed(true)
                        .violations(List.of())
                        .checkStatus(buildSuccessStatus())
                        .build();
            }

            List<PolicyViolation> violations = new ArrayList<>();
            
            // Check for high-risk classes without tests
            if (appProperties.getPolicyGate().isRequireTestsForHighRisk()) {
                violations.addAll(checkHighRiskWithoutTests(riskAnalysis));
            }
            
            // Check for critical components
            violations.addAll(checkCriticalComponents(riskAnalysis));
            
            // Check test coverage change
            violations.addAll(checkTestCoverageChange(riskAnalysis));

            boolean passed = violations.isEmpty();
            boolean shouldBlock = !passed && appProperties.getPolicyGate().isBlockOnHighRisk();

            // Update metrics
            if (violations.isEmpty()) {
                policyPassCounter.increment();
            } else {
                policyViolationsCounter.increment(violations.size());
                if (shouldBlock) {
                    policyBlockCounter.increment();
                }
            }

            span.setAttribute("policy.passed", passed);
            span.setAttribute("policy.violations_count", violations.size());
            span.setAttribute("policy.should_block", shouldBlock);

            CheckStatus checkStatus = buildCheckStatus(violations, passed, shouldBlock);

            log.info("Policy gate evaluation: passed={}, violations={}, shouldBlock={}",
                    passed, violations.size(), shouldBlock);

            return PolicyGateResult.builder()
                    .passed(passed)
                    .shouldBlock(shouldBlock)
                    .violations(violations)
                    .checkStatus(checkStatus)
                    .build();
        } finally {
            span.end();
        }
    }

    /**
     * Check for high-risk classes modified without tests.
     */
    private List<PolicyViolation> checkHighRiskWithoutTests(RiskAnalysisResult riskAnalysis) {
        List<PolicyViolation> violations = new ArrayList<>();
        
        if (riskAnalysis.getClassRisks() == null) {
            return violations;
        }

        for (ClassRiskInfo classRisk : riskAnalysis.getClassRisks()) {
            if (classRisk.getRiskLevel() == RiskLevel.HIGH || 
                classRisk.getRiskLevel() == RiskLevel.CRITICAL) {
                
                boolean hasTests = Boolean.TRUE.equals(classRisk.getHasExistingTests()) ||
                                   Boolean.TRUE.equals(classRisk.getTestsAddedInPr());
                
                if (!hasTests) {
                    violations.add(PolicyViolation.builder()
                            .type("HIGH_RISK_NO_TESTS")
                            .severity("HIGH")
                            .className(classRisk.getClassName())
                            .filePath(classRisk.getFilePath())
                            .message(String.format(
                                    "High-risk class '%s' (risk score: %.2f) was modified without tests",
                                    classRisk.getClassName(),
                                    classRisk.getRiskScore()))
                            .recommendation(String.format(
                                    "Add tests for %s before merging. Risk factors: %s",
                                    classRisk.getClassName(),
                                    formatRiskFactors(classRisk)))
                            .autoFixable(false)
                            .build());
                }
            }
        }
        
        return violations;
    }

    /**
     * Check for modifications to critical components.
     */
    private List<PolicyViolation> checkCriticalComponents(RiskAnalysisResult riskAnalysis) {
        List<PolicyViolation> violations = new ArrayList<>();
        
        if (riskAnalysis.getClassRisks() == null) {
            return violations;
        }

        // Define critical path patterns
        List<String> criticalPatterns = List.of(
                "Security", "Auth", "Payment", "Transaction",
                "Encryption", "Token", "Session", "Permission"
        );

        for (ClassRiskInfo classRisk : riskAnalysis.getClassRisks()) {
            String className = classRisk.getClassName();
            if (className == null) continue;

            for (String pattern : criticalPatterns) {
                if (className.contains(pattern)) {
                    boolean hasTests = Boolean.TRUE.equals(classRisk.getHasExistingTests()) ||
                                       Boolean.TRUE.equals(classRisk.getTestsAddedInPr());
                    
                    if (!hasTests) {
                        violations.add(PolicyViolation.builder()
                                .type("CRITICAL_COMPONENT_NO_TESTS")
                                .severity("CRITICAL")
                                .className(classRisk.getClassName())
                                .filePath(classRisk.getFilePath())
                                .message(String.format(
                                        "Critical component '%s' was modified without tests",
                                        classRisk.getClassName()))
                                .recommendation(String.format(
                                        "Security-sensitive class %s requires comprehensive tests",
                                        classRisk.getClassName()))
                                .autoFixable(false)
                                .build());
                        break; // Only one violation per class
                    }
                }
            }
        }
        
        return violations;
    }

    /**
     * Check for test coverage decrease.
     */
    private List<PolicyViolation> checkTestCoverageChange(RiskAnalysisResult riskAnalysis) {
        List<PolicyViolation> violations = new ArrayList<>();
        
        // Calculate average coverage change
        if (riskAnalysis.getClassRisks() == null) {
            return violations;
        }

        double totalCoverageChange = riskAnalysis.getClassRisks().stream()
                .filter(cr -> cr.getTestCoverage() != null)
                .mapToDouble(cr -> cr.getTestCoverage())
                .average()
                .orElse(0.0);

        // If coverage dropped significantly (below 50%), flag it
        if (totalCoverageChange < 0.5 && !riskAnalysis.getClassRisks().isEmpty()) {
            long lowCoverageCount = riskAnalysis.getClassRisks().stream()
                    .filter(cr -> cr.getTestCoverage() != null && cr.getTestCoverage() < 0.5)
                    .count();
            
            if (lowCoverageCount > 0) {
                violations.add(PolicyViolation.builder()
                        .type("LOW_TEST_COVERAGE")
                        .severity("MEDIUM")
                        .message(String.format(
                                "%d modified classes have low test coverage (< 50%%)",
                                lowCoverageCount))
                        .recommendation("Consider adding tests to improve coverage")
                        .autoFixable(false)
                        .build());
            }
        }
        
        return violations;
    }

    /**
     * Build check status from violations.
     */
    private CheckStatus buildCheckStatus(List<PolicyViolation> violations, 
            boolean passed, boolean shouldBlock) {
        
        CheckStatus.State state;
        String description;

        if (passed) {
            state = CheckStatus.State.SUCCESS;
            description = "All policy checks passed";
        } else if (shouldBlock) {
            state = CheckStatus.State.FAILURE;
            description = String.format("Policy gate failed: %d violation(s) found", 
                    violations.size());
        } else {
            state = CheckStatus.State.WARNING;
            description = String.format("Policy warnings: %d issue(s) detected", 
                    violations.size());
        }

        return CheckStatus.builder()
                .state(state)
                .description(description)
                .context("test-prioritization/policy-gate")
                .details(CheckStatus.CheckDetails.builder()
                        .policyViolations(violations.stream()
                                .map(v -> CheckStatus.PolicyViolation.builder()
                                        .type(v.getType())
                                        .severity(v.getSeverity())
                                        .message(v.getMessage())
                                        .className(v.getClassName())
                                        .recommendation(v.getRecommendation())
                                        .build())
                                .toList())
                        .recommendation(passed ? null : 
                                "Add tests for high-risk classes before merging")
                        .build())
                .build();
    }

    /**
     * Build success status.
     */
    private CheckStatus buildSuccessStatus() {
        return CheckStatus.builder()
                .state(CheckStatus.State.SUCCESS)
                .description("Policy gate disabled")
                .context("test-prioritization/policy-gate")
                .build();
    }

    /**
     * Format risk factors for display.
     */
    private String formatRiskFactors(ClassRiskInfo classRisk) {
        if (classRisk.getRiskFactors() == null || classRisk.getRiskFactors().isEmpty()) {
            return "Multiple risk factors detected";
        }

        return classRisk.getRiskFactors().stream()
                .limit(3)
                .map(rf -> rf.getName() + " (" + rf.getSeverity() + ")")
                .reduce((a, b) -> a + ", " + b)
                .orElse("Multiple risk factors");
    }

    /**
     * Policy gate evaluation result.
     */
    @lombok.Data
    @lombok.Builder
    @lombok.NoArgsConstructor
    @lombok.AllArgsConstructor
    public static class PolicyGateResult {
        private boolean passed;
        private boolean shouldBlock;
        private List<PolicyViolation> violations;
        private CheckStatus checkStatus;
    }
}

