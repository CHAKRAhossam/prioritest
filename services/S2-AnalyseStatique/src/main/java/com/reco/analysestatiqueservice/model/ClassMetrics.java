package com.reco.analysestatiqueservice.model;

import java.util.List;

public class ClassMetrics {

    private String className;
    private String filePath;

    // JavaParser basic metrics
    private int loc;
    private int methodsCount;
    private int attributesCount;

    // CK Metrics
    private int wmc;
    private int dit;
    private int noc;
    private int cbo;
    private int rfc;
    private double lcom;

    // Smells
    private List<String> smells;

    // Dependencies
    private List<String> dependenciesOut;
    private List<String> dependenciesIn;

    // ===========================
    // Getters & Setters
    // ===========================

    public String getClassName() {
        return className;
    }

    public void setClassName(String className) {
        this.className = className;
    }

    public String getFilePath() {
        return filePath;
    }

    public void setFilePath(String filePath) {
        this.filePath = filePath;
    }

    public int getLoc() {
        return loc;
    }

    public void setLoc(int loc) {
        this.loc = loc;
    }

    public int getMethodsCount() {
        return methodsCount;
    }

    public void setMethodsCount(int methodsCount) {
        this.methodsCount = methodsCount;
    }

    public int getAttributesCount() {
        return attributesCount;
    }

    public void setAttributesCount(int attributesCount) {
        this.attributesCount = attributesCount;
    }

    public int getWmc() {
        return wmc;
    }

    public void setWmc(int wmc) {
        this.wmc = wmc;
    }

    public int getDit() {
        return dit;
    }

    public void setDit(int dit) {
        this.dit = dit;
    }

    public int getNoc() {
        return noc;
    }

    public void setNoc(int noc) {
        this.noc = noc;
    }

    public int getCbo() {
        return cbo;
    }

    public void setCbo(int cbo) {
        this.cbo = cbo;
    }

    public int getRfc() {
        return rfc;
    }

    public void setRfc(int rfc) {
        this.rfc = rfc;
    }

    public double getLcom() {
        return lcom;
    }

    public void setLcom(double lcom) {
        this.lcom = lcom;
    }

    public List<String> getSmells() {
        return smells;
    }

    public void setSmells(List<String> smells) {
        this.smells = smells;
    }

    public List<String> getDependenciesOut() {
        return dependenciesOut;
    }

    public void setDependenciesOut(List<String> dependenciesOut) {
        this.dependenciesOut = dependenciesOut;
    }

    public List<String> getDependenciesIn() {
        return dependenciesIn;
    }

    public void setDependenciesIn(List<String> dependenciesIn) {
        this.dependenciesIn = dependenciesIn;
    }
}
