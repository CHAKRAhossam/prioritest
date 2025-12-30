package com.testprioritization.service;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import com.testprioritization.config.AppProperties;
import com.testprioritization.model.response.RiskAnalysisResult;
import com.testprioritization.model.response.RiskAnalysisResult.ClassRiskInfo;
import com.testprioritization.model.response.RiskAnalysisResult.FeatureContribution;
import com.testprioritization.model.response.RiskAnalysisResult.RiskFactor;
import com.testprioritization.model.response.RiskAnalysisResult.RiskLevel;
import com.testprioritization.model.response.RiskAnalysisResult.ShapExplanation;
import com.testprioritization.model.webhook.FileChange;

import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Scope;
import lombok.extern.slf4j.Slf4j;
import reactor.core.publisher.Mono;

/**
 * Risk Analyzer Service - Analyzes modified classes and predicts test priority.
 * 
 * Integrates with the Prioritization microservice to get ML-based risk scores
 * with SHAP explanations for explainability.
 */
@Service
@Slf4j
@SuppressWarnings({"null", "unchecked"})
public class RiskAnalyzerService {

    private final WebClient prioritizationWebClient;
    private final AppProperties appProperties;
    private final Tracer tracer;
    private final Timer analysisTimer;

    public RiskAnalyzerService(WebClient prioritizationWebClient, AppProperties appProperties,
            Tracer tracer, MeterRegistry meterRegistry) {
        this.prioritizationWebClient = prioritizationWebClient;
        this.appProperties = appProperties;
        this.tracer = tracer;
        
        this.analysisTimer = Timer.builder("risk.analysis.duration")
                .description("Time taken to analyze risk")
                .register(meterRegistry);
    }

    /**
     * Analyze risk for a list of file changes.
     */
    public Mono<RiskAnalysisResult> analyzeRisk(String repository, String commitSha,
            Integer prNumber, List<FileChange> fileChanges) {
        
        Span span = tracer.spanBuilder("riskAnalyzer.analyze")
                .setAttribute("repository", repository)
                .setAttribute("commit_sha", commitSha)
                .setAttribute("files_count", fileChanges.size())
                .startSpan();

        return Mono.fromCallable(() -> analysisTimer.record(() -> {
            try (Scope scope = span.makeCurrent()) {
                // Filter to only class files (not tests)
                List<FileChange> classFiles = fileChanges.stream()
                        .filter(FileChange::isClassFile)
                        .filter(fc -> !fc.isTestFile())
                        .toList();

                // Get test files
                List<FileChange> testFiles = fileChanges.stream()
                        .filter(FileChange::isTestFile)
                        .toList();

                log.info("Analyzing {} class files and {} test files for {}", 
                        classFiles.size(), testFiles.size(), repository);

                // Get risk predictions from prioritization service
                List<ClassRiskInfo> classRisks = getPredictions(classFiles, testFiles);

                // Calculate overall risk
                double overallRisk = classRisks.stream()
                        .mapToDouble(cr -> cr.getRiskScore() != null ? cr.getRiskScore() : 0.0)
                        .max()
                        .orElse(0.0);

                RiskLevel overallLevel = RiskAnalysisResult.calculateOverallRiskLevel(
                        classRisks,
                        appProperties.getRisk().getThreshold().getHigh(),
                        appProperties.getRisk().getThreshold().getMedium());

                RiskAnalysisResult result = RiskAnalysisResult.builder()
                        .analysisId(UUID.randomUUID().toString())
                        .repository(repository)
                        .commitSha(commitSha)
                        .prNumber(prNumber)
                        .analyzedAt(Instant.now())
                        .classRisks(classRisks)
                        .overallRiskScore(overallRisk)
                        .overallRiskLevel(overallLevel)
                        .testFilesAdded(testFiles.stream()
                                .filter(tf -> "added".equals(tf.getStatus()))
                                .map(FileChange::getPath)
                                .toList())
                        .testFilesModified(testFiles.stream()
                                .filter(tf -> "modified".equals(tf.getStatus()))
                                .map(FileChange::getPath)
                                .toList())
                        .build();

                span.setAttribute("overall_risk_score", overallRisk);
                span.setAttribute("overall_risk_level", overallLevel.name());

                return result;
            }
        })).doOnError(error -> {
            log.error("Risk analysis failed: {}", error.getMessage());
            span.recordException(error);
        }).doFinally(signalType -> span.end());
    }

    /**
     * Get risk predictions from the prioritization service.
     */
    private List<ClassRiskInfo> getPredictions(List<FileChange> classFiles, 
            List<FileChange> testFiles) {
        
        List<ClassRiskInfo> predictions = new ArrayList<>();

        for (FileChange classFile : classFiles) {
            try {
                // Call prioritization service for prediction
                ClassRiskInfo riskInfo = callPrioritizationService(classFile, testFiles);
                predictions.add(riskInfo);
            } catch (Exception e) {
                log.warn("Failed to get prediction for {}, using fallback: {}", 
                        classFile.getPath(), e.getMessage());
                // Use fallback heuristic-based prediction
                predictions.add(createFallbackPrediction(classFile, testFiles));
            }
        }

        return predictions;
    }

    /**
     * Call the prioritization microservice to get ML prediction with SHAP explanation.
     */
    private ClassRiskInfo callPrioritizationService(FileChange classFile, 
            List<FileChange> testFiles) {
        
        Map<String, Object> request = Map.of(
                "class_name", classFile.extractClassName(),
                "file_path", classFile.getPath(),
                "lines_added", classFile.getAdditions() != null ? classFile.getAdditions() : 0,
                "lines_removed", classFile.getDeletions() != null ? classFile.getDeletions() : 0,
                "change_type", classFile.getStatus()
        );

        try {
            Map<String, Object> response = prioritizationWebClient.post()
                    .uri("/predict")
                    .bodyValue(request)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();

            if (response != null) {
                return mapResponseToClassRiskInfo(response, classFile, testFiles);
            }
        } catch (Exception e) {
            log.debug("Prioritization service call failed: {}", e.getMessage());
        }

        return createFallbackPrediction(classFile, testFiles);
    }

    /**
     * Map prioritization service response to ClassRiskInfo.
     */
    private ClassRiskInfo mapResponseToClassRiskInfo(Map<String, Object> response,
            FileChange classFile, List<FileChange> testFiles) {
        
        Double riskScore = ((Number) response.getOrDefault("risk_score", 0.5)).doubleValue();
        Map<String, Object> shapValues = (Map<String, Object>) response.get("shap_explanation");
        
        // Determine if tests exist for this class
        String className = classFile.extractClassName();
        boolean hasTests = testFiles.stream()
                .anyMatch(tf -> tf.getPath() != null && 
                        tf.getPath().contains(className + "Test"));
        boolean testsAdded = testFiles.stream()
                .anyMatch(tf -> "added".equals(tf.getStatus()) && 
                        tf.getPath() != null && 
                        tf.getPath().contains(className));

        return ClassRiskInfo.builder()
                .className(className)
                .filePath(classFile.getPath())
                .packageName(classFile.extractPackagePath())
                .riskScore(riskScore)
                .riskLevel(calculateRiskLevel(riskScore))
                .changeType(classFile.getStatus())
                .linesAdded(classFile.getAdditions())
                .linesRemoved(classFile.getDeletions())
                .hasExistingTests(hasTests)
                .testsAddedInPr(testsAdded)
                .shapExplanation(mapShapExplanation(shapValues))
                .riskFactors(extractRiskFactors(response))
                .recommendedTests(generateTestRecommendations(className, riskScore))
                .build();
    }

    /**
     * Create fallback prediction using heuristics when ML service unavailable.
     */
    private ClassRiskInfo createFallbackPrediction(FileChange classFile, 
            List<FileChange> testFiles) {
        
        String className = classFile.extractClassName();
        
        // Heuristic-based risk calculation
        double riskScore = calculateHeuristicRisk(classFile);
        
        // Check for existing tests
        boolean hasTests = testFiles.stream()
                .anyMatch(tf -> tf.getPath() != null && 
                        (tf.getPath().contains(className + "Test") ||
                         tf.getPath().contains(className + "Tests") ||
                         tf.getPath().contains(className + "Spec")));
        
        boolean testsAdded = testFiles.stream()
                .anyMatch(tf -> "added".equals(tf.getStatus()) && 
                        tf.getPath() != null && 
                        tf.getPath().contains(className));

        List<RiskFactor> riskFactors = new ArrayList<>();
        
        // Add risk factors based on heuristics
        if (classFile.getAdditions() != null && classFile.getAdditions() > 100) {
            riskFactors.add(RiskFactor.builder()
                    .name("Large Change")
                    .description("Many lines added")
                    .value((double) classFile.getAdditions())
                    .weight(0.3)
                    .severity("MEDIUM")
                    .build());
        }
        
        if (!hasTests) {
            riskFactors.add(RiskFactor.builder()
                    .name("No Tests")
                    .description("No existing test coverage")
                    .value(1.0)
                    .weight(0.4)
                    .severity("HIGH")
                    .build());
        }

        return ClassRiskInfo.builder()
                .className(className)
                .filePath(classFile.getPath())
                .packageName(classFile.extractPackagePath())
                .riskScore(riskScore)
                .riskLevel(calculateRiskLevel(riskScore))
                .changeType(classFile.getStatus())
                .linesAdded(classFile.getAdditions())
                .linesRemoved(classFile.getDeletions())
                .hasExistingTests(hasTests)
                .testsAddedInPr(testsAdded)
                .riskFactors(riskFactors)
                .recommendedTests(generateTestRecommendations(className, riskScore))
                .shapExplanation(createFallbackShapExplanation(classFile, hasTests))
                .build();
    }

    /**
     * Calculate heuristic-based risk score.
     */
    private double calculateHeuristicRisk(FileChange classFile) {
        double risk = 0.3; // Base risk
        
        // More lines changed = higher risk
        int totalChanges = (classFile.getAdditions() != null ? classFile.getAdditions() : 0) +
                          (classFile.getDeletions() != null ? classFile.getDeletions() : 0);
        
        if (totalChanges > 200) {
            risk += 0.3;
        } else if (totalChanges > 100) {
            risk += 0.2;
        } else if (totalChanges > 50) {
            risk += 0.1;
        }
        
        // Check for risky file patterns
        String path = classFile.getPath() != null ? classFile.getPath() : "";
        if (path.contains("Service") || path.contains("Repository") || 
            path.contains("Controller")) {
            risk += 0.1;
        }
        if (path.contains("Security") || path.contains("Auth") || 
            path.contains("Payment")) {
            risk += 0.2;
        }
        
        return Math.min(risk, 1.0);
    }

    /**
     * Calculate risk level from score.
     */
    private RiskLevel calculateRiskLevel(double riskScore) {
        double highThreshold = appProperties.getRisk().getThreshold().getHigh();
        double mediumThreshold = appProperties.getRisk().getThreshold().getMedium();
        
        if (riskScore >= highThreshold) {
            return RiskLevel.HIGH;
        } else if (riskScore >= mediumThreshold) {
            return RiskLevel.MEDIUM;
        }
        return RiskLevel.LOW;
    }

    /**
     * Map SHAP explanation from response.
     */
    private ShapExplanation mapShapExplanation(Map<String, Object> shapValues) {
        if (shapValues == null) {
            return null;
        }

        Map<String, Double> featureContributions = (Map<String, Double>) 
                shapValues.getOrDefault("feature_contributions", Map.of());
        
        List<FeatureContribution> topPositive = featureContributions.entrySet().stream()
                .filter(e -> e.getValue() > 0)
                .sorted((a, b) -> Double.compare(b.getValue(), a.getValue()))
                .limit(5)
                .map(e -> FeatureContribution.builder()
                        .feature(e.getKey())
                        .contribution(e.getValue())
                        .description(getFeatureDescription(e.getKey()))
                        .build())
                .toList();

        List<FeatureContribution> topNegative = featureContributions.entrySet().stream()
                .filter(e -> e.getValue() < 0)
                .sorted((a, b) -> Double.compare(a.getValue(), b.getValue()))
                .limit(5)
                .map(e -> FeatureContribution.builder()
                        .feature(e.getKey())
                        .contribution(e.getValue())
                        .description(getFeatureDescription(e.getKey()))
                        .build())
                .toList();

        return ShapExplanation.builder()
                .baseValue(((Number) shapValues.getOrDefault("base_value", 0.5)).doubleValue())
                .outputValue(((Number) shapValues.getOrDefault("output_value", 0.5)).doubleValue())
                .featureContributions(featureContributions)
                .topPositiveFeatures(topPositive)
                .topNegativeFeatures(topNegative)
                .explanationText(generateExplanationText(topPositive, topNegative))
                .build();
    }

    /**
     * Create fallback SHAP explanation.
     */
    private ShapExplanation createFallbackShapExplanation(FileChange classFile, 
            boolean hasTests) {
        
        List<FeatureContribution> positiveFactors = new ArrayList<>();
        List<FeatureContribution> negativeFactors = new ArrayList<>();
        
        int changes = (classFile.getAdditions() != null ? classFile.getAdditions() : 0) +
                     (classFile.getDeletions() != null ? classFile.getDeletions() : 0);
        
        if (changes > 50) {
            positiveFactors.add(FeatureContribution.builder()
                    .feature("lines_changed")
                    .value((double) changes)
                    .contribution(0.15)
                    .description("Number of lines modified")
                    .build());
        }
        
        if (!hasTests) {
            positiveFactors.add(FeatureContribution.builder()
                    .feature("test_coverage")
                    .value(0.0)
                    .contribution(0.25)
                    .description("Low/no test coverage")
                    .build());
        } else {
            negativeFactors.add(FeatureContribution.builder()
                    .feature("test_coverage")
                    .value(1.0)
                    .contribution(-0.15)
                    .description("Has existing tests")
                    .build());
        }

        return ShapExplanation.builder()
                .baseValue(0.5)
                .featureContributions(Map.of(
                        "lines_changed", (double) changes,
                        "has_tests", hasTests ? 1.0 : 0.0
                ))
                .topPositiveFeatures(positiveFactors)
                .topNegativeFeatures(negativeFactors)
                .explanationText(generateExplanationText(positiveFactors, negativeFactors))
                .build();
    }

    /**
     * Extract risk factors from response.
     */
    private List<RiskFactor> extractRiskFactors(Map<String, Object> response) {
        List<Map<String, Object>> factors = (List<Map<String, Object>>) 
                response.get("risk_factors");
        if (factors == null) {
            return List.of();
        }

        return factors.stream()
                .map(f -> RiskFactor.builder()
                        .name((String) f.get("name"))
                        .description((String) f.get("description"))
                        .value(((Number) f.getOrDefault("value", 0.0)).doubleValue())
                        .weight(((Number) f.getOrDefault("weight", 1.0)).doubleValue())
                        .severity((String) f.getOrDefault("severity", "MEDIUM"))
                        .build())
                .toList();
    }

    /**
     * Generate test recommendations based on class and risk.
     */
    private List<String> generateTestRecommendations(String className, double riskScore) {
        List<String> recommendations = new ArrayList<>();
        
        recommendations.add(className + "Test");
        
        if (riskScore > 0.7) {
            recommendations.add(className + "IntegrationTest");
            recommendations.add(className + "EdgeCaseTest");
        }
        
        return recommendations;
    }

    /**
     * Get human-readable feature description.
     */
    private String getFeatureDescription(String feature) {
        return switch (feature) {
            case "cyclomatic_complexity" -> "Code complexity measure";
            case "lines_changed" -> "Number of lines modified";
            case "test_coverage" -> "Existing test coverage";
            case "bugfix_proximity" -> "Proximity to recent bug fixes";
            case "coupling" -> "Class coupling/dependencies";
            case "commit_frequency" -> "How often this file changes";
            case "author_experience" -> "Author's experience with this code";
            default -> feature.replace("_", " ");
        };
    }

    /**
     * Generate human-readable explanation text.
     */
    private String generateExplanationText(List<FeatureContribution> positive,
            List<FeatureContribution> negative) {
        
        StringBuilder sb = new StringBuilder();
        
        if (!positive.isEmpty()) {
            sb.append("Risk increased by: ");
            sb.append(positive.stream()
                    .map(f -> f.getFeature().replace("_", " "))
                    .reduce((a, b) -> a + ", " + b)
                    .orElse(""));
            sb.append(". ");
        }
        
        if (!negative.isEmpty()) {
            sb.append("Risk decreased by: ");
            sb.append(negative.stream()
                    .map(f -> f.getFeature().replace("_", " "))
                    .reduce((a, b) -> a + ", " + b)
                    .orElse(""));
            sb.append(".");
        }
        
        return sb.toString();
    }
}

