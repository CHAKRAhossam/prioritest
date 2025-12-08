package com.reco.analysestatiqueservice.extractor;

import com.reco.analysestatiqueservice.model.SmellResult;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.w3c.dom.*;
import javax.xml.parsers.DocumentBuilderFactory;
import java.io.File;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

@Component
public class PMDSmellDetectorCli {
    private static final Logger logger = LoggerFactory.getLogger(PMDSmellDetectorCli.class);

    @Value("${pmd.cli.path:pmd}")
    private String pmdCliPath; // Ex: "pmd" si dans le PATH, ou chemin complet
    @Value("${pmd.ruleset:category/java/bestpractices.xml}")
    private String ruleSetPath;
    @Value("${pmd.java.version:17}")
    private String javaVersion;

    public List<SmellResult> detect(File file) {
        List<SmellResult> results = new ArrayList<>();
        try {
            // Commande PMD CLI
            // pmd -d <fichier> -R <ruleset> -f xml -language java
            ProcessBuilder pb = new ProcessBuilder(
                    pmdCliPath,
                    "-d", file.getAbsolutePath(),
                    "-R", ruleSetPath,
                    "-f", "xml",
                    "-language", "java",
                    "-version", javaVersion
            );
            Process proc = pb.start();
            InputStream is = proc.getInputStream();

            Document doc = DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(is);
            doc.getDocumentElement().normalize();

            NodeList fileNodes = doc.getElementsByTagName("file");
            for (int i = 0; i < fileNodes.getLength(); i++) {
                Element fileElem = (Element) fileNodes.item(i);
                String filename = fileElem.getAttribute("name");
                NodeList violationNodes = fileElem.getElementsByTagName("violation");
                for (int j = 0; j < violationNodes.getLength(); j++) {
                    Element violElem = (Element) violationNodes.item(j);
                    String rule = violElem.getAttribute("rule");
                    int beginLine = Integer.parseInt(violElem.getAttribute("beginline"));
                    String message = violElem.getTextContent().trim();
                    SmellResult res = new SmellResult("PMD-"+rule, filename, beginLine, message);
                    results.add(res);
                }
            }
        } catch (Exception e) {
            logger.warn("PMD CLI scan failed on file {}: {}", file.getName(), e.getMessage());
        }
        return results;
    }
}

