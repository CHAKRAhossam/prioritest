package com.prioritest.discovery;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.netflix.eureka.server.EnableEurekaServer;

/**
 * Eureka Discovery Server for PRIORITEST Platform.
 * 
 * All microservices register here for service discovery.
 * 
 * Services:
 * - S1-CollecteDepots (Python/FastAPI) - Port 8001
 * - S2-AnalyseStatique (Java/Spring) - Port 8081
 * - S3-HistoriqueTests (Java/Spring) - Port 8082
 * - S4-PretraitementFeatures (Python/FastAPI) - Port 8004
 * - S5-MLService (Python/FastAPI) - Port 8005
 * - S6-MoteurPriorisation (Python/FastAPI) - Port 8006
 * - S7-TestScaffolder (Python/FastAPI) - Port 8007
 * - S8-DashboardQualite (React) - Port 3000
 * - S9-Integrations (Java/Spring) - Port 8009
 * 
 * @author PRIORITEST Team
 */
@SpringBootApplication
@EnableEurekaServer
public class DiscoveryServerApplication {

    public static void main(String[] args) {
        SpringApplication.run(DiscoveryServerApplication.class, args);
    }
}
