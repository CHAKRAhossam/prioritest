package com.example.historiquetests.controller;

import com.example.historiquetests.service.MetricsAggregationService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(MetricsController.class)
class MetricsControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private MetricsAggregationService metricsService;

    @Test
    void testGetCommitMetrics() throws Exception {
        MetricsAggregationService.CommitMetrics metrics = new MetricsAggregationService.CommitMetrics();
        metrics.commitSha = "abc123";
        metrics.totalCoverage = 85.0;

        when(metricsService.generateCommitMetrics(anyString())).thenReturn(metrics);

        mockMvc.perform(get("/api/metrics/commit/abc123"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.commitSha").value("abc123"));
    }
}

