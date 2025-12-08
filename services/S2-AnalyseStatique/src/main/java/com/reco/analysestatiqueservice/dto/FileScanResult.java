package com.reco.analysestatiqueservice.dto;

public class FileScanResult {

    private String path;      // chemin complet du fichier
    private String className; // nom de la classe

    public FileScanResult(String path, String className) {
        this.path = path;
        this.className = className;
    }

    public String getPath() {
        return path;
    }

    public String getClassName() {
        return className;
    }
}
