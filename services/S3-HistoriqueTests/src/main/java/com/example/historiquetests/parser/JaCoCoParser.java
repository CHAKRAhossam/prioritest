package com.example.historiquetests.parser;

import com.example.historiquetests.model.ClassTestMap;
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
public class JaCoCoParser {

    /**
     * Parse JaCoCo XML report and extract coverage metrics per class
     */
    public List<TestCoverage> parseJaCoCoReport(InputStream xmlStream, String commitSha, String buildId, String branch) throws Exception {
        return parseJaCoCoReport(xmlStream, commitSha, buildId, branch, null);
    }
    
    /**
     * Parse JaCoCo XML report and extract coverage metrics per class with repositoryId
     */
    public List<TestCoverage> parseJaCoCoReport(InputStream xmlStream, String commitSha, String buildId, String branch, String repositoryId) throws Exception {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        // Disable DTD loading to avoid external entity resolution issues
        factory.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
        factory.setFeature("http://xml.org/sax/features/external-general-entities", false);
        factory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
        factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", false);
        DocumentBuilder builder = factory.newDocumentBuilder();
        Document doc = builder.parse(xmlStream);
        doc.getDocumentElement().normalize();

        List<TestCoverage> coverageList = new ArrayList<>();
        
        // Parse packages
        NodeList packageNodes = doc.getElementsByTagName("package");
        
        for (int i = 0; i < packageNodes.getLength(); i++) {
            Element packageElement = (Element) packageNodes.item(i);
            String packageName = packageElement.getAttribute("name").replace('/', '.');
            
            // Parse classes within package
            NodeList classNodes = packageElement.getElementsByTagName("class");
            
            for (int j = 0; j < classNodes.getLength(); j++) {
                Element classElement = (Element) classNodes.item(j);
                TestCoverage coverage = parseClass(classElement, packageName, commitSha, buildId, branch, repositoryId);
                
                if (coverage != null) {
                    coverageList.add(coverage);
                }
            }
        }
        
        log.info("Parsed {} classes from JaCoCo report for commit {}", coverageList.size(), commitSha);
        return coverageList;
    }
    
    private TestCoverage parseClass(Element classElement, String packageName, String commitSha, String buildId, String branch, String repositoryId) {
        String className = classElement.getAttribute("name").replace('/', '.');
        String sourceFile = classElement.getAttribute("sourcefilename");
        
        // Skip anonymous classes and synthetic classes
        if (className.contains("$") && !className.matches(".*\\$\\d+$")) {
            return null;
        }
        
        TestCoverage coverage = new TestCoverage();
        coverage.setRepositoryId(repositoryId != null ? repositoryId : "default");
        coverage.setCommitSha(commitSha);
        coverage.setClassName(className);
        coverage.setPackageName(packageName);
        coverage.setFilePath(sourceFile);
        coverage.setBuildId(buildId);
        coverage.setBranch(branch);
        
        // Parse counters
        NodeList counters = classElement.getElementsByTagName("counter");
        Map<String, Counter> counterMap = new HashMap<>();
        
        for (int i = 0; i < counters.getLength(); i++) {
            Element counter = (Element) counters.item(i);
            String type = counter.getAttribute("type");
            int missed = Integer.parseInt(counter.getAttribute("missed"));
            int covered = Integer.parseInt(counter.getAttribute("covered"));
            counterMap.put(type, new Counter(covered, missed));
        }
        
        // Extract metrics
        Counter lineCounter = counterMap.get("LINE");
        if (lineCounter != null) {
            coverage.setLinesCovered(lineCounter.covered);
            coverage.setLinesMissed(lineCounter.missed);
            coverage.setLineCoverage(lineCounter.getPercentage());
        }
        
        Counter branchCounter = counterMap.get("BRANCH");
        if (branchCounter != null) {
            coverage.setBranchesCovered(branchCounter.covered);
            coverage.setBranchesMissed(branchCounter.missed);
            coverage.setBranchCoverage(branchCounter.getPercentage());
        }
        
        Counter methodCounter = counterMap.get("METHOD");
        if (methodCounter != null) {
            coverage.setMethodsCovered(methodCounter.covered);
            coverage.setMethodsMissed(methodCounter.missed);
            coverage.setMethodCoverage(methodCounter.getPercentage());
        }
        
        Counter instructionCounter = counterMap.get("INSTRUCTION");
        if (instructionCounter != null) {
            coverage.setInstructionsCovered(instructionCounter.covered);
            coverage.setInstructionsMissed(instructionCounter.missed);
            coverage.setInstructionCoverage(instructionCounter.getPercentage());
        }
        
        return coverage;
    }
    
    /**
     * Parse JaCoCo test execution data to map tests to classes they cover
     * This requires the jacoco.exec file processed with the report goal
     */
    public List<ClassTestMap> parseTestClassMapping(InputStream xmlStream, String commitSha) throws Exception {
        // This is an advanced feature that requires JaCoCo execution data
        // For now, return empty list. Can be enhanced with proper exec analysis
        List<ClassTestMap> mappings = new ArrayList<>();
        log.warn("Test-to-class mapping from JaCoCo exec not yet implemented");
        return mappings;
    }
    
    private static class Counter {
        int covered;
        int missed;
        
        Counter(int covered, int missed) {
            this.covered = covered;
            this.missed = missed;
        }
        
        double getPercentage() {
            int total = covered + missed;
            return total == 0 ? 0.0 : (double) covered / total * 100.0;
        }
    }
}


