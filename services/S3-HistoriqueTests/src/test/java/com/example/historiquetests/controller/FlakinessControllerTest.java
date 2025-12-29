package com.example.historiquetests.controller;

import com.example.historiquetests.model.TestFlakiness;
import com.example.historiquetests.service.FlakinessService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(FlakinessController.class)
class FlakinessControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private FlakinessService flakinessService;

    @BeforeEach
    void setUp() {
    }

    @Test
    void testCalculateFlakiness() throws Exception {
        List<TestFlakiness> flakiness = new ArrayList<>();
        when(flakinessService.calculateFlakiness(any(LocalDateTime.class), any(LocalDateTime.class)))
                .thenReturn(flakiness);

        mockMvc.perform(post("/api/flakiness/calculate")
                        .param("start", "2024-01-01T00:00:00")
                        .param("end", "2024-01-31T23:59:59"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.message").exists());
    }

    @Test
    void testGetFlakyTests() throws Exception {
        List<TestFlakiness> flakyTests = new ArrayList<>();
        when(flakinessService.getFlakyTests(anyDouble())).thenReturn(flakyTests);

        mockMvc.perform(get("/api/flakiness/flaky")
                        .param("threshold", "0.3"))
                .andExpect(status().isOk());
    }

    @Test
    void testGetFlakyTestsWithDefaultThreshold() throws Exception {
        List<TestFlakiness> flakyTests = new ArrayList<>();
        when(flakinessService.getFlakyTests(0.3)).thenReturn(flakyTests);

        mockMvc.perform(get("/api/flakiness/flaky"))
                .andExpect(status().isOk());
    }

    @Test
    void testGetMostFlakyTests() throws Exception {
        List<TestFlakiness> flakyTests = new ArrayList<>();
        when(flakinessService.getMostFlakyTests()).thenReturn(flakyTests);

        mockMvc.perform(get("/api/flakiness/most-flaky"))
                .andExpect(status().isOk());
    }

    @Test
    void testGetTestFlakiness() throws Exception {
        TestFlakiness flakiness = new TestFlakiness();
        when(flakinessService.getTestFlakiness(anyString(), anyString()))
                .thenReturn(Optional.of(flakiness));

        mockMvc.perform(get("/api/flakiness/test/TestClass/testMethod"))
                .andExpect(status().isOk());
    }

    @Test
    void testGetTestFlakinessNotFound() throws Exception {
        when(flakinessService.getTestFlakiness(anyString(), anyString()))
                .thenReturn(Optional.empty());

        mockMvc.perform(get("/api/flakiness/test/TestClass/testMethod"))
                .andExpect(status().isNotFound());
    }
}

