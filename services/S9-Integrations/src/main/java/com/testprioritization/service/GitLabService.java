package com.testprioritization.service;

import java.util.List;
import java.util.Map;

import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import com.testprioritization.config.AppProperties;
import com.testprioritization.model.response.CheckStatus;
import com.testprioritization.model.response.PRComment;
import com.testprioritization.model.webhook.FileChange;

import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Scope;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import reactor.core.publisher.Mono;

/**
 * Service for GitLab API interactions.
 * Handles Pipeline Status, MR Comments, and file change retrieval.
 */
@Service
@RequiredArgsConstructor
@Slf4j
@SuppressWarnings("null")
public class GitLabService {

    private final WebClient gitlabWebClient;
    private final AppProperties appProperties;
    private final Tracer tracer;

    private static final String PIPELINE_NAME = "test-prioritization";

    /**
     * Create or update a commit status on GitLab.
     */
    public Mono<Map<String, Object>> createCommitStatus(Long projectId, String sha,
            CheckStatus checkStatus) {
        
        Span span = tracer.spanBuilder("gitlab.createCommitStatus")
                .setAttribute("gitlab.project_id", projectId)
                .setAttribute("gitlab.sha", sha)
                .startSpan();

        try (Scope scope = span.makeCurrent()) {
            String state = mapStateToGitLab(checkStatus.getState());
            
            Map<String, Object> body = Map.of(
                    "state", state,
                    "name", PIPELINE_NAME,
                    "description", checkStatus.getDescription() != null ? 
                            checkStatus.getDescription() : "Test Prioritization Check",
                    "target_url", checkStatus.getTargetUrl() != null ? 
                            checkStatus.getTargetUrl() : ""
            );

            return gitlabWebClient.post()
                    .uri("/projects/{project_id}/statuses/{sha}", projectId, sha)
                    .header("PRIVATE-TOKEN", appProperties.getGitlab().getToken())
                    .bodyValue(body)
                    .retrieve()
                    .bodyToMono(new org.springframework.core.ParameterizedTypeReference<Map<String, Object>>() {})
                    .doOnSuccess(result -> {
                        log.info("Created GitLab commit status for project {} sha={}", 
                                projectId, sha);
                        span.setAttribute("status.id", String.valueOf(result.get("id")));
                    })
                    .doOnError(error -> {
                        log.error("Failed to create commit status: {}", error.getMessage());
                        span.recordException(error);
                    })
                    .doFinally(signalType -> span.end());
        }
    }

    /**
     * Post a note (comment) on a Merge Request.
     */
    public Mono<Map<String, Object>> postMRNote(Long projectId, Long mrIid, PRComment comment) {
        
        Span span = tracer.spanBuilder("gitlab.postMRNote")
                .setAttribute("gitlab.project_id", projectId)
                .setAttribute("gitlab.mr_iid", mrIid)
                .startSpan();

        try (Scope scope = span.makeCurrent()) {
            Map<String, Object> body = Map.of("body", comment.toMarkdown());

            return gitlabWebClient.post()
                    .uri("/projects/{project_id}/merge_requests/{merge_request_iid}/notes", 
                            projectId, mrIid)
                    .header("PRIVATE-TOKEN", appProperties.getGitlab().getToken())
                    .bodyValue(body)
                    .retrieve()
                    .bodyToMono(new org.springframework.core.ParameterizedTypeReference<Map<String, Object>>() {})
                    .doOnSuccess(result -> {
                        log.info("Posted note on MR !{} for project {}", mrIid, projectId);
                        span.setAttribute("note.id", String.valueOf(result.get("id")));
                    })
                    .doOnError(error -> {
                        log.error("Failed to post MR note: {}", error.getMessage());
                        span.recordException(error);
                    })
                    .doFinally(signalType -> span.end());
        }
    }

    /**
     * Update an existing MR note.
     */
    public Mono<Map<String, Object>> updateMRNote(Long projectId, Long mrIid, Long noteId, 
            PRComment comment) {
        
        Map<String, Object> body = Map.of("body", comment.toMarkdown());

        return gitlabWebClient.put()
                .uri("/projects/{project_id}/merge_requests/{merge_request_iid}/notes/{note_id}", 
                        projectId, mrIid, noteId)
                .header("PRIVATE-TOKEN", appProperties.getGitlab().getToken())
                .bodyValue(body)
                .retrieve()
                .bodyToMono(new org.springframework.core.ParameterizedTypeReference<Map<String, Object>>() {})
                .doOnSuccess(result -> log.info("Updated note {} on MR !{}", noteId, mrIid))
                .doOnError(error -> log.error("Failed to update MR note: {}", error.getMessage()));
    }

    /**
     * Get list of files changed in a Merge Request.
     */
    public Mono<List<FileChange>> getMRChanges(Long projectId, Long mrIid) {
        
        Span span = tracer.spanBuilder("gitlab.getMRChanges")
                .setAttribute("gitlab.project_id", projectId)
                .setAttribute("gitlab.mr_iid", mrIid)
                .startSpan();

        try (Scope scope = span.makeCurrent()) {
            return gitlabWebClient.get()
                    .uri("/projects/{project_id}/merge_requests/{merge_request_iid}/changes", 
                            projectId, mrIid)
                    .header("PRIVATE-TOKEN", appProperties.getGitlab().getToken())
                    .retrieve()
                    .bodyToMono(new org.springframework.core.ParameterizedTypeReference<Map<String, Object>>() {})
                    .map(this::extractChangesFromResponse)
                    .doOnSuccess(files -> {
                        log.info("Retrieved {} file changes from MR !{} for project {}", 
                                files.size(), mrIid, projectId);
                        span.setAttribute("files.count", files.size());
                    })
                    .doOnError(error -> {
                        log.error("Failed to get MR changes: {}", error.getMessage());
                        span.recordException(error);
                    })
                    .doFinally(signalType -> span.end());
        }
    }

    /**
     * Get Merge Request details.
     */
    public Mono<Map<String, Object>> getMRDetails(Long projectId, Long mrIid) {
        return gitlabWebClient.get()
                .uri("/projects/{project_id}/merge_requests/{merge_request_iid}", projectId, mrIid)
                .header("PRIVATE-TOKEN", appProperties.getGitlab().getToken())
                .retrieve()
                .bodyToMono(new org.springframework.core.ParameterizedTypeReference<Map<String, Object>>() {})
                .doOnSuccess(result -> log.debug("Retrieved MR !{} details for project {}", 
                        mrIid, projectId))
                .doOnError(error -> log.error("Failed to get MR details: {}", error.getMessage()));
    }

    /**
     * Get project details.
     */
    public Mono<Map<String, Object>> getProject(Long projectId) {
        return gitlabWebClient.get()
                .uri("/projects/{project_id}", projectId)
                .header("PRIVATE-TOKEN", appProperties.getGitlab().getToken())
                .retrieve()
                .bodyToMono(new org.springframework.core.ParameterizedTypeReference<Map<String, Object>>() {})
                .doOnSuccess(result -> log.debug("Retrieved project {} details", projectId))
                .doOnError(error -> log.error("Failed to get project: {}", error.getMessage()));
    }

    /**
     * Create a pipeline for a specific branch/commit.
     */
    public Mono<Map<String, Object>> createPipeline(Long projectId, String ref, 
            Map<String, String> variables) {
        
        Span span = tracer.spanBuilder("gitlab.createPipeline")
                .setAttribute("gitlab.project_id", projectId)
                .setAttribute("gitlab.ref", ref)
                .startSpan();

        try (Scope scope = span.makeCurrent()) {
            Map<String, Object> body = Map.of(
                    "ref", ref,
                    "variables", variables.entrySet().stream()
                            .map(e -> Map.of("key", e.getKey(), "value", e.getValue()))
                            .toList()
            );

            return gitlabWebClient.post()
                    .uri("/projects/{project_id}/pipeline", projectId)
                    .header("PRIVATE-TOKEN", appProperties.getGitlab().getToken())
                    .bodyValue(body)
                    .retrieve()
                    .bodyToMono(new org.springframework.core.ParameterizedTypeReference<Map<String, Object>>() {})
                    .doOnSuccess(result -> {
                        log.info("Created pipeline for project {} ref={}", projectId, ref);
                        span.setAttribute("pipeline.id", String.valueOf(result.get("id")));
                    })
                    .doOnError(error -> {
                        log.error("Failed to create pipeline: {}", error.getMessage());
                        span.recordException(error);
                    })
                    .doFinally(signalType -> span.end());
        }
    }

    /**
     * Map internal state to GitLab status.
     */
    private String mapStateToGitLab(CheckStatus.State state) {
        return switch (state) {
            case SUCCESS -> "success";
            case FAILURE -> "failed";
            case WARNING -> "success"; // GitLab doesn't have warning, use success with description
            case PENDING -> "pending";
            case ERROR -> "failed";
            case NEUTRAL -> "success";
        };
    }

    /**
     * Extract file changes from GitLab MR changes response.
     */
    @SuppressWarnings("unchecked")
    private List<FileChange> extractChangesFromResponse(Map<String, Object> response) {
        List<Map<String, Object>> changes = (List<Map<String, Object>>) response.get("changes");
        if (changes == null) {
            return List.of();
        }

        return changes.stream()
                .map(change -> FileChange.builder()
                        .path((String) change.get("new_path"))
                        .filename((String) change.get("new_path"))
                        .status(determineChangeStatus(change))
                        .additions(countAdditions((String) change.get("diff")))
                        .deletions(countDeletions((String) change.get("diff")))
                        .patch((String) change.get("diff"))
                        .previousFilename((String) change.get("old_path"))
                        .build())
                .toList();
    }

    /**
     * Determine the status of a file change.
     */
    private String determineChangeStatus(Map<String, Object> change) {
        Boolean newFile = (Boolean) change.get("new_file");
        Boolean renamedFile = (Boolean) change.get("renamed_file");
        Boolean deletedFile = (Boolean) change.get("deleted_file");

        if (Boolean.TRUE.equals(newFile)) {
            return "added";
        } else if (Boolean.TRUE.equals(deletedFile)) {
            return "removed";
        } else if (Boolean.TRUE.equals(renamedFile)) {
            return "renamed";
        }
        return "modified";
    }

    /**
     * Count additions in a diff.
     */
    private Integer countAdditions(String diff) {
        if (diff == null) return 0;
        return (int) diff.lines()
                .filter(line -> line.startsWith("+") && !line.startsWith("+++"))
                .count();
    }

    /**
     * Count deletions in a diff.
     */
    private Integer countDeletions(String diff) {
        if (diff == null) return 0;
        return (int) diff.lines()
                .filter(line -> line.startsWith("-") && !line.startsWith("---"))
                .count();
    }
}

