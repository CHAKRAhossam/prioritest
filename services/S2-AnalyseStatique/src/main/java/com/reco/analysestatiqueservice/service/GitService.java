package com.reco.analysestatiqueservice.service;

import org.eclipse.jgit.api.Git;
import org.eclipse.jgit.api.errors.GitAPIException;
import org.eclipse.jgit.lib.Repository;
import org.eclipse.jgit.revwalk.RevCommit;
import org.eclipse.jgit.storage.file.FileRepositoryBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Service for Git operations: cloning repositories and checking out specific commits.
 */
@Service
public class GitService {
    
    private static final Logger logger = LoggerFactory.getLogger(GitService.class);
    
    @Value("${git.temp.dir:./temp-repos}")
    private String tempReposDir;
    
    /**
     * Clones a repository and checks out a specific commit.
     * 
     * @param repositoryUrl The Git repository URL
     * @param commitSha The commit SHA to checkout
     * @return The local directory path where the repository was cloned
     * @throws GitAPIException if Git operations fail
     * @throws IOException if file operations fail
     */
    public File cloneAndCheckout(String repositoryUrl, String commitSha) throws GitAPIException, IOException {
        logger.info("Cloning repository {} at commit {}", repositoryUrl, commitSha);
        
        // Create temp directory for this clone
        Path tempDir = Path.of(tempReposDir, sanitizeRepoName(repositoryUrl), commitSha.substring(0, 7));
        Files.createDirectories(tempDir.getParent());
        
        // If directory already exists, reuse it
        File repoDir = tempDir.toFile();
        if (repoDir.exists() && new File(repoDir, ".git").exists()) {
            logger.debug("Repository already cloned at: {}", repoDir.getAbsolutePath());
            try (Git git = Git.open(repoDir)) {
                git.checkout().setName(commitSha).call();
                return repoDir;
            }
        }
        
        // Clone repository
        try (Git git = Git.cloneRepository()
                .setURI(repositoryUrl)
                .setDirectory(repoDir)
                .setCloneAllBranches(false)
                .call()) {
            
            logger.debug("Repository cloned to: {}", repoDir.getAbsolutePath());
            
            // Checkout specific commit
            git.checkout().setName(commitSha).call();
            logger.info("Checked out commit: {}", commitSha);
            
            return repoDir;
        }
    }
    
    /**
     * Gets repository information from a local directory.
     * 
     * @param repoDir The repository directory
     * @return Repository object
     * @throws IOException if repository cannot be opened
     */
    public Repository openRepository(File repoDir) throws IOException {
        FileRepositoryBuilder builder = new FileRepositoryBuilder();
        return builder
                .setGitDir(new File(repoDir, ".git"))
                .readEnvironment()
                .findGitDir()
                .build();
    }
    
    /**
     * Gets commit information.
     * 
     * @param repoDir The repository directory
     * @param commitSha The commit SHA
     * @return RevCommit object
     * @throws IOException if repository cannot be opened
     * @throws GitAPIException if Git operations fail
     */
    public RevCommit getCommit(File repoDir, String commitSha) throws IOException, GitAPIException {
        try (Repository repo = openRepository(repoDir);
             Git git = new Git(repo)) {
            return git.log().add(repo.resolve(commitSha)).setMaxCount(1).call().iterator().next();
        }
    }
    
    /**
     * Sanitizes repository name for use in file paths.
     */
    private String sanitizeRepoName(String repoUrl) {
        // Extract repo name from URL
        String name = repoUrl;
        if (name.contains("/")) {
            name = name.substring(name.lastIndexOf("/") + 1);
        }
        if (name.endsWith(".git")) {
            name = name.substring(0, name.length() - 4);
        }
        // Remove invalid characters
        return name.replaceAll("[^a-zA-Z0-9_-]", "_");
    }
    
    /**
     * Cleans up temporary repository directory.
     */
    public void cleanup(File repoDir) {
        if (repoDir != null && repoDir.exists()) {
            try {
                deleteDirectory(repoDir.toPath());
                logger.debug("Cleaned up repository directory: {}", repoDir.getAbsolutePath());
            } catch (IOException e) {
                logger.warn("Failed to cleanup repository directory: {}", repoDir.getAbsolutePath(), e);
            }
        }
    }
    
    private void deleteDirectory(Path directory) throws IOException {
        if (Files.exists(directory)) {
            Files.walk(directory)
                    .sorted((a, b) -> b.compareTo(a))
                    .forEach(path -> {
                        try {
                            Files.delete(path);
                        } catch (IOException e) {
                            logger.warn("Failed to delete: {}", path, e);
                        }
                    });
        }
    }
}

