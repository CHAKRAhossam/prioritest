package com.example.historiquetests.service;

import com.example.historiquetests.model.TestCoverage;
import com.example.historiquetests.parser.JaCoCoParser;
import com.example.historiquetests.parser.PITParser;
import com.example.historiquetests.repository.TestCoverageRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.web.multipart.MultipartFile;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class CoverageServiceTestExtended {

    @Mock
    private TestCoverageRepository coverageRepository;

    @Mock
    private MinioService minioService;

    @Mock
    private JaCoCoParser jacocoParser;

    @Mock
    private PITParser pitParser;

    @InjectMocks
    private CoverageService coverageService;

    private MockMultipartFile mockFile;

    @BeforeEach
    void setUp() {
        mockFile = new MockMultipartFile(
                "file",
                "test.xml",
                "application/xml",
                "<report></report>".getBytes()
        );
    }

    @Test
    void testProcessJaCoCoReportWithoutRepositoryId() throws Exception {
        List<TestCoverage> mockCoverages = new ArrayList<>();
        when(jacocoParser.parseJaCoCoReport(any(), anyString(), anyString(), anyString(), anyString()))
                .thenReturn(mockCoverages);
        when(coverageRepository.saveAll(anyList())).thenReturn(mockCoverages);

        List<TestCoverage> result = coverageService.processJaCoCoReport(
                mockFile, "abc123", "build1", "main");

        assertNotNull(result);
        verify(minioService).upload(contains("default"), any(MultipartFile.class));
    }

    @Test
    void testProcessPITReportWithoutRepositoryId() throws Exception {
        List<TestCoverage> existingCoverages = new ArrayList<>();
        when(coverageRepository.findByCommitShaAndRepositoryId(anyString(), eq("default")))
                .thenReturn(existingCoverages);
        when(coverageRepository.saveAll(anyList())).thenReturn(existingCoverages);

        coverageService.processPITReport(mockFile, "abc123");

        verify(minioService).upload(contains("default"), any(MultipartFile.class));
    }

    @Test
    void testGetCoverageSummaryWithEmptyList() {
        when(coverageRepository.findByCommitSha(anyString())).thenReturn(new ArrayList<>());

        CoverageService.CoverageSummary summary = coverageService.getCoverageSummary("abc123");

        assertNotNull(summary);
        assertEquals("abc123", summary.commitSha);
        assertEquals(0, summary.totalClasses);
        assertEquals(0.0, summary.averageLineCoverage);
    }

    @Test
    void testGetCoverageSummaryWithMultipleCoverages() {
        List<TestCoverage> coverages = new ArrayList<>();
        TestCoverage coverage1 = new TestCoverage();
        coverage1.setLineCoverage(80.0);
        coverage1.setBranchCoverage(75.0);
        coverage1.setMutationScore(60.0);
        coverage1.setLinesCovered(100);
        coverage1.setLinesMissed(20);
        coverages.add(coverage1);

        TestCoverage coverage2 = new TestCoverage();
        coverage2.setLineCoverage(90.0);
        coverage2.setBranchCoverage(85.0);
        coverage2.setMutationScore(70.0);
        coverage2.setLinesCovered(200);
        coverage2.setLinesMissed(20);
        coverages.add(coverage2);

        when(coverageRepository.findByCommitSha(anyString())).thenReturn(coverages);

        CoverageService.CoverageSummary summary = coverageService.getCoverageSummary("abc123");

        assertNotNull(summary);
        assertEquals(2, summary.totalClasses);
        assertEquals(85.0, summary.averageLineCoverage);
        assertEquals(80.0, summary.averageBranchCoverage);
        assertEquals(65.0, summary.averageMutationScore);
        assertEquals(340, summary.totalLines);
        assertEquals(300, summary.coveredLines);
    }

    @Test
    void testGetCoverageHistoryByRepositoryAndBranch() {
        List<TestCoverage> history = new ArrayList<>();
        when(coverageRepository.findCoverageHistoryByRepositoryAndBranch(anyString(), anyString()))
                .thenReturn(history);

        List<TestCoverage> result = coverageService.getCoverageHistoryByRepositoryAndBranch("repo1", "main");

        assertNotNull(result);
        verify(coverageRepository).findCoverageHistoryByRepositoryAndBranch("repo1", "main");
    }

    @Test
    void testFindLowCoverageClasses() {
        List<TestCoverage> lowCoverage = new ArrayList<>();
        when(coverageRepository.findLowCoverageClasses(anyDouble())).thenReturn(lowCoverage);

        List<TestCoverage> result = coverageService.findLowCoverageClasses(50.0);

        assertNotNull(result);
        verify(coverageRepository).findLowCoverageClasses(50.0);
    }

    @Test
    void testProcessPITReportWithMutations() throws Exception {
        List<TestCoverage> existingCoverages = new ArrayList<>();
        TestCoverage coverage = new TestCoverage();
        coverage.setClassName("TestClass");
        existingCoverages.add(coverage);

        List<PITParser.Mutation> mutations = new ArrayList<>();
        Map<String, PITParser.MutationSummary> mutationScores = new HashMap<>();
        PITParser.MutationSummary summary = new PITParser.MutationSummary();
        summary.mutationScore = 75.0;
        mutationScores.put("TestClass", summary);

        when(coverageRepository.findByCommitShaAndRepositoryId(anyString(), anyString()))
                .thenReturn(existingCoverages);
        when(pitParser.parsePITReport(any(), anyString(), anyString())).thenReturn(mutations);
        when(pitParser.calculateMutationScores(anyList())).thenReturn(mutationScores);
        when(coverageRepository.saveAll(anyList())).thenReturn(existingCoverages);

        coverageService.processPITReport(mockFile, "abc123", "repo1");

        verify(pitParser).updateCoverageWithMutations(anyList(), anyMap());
    }
}

