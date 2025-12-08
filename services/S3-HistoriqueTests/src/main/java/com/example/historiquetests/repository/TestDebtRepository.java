package com.example.historiquetests.repository;

import com.example.historiquetests.model.TestDebt;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface TestDebtRepository extends JpaRepository<TestDebt, Long> {
    
    List<TestDebt> findByCommitSha(String commitSha);
    
    List<TestDebt> findByRepositoryId(String repositoryId);
    
    List<TestDebt> findByCommitShaAndRepositoryId(String commitSha, String repositoryId);
    
    Optional<TestDebt> findByCommitShaAndClassName(String commitSha, String className);
    
    Optional<TestDebt> findByCommitShaAndClassNameAndRepositoryId(String commitSha, String className, String repositoryId);
    
    @Query("SELECT td FROM TestDebt td WHERE td.commitSha = :commitSha ORDER BY td.debtScore DESC")
    List<TestDebt> findByCommitShaOrderedByDebt(@Param("commitSha") String commitSha);
    
    @Query("SELECT td FROM TestDebt td WHERE td.debtScore > :threshold ORDER BY td.debtScore DESC")
    List<TestDebt> findHighDebtClasses(@Param("threshold") double threshold);
    
    @Query("SELECT td FROM TestDebt td WHERE td.debtScore > :threshold AND td.repositoryId = :repositoryId ORDER BY td.debtScore DESC")
    List<TestDebt> findHighDebtClassesByRepository(@Param("threshold") double threshold, @Param("repositoryId") String repositoryId);
    
    @Query("SELECT AVG(td.debtScore) FROM TestDebt td WHERE td.commitSha = :commitSha")
    Double calculateAverageDebtForCommit(@Param("commitSha") String commitSha);
    
    @Query("SELECT td FROM TestDebt td WHERE td.className = :className AND td.repositoryId = :repositoryId ORDER BY td.calculatedAt DESC LIMIT 1")
    Optional<TestDebt> findLatestByClassNameAndRepositoryId(@Param("className") String className, @Param("repositoryId") String repositoryId);
}


