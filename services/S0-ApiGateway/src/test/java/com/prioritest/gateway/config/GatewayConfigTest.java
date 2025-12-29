package com.prioritest.gateway.config;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.cloud.gateway.route.RouteLocator;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class GatewayConfigTest {

    @Autowired
    private GatewayConfig gatewayConfig;

    @Autowired
    private RouteLocator routeLocator;

    @Test
    void testGatewayConfigBean() {
        assertNotNull(gatewayConfig);
    }

    @Test
    void testRouteLocatorBean() {
        assertNotNull(routeLocator);
    }

    @Test
    void testCustomRouteLocator() {
        // Verify routes are configured
        assertNotNull(routeLocator.getRoutes());
    }
}

