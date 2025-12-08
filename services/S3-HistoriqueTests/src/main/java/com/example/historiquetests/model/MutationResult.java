package com.example.historiquetests.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "mutation_result", indexes = {
    @Index(name = "idx_mutation_class", columnList = "className"),
    @Index(name = "idx_mutation_commit", columnList = "commitSha"),
    @Index(name = "idx_mutation_repository", columnList = "repositoryId")
})
@Data
@NoArgsConstructor
public class MutationResult {
    
    @Id 
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String repositoryId;
    
    @Column(nullable = false)
    private String commitSha;
    
    @Column(nullable = false)
    private String className;
    
    private String methodName;
    private int lineNumber;
    
    // Mutation details
    private String mutator;
    
    @Column(columnDefinition = "TEXT")
    private String mutationDescription;
    
    @Enumerated(EnumType.STRING)
    private MutationStatus status;
    
    // Test that killed the mutation (if killed)
    private String killingTest;
    
    @Column(nullable = false, updatable = false)
    private LocalDateTime timestamp = LocalDateTime.now();
    
    public enum MutationStatus {
        KILLED,      // Mutation detected by tests (good)
        SURVIVED,    // Mutation not detected (bad - test gap)
        NO_COVERAGE, // No tests cover this code
        TIMED_OUT,   // Test ran too long
        NON_VIABLE,  // Mutation doesn't compile
        MEMORY_ERROR,
        RUN_ERROR
    }
}


