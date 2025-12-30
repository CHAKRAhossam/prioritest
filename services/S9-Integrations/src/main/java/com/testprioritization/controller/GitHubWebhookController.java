package com.testprioritization.controller;

import java.nio.charset.StandardCharsets;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.util.List;
import java.util.Map;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

import org.apache.commons.codec.binary.Hex;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.testprioritization.config.AppProperties;
import com.testprioritization.model.response.CheckStatus;
import com.testprioritization.model.response.PRComment;
import com.testprioritization.model.response.RiskAnalysisResult;
import com.testprioritization.model.webhook.FileChange;
import com.testprioritization.model.webhook.GitHubWebhook;
import com.testprioritization.service.CommentGeneratorService;
import com.testprioritization.service.GitHubService;
import com.testprioritization.service.PolicyGateService;
import com.testprioritization.service.PolicyGateService.PolicyGateResult;
import com.testprioritization.service.RiskAnalyzerService;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Scope;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import reactor.core.publisher.Mono;

/**
 * Controller for handling GitHub webhook events.
 */
@RestController
@RequestMapping("/v1/webhooks/github")
@Tag(name = "GitHub Webhooks", description = "GitHub webhook integration endpoints")
@Slf4j
public class GitHubWebhookController {

    private final GitHubService gitHubService;
    private final RiskAnalyzerService riskAnalyzerService;
    private final PolicyGateService policyGateService;
    private final CommentGeneratorService commentGeneratorService;
    private final AppProperties appProperties;
    private final ObjectMapper objectMapper;
    private final Tracer tracer;
    private final Counter webhookCounter;
    private final Counter webhookErrorCounter;

    public GitHubWebhookController(
            GitHubService gitHubService,
            RiskAnalyzerService riskAnalyzerService,
            PolicyGateService policyGateService,
            CommentGeneratorService commentGeneratorService,
            AppProperties appProperties,
            ObjectMapper objectMapper,
            Tracer tracer,
            MeterRegistry meterRegistry) {
        this.gitHubService = gitHubService;
        this.riskAnalyzerService = riskAnalyzerService;
        this.policyGateService = policyGateService;
        this.commentGeneratorService = commentGeneratorService;
        this.appProperties = appProperties;
        this.objectMapper = objectMapper;
        this.tracer = tracer;
        
        this.webhookCounter = Counter.builder("webhook.github.received.total")
                .description("Total GitHub webhooks received")
                .register(meterRegistry);
        
        this.webhookErrorCounter = Counter.builder("webhook.github.errors.total")
                .description("Total GitHub webhook errors")
                .register(meterRegistry);
    }

    /**
     * Handle GitHub webhook events.
     */
    @PostMapping
    @Operation(summary = "Receive GitHub webhook", 
               description = "Processes pull request events from GitHub")
    public Mono<ResponseEntity<Map<String, Object>>> handleWebhook(
            @RequestHeader(value = "X-GitHub-Event", required = false) String event,
            @RequestHeader(value = "X-Hub-Signature-256", required = false) String signature,
            @RequestHeader(value = "X-GitHub-Delivery", required = false) String deliveryId,
            @RequestBody String payload) {

        webhookCounter.increment();
        
        Span span = tracer.spanBuilder("github.webhook.handle")
                .setAttribute("github.event", event != null ? event : "unknown")
                .setAttribute("github.delivery_id", deliveryId != null ? deliveryId : "unknown")
                .startSpan();

        try (Scope scope = span.makeCurrent()) {
            // Validate signature if secret is configured
            if (appProperties.getGithub().getWebhookSecret() != null && 
                !appProperties.getGithub().getWebhookSecret().isEmpty()) {
                
                if (!validateSignature(payload, signature)) {
                    log.warn("Invalid webhook signature for delivery {}", deliveryId);
                    webhookErrorCounter.increment();
                    return Mono.just(ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                            .body(Map.of("error", "Invalid signature")));
                }
            }

            // Only process pull_request events
            if (!"pull_request".equals(event)) {
                log.debug("Ignoring non-PR event: {}", event);
                return Mono.just(ResponseEntity.ok(Map.of(
                        "status", "ignored",
                        "reason", "Not a pull_request event"
                )));
            }

            // Parse webhook payload
            GitHubWebhook webhook;
            try {
                webhook = objectMapper.readValue(payload, GitHubWebhook.class);
            } catch (Exception e) {
                log.error("Failed to parse webhook payload: {}", e.getMessage());
                webhookErrorCounter.increment();
                return Mono.just(ResponseEntity.badRequest()
                        .body(Map.of("error", "Invalid payload format")));
            }

            // Only process opened and synchronize actions
            String action = webhook.getAction();
            if (!"opened".equals(action) && !"synchronize".equals(action)) {
                log.debug("Ignoring PR action: {}", action);
                return Mono.just(ResponseEntity.ok(Map.of(
                        "status", "ignored",
                        "reason", "Action not processed: " + action
                )));
            }

            return processPullRequest(webhook)
                    .map(result -> ResponseEntity.ok(result))
                    .doOnError(error -> {
                        log.error("Error processing webhook: {}", error.getMessage());
                        webhookErrorCounter.increment();
                        span.recordException(error);
                    })
                    .onErrorReturn(ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                            .body(Map.of("error", "Processing failed")));
        } finally {
            span.end();
        }
    }

    /**
     * Process a pull request event.
     */
    private Mono<Map<String, Object>> processPullRequest(GitHubWebhook webhook) {
        String owner = webhook.getRepository().getOwner().getLogin();
        String repo = webhook.getRepository().getName();
        Integer prNumber = webhook.getPullRequest().getNumber();
        String headSha = webhook.getPullRequest().getHead().getSha();
        Long installationId = webhook.getInstallation() != null ? 
                webhook.getInstallation().getId() : null;

        log.info("Processing PR #{} for {}/{}", prNumber, owner, repo);

        // Create initial pending check
        CheckStatus pendingStatus = CheckStatus.builder()
                .state(CheckStatus.State.PENDING)
                .description("Analyzing changes...")
                .context("test-prioritization")
                .build();

        return gitHubService.createCheckRun(owner, repo, headSha, pendingStatus, installationId)
                .flatMap(checkRun -> {
                    Long checkRunId = ((Number) checkRun.get("id")).longValue();
                    
                    // Get PR files
                    return gitHubService.getPRFiles(owner, repo, prNumber, installationId)
                            .flatMap(files -> analyzeAndReport(
                                    owner, repo, prNumber, headSha, 
                                    checkRunId, installationId, files));
                })
                .map(result -> Map.<String, Object>of(
                        "status", "processed",
                        "pr_number", prNumber,
                        "repository", owner + "/" + repo,
                        "risk_level", result.getOverallRiskLevel().name()
                ));
    }

    /**
     * Analyze files and report results.
     */
    private Mono<RiskAnalysisResult> analyzeAndReport(
            String owner, String repo, Integer prNumber, String headSha,
            Long checkRunId, Long installationId, List<FileChange> files) {

        String fullRepo = owner + "/" + repo;

        return riskAnalyzerService.analyzeRisk(fullRepo, headSha, prNumber, files)
                .flatMap(analysis -> {
                    // Evaluate policy gate
                    PolicyGateResult policyResult = policyGateService.evaluatePolicy(analysis);
                    analysis.setPolicyGatePassed(policyResult.isPassed());
                    analysis.setPolicyViolations(policyResult.getViolations());

                    // Generate comment
                    PRComment comment = commentGeneratorService.generateComment(
                            analysis, policyResult);

                    // Build final check status
                    CheckStatus finalStatus = buildFinalCheckStatus(analysis, policyResult);

                    // Update check run and post comment in parallel
                    Mono<Map<String, Object>> updateCheck = gitHubService.updateCheckRun(
                            owner, repo, checkRunId, finalStatus, installationId);
                    
                    Mono<Map<String, Object>> postComment = gitHubService.postPRComment(
                            owner, repo, prNumber, comment, installationId);

                    return Mono.zip(updateCheck, postComment)
                            .thenReturn(analysis);
                });
    }

    /**
     * Build final check status from analysis results.
     */
    private CheckStatus buildFinalCheckStatus(RiskAnalysisResult analysis, 
            PolicyGateResult policyResult) {
        
        CheckStatus.State state;
        String description;

        if (policyResult.isPassed()) {
            if (analysis.getOverallRiskLevel() == RiskAnalysisResult.RiskLevel.HIGH) {
                state = CheckStatus.State.WARNING;
                description = "High-risk changes detected - tests recommended";
            } else {
                state = CheckStatus.State.SUCCESS;
                description = "Risk analysis completed successfully";
            }
        } else if (policyResult.isShouldBlock()) {
            state = CheckStatus.State.FAILURE;
            description = "Policy gate failed - tests required for high-risk changes";
        } else {
            state = CheckStatus.State.WARNING;
            description = "Policy warnings - review recommended";
        }

        // Count risk levels
        int highRisk = 0, mediumRisk = 0, lowRisk = 0, testsAdded = 0;
        
        if (analysis.getClassRisks() != null) {
            for (var classRisk : analysis.getClassRisks()) {
                switch (classRisk.getRiskLevel()) {
                    case HIGH, CRITICAL -> highRisk++;
                    case MEDIUM -> mediumRisk++;
                    case LOW -> lowRisk++;
                }
                if (Boolean.TRUE.equals(classRisk.getTestsAddedInPr())) {
                    testsAdded++;
                }
            }
        }

        return CheckStatus.builder()
                .state(state)
                .description(description)
                .context("test-prioritization")
                .details(CheckStatus.CheckDetails.builder()
                        .highRiskClassesModified(highRisk)
                        .mediumRiskClassesModified(mediumRisk)
                        .lowRiskClassesModified(lowRisk)
                        .testsAdded(testsAdded)
                        .testsModified(analysis.getTestFilesModified() != null ? 
                                analysis.getTestFilesModified().size() : 0)
                        .recommendation(policyResult.isPassed() ? null :
                                "Add tests for high-risk classes before merging")
                        .build())
                .build();
    }

    /**
     * Validate GitHub webhook signature.
     */
    private boolean validateSignature(String payload, String signature) {
        if (signature == null || !signature.startsWith("sha256=")) {
            return false;
        }

        try {
            String secret = appProperties.getGithub().getWebhookSecret();
            Mac mac = Mac.getInstance("HmacSHA256");
            SecretKeySpec secretKeySpec = new SecretKeySpec(
                    secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256");
            mac.init(secretKeySpec);
            
            byte[] hash = mac.doFinal(payload.getBytes(StandardCharsets.UTF_8));
            String expectedSignature = "sha256=" + Hex.encodeHexString(hash);
            
            return signature.equals(expectedSignature);
        } catch (NoSuchAlgorithmException | InvalidKeyException e) {
            log.error("Error validating signature: {}", e.getMessage());
            return false;
        }
    }
}

