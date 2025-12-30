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
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class CoverageServiceTest {

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
    void testProcessJaCoCoReport() throws Exception {
        List<TestCoverage> mockCoverages = new ArrayList<>();
        TestCoverage coverage = new TestCoverage();
        coverage.setClassName("TestClass");
        mockCoverages.add(coverage);

        when(jacocoParser.parseJaCoCoReport(any(), anyString(), anyString(), anyString(), anyString()))
                .thenReturn(mockCoverages);
        when(coverageRepository.saveAll(anyList())).thenReturn(mockCoverages);

        List<TestCoverage> result = coverageService.processJaCoCoReport(
                mockFile, "abc123", "build1", "main", "repo1");

        assertNotNull(result);
        assertEquals(1, result.size());
        verify(minioService).upload(anyString(), any(MultipartFile.class));
        verify(coverageRepository).saveAll(anyList());
    }

    @Test
    void testProcessPITReport() throws Exception {
        List<TestCoverage> existingCoverages = new ArrayList<>();
        TestCoverage coverage = new TestCoverage();
        existingCoverages.add(coverage);

        when(coverageRepository.findByCommitShaAndRepositoryId(anyString(), anyString()))
                .thenReturn(existingCoverages);
        when(coverageRepository.saveAll(anyList())).thenReturn(existingCoverages);

        coverageService.processPITReport(mockFile, "abc123", "repo1");

        verify(minioService).upload(anyString(), any(MultipartFile.class));
        verify(pitParser).parsePITReport(any(), anyString(), anyString());
        verify(coverageRepository).saveAll(anyList());
    }

    @Test
    void testGetCoverageSummary() {
        List<TestCoverage> coverages = new ArrayList<>();
        TestCoverage coverage = new TestCoverage();
        coverage.setLineCoverage(80.0);
        coverages.add(coverage);

        when(coverageRepository.findByCommitSha(anyString())).thenReturn(coverages);

        CoverageService.CoverageSummary summary = coverageService.getCoverageSummary("abc123");

        assertNotNull(summary);
        assertEquals("abc123", summary.commitSha);
        assertEquals(1, summary.totalClasses);
        assertEquals(80.0, summary.averageLineCoverage);
    }

    @Test
    void testGetCoverageHistory() {
        List<TestCoverage> history = new ArrayList<>();
        when(coverageRepository.findCoverageHistoryByClass(anyString())).thenReturn(history);

        List<TestCoverage> result = coverageService.getCoverageHistory("TestClass");

        assertNotNull(result);
        verify(coverageRepository).findCoverageHistoryByClass("TestClass");
    }
}

