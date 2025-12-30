package com.testprioritization.controller;

import java.util.List;
import java.util.Map;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.testprioritization.config.AppProperties;
import com.testprioritization.model.response.CheckStatus;
import com.testprioritization.model.response.PRComment;
import com.testprioritization.model.response.RiskAnalysisResult;
import com.testprioritization.model.webhook.FileChange;
import com.testprioritization.model.webhook.GitLabWebhook;
import com.testprioritization.service.CommentGeneratorService;
import com.testprioritization.service.GitLabService;
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
 * Controller for handling GitLab webhook events.
 */
@RestController
@RequestMapping("/v1/webhooks/gitlab")
@Tag(name = "GitLab Webhooks", description = "GitLab webhook integration endpoints")
@Slf4j
public class GitLabWebhookController {

    private final GitLabService gitLabService;
    private final RiskAnalyzerService riskAnalyzerService;
    private final PolicyGateService policyGateService;
    private final CommentGeneratorService commentGeneratorService;
    private final AppProperties appProperties;
    private final Tracer tracer;
    private final Counter webhookCounter;
    private final Counter webhookErrorCounter;

    public GitLabWebhookController(
            GitLabService gitLabService,
            RiskAnalyzerService riskAnalyzerService,
            PolicyGateService policyGateService,
            CommentGeneratorService commentGeneratorService,
            AppProperties appProperties,
            Tracer tracer,
            MeterRegistry meterRegistry) {
        this.gitLabService = gitLabService;
        this.riskAnalyzerService = riskAnalyzerService;
        this.policyGateService = policyGateService;
        this.commentGeneratorService = commentGeneratorService;
        this.appProperties = appProperties;
        this.tracer = tracer;

        this.webhookCounter = Counter.builder("webhook.gitlab.received.total")
                .description("Total GitLab webhooks received")
                .register(meterRegistry);

        this.webhookErrorCounter = Counter.builder("webhook.gitlab.errors.total")
                .description("Total GitLab webhook errors")
                .register(meterRegistry);
    }

    /**
     * Handle GitLab webhook events.
     */
    @PostMapping
    @Operation(summary = "Receive GitLab webhook",
            description = "Processes merge request events from GitLab")
    public Mono<ResponseEntity<Map<String, Object>>> handleWebhook(
            @RequestHeader(value = "X-Gitlab-Token", required = false) String token,
            @RequestHeader(value = "X-Gitlab-Event", required = false) String event,
            @RequestBody GitLabWebhook webhook) {

        webhookCounter.increment();

        Span span = tracer.spanBuilder("gitlab.webhook.handle")
                .setAttribute("gitlab.event", event != null ? event : "unknown")
                .setAttribute("gitlab.event_type", webhook.getEventType() != null ? 
                        webhook.getEventType() : "unknown")
                .startSpan();

        try (Scope scope = span.makeCurrent()) {
            // Validate token if secret is configured
            if (appProperties.getGitlab().getWebhookSecret() != null &&
                    !appProperties.getGitlab().getWebhookSecret().isEmpty()) {

                if (!appProperties.getGitlab().getWebhookSecret().equals(token)) {
                    log.warn("Invalid webhook token received");
                    webhookErrorCounter.increment();
                    return Mono.just(ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                            .body(Map.of("error", "Invalid token")));
                }
            }

            // Only process merge_request events
            if (!"merge_request".equals(webhook.getObjectKind()) &&
                    !"merge_request".equals(webhook.getEventType())) {
                log.debug("Ignoring non-MR event: {}", webhook.getObjectKind());
                return Mono.just(ResponseEntity.ok(Map.of(
                        "status", "ignored",
                        "reason", "Not a merge_request event"
                )));
            }

            // Only process open, update, and reopen actions
            String action = webhook.getObjectAttributes() != null ?
                    webhook.getObjectAttributes().getAction() : null;
            if (action != null && !"open".equals(action) && 
                    !"update".equals(action) && !"reopen".equals(action)) {
                log.debug("Ignoring MR action: {}", action);
                return Mono.just(ResponseEntity.ok(Map.of(
                        "status", "ignored",
                        "reason", "Action not processed: " + action
                )));
            }

            return processMergeRequest(webhook)
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
     * Process a merge request event.
     */
    private Mono<Map<String, Object>> processMergeRequest(GitLabWebhook webhook) {
        Long projectId = webhook.getProject().getId();
        Long mrIid = webhook.getObjectAttributes().getIid();
        String commitSha = webhook.getObjectAttributes().getLastCommit() != null ?
                webhook.getObjectAttributes().getLastCommit().getId() : null;
        String projectPath = webhook.getProject().getPathWithNamespace();

        log.info("Processing MR !{} for project {}", mrIid, projectPath);

        // Create initial pending status
        CheckStatus pendingStatus = CheckStatus.builder()
                .state(CheckStatus.State.PENDING)
                .description("Analyzing changes...")
                .build();

        return gitLabService.createCommitStatus(projectId, commitSha, pendingStatus)
                .flatMap(status -> {
                    // Get MR changes
                    return gitLabService.getMRChanges(projectId, mrIid)
                            .flatMap(files -> analyzeAndReport(
                                    projectId, mrIid, projectPath, 
                                    commitSha, files));
                })
                .map(result -> Map.<String, Object>of(
                        "status", "processed",
                        "mr_iid", mrIid,
                        "project", projectPath,
                        "risk_level", result.getOverallRiskLevel().name()
                ));
    }

    /**
     * Analyze files and report results.
     */
    private Mono<RiskAnalysisResult> analyzeAndReport(
            Long projectId, Long mrIid, String projectPath,
            String commitSha, List<FileChange> files) {

        return riskAnalyzerService.analyzeRisk(projectPath, commitSha, mrIid.intValue(), files)
                .flatMap(analysis -> {
                    // Evaluate policy gate
                    PolicyGateResult policyResult = policyGateService.evaluatePolicy(analysis);
                    analysis.setPolicyGatePassed(policyResult.isPassed());
                    analysis.setPolicyViolations(policyResult.getViolations());

                    // Generate comment
                    PRComment comment = commentGeneratorService.generateComment(
                            analysis, policyResult);

                    // Build final status
                    CheckStatus finalStatus = buildFinalCheckStatus(analysis, policyResult);

                    // Update status and post note in parallel
                    Mono<Map<String, Object>> updateStatus = 
                            gitLabService.createCommitStatus(projectId, commitSha, finalStatus);

                    Mono<Map<String, Object>> postNote = 
                            gitLabService.postMRNote(projectId, mrIid, comment);

                    return Mono.zip(updateStatus, postNote)
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
}

