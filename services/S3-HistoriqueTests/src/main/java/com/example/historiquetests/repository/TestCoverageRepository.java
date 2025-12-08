package com.example.historiquetests.repository;

import com.example.historiquetests.model.TestCoverage;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface TestCoverageRepository extends JpaRepository<TestCoverage, Long> {
    
    List<TestCoverage> findByCommitSha(String commitSha);
    
    List<TestCoverage> findByRepositoryId(String repositoryId);
    
    List<TestCoverage> findByCommitShaAndRepositoryId(String commitSha, String repositoryId);
    
    Optional<TestCoverage> findByCommitShaAndClassName(String commitSha, String className);
    
    Optional<TestCoverage> findByCommitShaAndClassNameAndRepositoryId(String commitSha, String className, String repositoryId);
    
    List<TestCoverage> findByClassName(String className);
    
    List<TestCoverage> findByClassNameAndRepositoryId(String className, String repositoryId);
    
    @Query("SELECT tc FROM TestCoverage tc WHERE tc.className = :className ORDER BY tc.timestamp DESC")
    List<TestCoverage> findCoverageHistoryByClass(@Param("className") String className);
    
    @Query("SELECT tc FROM TestCoverage tc WHERE tc.className = :className AND tc.repositoryId = :repositoryId ORDER BY tc.timestamp DESC")
    List<TestCoverage> findCoverageHistoryByClassAndRepository(@Param("className") String className, @Param("repositoryId") String repositoryId);
    
    @Query("SELECT tc FROM TestCoverage tc WHERE tc.timestamp BETWEEN :start AND :end ORDER BY tc.timestamp")
    List<TestCoverage> findByTimestampBetween(@Param("start") LocalDateTime start, @Param("end") LocalDateTime end);
    
    @Query("SELECT AVG(tc.lineCoverage) FROM TestCoverage tc WHERE tc.commitSha = :commitSha")
    Double calculateAverageLineCoverageForCommit(@Param("commitSha") String commitSha);
    
    @Query("SELECT AVG(tc.branchCoverage) FROM TestCoverage tc WHERE tc.commitSha = :commitSha")
    Double calculateAverageBranchCoverageForCommit(@Param("commitSha") String commitSha);
    
    @Query("SELECT tc FROM TestCoverage tc WHERE tc.lineCoverage < :threshold ORDER BY tc.lineCoverage")
    List<TestCoverage> findLowCoverageClasses(@Param("threshold") double threshold);
    
    @Query("SELECT tc FROM TestCoverage tc WHERE tc.lineCoverage < :threshold AND tc.repositoryId = :repositoryId ORDER BY tc.lineCoverage")
    List<TestCoverage> findLowCoverageClassesByRepository(@Param("threshold") double threshold, @Param("repositoryId") String repositoryId);
    
    @Query("SELECT tc FROM TestCoverage tc WHERE tc.className = :className AND tc.repositoryId = :repositoryId ORDER BY tc.timestamp DESC LIMIT 1")
    Optional<TestCoverage> findLatestByClassNameAndRepositoryId(@Param("className") String className, @Param("repositoryId") String repositoryId);
}
