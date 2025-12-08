package com.example.historiquetests.service;

import com.example.historiquetests.dto.ArtifactEvent;
import com.example.historiquetests.model.MutationResult;
import com.example.historiquetests.model.TestCoverage;
import com.example.historiquetests.model.TestResult;
import com.example.historiquetests.parser.JaCoCoParser;
import com.example.historiquetests.parser.PITParser;
import com.example.historiquetests.parser.SurefireParser;
import com.example.historiquetests.repository.MutationResultRepository;
import com.example.historiquetests.repository.TestCoverageRepository;
import com.example.historiquetests.repository.TestResultRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.InputStream;
import java.util.List;
import java.util.Map;

/**
 * Service to process artifacts received from Kafka events.
 * Downloads artifacts from MinIO and processes them based on type.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class ArtifactProcessingService {

    private final MinioService minioService;
    private final JaCoCoParser jacocoParser;
    private final SurefireParser surefireParser;
    private final PITParser pitParser;
    private final TestCoverageRepository coverageRepository;
    private final TestResultRepository testResultRepository;
    private final MutationResultRepository mutationResultRepository;
    private final TestDebtService testDebtService;

    /**
     * Process an artifact based on its type
     */
    @Transactional
    public void processArtifact(ArtifactEvent event) throws Exception {
        log.info("Processing artifact: type={}, url={}", event.getArtifactType(), event.getArtifactUrl());
        
        if (event.isJaCoCo()) {
            processJaCoCoArtifact(event);
        } else if (event.isSurefire()) {
            processSurefireArtifact(event);
        } else if (event.isPIT()) {
            processPITArtifact(event);
        } else {
            log.warn("Unknown artifact type: {}", event.getArtifactType());
        }
    }
    
    /**
     * Process JaCoCo coverage report
     */
    private void processJaCoCoArtifact(ArtifactEvent event) throws Exception {
        log.info("Processing JaCoCo artifact for commit: {}", event.getCommitSha());
        
        // Download from MinIO
        InputStream xmlStream = minioService.download(event.getArtifactUrl());
        
        // Parse the report
        List<TestCoverage> coverages = jacocoParser.parseJaCoCoReport(
            xmlStream,
            event.getCommitSha(),
            event.getBuildId(),
            event.getBranch()
        );
        
        // Set repositoryId for all coverage records
        coverages.forEach(c -> c.setRepositoryId(event.getRepositoryId()));
        
        // Save to database
        coverageRepository.saveAll(coverages);
        
        log.info("Saved {} coverage records from JaCoCo for repository {} commit {}", 
                coverages.size(), event.getRepositoryId(), event.getCommitSha());
        
        // Calculate test debt
        testDebtService.calculateTestDebt(event.getCommitSha(), event.getRepositoryId());
    }
    
    /**
     * Process Surefire test results report
     */
    private void processSurefireArtifact(ArtifactEvent event) throws Exception {
        log.info("Processing Surefire artifact for commit: {}", event.getCommitSha());
        
        // Download from MinIO
        InputStream xmlStream = minioService.download(event.getArtifactUrl());
        
        // Parse the report
        List<TestResult> results = surefireParser.parseSurefireReport(
            xmlStream,
            event.getCommitSha(),
            event.getBuildId(),
            event.getBranch()
        );
        
        // Set repositoryId for all test results
        results.forEach(r -> r.setRepositoryId(event.getRepositoryId()));
        
        // Save to database
        testResultRepository.saveAll(results);
        
        log.info("Saved {} test results from Surefire for repository {} commit {}", 
                results.size(), event.getRepositoryId(), event.getCommitSha());
    }
    
    /**
     * Process PIT mutation testing report
     */
    private void processPITArtifact(ArtifactEvent event) throws Exception {
        log.info("Processing PIT artifact for commit: {}", event.getCommitSha());
        
        // Download from MinIO
        InputStream xmlStream = minioService.download(event.getArtifactUrl());
        
        // Parse the report
        List<MutationResult> mutations = pitParser.parsePITReport(
            xmlStream,
            event.getCommitSha()
        );
        
        // Set repositoryId for all mutations
        mutations.forEach(m -> m.setRepositoryId(event.getRepositoryId()));
        
        // Save mutations
        mutationResultRepository.saveAll(mutations);
        
        // Calculate mutation scores and update coverage records
        Map<String, PITParser.MutationSummary> mutationScores = pitParser.calculateMutationScores(mutations);
        List<TestCoverage> coverages = coverageRepository.findByCommitShaAndRepositoryId(
            event.getCommitSha(), event.getRepositoryId());
        pitParser.updateCoverageWithMutations(coverages, mutationScores);
        coverageRepository.saveAll(coverages);
        
        log.info("Saved {} mutations from PIT for repository {} commit {}", 
                mutations.size(), event.getRepositoryId(), event.getCommitSha());
    }
}


