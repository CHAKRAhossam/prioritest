package com.reco.analysestatiqueservice.dto;

import com.reco.analysestatiqueservice.model.ClassMetrics;
import com.reco.analysestatiqueservice.model.DependencyEdge;
import com.reco.analysestatiqueservice.model.SmellResult;

import java.util.List;
import java.util.Map;

public class MetricsResponse {

    private List<ClassMetrics> classes;
    private List<DependencyEdge> dependencies;
    private List<SmellResult> smells;

    private List<FileScanResult> files;   // <── ici la vraie correction

    private int nbClasses;
    private int nbDependencies;
    private int nbSmells;
    private int nbFiles;

    private Map<String, Object> smellThresholds;

    public List<ClassMetrics> getClasses() { return classes; }
    public void setClasses(List<ClassMetrics> classes) { this.classes = classes; }

    public List<DependencyEdge> getDependencies() { return dependencies; }
    public void setDependencies(List<DependencyEdge> dependencies) { this.dependencies = dependencies; }

    public List<SmellResult> getSmells() { return smells; }
    public void setSmells(List<SmellResult> smells) { this.smells = smells; }

    public List<FileScanResult> getFiles() { return files; }
    public void setFiles(List<FileScanResult> files) { this.files = files; }

    public int getNbClasses() { return nbClasses; }
    public void setNbClasses(int nbClasses) { this.nbClasses = nbClasses; }

    public int getNbDependencies() { return nbDependencies; }
    public void setNbDependencies(int nbDependencies) { this.nbDependencies = nbDependencies; }

    public int getNbSmells() { return nbSmells; }
    public void setNbSmells(int nbSmells) { this.nbSmells = nbSmells; }

    public int getNbFiles() { return nbFiles; }
    public void setNbFiles(int nbFiles) { this.nbFiles = nbFiles; }

    public Map<String, Object> getSmellThresholds() {
        return smellThresholds;
    }
    public void setSmellThresholds(Map<String, Object> smellThresholds) {
        this.smellThresholds = smellThresholds;
    }
}
