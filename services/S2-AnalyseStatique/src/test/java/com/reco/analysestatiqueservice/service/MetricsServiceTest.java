package com.reco.analysestatiqueservice.service;

import com.reco.analysestatiqueservice.extractor.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.web.multipart.MultipartFile;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.when;

/**
 * Unit tests for MetricsService.
 *
 * @author Reco Team
 */
@ExtendWith(MockitoExtension.class)
class MetricsServiceTest {

    @Mock
    private ZipExtractor zipExtractor;

    @Mock
    private JavaParserExtractor javaParserExtractor;

    @Mock
    private CKMetricsExtractor ckMetricsExtractor;

    @Mock
    private DependencyGraphExtractor dependencyGraphExtractor;

    @Mock
    private SmellDetector smellDetector;

    @Mock
    private PMDSmellDetectorCli pmdSmellDetectorCli;

    @Mock
    private GitService gitService;

    @Mock
    private GlobalMetricsService globalMetricsService;

    @Mock
    private KafkaServiceInterface kafkaService;

    @Mock
    private FeastServiceInterface feastService;

    @Mock
    private MultipartFile zipFile;

    private MetricsService metricsService;

    @BeforeEach
    void setUp() {
        metricsService = new MetricsService(
                zipExtractor,
                javaParserExtractor,
                ckMetricsExtractor,
                dependencyGraphExtractor,
                smellDetector,
                pmdSmellDetectorCli,
                gitService,
                globalMetricsService,
                kafkaService,
                feastService
        );
    }

    @Test
    void testAnalyzeProjectWithNullFile() {
        assertThrows(IllegalArgumentException.class, () -> {
            metricsService.analyzeProject(null);
        });
    }

    @Test
    void testAnalyzeProjectWithEmptyFile() {
        when(zipFile.isEmpty()).thenReturn(true);

        assertThrows(IllegalArgumentException.class, () -> {
            metricsService.analyzeProject(zipFile);
        });
    }
}

