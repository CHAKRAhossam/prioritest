package com.reco.analysestatiqueservice.dto;

public class FileScanResult {

    private String relativePath;  // chemin relatif (ex: src/main/java/com/example/Class.java)
    private String absolutePath;  // chemin absolu (ex: /tmp/repo123/src/main/java/com/example/Class.java)

    public FileScanResult(String relativePath, String absolutePath) {
        this.relativePath = relativePath;
        this.absolutePath = absolutePath;
    }

    public String getPath() {
        return relativePath;
    }
    
    public String getRelativePath() {
        return relativePath;
    }

    public String getAbsolutePath() {
        return absolutePath;
    }
}