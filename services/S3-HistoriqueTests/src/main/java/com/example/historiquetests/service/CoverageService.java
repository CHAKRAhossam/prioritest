package com.example.historiquetests.service;

import com.example.historiquetests.model.TestCoverage;
import com.example.historiquetests.parser.JaCoCoParser;
import com.example.historiquetests.parser.PITParser;
import com.example.historiquetests.repository.TestCoverageRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
@Slf4j
public class CoverageService {

    private final TestCoverageRepository coverageRepository;
    private final MinioService minioService;
    private final JaCoCoParser jacocoParser;
    private final PITParser pitParser;

    /**
     * Process JaCoCo XML report and store coverage data
     */
    public List<TestCoverage> processJaCoCoReport(MultipartFile xmlFile, String commitSha, String buildId, String branch) throws Exception {
        return processJaCoCoReport(xmlFile, commitSha, buildId, branch, "default");
    }
    
    /**
     * Process JaCoCo XML report and store coverage data with repositoryId
     */
    public List<TestCoverage> processJaCoCoReport(MultipartFile xmlFile, String commitSha, String buildId, String branch, String repositoryId) throws Exception {
        log.info("Processing JaCoCo report for commit: {}, repository: {}", commitSha, repositoryId);
        
        // Upload raw file for archival
        minioService.upload(repositoryId + "/" + commitSha + "/jacoco.xml", xmlFile);
        
        // Parse the report
        List<TestCoverage> coverages = jacocoParser.parseJaCoCoReport(
            xmlFile.getInputStream(), 
            commitSha, 
            buildId, 
            branch,
            repositoryId
        );
        
        // Save all coverage data
        List<TestCoverage> saved = coverageRepository.saveAll(coverages);
        
        log.info("Saved {} coverage records for commit {} in repository {}", saved.size(), commitSha, repositoryId);
        return saved;
    }
    
    /**
     * Process PIT mutation report and update coverage data with mutation scores
     */
    public void processPITReport(MultipartFile xmlFile, String commitSha) throws Exception {
        processPITReport(xmlFile, commitSha, "default");
    }
    
    /**
     * Process PIT mutation report and update coverage data with mutation scores with repositoryId
     */
    public void processPITReport(MultipartFile xmlFile, String commitSha, String repositoryId) throws Exception {
        log.info("Processing PIT mutation report for commit: {}, repository: {}", commitSha, repositoryId);
        
        // Upload raw file
        minioService.upload(repositoryId + "/" + commitSha + "/pit-mutations.xml", xmlFile);
        
        // Parse mutations
        var mutations = pitParser.parsePITReport(xmlFile.getInputStream(), commitSha, repositoryId);
        
        // Calculate mutation scores per class
        Map<String, PITParser.MutationSummary> mutationScores = pitParser.calculateMutationScores(mutations);
        
        // Update existing coverage records with mutation data
        List<TestCoverage> coverages = coverageRepository.findByCommitShaAndRepositoryId(commitSha, repositoryId);
        pitParser.updateCoverageWithMutations(coverages, mutationScores);
        coverageRepository.saveAll(coverages);
        
        log.info("Updated coverage with mutation scores for {} classes", mutationScores.size());
    }
    
    /**
     * Get coverage summary for a commit
     */
    public CoverageSummary getCoverageSummary(String commitSha) {
        List<TestCoverage> coverages = coverageRepository.findByCommitSha(commitSha);
        
        CoverageSummary summary = new CoverageSummary();
        summary.commitSha = commitSha;
        summary.totalClasses = coverages.size();
        
        if (!coverages.isEmpty()) {
            summary.averageLineCoverage = coverages.stream()
                .mapToDouble(TestCoverage::getLineCoverage)
                .average()
                .orElse(0.0);
            
            summary.averageBranchCoverage = coverages.stream()
                .mapToDouble(TestCoverage::getBranchCoverage)
                .average()
                .orElse(0.0);
            
            summary.averageMutationScore = coverages.stream()
                .filter(c -> c.getMutationScore() != null)
                .mapToDouble(TestCoverage::getMutationScore)
                .average()
                .orElse(0.0);
            
            summary.totalLines = coverages.stream()
                .mapToInt(c -> c.getLinesCovered() + c.getLinesMissed())
                .sum();
            
            summary.coveredLines = coverages.stream()
                .mapToInt(TestCoverage::getLinesCovered)
                .sum();
        }
        
        return summary;
    }
    
    /**
     * Get coverage history for a specific class
     */
    public List<TestCoverage> getCoverageHistory(String className) {
        return coverageRepository.findCoverageHistoryByClass(className);
    }
    
    /**
     * Get coverage history by repository and branch
     */
    public List<TestCoverage> getCoverageHistoryByRepositoryAndBranch(String repositoryId, String branch) {
        return coverageRepository.findCoverageHistoryByRepositoryAndBranch(repositoryId, branch);
    }
    
    /**
     * Find classes with low coverage
     */
    public List<TestCoverage> findLowCoverageClasses(double threshold) {
        return coverageRepository.findLowCoverageClasses(threshold);
    }
    
    /**
     * DTO for coverage summary
     */
    public static class CoverageSummary {
        public String commitSha;
        public int totalClasses;
        public double averageLineCoverage;
        public double averageBranchCoverage;
        public double averageMutationScore;
        public int totalLines;
        public int coveredLines;
    }
}
