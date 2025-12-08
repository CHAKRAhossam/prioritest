package com.example.historiquetests.parser;

import com.example.historiquetests.model.TestResult;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

@Component
@Slf4j
public class SurefireParser {

    /**
     * Parse Surefire/Failsafe XML test reports (TEST-*.xml files)
     */
    public List<TestResult> parseSurefireReport(InputStream xmlStream, String commitSha, String buildId, String branch) throws Exception {
        return parseSurefireReport(xmlStream, commitSha, buildId, branch, null);
    }
    
    /**
     * Parse Surefire/Failsafe XML test reports with repositoryId
     */
    public List<TestResult> parseSurefireReport(InputStream xmlStream, String commitSha, String buildId, String branch, String repositoryId) throws Exception {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        // Disable DTD loading to avoid external entity resolution issues
        factory.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
        factory.setFeature("http://xml.org/sax/features/external-general-entities", false);
        factory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
        factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", false);
        DocumentBuilder builder = factory.newDocumentBuilder();
        Document doc = builder.parse(xmlStream);
        doc.getDocumentElement().normalize();

        List<TestResult> results = new ArrayList<>();
        
        Element testsuiteElement = doc.getDocumentElement();
        if (!"testsuite".equals(testsuiteElement.getNodeName())) {
            throw new IllegalArgumentException("Invalid Surefire XML: root element should be 'testsuite'");
        }
        
        String testClass = testsuiteElement.getAttribute("name");
        
        // Parse individual test cases
        NodeList testcases = testsuiteElement.getElementsByTagName("testcase");
        
        for (int i = 0; i < testcases.getLength(); i++) {
            Element testcase = (Element) testcases.item(i);
            TestResult result = parseTestCase(testcase, testClass, commitSha, buildId, branch, repositoryId);
            results.add(result);
        }
        
        log.info("Parsed {} test results from Surefire report for commit {}", results.size(), commitSha);
        return results;
    }
    
    private TestResult parseTestCase(Element testcase, String testClass, String commitSha, String buildId, String branch, String repositoryId) {
        TestResult result = new TestResult();
        
        result.setRepositoryId(repositoryId != null ? repositoryId : "default");
        result.setCommitSha(commitSha);
        result.setBuildId(buildId);
        result.setBranch(branch);
        
        // Basic test info
        String testName = testcase.getAttribute("name");
        String className = testcase.getAttribute("classname");
        if (className == null || className.isEmpty()) {
            className = testClass;
        }
        
        result.setTestName(testName);
        result.setTestClass(className);
        
        // Execution time
        String timeStr = testcase.getAttribute("time");
        if (timeStr != null && !timeStr.isEmpty()) {
            try {
                result.setExecutionTime(Double.parseDouble(timeStr));
            } catch (NumberFormatException e) {
                log.warn("Invalid time format for test {}: {}", testName, timeStr);
                result.setExecutionTime(0.0);
            }
        }
        
        // Determine status
        NodeList failures = testcase.getElementsByTagName("failure");
        NodeList errors = testcase.getElementsByTagName("error");
        NodeList skipped = testcase.getElementsByTagName("skipped");
        
        if (failures.getLength() > 0) {
            result.setStatus(TestResult.TestStatus.FAILED);
            Element failure = (Element) failures.item(0);
            result.setErrorMessage(failure.getAttribute("message"));
            result.setStackTrace(failure.getTextContent());
        } else if (errors.getLength() > 0) {
            result.setStatus(TestResult.TestStatus.ERROR);
            Element error = (Element) errors.item(0);
            result.setErrorMessage(error.getAttribute("message"));
            result.setStackTrace(error.getTextContent());
        } else if (skipped.getLength() > 0) {
            result.setStatus(TestResult.TestStatus.SKIPPED);
            Element skip = (Element) skipped.item(0);
            result.setErrorMessage(skip.getAttribute("message"));
        } else {
            result.setStatus(TestResult.TestStatus.PASSED);
        }
        
        return result;
    }
    
    /**
     * Parse multiple Surefire report files (usually multiple TEST-*.xml files)
     */
    public List<TestResult> parseMultipleReports(List<InputStream> xmlStreams, String commitSha, String buildId, String branch) {
        List<TestResult> allResults = new ArrayList<>();
        
        for (InputStream stream : xmlStreams) {
            try {
                List<TestResult> results = parseSurefireReport(stream, commitSha, buildId, branch);
                allResults.addAll(results);
            } catch (Exception e) {
                log.error("Error parsing Surefire report", e);
            }
        }
        
        return allResults;
    }
}


