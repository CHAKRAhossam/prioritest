package com.testprioritization.service;

import java.util.ArrayList;
import java.util.List;

import org.springframework.stereotype.Service;

import com.testprioritization.model.response.PRComment;
import com.testprioritization.model.response.PRComment.Recommendation;
import com.testprioritization.model.response.PRComment.RiskSummary;
import com.testprioritization.model.response.RiskAnalysisResult;
import com.testprioritization.model.response.RiskAnalysisResult.ClassRiskInfo;
import com.testprioritization.model.response.RiskAnalysisResult.RiskLevel;
import com.testprioritization.service.PolicyGateService.PolicyGateResult;

import lombok.extern.slf4j.Slf4j;

/**
 * Service for generating PR/MR comments based on risk analysis results.
 */
@Service
@Slf4j
public class CommentGeneratorService {

    private static final String TEST_SCAFFOLDER_BASE_URL = "https://test-scaffolder.example.com";

    /**
     * Generate a PR comment from risk analysis and policy gate results.
     */
    public PRComment generateComment(RiskAnalysisResult riskAnalysis, 
            PolicyGateResult policyResult) {
        
        log.debug("Generating comment for analysis {}", riskAnalysis.getAnalysisId());

        RiskSummary summary = buildRiskSummary(riskAnalysis);
        List<Recommendation> recommendations = buildRecommendations(riskAnalysis, policyResult);
        String testScaffolderLink = buildTestScaffolderLink(riskAnalysis);

        PRComment comment = PRComment.builder()
                .riskSummary(summary)
                .recommendations(recommendations)
                .testScaffolderLink(testScaffolderLink)
                .build();

        // Set the formatted markdown body
        comment.setMarkdownBody(comment.toMarkdown());
        comment.setComment(comment.toMarkdown());

        return comment;
    }

    /**
     * Generate a simple warning comment for high-risk classes.
     */
    public PRComment generateWarningComment(ClassRiskInfo classRisk) {
        String warningMessage = String.format(
                "⚠️ **Warning**: Modified class '%s' has high risk score (%.2f) but no tests added.\n\n" +
                "**Recommendation**: Add tests before merging.\n\n" +
                "**Risk factors**:\n%s\n\n" +
                "**Suggested test cases**: [View in TestScaffolder](%s)",
                classRisk.getClassName(),
                classRisk.getRiskScore(),
                formatRiskFactors(classRisk),
                buildTestScaffolderLinkForClass(classRisk)
        );

        return PRComment.builder()
                .comment(warningMessage)
                .markdownBody(warningMessage)
                .recommendations(List.of(
                        Recommendation.builder()
                                .type("ADD_TESTS")
                                .priority("HIGH")
                                .targetClass(classRisk.getClassName())
                                .message("Add tests for high-risk class")
                                .suggestedAction("Create unit tests")
                                .build()
                ))
                .build();
    }

    /**
     * Build risk summary from analysis result.
     */
    private RiskSummary buildRiskSummary(RiskAnalysisResult riskAnalysis) {
        if (riskAnalysis.getClassRisks() == null) {
            return RiskSummary.builder()
                    .totalFilesModified(0)
                    .highRiskCount(0)
                    .mediumRiskCount(0)
                    .lowRiskCount(0)
                    .overallRiskLevel("LOW")
                    .testsCoverageStatus("Unknown")
                    .build();
        }

        int highRisk = (int) riskAnalysis.getClassRisks().stream()
                .filter(cr -> cr.getRiskLevel() == RiskLevel.HIGH || 
                              cr.getRiskLevel() == RiskLevel.CRITICAL)
                .count();
        
        int mediumRisk = (int) riskAnalysis.getClassRisks().stream()
                .filter(cr -> cr.getRiskLevel() == RiskLevel.MEDIUM)
                .count();
        
        int lowRisk = (int) riskAnalysis.getClassRisks().stream()
                .filter(cr -> cr.getRiskLevel() == RiskLevel.LOW)
                .count();

        // Determine test coverage status
        long withTests = riskAnalysis.getClassRisks().stream()
                .filter(cr -> Boolean.TRUE.equals(cr.getHasExistingTests()) || 
                              Boolean.TRUE.equals(cr.getTestsAddedInPr()))
                .count();
        
        int total = riskAnalysis.getClassRisks().size();
        String coverageStatus;
        if (total == 0) {
            coverageStatus = "No classes modified";
        } else if (withTests == total) {
            coverageStatus = "✅ All modified classes have tests";
        } else if (withTests == 0) {
            coverageStatus = "❌ No tests for modified classes";
        } else {
            coverageStatus = String.format("⚠️ %d/%d classes have tests", withTests, total);
        }

        return RiskSummary.builder()
                .totalFilesModified(total)
                .highRiskCount(highRisk)
                .mediumRiskCount(mediumRisk)
                .lowRiskCount(lowRisk)
                .overallRiskLevel(riskAnalysis.getOverallRiskLevel() != null ? 
                        riskAnalysis.getOverallRiskLevel().name() : "LOW")
                .testsCoverageStatus(coverageStatus)
                .build();
    }

    /**
     * Build recommendations from analysis and policy results.
     */
    private List<Recommendation> buildRecommendations(RiskAnalysisResult riskAnalysis,
            PolicyGateResult policyResult) {
        
        List<Recommendation> recommendations = new ArrayList<>();

        // Add recommendations for high-risk classes without tests
        if (riskAnalysis.getClassRisks() != null) {
            for (ClassRiskInfo classRisk : riskAnalysis.getClassRisks()) {
                if ((classRisk.getRiskLevel() == RiskLevel.HIGH || 
                     classRisk.getRiskLevel() == RiskLevel.CRITICAL) &&
                    Boolean.FALSE.equals(classRisk.getHasExistingTests()) &&
                    Boolean.FALSE.equals(classRisk.getTestsAddedInPr())) {
                    
                    recommendations.add(Recommendation.builder()
                            .type("ADD_TESTS")
                            .priority("HIGH")
                            .targetClass(classRisk.getClassName())
                            .message(String.format("High-risk class '%s' needs tests (risk: %.2f)",
                                    classRisk.getClassName(), classRisk.getRiskScore()))
                            .suggestedAction("Add unit tests covering main functionality")
                            .actionUrl(buildTestScaffolderLinkForClass(classRisk))
                            .build());
                }
            }
        }

        // Add recommendations from policy violations
        if (policyResult != null && policyResult.getViolations() != null) {
            for (var violation : policyResult.getViolations()) {
                recommendations.add(Recommendation.builder()
                        .type("POLICY_VIOLATION")
                        .priority(violation.getSeverity())
                        .targetClass(violation.getClassName())
                        .message(violation.getMessage())
                        .suggestedAction(violation.getRecommendation())
                        .build());
            }
        }

        // Add general recommendations
        if (riskAnalysis.getOverallRiskLevel() == RiskLevel.HIGH ||
            riskAnalysis.getOverallRiskLevel() == RiskLevel.CRITICAL) {
            
            recommendations.add(Recommendation.builder()
                    .type("REVIEW_RECOMMENDED")
                    .priority("MEDIUM")
                    .message("Consider requesting additional review due to high-risk changes")
                    .suggestedAction("Request review from senior developer or domain expert")
                    .build());
        }

        return recommendations;
    }

    /**
     * Build test scaffolder link for all high-risk classes.
     */
    private String buildTestScaffolderLink(RiskAnalysisResult riskAnalysis) {
        if (riskAnalysis.getClassRisks() == null || riskAnalysis.getClassRisks().isEmpty()) {
            return null;
        }

        List<String> classNames = riskAnalysis.getClassRisks().stream()
                .filter(cr -> cr.getRiskLevel() == RiskLevel.HIGH || 
                              cr.getRiskLevel() == RiskLevel.CRITICAL)
                .filter(cr -> Boolean.FALSE.equals(cr.getHasExistingTests()))
                .map(ClassRiskInfo::getClassName)
                .toList();

        if (classNames.isEmpty()) {
            return null;
        }

        return String.format("%s/generate?classes=%s&repo=%s&commit=%s",
                TEST_SCAFFOLDER_BASE_URL,
                String.join(",", classNames),
                riskAnalysis.getRepository(),
                riskAnalysis.getCommitSha());
    }

    /**
     * Build test scaffolder link for a specific class.
     */
    private String buildTestScaffolderLinkForClass(ClassRiskInfo classRisk) {
        return String.format("%s/generate?class=%s",
                TEST_SCAFFOLDER_BASE_URL,
                classRisk.getClassName());
    }

    /**
     * Format risk factors for display.
     */
    private String formatRiskFactors(ClassRiskInfo classRisk) {
        StringBuilder sb = new StringBuilder();

        if (classRisk.getShapExplanation() != null && 
            classRisk.getShapExplanation().getTopPositiveFeatures() != null) {
            
            for (var feature : classRisk.getShapExplanation().getTopPositiveFeatures()) {
                sb.append(String.format("- %s (contribution: %.2f)\n", 
                        feature.getDescription() != null ? feature.getDescription() : 
                                feature.getFeature(),
                        feature.getContribution()));
            }
        } else if (classRisk.getRiskFactors() != null) {
            for (var factor : classRisk.getRiskFactors()) {
                sb.append(String.format("- %s: %s\n", factor.getName(), factor.getDescription()));
            }
        } else {
            sb.append("- Multiple risk factors detected\n");
        }

        return sb.toString();
    }
}

