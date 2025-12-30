package com.example.historiquetests.repository;

import com.example.historiquetests.model.TestFlakiness;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface TestFlakinessRepository extends JpaRepository<TestFlakiness, Long> {
    
    Optional<TestFlakiness> findByTestClassAndTestName(String testClass, String testName);
    
    Optional<TestFlakiness> findByTestClassAndTestNameAndRepositoryId(String testClass, String testName, String repositoryId);
    
    List<TestFlakiness> findByFlakinessScoreGreaterThan(double threshold);
    
    @Query("SELECT tf FROM TestFlakiness tf ORDER BY tf.flakinessScore DESC")
    List<TestFlakiness> findMostFlakyTests();
    
    @Query("SELECT tf FROM TestFlakiness tf WHERE tf.flakinessScore > :threshold ORDER BY tf.flakinessScore DESC")
    List<TestFlakiness> findFlakyTestsAboveThreshold(@Param("threshold") double threshold);
}


