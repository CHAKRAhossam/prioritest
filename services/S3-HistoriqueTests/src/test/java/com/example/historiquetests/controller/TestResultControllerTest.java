package com.example.historiquetests.controller;

import com.example.historiquetests.model.TestResult;
import com.example.historiquetests.service.TestResultService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.web.servlet.MockMvc;

import java.util.ArrayList;
import java.util.List;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(TestResultController.class)
class TestResultControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private TestResultService testResultService;

    private MockMultipartFile mockFile;

    @BeforeEach
    void setUp() {
        mockFile = new MockMultipartFile(
                "file",
                "test.xml",
                MediaType.APPLICATION_XML_VALUE,
                "<testsuite></testsuite>".getBytes()
        );
    }

    @Test
    void testUploadSurefireReport() throws Exception {
        List<TestResult> mockResults = new ArrayList<>();
        when(testResultService.processSurefireReport(any(), anyString(), anyString(), anyString(), anyString()))
                .thenReturn(mockResults);

        mockMvc.perform(multipart("/api/tests/surefire")
                        .file(mockFile)
                        .param("commit", "abc123")
                        .param("repository_id", "repo1")
                        .param("buildId", "build1")
                        .param("branch", "main"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.message").exists())
                .andExpect(jsonPath("$.testsProcessed").value(0));
    }

    @Test
    void testGetTestSummary() throws Exception {
        TestResultService.TestSummary summary = new TestResultService.TestSummary();
        summary.commitSha = "abc123";
        summary.totalTests = 10;
        summary.passedTests = 8;
        summary.failedTests = 2;

        when(testResultService.getTestSummary(anyString())).thenReturn(summary);

        mockMvc.perform(get("/api/tests/commit/abc123"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.commitSha").value("abc123"))
                .andExpect(jsonPath("$.totalTests").value(10));
    }

    @Test
    void testGetTestHistory() throws Exception {
        List<TestResult> history = new ArrayList<>();
        when(testResultService.getTestHistory(anyString(), anyString())).thenReturn(history);

        mockMvc.perform(get("/api/tests/history/TestClass/testMethod"))
                .andExpect(status().isOk());
    }

    @Test
    void testGetFailedTests() throws Exception {
        List<TestResult> failedTests = new ArrayList<>();
        when(testResultService.getFailedTests(anyString())).thenReturn(failedTests);

        mockMvc.perform(get("/api/tests/failed/abc123"))
                .andExpect(status().isOk());
    }
}

