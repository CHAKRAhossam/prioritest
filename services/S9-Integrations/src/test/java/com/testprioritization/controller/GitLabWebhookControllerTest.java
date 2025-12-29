package com.testprioritization.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.testprioritization.config.AppProperties;
import com.testprioritization.service.CommentGeneratorService;
import com.testprioritization.service.GitLabService;
import com.testprioritization.service.PolicyGateService;
import com.testprioritization.service.RiskAnalyzerService;
import io.micrometer.core.instrument.MeterRegistry;
import io.opentelemetry.api.trace.Tracer;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.reactive.AutoConfigureWebTestClient;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.reactive.server.WebTestClient;

import reactor.core.publisher.Mono;
import java.util.Map;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureWebTestClient
@ActiveProfiles("test")
class GitLabWebhookControllerTest {

    @Autowired
    private WebTestClient webTestClient;

    @MockBean
    private GitLabService gitLabService;

    @MockBean
    private RiskAnalyzerService riskAnalyzerService;

    @MockBean
    private PolicyGateService policyGateService;

    @MockBean
    private CommentGeneratorService commentGeneratorService;

    @MockBean
    private AppProperties appProperties;

    @MockBean
    private ObjectMapper objectMapper;

    @MockBean
    private Tracer tracer;

    @MockBean
    private MeterRegistry meterRegistry;

    private String webhookPayload;

    @BeforeEach
    void setUp() {
        webhookPayload = """
            {
                "object_kind": "merge_request",
                "object_attributes": {
                    "iid": 123,
                    "state": "opened",
                    "source_branch": "feature-branch",
                    "target_branch": "main",
                    "last_commit": {
                        "id": "abc123"
                    }
                },
                "project": {
                    "id": 1,
                    "path_with_namespace": "test/repo"
                }
            }
            """;
        
        // Mock AppProperties to avoid token validation
        when(appProperties.getGitlab()).thenReturn(new AppProperties.GitLab());
        when(appProperties.getGitlab().getWebhookSecret()).thenReturn(null);
        
        // Mock services to return empty results
        when(gitLabService.createCommitStatus(any(), any(), any()))
            .thenReturn(Mono.just(Map.of()));
        when(gitLabService.getMRChanges(any(), any()))
            .thenReturn(Mono.just(java.util.Collections.emptyList()));
        when(riskAnalyzerService.analyzeRisk(any(), any(), any(), any()))
            .thenReturn(Mono.just(new com.testprioritization.model.response.RiskAnalysisResult()));
        when(policyGateService.evaluatePolicy(any()))
            .thenReturn(com.testprioritization.service.PolicyGateService.PolicyGateResult.builder()
                .passed(true)
                .shouldBlock(false)
                .violations(java.util.Collections.emptyList())
                .build());
        when(commentGeneratorService.generateComment(any(), any()))
            .thenReturn(new com.testprioritization.model.response.PRComment());
        when(gitLabService.postMRNote(any(), any(), any()))
            .thenReturn(Mono.just(Map.of()));
    }

    @Test
    void testHandleWebhook() {
        webTestClient.post()
                .uri("/v1/webhooks/gitlab")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(webhookPayload)
                .exchange()
                .expectStatus().isOk();
    }

    @Test
    void testHandleWebhookWithInvalidToken() {
        webTestClient.post()
                .uri("/v1/webhooks/gitlab")
                .header("X-Gitlab-Token", "invalid")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(webhookPayload)
                .exchange()
                .expectStatus().is4xxClientError();
    }
}

