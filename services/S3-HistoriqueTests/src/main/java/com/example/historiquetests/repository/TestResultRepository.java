package com.example.historiquetests.repository;

import com.example.historiquetests.model.TestResult;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface TestResultRepository extends JpaRepository<TestResult, Long> {
    
    List<TestResult> findByCommitSha(String commitSha);
    
    List<TestResult> findByRepositoryId(String repositoryId);
    
    List<TestResult> findByCommitShaAndRepositoryId(String commitSha, String repositoryId);
    
    List<TestResult> findByTestClass(String testClass);
    
    List<TestResult> findByTestClassAndRepositoryId(String testClass, String repositoryId);
    
    List<TestResult> findByTestClassAndTestName(String testClass, String testName);
    
    List<TestResult> findByTestClassAndTestNameAndRepositoryId(String testClass, String testName, String repositoryId);
    
    List<TestResult> findByStatus(TestResult.TestStatus status);
    
    @Query("SELECT tr FROM TestResult tr WHERE tr.testClass = :testClass AND tr.testName = :testName ORDER BY tr.timestamp DESC")
    List<TestResult> findTestHistory(@Param("testClass") String testClass, @Param("testName") String testName);
    
    @Query("SELECT tr FROM TestResult tr WHERE tr.testClass = :testClass AND tr.testName = :testName AND tr.repositoryId = :repositoryId ORDER BY tr.timestamp DESC")
    List<TestResult> findTestHistoryByRepository(@Param("testClass") String testClass, @Param("testName") String testName, @Param("repositoryId") String repositoryId);
    
    @Query("SELECT tr FROM TestResult tr WHERE tr.timestamp BETWEEN :start AND :end ORDER BY tr.timestamp")
    List<TestResult> findByTimestampBetween(@Param("start") LocalDateTime start, @Param("end") LocalDateTime end);
    
    @Query("SELECT COUNT(tr) FROM TestResult tr WHERE tr.commitSha = :commitSha AND tr.status = 'PASSED'")
    long countPassedTests(@Param("commitSha") String commitSha);
    
    @Query("SELECT COUNT(tr) FROM TestResult tr WHERE tr.commitSha = :commitSha AND tr.status = 'FAILED'")
    long countFailedTests(@Param("commitSha") String commitSha);
    
    @Query("SELECT COUNT(tr) FROM TestResult tr WHERE tr.commitSha = :commitSha AND tr.status = 'SKIPPED'")
    long countSkippedTests(@Param("commitSha") String commitSha);
    
    @Query("SELECT COUNT(tr) FROM TestResult tr WHERE tr.commitSha = :commitSha AND tr.repositoryId = :repositoryId AND tr.status = 'PASSED'")
    long countPassedTestsByRepository(@Param("commitSha") String commitSha, @Param("repositoryId") String repositoryId);
    
    @Query("SELECT COUNT(tr) FROM TestResult tr WHERE tr.commitSha = :commitSha AND tr.repositoryId = :repositoryId AND tr.status = 'FAILED'")
    long countFailedTestsByRepository(@Param("commitSha") String commitSha, @Param("repositoryId") String repositoryId);
    
    @Query("SELECT SUM(tr.executionTime) FROM TestResult tr WHERE tr.commitSha = :commitSha")
    Double sumExecutionTimeForCommit(@Param("commitSha") String commitSha);
}
