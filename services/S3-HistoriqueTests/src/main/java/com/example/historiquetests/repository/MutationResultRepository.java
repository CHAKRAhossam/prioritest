package com.example.historiquetests.repository;

import com.example.historiquetests.model.MutationResult;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface MutationResultRepository extends JpaRepository<MutationResult, Long> {
    
    List<MutationResult> findByCommitSha(String commitSha);
    
    List<MutationResult> findByClassName(String className);
    
    List<MutationResult> findByCommitShaAndClassName(String commitSha, String className);
    
    @Query("SELECT mr FROM MutationResult mr WHERE mr.className = :className AND mr.repositoryId = :repositoryId")
    List<MutationResult> findByClassNameAndRepositoryId(
        @Param("className") String className,
        @Param("repositoryId") String repositoryId
    );
    
    List<MutationResult> findByStatus(MutationResult.MutationStatus status);
    
    @Query("SELECT mr FROM MutationResult mr WHERE mr.commitSha = :commitSha AND mr.status = :status")
    List<MutationResult> findByCommitShaAndStatus(
        @Param("commitSha") String commitSha, 
        @Param("status") MutationResult.MutationStatus status
    );
    
    @Query("SELECT COUNT(mr) FROM MutationResult mr WHERE mr.commitSha = :commitSha AND mr.status = 'SURVIVED'")
    long countSurvivedMutations(@Param("commitSha") String commitSha);
    
    @Query("SELECT COUNT(mr) FROM MutationResult mr WHERE mr.commitSha = :commitSha AND mr.status = 'KILLED'")
    long countKilledMutations(@Param("commitSha") String commitSha);
}


