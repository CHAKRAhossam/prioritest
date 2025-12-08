package com.reco.analysestatiqueservice.service;

import com.reco.analysestatiqueservice.dto.FileScanResult;
import com.reco.analysestatiqueservice.dto.MetricsResponse;
import com.reco.analysestatiqueservice.extractor.*;
import com.reco.analysestatiqueservice.model.ClassMetrics;
import com.reco.analysestatiqueservice.model.DependencyEdge;
import com.reco.analysestatiqueservice.model.SmellResult;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.HashMap;
import java.util.Map;

/**
 * Service responsible for analyzing Java projects and extracting code metrics.
 * Orchestrates the extraction of CK metrics, dependencies, and code smells.
 *
 * @author Reco Team
 */
@Service
public class MetricsService {

    private static final Logger logger = LoggerFactory.getLogger(MetricsService.class);

    private final ZipExtractor zipExtractor;
    private final JavaParserExtractor javaParserExtractor;
    private final CKMetricsExtractor ckMetricsExtractor;
    private final DependencyGraphExtractor dependencyGraphExtractor;
    private final SmellDetector smellDetector;
    private final PMDSmellDetectorCli pmdSmellDetectorCli;

    /**
     * Constructor with dependency injection.
     *
     * @param zipExtractor              Extractor for ZIP files
     * @param javaParserExtractor       Extractor for Java file discovery
     * @param ckMetricsExtractor        Extractor for CK metrics
     * @param dependencyGraphExtractor  Extractor for dependency graph
     * @param smellDetector             Detector for code smells
     */
    public MetricsService(
            ZipExtractor zipExtractor,
            JavaParserExtractor javaParserExtractor,
            CKMetricsExtractor ckMetricsExtractor,
            DependencyGraphExtractor dependencyGraphExtractor,
            SmellDetector smellDetector,
            PMDSmellDetectorCli pmdSmellDetectorCli) {
        this.zipExtractor = zipExtractor;
        this.javaParserExtractor = javaParserExtractor;
        this.ckMetricsExtractor = ckMetricsExtractor;
        this.dependencyGraphExtractor = dependencyGraphExtractor;
        this.smellDetector = smellDetector;
        this.pmdSmellDetectorCli = pmdSmellDetectorCli;
    }

    /**
     * Analyzes a Java project from a ZIP file and extracts all metrics.
     *
     * @param zipFile The ZIP file containing the Java project
     * @return MetricsResponse containing all extracted metrics
     * @throws IllegalArgumentException if the ZIP file is null or empty
     * @throws IOException              if file operations fail
     */
    public MetricsResponse analyzeProject(MultipartFile zipFile) throws IOException {
        if (zipFile == null || zipFile.isEmpty()) {
            logger.error("ZIP file is null or empty");
            throw new IllegalArgumentException("ZIP file cannot be null or empty");
        }

        logger.info("Starting project analysis for file: {}", zipFile.getOriginalFilename());

        File projectDir = null;
        try {
            // Extract ZIP to temporary directory
            projectDir = zipExtractor.extractToTempDir(zipFile);
            logger.debug("Extracted project to temporary directory: {}", projectDir.getAbsolutePath());

            // Discover all Java files
            List<FileScanResult> scannedFiles = javaParserExtractor.listJavaFilesDetailed(projectDir);
            logger.info("Found {} Java files to analyze", scannedFiles.size());

            if (scannedFiles.isEmpty()) {
                logger.warn("No Java files found in the project");
                return createEmptyResponse();
            }

            // Extract metrics for each file
            List<ClassMetrics> metricsList = new ArrayList<>();
            List<DependencyEdge> dependencies = new ArrayList<>();
            List<SmellResult> smellResults = new ArrayList<>();

            for (FileScanResult fs : scannedFiles) {
                File javaFile = new File(fs.getPath());
                logger.debug("Analyzing file: {}", javaFile.getName());

                try {
                    // Extract CK metrics
                    ClassMetrics cm = ckMetricsExtractor.extract(javaFile);
                    if (cm != null) {
                        metricsList.add(cm);
                    }

                    // Extract dependencies
                    List<DependencyEdge> deps = dependencyGraphExtractor.extract(javaFile);
                    dependencies.addAll(deps);

                    // Detect smells (custom)
                    List<SmellResult> smells = smellDetector.detect(javaFile);
                    smellResults.addAll(smells);
                    // Detect smells (PMD CLI)
                    List<SmellResult> pmdSmells = pmdSmellDetectorCli.detect(javaFile);
                    smellResults.addAll(pmdSmells);
                } catch (Exception e) {
                    logger.error("Error analyzing file: {}", javaFile.getAbsolutePath(), e);
                    // Continue with other files even if one fails
                }
            }

            // Build response
            MetricsResponse response = new MetricsResponse();
            response.setClasses(metricsList);
            response.setDependencies(dependencies);
            response.setSmells(smellResults);
            response.setFiles(scannedFiles);
            response.setNbClasses(metricsList.size());
            response.setNbDependencies(dependencies.size());
            response.setNbSmells(smellResults.size());
            response.setNbFiles(scannedFiles.size());

            Map<String, Object> smellThresholds = new HashMap<>();
            smellThresholds.put("godClassLocThreshold", smellDetector.godClassLocThreshold);
            smellThresholds.put("godClassWmcThreshold", smellDetector.godClassWmcThreshold);
            smellThresholds.put("godClassCboThreshold", smellDetector.godClassCboThreshold);
            smellThresholds.put("longMethodLocThreshold", smellDetector.longMethodLocThreshold);
            smellThresholds.put("longParameterListThreshold", smellDetector.longParameterListThreshold);
            smellThresholds.put("dataClassMethodThreshold", smellDetector.dataClassMethodThreshold);
            smellThresholds.put("featureEnvyRatioThreshold", smellDetector.featureEnvyRatioThreshold);
            response.setSmellThresholds(smellThresholds);

            logger.info("Analysis completed. Classes: {}, Dependencies: {}, Smells: {}",
                    metricsList.size(), dependencies.size(), smellResults.size());

            return response;

        } finally {
            // Clean up temporary directory
            if (projectDir != null && projectDir.exists()) {
                cleanupTempDirectory(projectDir.toPath());
            }
        }
    }

    /**
     * Creates an empty response when no Java files are found.
     *
     * @return Empty MetricsResponse
     */
    private MetricsResponse createEmptyResponse() {
        MetricsResponse response = new MetricsResponse();
        response.setClasses(new ArrayList<>());
        response.setDependencies(new ArrayList<>());
        response.setSmells(new ArrayList<>());
        response.setFiles(new ArrayList<>());
        response.setNbClasses(0);
        response.setNbDependencies(0);
        response.setNbSmells(0);
        response.setNbFiles(0);
        return response;
    }

    /**
     * Recursively deletes a temporary directory and its contents.
     *
     * @param tempDir Path to the temporary directory
     */
    private void cleanupTempDirectory(Path tempDir) {
        try {
            if (Files.exists(tempDir)) {
                Files.walk(tempDir)
                        .sorted((a, b) -> b.compareTo(a)) // Delete files before directories
                        .forEach(path -> {
                            try {
                                Files.delete(path);
                            } catch (IOException e) {
                                logger.warn("Failed to delete temporary file: {}", path, e);
                            }
                        });
                logger.debug("Cleaned up temporary directory: {}", tempDir);
            }
        } catch (IOException e) {
            logger.error("Error cleaning up temporary directory: {}", tempDir, e);
        }
    }
}
