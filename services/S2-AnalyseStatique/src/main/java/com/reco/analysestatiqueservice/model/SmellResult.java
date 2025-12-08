package com.reco.analysestatiqueservice.model;

public class SmellResult {

    private String smellType;
    private String className;
    private int line;
    private String details;

    public SmellResult() {
    }

    public SmellResult(String smellType, String className, int line) {
        this(smellType, className, line, null);
    }
    public SmellResult(String smellType, String className, int line, String details) {
        this.smellType = smellType;
        this.className = className;
        this.line = line;
        this.details = details;
    }

    public String getSmellType() {
        return smellType;
    }

    public void setSmellType(String smellType) {
        this.smellType = smellType;
    }

    public String getClassName() {
        return className;
    }

    public void setClassName(String className) {
        this.className = className;
    }

    public int getLine() {
        return line;
    }

    public void setLine(int line) {
        this.line = line;
    }

    public String getDetails() { return details; }
    public void setDetails(String details) { this.details = details; }

    @Override
    public String toString() {
        return "Smell: " + smellType + " in " + className + " at line " + line + (details != null ? " [" + details + "]" : "");
    }
}
