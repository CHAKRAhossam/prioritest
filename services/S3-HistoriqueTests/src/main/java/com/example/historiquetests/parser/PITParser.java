package com.example.historiquetests.parser;

import com.example.historiquetests.model.MutationResult;
import com.example.historiquetests.model.TestCoverage;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Component
@Slf4j
public class PITParser {

    /**
     * Parse PIT (PIT Mutation Testing) XML report
     */
    public List<MutationResult> parsePITReport(InputStream xmlStream, String commitSha) throws Exception {
        return parsePITReport(xmlStream, commitSha, null);
    }
    
    /**
     * Parse PIT (PIT Mutation Testing) XML report with repositoryId
     */
    public List<MutationResult> parsePITReport(InputStream xmlStream, String commitSha, String repositoryId) throws Exception {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        // Disable DTD loading to avoid external entity resolution issues
        factory.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
        factory.setFeature("http://xml.org/sax/features/external-general-entities", false);
        factory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
        factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", false);
        DocumentBuilder builder = factory.newDocumentBuilder();
        Document doc = builder.parse(xmlStream);
        doc.getDocumentElement().normalize();

        List<MutationResult> mutations = new ArrayList<>();
        
        // PIT XML structure: <mutations><mutation>...</mutation></mutations>
        NodeList mutationNodes = doc.getElementsByTagName("mutation");
        
        for (int i = 0; i < mutationNodes.getLength(); i++) {
            Element mutationElement = (Element) mutationNodes.item(i);
            MutationResult mutation = parseMutation(mutationElement, commitSha, repositoryId);
            mutations.add(mutation);
        }
        
        log.info("Parsed {} mutations from PIT report for commit {}", mutations.size(), commitSha);
        return mutations;
    }
    
    private MutationResult parseMutation(Element mutationElement, String commitSha, String repositoryId) {
        MutationResult mutation = new MutationResult();
        mutation.setRepositoryId(repositoryId != null ? repositoryId : "default");
        mutation.setCommitSha(commitSha);
        
        // Parse mutation details
        String detected = getTextContent(mutationElement, "detected");
        String status = getTextContent(mutationElement, "status");
        
        // Map PIT status to our enum
        mutation.setStatus(mapPITStatus(status, detected));
        
        // Class and method info
        String mutatedClass = getTextContent(mutationElement, "mutatedClass");
        mutation.setClassName(mutatedClass);
        
        String mutatedMethod = getTextContent(mutationElement, "mutatedMethod");
        mutation.setMethodName(mutatedMethod);
        
        // Line number
        String lineNumber = getTextContent(mutationElement, "lineNumber");
        if (lineNumber != null && !lineNumber.isEmpty()) {
            try {
                mutation.setLineNumber(Integer.parseInt(lineNumber));
            } catch (NumberFormatException e) {
                log.warn("Invalid line number: {}", lineNumber);
            }
        }
        
        // Mutator
        String mutator = getTextContent(mutationElement, "mutator");
        mutation.setMutator(mutator);
        
        // Description
        String description = getTextContent(mutationElement, "description");
        mutation.setMutationDescription(description);
        
        // Killing test
        String killingTest = getTextContent(mutationElement, "killingTest");
        if (killingTest != null && !killingTest.isEmpty() && !"none".equals(killingTest)) {
            mutation.setKillingTest(killingTest);
        }
        
        return mutation;
    }
    
    private MutationResult.MutationStatus mapPITStatus(String status, String detected) {
        if ("KILLED".equals(status) || "true".equals(detected)) {
            return MutationResult.MutationStatus.KILLED;
        } else if ("SURVIVED".equals(status)) {
            return MutationResult.MutationStatus.SURVIVED;
        } else if ("NO_COVERAGE".equals(status)) {
            return MutationResult.MutationStatus.NO_COVERAGE;
        } else if ("TIMED_OUT".equals(status)) {
            return MutationResult.MutationStatus.TIMED_OUT;
        } else if ("NON_VIABLE".equals(status)) {
            return MutationResult.MutationStatus.NON_VIABLE;
        } else if ("MEMORY_ERROR".equals(status)) {
            return MutationResult.MutationStatus.MEMORY_ERROR;
        } else if ("RUN_ERROR".equals(status)) {
            return MutationResult.MutationStatus.RUN_ERROR;
        } else {
            log.warn("Unknown PIT mutation status: {}", status);
            return MutationResult.MutationStatus.RUN_ERROR;
        }
    }
    
    private String getTextContent(Element parent, String tagName) {
        NodeList nodes = parent.getElementsByTagName(tagName);
        if (nodes.getLength() > 0) {
            return nodes.item(0).getTextContent();
        }
        return null;
    }
    
    /**
     * Calculate mutation score summary from mutations list
     */
    public Map<String, MutationSummary> calculateMutationScores(List<MutationResult> mutations) {
        Map<String, MutationSummary> summaryByClass = new HashMap<>();
        
        for (MutationResult mutation : mutations) {
            String className = mutation.getClassName();
            MutationSummary summary = summaryByClass.computeIfAbsent(className, k -> new MutationSummary());
            
            switch (mutation.getStatus()) {
                case KILLED:
                    summary.killed++;
                    break;
                case SURVIVED:
                    summary.survived++;
                    break;
                case NO_COVERAGE:
                    summary.noCoverage++;
                    break;
                default:
                    summary.other++;
                    break;
            }
        }
        
        // Calculate scores
        for (MutationSummary summary : summaryByClass.values()) {
            summary.calculateScore();
        }
        
        return summaryByClass;
    }
    
    /**
     * Update TestCoverage entities with mutation scores
     */
    public void updateCoverageWithMutations(List<TestCoverage> coverages, Map<String, MutationSummary> mutationScores) {
        for (TestCoverage coverage : coverages) {
            MutationSummary summary = mutationScores.get(coverage.getClassName());
            if (summary != null) {
                coverage.setMutationScore(summary.score);
                coverage.setMutationsKilled(summary.killed);
                coverage.setMutationsSurvived(summary.survived);
                coverage.setMutationsNoCoverage(summary.noCoverage);
            }
        }
    }
    
    public static class MutationSummary {
        public int killed = 0;
        public int survived = 0;
        public int noCoverage = 0;
        public int other = 0;
        public double score = 0.0;
        
        public void calculateScore() {
            int total = killed + survived;
            if (total > 0) {
                score = (double) killed / total * 100.0;
            }
        }
        
        public int getTotal() {
            return killed + survived + noCoverage + other;
        }
    }
}


