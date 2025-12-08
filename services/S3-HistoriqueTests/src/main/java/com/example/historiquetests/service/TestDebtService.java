package com.example.historiquetests.service;

import com.example.historiquetests.model.TestCoverage;
import com.example.historiquetests.model.TestDebt;
import com.example.historiquetests.repository.TestCoverageRepository;
import com.example.historiquetests.repository.TestDebtRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class TestDebtService {

    private final TestDebtRepository testDebtRepository;
    private final TestCoverageRepository testCoverageRepository;
    
    // Coverage targets
    private static final double TARGET_LINE_COVERAGE = 80.0;
    private static final double TARGET_BRANCH_COVERAGE = 75.0;
    private static final double TARGET_MUTATION_SCORE = 70.0;
    
    /**
     * Calculate test debt for all classes in a commit
     */
    public List<TestDebt> calculateTestDebt(String commitSha) {
        return calculateTestDebt(commitSha, null);
    }
    
    /**
     * Calculate test debt for all classes in a commit for a specific repository
     */
    public List<TestDebt> calculateTestDebt(String commitSha, String repositoryId) {
        log.info("Calculating test debt for commit: {}, repository: {}", commitSha, repositoryId);
        
        List<TestCoverage> coverages;
        if (repositoryId != null) {
            coverages = testCoverageRepository.findByCommitShaAndRepositoryId(commitSha, repositoryId);
        } else {
            coverages = testCoverageRepository.findByCommitSha(commitSha);
        }
        
        List<TestDebt> debts = new ArrayList<>();
        
        for (TestCoverage coverage : coverages) {
            TestDebt debt = calculateClassDebt(coverage);
            debts.add(debt);
        }
        
        // Save all debt records
        List<TestDebt> saved = testDebtRepository.saveAll(debts);
        
        log.info("Calculated test debt for {} classes", saved.size());
        return saved;
    }
    
    private TestDebt calculateClassDebt(TestCoverage coverage) {
        TestDebt debt = new TestDebt();
        debt.setRepositoryId(coverage.getRepositoryId());
        debt.setCommitSha(coverage.getCommitSha());
        debt.setClassName(coverage.getClassName());
        
        // Calculate coverage deficit
        double lineCoverageDeficit = Math.max(0, TARGET_LINE_COVERAGE - coverage.getLineCoverage());
        double branchCoverageDeficit = Math.max(0, TARGET_BRANCH_COVERAGE - coverage.getBranchCoverage());
        debt.setCoverageDeficit((lineCoverageDeficit + branchCoverageDeficit) / 2);
        
        debt.setUncoveredLines(coverage.getLinesMissed());
        debt.setUncoveredBranches(coverage.getBranchesMissed());
        debt.setUncoveredMethods(coverage.getMethodsMissed());
        
        // Calculate mutation deficit
        double mutationScore = coverage.getMutationScore() != null ? coverage.getMutationScore() : 0.0;
        double mutationDeficit = Math.max(0, TARGET_MUTATION_SCORE - mutationScore);
        debt.setMutationDeficit(mutationDeficit);
        debt.setSurvivedMutants(coverage.getMutationsSurvived() != null ? coverage.getMutationsSurvived() : 0);
        
        // Calculate overall debt score (0-100, higher = worse)
        double debtScore = calculateDebtScore(
            lineCoverageDeficit,
            branchCoverageDeficit,
            mutationDeficit,
            coverage.getLinesMissed(),
            coverage.getMutationsSurvived() != null ? coverage.getMutationsSurvived() : 0
        );
        debt.setDebtScore(debtScore);
        
        // Generate recommendations
        debt.setRecommendations(generateRecommendations(coverage, debt));
        
        return debt;
    }
    
    private double calculateDebtScore(double lineCoverageDeficit, 
                                     double branchCoverageDeficit,
                                     double mutationDeficit,
                                     int uncoveredLines,
                                     int survivedMutants) {
        // Weighted scoring
        double coverageScore = (lineCoverageDeficit * 0.4) + (branchCoverageDeficit * 0.3);
        double mutationScoreCalc = mutationDeficit * 0.2;
        double volumeScore = Math.min(10.0, uncoveredLines / 10.0); // Max 10 points for volume
        double mutantScore = Math.min(10.0, survivedMutants / 5.0); // Max 10 points for survived mutants
        
        return Math.min(100.0, coverageScore + mutationScoreCalc + volumeScore + mutantScore);
    }
    
    private String generateRecommendations(TestCoverage coverage, TestDebt debt) {
        List<String> recommendations = new ArrayList<>();
        
        if (coverage.getLineCoverage() < TARGET_LINE_COVERAGE) {
            recommendations.add(String.format(
                "Add tests to improve line coverage from %.1f%% to %.1f%% (add %d line(s))",
                coverage.getLineCoverage(), TARGET_LINE_COVERAGE, debt.getUncoveredLines()
            ));
        }
        
        if (coverage.getBranchCoverage() < TARGET_BRANCH_COVERAGE) {
            recommendations.add(String.format(
                "Add tests for conditional logic - branch coverage is %.1f%%, target is %.1f%%",
                coverage.getBranchCoverage(), TARGET_BRANCH_COVERAGE
            ));
        }
        
        if (coverage.getMutationScore() != null && coverage.getMutationScore() < TARGET_MUTATION_SCORE) {
            recommendations.add(String.format(
                "Strengthen test assertions - %d mutants survived (mutation score: %.1f%%)",
                debt.getSurvivedMutants(), coverage.getMutationScore()
            ));
        }
        
        if (coverage.getMethodsMissed() > 0) {
            recommendations.add(String.format(
                "Add tests for %d untested method(s)",
                coverage.getMethodsMissed()
            ));
        }
        
        if (recommendations.isEmpty()) {
            recommendations.add("Good test coverage! Consider maintaining current quality.");
        }
        
        return String.join("; ", recommendations);
    }
    
    /**
     * Get test debt summary for a commit
     */
    public DebtSummary getDebtSummary(String commitSha) {
        List<TestDebt> debts = testDebtRepository.findByCommitSha(commitSha);
        
        DebtSummary summary = new DebtSummary();
        summary.commitSha = commitSha;
        summary.totalClasses = debts.size();
        
        if (!debts.isEmpty()) {
            summary.averageDebtScore = debts.stream()
                .mapToDouble(TestDebt::getDebtScore)
                .average()
                .orElse(0.0);
            
            summary.highDebtClasses = debts.stream()
                .filter(d -> d.getDebtScore() > 50)
                .count();
            
            summary.totalUncoveredLines = debts.stream()
                .mapToInt(TestDebt::getUncoveredLines)
                .sum();
            
            summary.totalSurvivedMutants = debts.stream()
                .mapToInt(TestDebt::getSurvivedMutants)
                .sum();
        }
        
        return summary;
    }
    
    /**
     * Get classes with highest debt
     */
    public List<TestDebt> getHighDebtClasses(double threshold) {
        return testDebtRepository.findHighDebtClasses(threshold);
    }
    
    public static class DebtSummary {
        public String commitSha;
        public int totalClasses;
        public double averageDebtScore;
        public long highDebtClasses;
        public int totalUncoveredLines;
        public int totalSurvivedMutants;
    }
}
