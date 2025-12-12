package com.reco.analysestatiqueservice.service;

import com.reco.analysestatiqueservice.dto.*;
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
import java.util.*;
import java.util.stream.Collectors;

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
    private final GitService gitService;
    private final GlobalMetricsService globalMetricsService;
    private final KafkaServiceInterface kafkaService;
    private final FeastServiceInterface feastService;

    /**
     * Constructor with dependency injection.
     *
     * @param zipExtractor              Extractor for ZIP files
     * @param javaParserExtractor       Extractor for Java file discovery
     * @param ckMetricsExtractor        Extractor for CK metrics
     * @param dependencyGraphExtractor  Extractor for dependency graph
     * @param smellDetector             Detector for code smells
     * @param gitService                Service for Git operations
     * @param globalMetricsService      Service for global metrics (NOC, in/out degree)
     * @param kafkaService              Service for Kafka publishing
     * @param feastService              Service for Feast publishing
     */
    public MetricsService(
            ZipExtractor zipExtractor,
            JavaParserExtractor javaParserExtractor,
            CKMetricsExtractor ckMetricsExtractor,
            DependencyGraphExtractor dependencyGraphExtractor,
            SmellDetector smellDetector,
            PMDSmellDetectorCli pmdSmellDetectorCli,
            GitService gitService,
            GlobalMetricsService globalMetricsService,
            KafkaServiceInterface kafkaService,
            FeastServiceInterface feastService) {
        this.zipExtractor = zipExtractor;
        this.javaParserExtractor = javaParserExtractor;
        this.ckMetricsExtractor = ckMetricsExtractor;
        this.dependencyGraphExtractor = dependencyGraphExtractor;
        this.smellDetector = smellDetector;
        this.pmdSmellDetectorCli = pmdSmellDetectorCli;
        this.gitService = gitService;
        this.globalMetricsService = globalMetricsService;
        this.kafkaService = kafkaService;
        this.feastService = feastService;
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
    
    /**
     * Processes a commit event from Kafka.
     * Clones the repository, analyzes changed files, and publishes metrics.
     *
     * @param event The commit event from Kafka
     */
    public void processCommitEvent(CommitEvent event) {
        logger.info("Processing commit event: {} for repository: {} at commit: {}", 
                event.getEventId(), event.getRepositoryId(), event.getCommitSha());
        
        File repoDir = null;
        try {
            // TODO: Get repository URL from repository_id (would need a repository service)
            // For now, we'll assume the repository URL is provided or stored
            String repositoryUrl = "https://github.com/" + event.getRepositoryId() + ".git";
            
            // Clone repository and checkout commit
            repoDir = gitService.cloneAndCheckout(repositoryUrl, event.getCommitSha());
            
            // Analyze changed files
            List<FileScanResult> filesToAnalyze = new ArrayList<>();
            for (CommitEvent.FileChanged fileChanged : event.getFilesChanged()) {
                if ("deleted".equals(fileChanged.getStatus())) {
                    continue; // Skip deleted files
                }
                
                File file = new File(repoDir, fileChanged.getPath());
                if (file.exists() && fileChanged.getPath().endsWith(".java")) {
                    filesToAnalyze.add(new FileScanResult(fileChanged.getPath(), file.getAbsolutePath()));
                }
            }
            
            if (filesToAnalyze.isEmpty()) {
                logger.warn("No Java files to analyze in commit event: {}", event.getEventId());
                return;
            }
            
            // Extract metrics for all files first
            List<ClassMetrics> allMetrics = new ArrayList<>();
            Map<String, List<DependencyEdge>> allDependencies = new HashMap<>();
            Map<String, List<SmellResult>> allSmells = new HashMap<>();
            
            for (FileScanResult fs : filesToAnalyze) {
                File javaFile = new File(fs.getPath());
                try {
                    ClassMetrics cm = ckMetricsExtractor.extract(javaFile);
                    if (cm != null) {
                        allMetrics.add(cm);
                        allDependencies.put(cm.getClassName(), dependencyGraphExtractor.extract(javaFile));
                        allSmells.put(cm.getClassName(), new ArrayList<>());
                        allSmells.get(cm.getClassName()).addAll(smellDetector.detect(javaFile));
                        allSmells.get(cm.getClassName()).addAll(pmdSmellDetectorCli.detect(javaFile));
                    }
                } catch (Exception e) {
                    logger.error("Error analyzing file: {}", javaFile.getAbsolutePath(), e);
                }
            }
            
            // Calculate global metrics (NOC, in/out degree)
            Map<String, Integer> nocMap = globalMetricsService.calculateNOC(repoDir, allMetrics);
            Map<String, GlobalMetricsService.DependencyDegrees> degreesMap = 
                    globalMetricsService.calculateDependencyDegrees(repoDir, allMetrics);
            
            // Update metrics with global values
            for (ClassMetrics cm : allMetrics) {
                String fqn = getFullyQualifiedName(cm);
                cm.setNoc(nocMap.getOrDefault(fqn, 0));
                
                GlobalMetricsService.DependencyDegrees degrees = degreesMap.get(fqn);
                if (degrees != null) {
                    cm.setDependenciesIn(Collections.singletonList(String.valueOf(degrees.getInDegree())));
                    cm.setDependenciesOut(allDependencies.getOrDefault(cm.getClassName(), Collections.emptyList())
                            .stream().map(DependencyEdge::getToClass).collect(Collectors.toList()));
                }
            }
            
            // Publish metrics for each class
            for (ClassMetrics cm : allMetrics) {
                CodeMetricsEvent codeMetricsEvent = buildCodeMetricsEvent(event, cm, allSmells.get(cm.getClassName()));
                kafkaService.publishCodeMetrics(codeMetricsEvent);
                feastService.publishToFeast(codeMetricsEvent);
            }
            
            logger.info("Processed {} classes from commit event: {}", allMetrics.size(), event.getEventId());
            
        } catch (Exception e) {
            logger.error("Error processing commit event: {}", event.getEventId(), e);
        } finally {
            // Cleanup repository directory (optional - could keep for caching)
            // gitService.cleanup(repoDir);
        }
    }
    
    /**
     * Builds CodeMetricsEvent from ClassMetrics.
     * Aligned with architecture specification format.
     */
    private CodeMetricsEvent buildCodeMetricsEvent(
            CommitEvent commitEvent, 
            ClassMetrics classMetrics, 
            List<SmellResult> smells) {
        
        CodeMetricsEvent event = new CodeMetricsEvent();
        // Generate unique event ID for metrics event (different from commit event)
        event.setEventId("evt_" + System.currentTimeMillis() + "_" + classMetrics.getClassName().hashCode());
        event.setTimestamp(java.time.Instant.now().toString()); // ISO-8601 format
        event.setRepositoryId(commitEvent.getRepositoryId());
        event.setCommitSha(commitEvent.getCommitSha());
        event.setClassName(classMetrics.getClassName());
        event.setFilePath(classMetrics.getFilePath());
        
        CodeMetricsEvent.Metrics metrics = new CodeMetricsEvent.Metrics();
        metrics.setLoc(classMetrics.getLoc());
        metrics.setCyclomaticComplexity(classMetrics.getWmc()); // WMC approximates cyclomatic complexity
        
        CodeMetricsEvent.CKMetrics ckMetrics = new CodeMetricsEvent.CKMetrics();
        ckMetrics.setWmc(classMetrics.getWmc());
        ckMetrics.setDit(classMetrics.getDit());
        ckMetrics.setNoc(classMetrics.getNoc());
        ckMetrics.setCbo(classMetrics.getCbo());
        ckMetrics.setRfc(classMetrics.getRfc());
        ckMetrics.setLcom(classMetrics.getLcom());
        metrics.setCkMetrics(ckMetrics);
        
        CodeMetricsEvent.Dependencies dependencies = new CodeMetricsEvent.Dependencies();
        if (classMetrics.getDependenciesIn() != null && !classMetrics.getDependenciesIn().isEmpty()) {
            dependencies.setInDegree(Integer.parseInt(classMetrics.getDependenciesIn().get(0)));
        } else {
            dependencies.setInDegree(0);
        }
        dependencies.setOutDegree(classMetrics.getDependenciesOut() != null ? 
                classMetrics.getDependenciesOut().size() : 0);
        dependencies.setDependenciesList(classMetrics.getDependenciesOut() != null ? 
                classMetrics.getDependenciesOut() : Collections.emptyList());
        metrics.setDependencies(dependencies);
        
        List<CodeMetricsEvent.CodeSmell> codeSmells = smells != null ? 
                smells.stream().map(s -> {
                    CodeMetricsEvent.CodeSmell smell = new CodeMetricsEvent.CodeSmell();
                    smell.setType(s.getSmellType());
                    smell.setSeverity("medium"); // Could be calculated based on metrics
                    smell.setLine(s.getLine());
                    return smell;
                }).collect(Collectors.toList()) : Collections.emptyList();
        metrics.setCodeSmells(codeSmells);
        
        event.setMetrics(metrics);
        return event;
    }
    
    /**
     * Gets fully qualified name from ClassMetrics.
     */
    private String getFullyQualifiedName(ClassMetrics metrics) {
        String filePath = metrics.getFilePath();
        if (filePath.contains("src/main/java/")) {
            int startIdx = filePath.indexOf("src/main/java/") + "src/main/java/".length();
            int endIdx = filePath.lastIndexOf("/");
            if (endIdx > startIdx) {
                String packagePath = filePath.substring(startIdx, endIdx);
                return packagePath.replace("/", ".").replace("\\", ".") + "." + metrics.getClassName();
            }
        }
        return metrics.getClassName();
    }
}
