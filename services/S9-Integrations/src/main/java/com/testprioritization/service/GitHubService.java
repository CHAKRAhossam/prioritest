package com.testprioritization.service;

import java.security.KeyFactory;
import java.security.PrivateKey;
import java.security.spec.PKCS8EncodedKeySpec;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Base64;
import java.util.Date;
import java.util.List;
import java.util.Map;

import org.springframework.http.HttpHeaders;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import com.testprioritization.config.AppProperties;
import com.testprioritization.model.response.CheckStatus;
import com.testprioritization.model.response.PRComment;
import com.testprioritization.model.webhook.FileChange;

import io.jsonwebtoken.Jwts;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Scope;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import reactor.core.publisher.Mono;

/**
 * Service for GitHub API interactions.
 * Handles Check Runs, PR Comments, and file change retrieval.
 */
@Service
@RequiredArgsConstructor
@Slf4j
@SuppressWarnings("null")
public class GitHubService {

    private final WebClient githubWebClient;
    private final AppProperties appProperties;
    private final Tracer tracer;

    private static final String GITHUB_API_VERSION = "2022-11-28";
    private static final String CHECK_NAME = "Test Prioritization Analysis";

    /**
     * Create a GitHub Check Run for a PR.
     */
    public Mono<Map<String, Object>> createCheckRun(String owner, String repo, String headSha, 
            CheckStatus checkStatus, Long installationId) {
        
        Span span = tracer.spanBuilder("github.createCheckRun")
                .setAttribute("github.owner", owner)
                .setAttribute("github.repo", repo)
                .setAttribute("github.sha", headSha)
                .startSpan();

        try (Scope scope = span.makeCurrent()) {
            Map<String, Object> body = buildCheckRunBody(headSha, checkStatus);
            
            return getInstallationToken(installationId)
                    .flatMap(token -> githubWebClient.post()
                            .uri("/repos/{owner}/{repo}/check-runs", owner, repo)
                            .header(HttpHeaders.AUTHORIZATION, "Bearer " + token)
                            .header("X-GitHub-Api-Version", GITHUB_API_VERSION)
                            .header(HttpHeaders.ACCEPT, "application/vnd.github+json")
                            .bodyValue(body)
                            .retrieve()
                            .bodyToMono(new org.springframework.core.ParameterizedTypeReference<Map<String, Object>>() {}))
                    .doOnSuccess(result -> {
                        log.info("Created GitHub check run for {}/{} sha={}", owner, repo, headSha);
                        span.setAttribute("check_run.id", String.valueOf(result.get("id")));
                    })
                    .doOnError(error -> {
                        log.error("Failed to create check run: {}", error.getMessage());
                        span.recordException(error);
                    })
                    .doFinally(signalType -> span.end());
        }
    }

    /**
     * Update an existing GitHub Check Run.
     */
    public Mono<Map<String, Object>> updateCheckRun(String owner, String repo, Long checkRunId,
            CheckStatus checkStatus, Long installationId) {
        
        Span span = tracer.spanBuilder("github.updateCheckRun")
                .setAttribute("github.owner", owner)
                .setAttribute("github.repo", repo)
                .setAttribute("check_run.id", checkRunId)
                .startSpan();

        try (Scope scope = span.makeCurrent()) {
            Map<String, Object> body = buildCheckRunUpdateBody(checkStatus);
            
            return getInstallationToken(installationId)
                    .flatMap(token -> githubWebClient.patch()
                            .uri("/repos/{owner}/{repo}/check-runs/{check_run_id}", 
                                    owner, repo, checkRunId)
                            .header(HttpHeaders.AUTHORIZATION, "Bearer " + token)
                            .header("X-GitHub-Api-Version", GITHUB_API_VERSION)
                            .header(HttpHeaders.ACCEPT, "application/vnd.github+json")
                            .bodyValue(body)
                            .retrieve()
                            .bodyToMono(new org.springframework.core.ParameterizedTypeReference<Map<String, Object>>() {}))
                    .doOnSuccess(result -> log.info("Updated check run {} for {}/{}", 
                            checkRunId, owner, repo))
                    .doOnError(error -> {
                        log.error("Failed to update check run: {}", error.getMessage());
                        span.recordException(error);
                    })
                    .doFinally(signalType -> span.end());
        }
    }

    /**
     * Post a comment on a Pull Request.
     */
    public Mono<Map<String, Object>> postPRComment(String owner, String repo, Integer prNumber,
            PRComment comment, Long installationId) {
        
        Span span = tracer.spanBuilder("github.postPRComment")
                .setAttribute("github.owner", owner)
                .setAttribute("github.repo", repo)
                .setAttribute("github.pr_number", prNumber)
                .startSpan();

        try (Scope scope = span.makeCurrent()) {
            Map<String, Object> body = Map.of("body", comment.toMarkdown());
            
            return getInstallationToken(installationId)
                    .flatMap(token -> githubWebClient.post()
                            .uri("/repos/{owner}/{repo}/issues/{issue_number}/comments", 
                                    owner, repo, prNumber)
                            .header(HttpHeaders.AUTHORIZATION, "Bearer " + token)
                            .header("X-GitHub-Api-Version", GITHUB_API_VERSION)
                            .header(HttpHeaders.ACCEPT, "application/vnd.github+json")
                            .bodyValue(body)
                            .retrieve()
                            .bodyToMono(new org.springframework.core.ParameterizedTypeReference<Map<String, Object>>() {}))
                    .doOnSuccess(result -> log.info("Posted comment on PR #{} for {}/{}", 
                            prNumber, owner, repo))
                    .doOnError(error -> {
                        log.error("Failed to post PR comment: {}", error.getMessage());
                        span.recordException(error);
                    })
                    .doFinally(signalType -> span.end());
        }
    }

    /**
     * Get list of files changed in a Pull Request.
     */
    public Mono<List<FileChange>> getPRFiles(String owner, String repo, Integer prNumber, 
            Long installationId) {
        
        Span span = tracer.spanBuilder("github.getPRFiles")
                .setAttribute("github.owner", owner)
                .setAttribute("github.repo", repo)
                .setAttribute("github.pr_number", prNumber)
                .startSpan();

        try (Scope scope = span.makeCurrent()) {
            return getInstallationToken(installationId)
                    .flatMap(token -> githubWebClient.get()
                            .uri("/repos/{owner}/{repo}/pulls/{pull_number}/files?per_page=100", 
                                    owner, repo, prNumber)
                            .header(HttpHeaders.AUTHORIZATION, "Bearer " + token)
                            .header("X-GitHub-Api-Version", GITHUB_API_VERSION)
                            .header(HttpHeaders.ACCEPT, "application/vnd.github+json")
                            .retrieve()
                            .bodyToFlux(FileChange.class)
                            .collectList())
                    .doOnSuccess(files -> {
                        log.info("Retrieved {} files from PR #{} for {}/{}", 
                                files.size(), prNumber, owner, repo);
                        span.setAttribute("files.count", files.size());
                    })
                    .doOnError(error -> {
                        log.error("Failed to get PR files: {}", error.getMessage());
                        span.recordException(error);
                    })
                    .doFinally(signalType -> span.end());
        }
    }

    /**
     * Create a commit status (legacy API, used as fallback).
     */
    public Mono<Map<String, Object>> createCommitStatus(String owner, String repo, String sha,
            CheckStatus.State state, String description, String context, Long installationId) {
        
        Map<String, Object> body = Map.of(
                "state", state.getValue(),
                "description", description,
                "context", context
        );
        
        return getInstallationToken(installationId)
                .flatMap(token -> githubWebClient.post()
                        .uri("/repos/{owner}/{repo}/statuses/{sha}", owner, repo, sha)
                        .header(HttpHeaders.AUTHORIZATION, "Bearer " + token)
                        .header("X-GitHub-Api-Version", GITHUB_API_VERSION)
                        .header(HttpHeaders.ACCEPT, "application/vnd.github+json")
                        .bodyValue(body)
                        .retrieve()
                        .bodyToMono(new org.springframework.core.ParameterizedTypeReference<Map<String, Object>>() {}));
    }

    /**
     * Get installation access token using JWT authentication.
     */
    private Mono<String> getInstallationToken(Long installationId) {
        String jwt = generateJWT();
        
        return githubWebClient.post()
                .uri("/app/installations/{installation_id}/access_tokens", installationId)
                .header(HttpHeaders.AUTHORIZATION, "Bearer " + jwt)
                .header("X-GitHub-Api-Version", GITHUB_API_VERSION)
                .header(HttpHeaders.ACCEPT, "application/vnd.github+json")
                .retrieve()
                .bodyToMono(Map.class)
                .map(response -> (String) response.get("token"))
                .doOnError(error -> log.error("Failed to get installation token: {}", 
                        error.getMessage()));
    }

    /**
     * Generate JWT for GitHub App authentication.
     */
    private String generateJWT() {
        try {
            String privateKeyPEM = appProperties.getGithub().getPrivateKey()
                    .replace("-----BEGIN RSA PRIVATE KEY-----", "")
                    .replace("-----END RSA PRIVATE KEY-----", "")
                    .replace("-----BEGIN PRIVATE KEY-----", "")
                    .replace("-----END PRIVATE KEY-----", "")
                    .replaceAll("\\s", "");

            byte[] keyBytes = Base64.getDecoder().decode(privateKeyPEM);
            PKCS8EncodedKeySpec spec = new PKCS8EncodedKeySpec(keyBytes);
            KeyFactory keyFactory = KeyFactory.getInstance("RSA");
            PrivateKey privateKey = keyFactory.generatePrivate(spec);

            Instant now = Instant.now();
            
            return Jwts.builder()
                    .issuer(appProperties.getGithub().getAppId())
                    .issuedAt(Date.from(now.minus(60, ChronoUnit.SECONDS)))
                    .expiration(Date.from(now.plus(10, ChronoUnit.MINUTES)))
                    .signWith(privateKey)
                    .compact();
        } catch (Exception e) {
            log.error("Failed to generate JWT: {}", e.getMessage());
            throw new RuntimeException("Failed to generate GitHub App JWT", e);
        }
    }

    /**
     * Build check run request body.
     */
    private Map<String, Object> buildCheckRunBody(String headSha, CheckStatus checkStatus) {
        String conclusion = mapStateToConclusion(checkStatus.getState());
        
        return Map.of(
                "name", CHECK_NAME,
                "head_sha", headSha,
                "status", "completed",
                "conclusion", conclusion,
                "started_at", Instant.now().toString(),
                "completed_at", Instant.now().toString(),
                "output", Map.of(
                        "title", "Test Prioritization Results",
                        "summary", checkStatus.getDescription(),
                        "text", buildCheckOutputText(checkStatus)
                )
        );
    }

    /**
     * Build check run update body.
     */
    private Map<String, Object> buildCheckRunUpdateBody(CheckStatus checkStatus) {
        String conclusion = mapStateToConclusion(checkStatus.getState());
        
        return Map.of(
                "status", "completed",
                "conclusion", conclusion,
                "completed_at", Instant.now().toString(),
                "output", Map.of(
                        "title", "Test Prioritization Results",
                        "summary", checkStatus.getDescription(),
                        "text", buildCheckOutputText(checkStatus)
                )
        );
    }

    /**
     * Map internal state to GitHub conclusion.
     */
    private String mapStateToConclusion(CheckStatus.State state) {
        return switch (state) {
            case SUCCESS -> "success";
            case FAILURE -> "failure";
            case WARNING -> "neutral";
            case PENDING -> "neutral";
            case ERROR -> "failure";
            case NEUTRAL -> "neutral";
        };
    }

    /**
     * Build detailed output text for check run.
     */
    private String buildCheckOutputText(CheckStatus checkStatus) {
        StringBuilder sb = new StringBuilder();
        
        if (checkStatus.getDetails() != null) {
            CheckStatus.CheckDetails details = checkStatus.getDetails();
            
            sb.append("## Analysis Details\n\n");
            sb.append("| Risk Level | Classes Modified |\n");
            sb.append("|------------|------------------|\n");
            
            if (details.getHighRiskClassesModified() != null) {
                sb.append(String.format("| 🔴 High | %d |\n", details.getHighRiskClassesModified()));
            }
            if (details.getMediumRiskClassesModified() != null) {
                sb.append(String.format("| 🟡 Medium | %d |\n", details.getMediumRiskClassesModified()));
            }
            if (details.getLowRiskClassesModified() != null) {
                sb.append(String.format("| 🟢 Low | %d |\n", details.getLowRiskClassesModified()));
            }
            
            sb.append("\n### Tests Status\n");
            sb.append(String.format("- Tests Added: %d\n", 
                    details.getTestsAdded() != null ? details.getTestsAdded() : 0));
            sb.append(String.format("- Tests Modified: %d\n", 
                    details.getTestsModified() != null ? details.getTestsModified() : 0));
            
            if (details.getRecommendation() != null) {
                sb.append(String.format("\n### Recommendation\n%s\n", details.getRecommendation()));
            }
        }
        
        return sb.toString();
    }
}

