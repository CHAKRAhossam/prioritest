package com.reco.analysestatiqueservice.model;

public class DependencyEdge {

    private String fromClass;
    private String toClass;

    public DependencyEdge() {
    }

    public DependencyEdge(String fromClass, String toClass) {
        this.fromClass = fromClass;
        this.toClass = toClass;
    }

    public String getFromClass() {
        return fromClass;
    }

    public void setFromClass(String fromClass) {
        this.fromClass = fromClass;
    }

    public String getToClass() {
        return toClass;
    }

    public void setToClass(String toClass) {
        this.toClass = toClass;
    }

    @Override
    public String toString() {
        return fromClass + " -> " + toClass;
    }
}
