package com.example.historiquetests.repository;

import com.example.historiquetests.model.ClassTestMap;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ClassTestMapRepository extends JpaRepository<ClassTestMap, Long> {
    
    List<ClassTestMap> findByCommitSha(String commitSha);
    
    List<ClassTestMap> findByClassName(String className);
    
    List<ClassTestMap> findByTestName(String testName);
    
    @Query("SELECT ctm FROM ClassTestMap ctm WHERE ctm.className = :className ORDER BY ctm.coveragePercent DESC")
    List<ClassTestMap> findTestsCoveringClass(@Param("className") String className);
    
    @Query("SELECT ctm FROM ClassTestMap ctm WHERE ctm.testName = :testName ORDER BY ctm.coveragePercent DESC")
    List<ClassTestMap> findClassesCoveredByTest(@Param("testName") String testName);
    
    @Query("SELECT DISTINCT ctm.className FROM ClassTestMap ctm WHERE ctm.testName = :testName")
    List<String> findClassNamesCoveredByTest(@Param("testName") String testName);
    
    @Query("SELECT DISTINCT ctm.testName FROM ClassTestMap ctm WHERE ctm.className = :className")
    List<String> findTestNamesCoveringClass(@Param("className") String className);
}
