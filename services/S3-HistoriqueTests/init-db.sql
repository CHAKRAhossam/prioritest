-- Initialize TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Database is created by Docker environment variables
-- This script runs additional initialization

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE historique_tests TO admin;

-- Note: Tables will be created by Hibernate/JPA on application startup
-- or by Flyway/Liquibase migrations if configured


