package com.testprioritization.model.response;

import java.time.Instant;
import java.util.List;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * GitHub Check / GitLab Pipeline Status response.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class CheckStatus {

    public enum State {
        SUCCESS("success"),
        FAILURE("failure"),
        WARNING("warning"),
        PENDING("pending"),
        ERROR("error"),
        NEUTRAL("neutral");

        private final String value;

        State(String value) {
            this.value = value;
        }

        public String getValue() {
            return value;
        }
    }

    private State state;
    private String description;
    private String targetUrl;
    private String context;
    private CheckDetails details;
    
    @JsonProperty("started_at")
    private Instant startedAt;
    
    @JsonProperty("completed_at")
    private Instant completedAt;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonInclude(JsonInclude.Include.NON_NULL)
    public static class CheckDetails {
        
        @JsonProperty("high_risk_classes_modified")
        private Integer highRiskClassesModified;
        
        @JsonProperty("medium_risk_classes_modified")
        private Integer mediumRiskClassesModified;
        
        @JsonProperty("low_risk_classes_modified")
        private Integer lowRiskClassesModified;
        
        @JsonProperty("tests_added")
        private Integer testsAdded;
        
        @JsonProperty("tests_modified")
        private Integer testsModified;
        
        @JsonProperty("test_coverage_change")
        private Double testCoverageChange;
        
        private String recommendation;
        
        @JsonProperty("risk_classes")
        private List<ClassRiskSummary> riskClasses;
        
        @JsonProperty("policy_violations")
        private List<PolicyViolation> policyViolations;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonInclude(JsonInclude.Include.NON_NULL)
    public static class ClassRiskSummary {
        private String className;
        private String filePath;
        private Double riskScore;
        private String riskLevel;
        private Boolean hasTests;
        private Boolean testsAdded;
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
        private String className;
        private String recommendation;
    }
}

