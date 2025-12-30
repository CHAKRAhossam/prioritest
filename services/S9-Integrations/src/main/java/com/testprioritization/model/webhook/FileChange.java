package com.testprioritization.model.webhook;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Represents a file change in a PR/MR.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@JsonIgnoreProperties(ignoreUnknown = true)
public class FileChange {
    
    private String path;
    private String filename;
    private String status; // added, modified, removed, renamed
    private Integer additions;
    private Integer deletions;
    private Integer changes;
    private String patch;
    private String previousFilename;
    private String sha;
    private String blobUrl;
    private String rawUrl;
    private String contentsUrl;
    
    /**
     * Check if this is a Java/Kotlin class file.
     */
    public boolean isClassFile() {
        String filePath = path != null ? path : filename;
        if (filePath == null) return false;
        return filePath.endsWith(".java") || filePath.endsWith(".kt") || 
               filePath.endsWith(".scala") || filePath.endsWith(".groovy");
    }
    
    /**
     * Check if this is a test file.
     */
    public boolean isTestFile() {
        String filePath = path != null ? path : filename;
        if (filePath == null) return false;
        return filePath.contains("/test/") || 
               filePath.contains("Test.java") || 
               filePath.contains("Tests.java") ||
               filePath.contains("Spec.java") ||
               filePath.contains("IT.java") ||
               filePath.contains("_test.go") ||
               filePath.contains(".test.") ||
               filePath.contains(".spec.");
    }
    
    /**
     * Extract class name from file path.
     */
    public String extractClassName() {
        String filePath = path != null ? path : filename;
        if (filePath == null) return null;
        
        // Remove path and extension
        String fileName = filePath;
        int lastSlash = fileName.lastIndexOf('/');
        if (lastSlash >= 0) {
            fileName = fileName.substring(lastSlash + 1);
        }
        int lastDot = fileName.lastIndexOf('.');
        if (lastDot >= 0) {
            fileName = fileName.substring(0, lastDot);
        }
        return fileName;
    }
    
    /**
     * Extract package/module path.
     */
    public String extractPackagePath() {
        String filePath = path != null ? path : filename;
        if (filePath == null) return null;
        
        // Find src/main/java or src/test/java and extract package path
        int srcIndex = filePath.indexOf("src/main/java/");
        if (srcIndex >= 0) {
            String packagePath = filePath.substring(srcIndex + "src/main/java/".length());
            int lastSlash = packagePath.lastIndexOf('/');
            if (lastSlash >= 0) {
                return packagePath.substring(0, lastSlash).replace('/', '.');
            }
        }
        
        srcIndex = filePath.indexOf("src/test/java/");
        if (srcIndex >= 0) {
            String packagePath = filePath.substring(srcIndex + "src/test/java/".length());
            int lastSlash = packagePath.lastIndexOf('/');
            if (lastSlash >= 0) {
                return packagePath.substring(0, lastSlash).replace('/', '.');
            }
        }
        
        return null;
    }
}

