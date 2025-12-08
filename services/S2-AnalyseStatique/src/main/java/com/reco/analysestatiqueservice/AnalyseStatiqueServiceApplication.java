package com.reco.analysestatiqueservice;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.Banner;

@SpringBootApplication
public class AnalyseStatiqueServiceApplication {

    public static void main(String[] args) {
        SpringApplication app = new SpringApplication(AnalyseStatiqueServiceApplication.class);
        app.setBannerMode(Banner.Mode.OFF);
        // Désactiver le support Groovy
        System.setProperty("spring.beaninfo.ignore", "true");
        app.run(args);
    }

}
