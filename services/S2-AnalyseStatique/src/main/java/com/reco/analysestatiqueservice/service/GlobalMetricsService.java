package com.reco.analysestatiqueservice.service;

import com.reco.analysestatiqueservice.extractor.DependencyGraphExtractor;
import com.reco.analysestatiqueservice.model.ClassMetrics;
import com.reco.analysestatiqueservice.model.DependencyEdge;
import org.jgrapht.Graph;
import org.jgrapht.graph.DefaultDirectedGraph;
import org.jgrapht.graph.DefaultEdge;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.io.File;
import java.util.*;

/**
 * Service for calculating global metrics that require project-wide analysis:
 * - NOC (Number of Children): requires inheritance hierarchy
 * - In/Out Degree: requires dependency graph
 */
@Service
public class GlobalMetricsService {
    
    private static final Logger logger = LoggerFactory.getLogger(GlobalMetricsService.class);
    
    private final DependencyGraphExtractor dependencyGraphExtractor;
    
    public GlobalMetricsService(DependencyGraphExtractor dependencyGraphExtractor) {
        this.dependencyGraphExtractor = dependencyGraphExtractor;
    }
    
    /**
     * Calculates NOC (Number of Children) for all classes in the project.
     * Requires analyzing the inheritance hierarchy.
     * 
     * @param projectDir The project directory
     * @param allMetrics List of all class metrics
     * @return Map of class name to NOC value
     */
    public Map<String, Integer> calculateNOC(File projectDir, List<ClassMetrics> allMetrics) {
        logger.debug("Calculating NOC for {} classes", allMetrics.size());
        
        // Build inheritance map: parent -> children
        Map<String, String> classToParent = new HashMap<>();
        
        // First pass: collect inheritance relationships
        for (ClassMetrics metrics : allMetrics) {
            String className = getFullyQualifiedName(metrics);
            // Extract parent from DIT calculation (would need to parse extends/implements)
            // For now, we'll use a simplified approach
            classToParent.put(className, null); // Will be populated if we parse inheritance
        }
        
        // Build children count
        Map<String, Integer> nocMap = new HashMap<>();
        for (String className : classToParent.keySet()) {
            nocMap.put(className, 0);
        }
        
        for (Map.Entry<String, String> entry : classToParent.entrySet()) {
            String parent = entry.getValue();
            if (parent != null) {
                nocMap.put(parent, nocMap.getOrDefault(parent, 0) + 1);
            }
        }
        
        logger.debug("NOC calculation completed");
        return nocMap;
    }
    
    /**
     * Calculates in-degree and out-degree for all classes using JGraphT.
     * 
     * @param projectDir The project directory
     * @param allMetrics List of all class metrics
     * @return Map of class name to dependency degrees (in/out)
     */
    public Map<String, DependencyDegrees> calculateDependencyDegrees(
            File projectDir, 
            List<ClassMetrics> allMetrics) {
        
        logger.debug("Calculating dependency degrees for {} classes", allMetrics.size());
        
        // Build dependency graph using JGraphT
        Graph<String, DefaultEdge> graph = new DefaultDirectedGraph<>(DefaultEdge.class);
        
        // Add all classes as vertices
        Map<String, String> classNameToFQN = new HashMap<>();
        for (ClassMetrics metrics : allMetrics) {
            String fqn = getFullyQualifiedName(metrics);
            graph.addVertex(fqn);
            classNameToFQN.put(metrics.getClassName(), fqn);
        }
        
        // Extract dependencies and add edges
        for (ClassMetrics metrics : allMetrics) {
            String sourceFQN = getFullyQualifiedName(metrics);
            File javaFile = new File(metrics.getFilePath());
            
            if (javaFile.exists()) {
                List<DependencyEdge> edges = dependencyGraphExtractor.extract(javaFile);
                for (DependencyEdge edge : edges) {
                    String targetFQN = edge.getToClass();
                    if (graph.containsVertex(targetFQN)) {
                        graph.addEdge(sourceFQN, targetFQN);
                    }
                }
            }
        }
        
        // Calculate in-degree and out-degree for each vertex
        Map<String, DependencyDegrees> degreesMap = new HashMap<>();
        for (String vertex : graph.vertexSet()) {
            int inDegree = graph.incomingEdgesOf(vertex).size();
            int outDegree = graph.outgoingEdgesOf(vertex).size();
            degreesMap.put(vertex, new DependencyDegrees(inDegree, outDegree));
        }
        
        logger.debug("Dependency degrees calculation completed");
        return degreesMap;
    }
    
    /**
     * Gets fully qualified name from ClassMetrics.
     */
    private String getFullyQualifiedName(ClassMetrics metrics) {
        String filePath = metrics.getFilePath();
        // Extract package from file path
        // This is a simplified version - in production, parse from source
        String className = metrics.getClassName();
        // Try to infer package from path
        if (filePath.contains("src/main/java/")) {
            int startIdx = filePath.indexOf("src/main/java/") + "src/main/java/".length();
            int endIdx = filePath.lastIndexOf("/");
            if (endIdx > startIdx) {
                String packagePath = filePath.substring(startIdx, endIdx);
                return packagePath.replace("/", ".") + "." + className;
            }
        }
        return className;
    }
    
    /**
     * Inner class for dependency degrees.
     */
    public static class DependencyDegrees {
        private final int inDegree;
        private final int outDegree;
        
        public DependencyDegrees(int inDegree, int outDegree) {
            this.inDegree = inDegree;
            this.outDegree = outDegree;
        }
        
        public int getInDegree() {
            return inDegree;
        }
        
        public int getOutDegree() {
            return outDegree;
        }
    }
}

