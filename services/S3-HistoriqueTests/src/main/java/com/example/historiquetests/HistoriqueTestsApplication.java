package com.example.historiquetests;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;

@SpringBootApplication
@EnableDiscoveryClient
public class HistoriqueTestsApplication {
    public static void main(String[] args) {
        SpringApplication.run(HistoriqueTestsApplication.class, args);
    }
}
