package com.example.historiquetests.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "test_debt", indexes = {
    @Index(name = "idx_debt_class", columnList = "className"),
    @Index(name = "idx_debt_commit", columnList = "commitSha"),
    @Index(name = "idx_debt_score", columnList = "debtScore"),
    @Index(name = "idx_debt_repository", columnList = "repositoryId")
})
@Data
@NoArgsConstructor
public class TestDebt {
    
    @Id 
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String repositoryId;
    
    @Column(nullable = false)
    private String commitSha;
    
    @Column(nullable = false)
    private String className;
    
    // Test debt indicators
    private double coverageDeficit; // % below target (e.g., if target is 80%, class at 60% has 20% deficit)
    private int uncoveredLines;
    private int uncoveredBranches;
    private int uncoveredMethods;
    
    // Mutation testing debt
    private double mutationDeficit;
    private int survivedMutants;
    
    // Flakiness debt
    private double flakinessImpact; // weighted by test importance
    private int flakyTestCount;
    
    // Missing tests
    private int publicMethodsWithoutTests;
    
    // Overall debt score (0-100, higher = more debt)
    private double debtScore;
    
    @Column(columnDefinition = "TEXT")
    private String recommendations;
    
    @Column(nullable = false, updatable = false)
    private LocalDateTime calculatedAt = LocalDateTime.now();
}


