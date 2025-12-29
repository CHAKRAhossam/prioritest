package com.example.historiquetests.controller;

import com.example.historiquetests.service.CoverageService;
import com.example.historiquetests.repository.MutationResultRepository;
import com.example.historiquetests.model.TestCoverage;
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

@WebMvcTest(CoverageController.class)
class CoverageControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private CoverageService coverageService;

    @MockBean
    private MutationResultRepository mutationResultRepository;

    private MockMultipartFile mockFile;

    @BeforeEach
    void setUp() {
        mockFile = new MockMultipartFile(
                "file",
                "test.xml",
                MediaType.APPLICATION_XML_VALUE,
                "<report></report>".getBytes()
        );
    }

    @Test
    void testUploadJaCoCoReport() throws Exception {
        List<TestCoverage> mockCoverages = new ArrayList<>();
        when(coverageService.processJaCoCoReport(any(), anyString(), anyString(), anyString(), anyString()))
                .thenReturn(mockCoverages);

        mockMvc.perform(multipart("/api/coverage/jacoco")
                        .file(mockFile)
                        .param("commit", "abc123")
                        .param("repository_id", "repo1")
                        .param("buildId", "build1")
                        .param("branch", "main"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.message").exists())
                .andExpect(jsonPath("$.classesProcessed").value(0));
    }

    @Test
    void testUploadPITReport() throws Exception {
        mockMvc.perform(multipart("/api/coverage/pit")
                        .file(mockFile)
                        .param("commit", "abc123")
                        .param("repository_id", "repo1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.message").exists());
    }

    @Test
    void testGetCoverageByCommit() throws Exception {
        CoverageService.CoverageSummary summary = new CoverageService.CoverageSummary();
        summary.commitSha = "abc123";
        summary.totalClasses = 5;
        summary.averageLineCoverage = 80.0;

        when(coverageService.getCoverageSummary(anyString())).thenReturn(summary);

        mockMvc.perform(get("/api/coverage/commit/abc123"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.commitSha").value("abc123"))
                .andExpect(jsonPath("$.totalClasses").value(5));
    }

    @Test
    void testGetCoverageHistory() throws Exception {
        List<TestCoverage> history = new ArrayList<>();
        when(coverageService.getCoverageHistory(anyString())).thenReturn(history);

        mockMvc.perform(get("/api/coverage/class/TestClass"))
                .andExpect(status().isOk());
    }
}

