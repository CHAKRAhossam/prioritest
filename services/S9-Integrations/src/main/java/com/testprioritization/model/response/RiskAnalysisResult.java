package com.testprioritization.model.response;

import java.time.Instant;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Result of risk analysis for modified classes with SHAP explanations.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class RiskAnalysisResult {

    @JsonProperty("analysis_id")
    private String analysisId;
    
    @JsonProperty("repository")
    private String repository;
    
    @JsonProperty("commit_sha")
    private String commitSha;
    
    @JsonProperty("pr_number")
    private Integer prNumber;
    
    @JsonProperty("analyzed_at")
    private Instant analyzedAt;
    
    @JsonProperty("class_risks")
    private List<ClassRiskInfo> classRisks;
    
    @JsonProperty("overall_risk_score")
    private Double overallRiskScore;
    
    @JsonProperty("overall_risk_level")
    private RiskLevel overallRiskLevel;
    
    @JsonProperty("test_files_added")
    private List<String> testFilesAdded;
    
    @JsonProperty("test_files_modified")
    private List<String> testFilesModified;
    
    @JsonProperty("policy_gate_passed")
    private Boolean policyGatePassed;
    
    @JsonProperty("policy_violations")
    private List<PolicyViolation> policyViolations;

    public enum RiskLevel {
        LOW,
        MEDIUM,
        HIGH,
        CRITICAL
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonInclude(JsonInclude.Include.NON_NULL)
    public static class ClassRiskInfo {
        
        @JsonProperty("class_name")
        private String className;
        
        @JsonProperty("file_path")
        private String filePath;
        
        @JsonProperty("package_name")
        private String packageName;
        
        @JsonProperty("risk_score")
        private Double riskScore;
        
        @JsonProperty("risk_level")
        private RiskLevel riskLevel;
        
        @JsonProperty("change_type")
        private String changeType; // added, modified, deleted
        
        @JsonProperty("lines_added")
        private Integer linesAdded;
        
        @JsonProperty("lines_removed")
        private Integer linesRemoved;
        
        @JsonProperty("has_existing_tests")
        private Boolean hasExistingTests;
        
        @JsonProperty("tests_added_in_pr")
        private Boolean testsAddedInPr;
        
        @JsonProperty("test_coverage")
        private Double testCoverage;
        
        @JsonProperty("shap_explanation")
        private ShapExplanation shapExplanation;
        
        @JsonProperty("risk_factors")
        private List<RiskFactor> riskFactors;
        
        @JsonProperty("recommended_tests")
        private List<String> recommendedTests;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonInclude(JsonInclude.Include.NON_NULL)
    public static class ShapExplanation {
        
        @JsonProperty("base_value")
        private Double baseValue;
        
        @JsonProperty("output_value")
        private Double outputValue;
        
        @JsonProperty("feature_values")
        private Map<String, Double> featureValues;
        
        @JsonProperty("feature_contributions")
        private Map<String, Double> featureContributions;
        
        @JsonProperty("top_positive_features")
        private List<FeatureContribution> topPositiveFeatures;
        
        @JsonProperty("top_negative_features")
        private List<FeatureContribution> topNegativeFeatures;
        
        @JsonProperty("explanation_text")
        private String explanationText;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonInclude(JsonInclude.Include.NON_NULL)
    public static class FeatureContribution {
        private String feature;
        private Double value;
        private Double contribution;
        private String description;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonInclude(JsonInclude.Include.NON_NULL)
    public static class RiskFactor {
        private String name;
        private String description;
        private Double value;
        private Double weight;
        private String severity;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonInclude(JsonInclude.Include.NON_NULL)
    public static class PolicyViolation {
        private String type;
        private String severity;
        private String message;
        
        @JsonProperty("class_name")
        private String className;
        
        @JsonProperty("file_path")
        private String filePath;
        
        private String recommendation;
        
        @JsonProperty("auto_fixable")
        private Boolean autoFixable;
    }

    /**
     * Check if any high-risk classes were modified without tests.
     */
    public boolean hasHighRiskWithoutTests() {
        if (classRisks == null) return false;
        return classRisks.stream()
                .anyMatch(cr -> cr.getRiskLevel() == RiskLevel.HIGH 
                        && Boolean.FALSE.equals(cr.getHasExistingTests())
                        && Boolean.FALSE.equals(cr.getTestsAddedInPr()));
    }

    /**
     * Get list of high-risk classes without tests.
     */
    public List<ClassRiskInfo> getHighRiskClassesWithoutTests() {
        if (classRisks == null) return List.of();
        return classRisks.stream()
                .filter(cr -> cr.getRiskLevel() == RiskLevel.HIGH 
                        && Boolean.FALSE.equals(cr.getHasExistingTests())
                        && Boolean.FALSE.equals(cr.getTestsAddedInPr()))
                .toList();
    }

    /**
     * Calculate overall risk level based on class risks.
     */
    public static RiskLevel calculateOverallRiskLevel(List<ClassRiskInfo> classRisks, 
            double highThreshold, double mediumThreshold) {
        if (classRisks == null || classRisks.isEmpty()) {
            return RiskLevel.LOW;
        }

        double maxRisk = classRisks.stream()
                .mapToDouble(cr -> cr.getRiskScore() != null ? cr.getRiskScore() : 0.0)
                .max()
                .orElse(0.0);

        if (maxRisk >= highThreshold) {
            return RiskLevel.HIGH;
        } else if (maxRisk >= mediumThreshold) {
            return RiskLevel.MEDIUM;
        }
        return RiskLevel.LOW;
    }
}

