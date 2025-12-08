-- Initial schema for test metrics tracking with TimescaleDB support

-- Enable TimescaleDB extension (requires superuser privileges)
-- CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Test Coverage table (tracks coverage metrics per class per commit)
CREATE TABLE IF NOT EXISTS test_coverage (
    id BIGSERIAL PRIMARY KEY,
    repository_id VARCHAR(255) NOT NULL,
    commit_sha VARCHAR(255) NOT NULL,
    class_name VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000),
    package_name VARCHAR(500),
    
    -- Line coverage
    lines_covered INTEGER DEFAULT 0,
    lines_missed INTEGER DEFAULT 0,
    
    -- Branch coverage
    branches_covered INTEGER DEFAULT 0,
    branches_missed INTEGER DEFAULT 0,
    
    -- Method coverage
    methods_covered INTEGER DEFAULT 0,
    methods_missed INTEGER DEFAULT 0,
    
    -- Instruction coverage
    instructions_covered INTEGER DEFAULT 0,
    instructions_missed INTEGER DEFAULT 0,
    
    -- Percentages
    line_coverage DOUBLE PRECISION DEFAULT 0,
    branch_coverage DOUBLE PRECISION DEFAULT 0,
    method_coverage DOUBLE PRECISION DEFAULT 0,
    instruction_coverage DOUBLE PRECISION DEFAULT 0,
    
    -- Mutation testing
    mutation_score DOUBLE PRECISION,
    mutations_killed INTEGER,
    mutations_survived INTEGER,
    mutations_no_coverage INTEGER,
    
    -- Metadata
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    build_id VARCHAR(255),
    branch VARCHAR(255)
);

-- Create indices for common queries
CREATE INDEX idx_coverage_class ON test_coverage(class_name);
CREATE INDEX idx_coverage_commit ON test_coverage(commit_sha);
CREATE INDEX idx_coverage_timestamp ON test_coverage(timestamp DESC);
CREATE INDEX idx_coverage_package ON test_coverage(package_name);
CREATE INDEX idx_coverage_repository ON test_coverage(repository_id);
CREATE INDEX idx_coverage_repo_class ON test_coverage(repository_id, class_name);

-- Convert to TimescaleDB hypertable for time-series optimization
-- Uncomment if TimescaleDB is available
-- SELECT create_hypertable('test_coverage', 'timestamp', if_not_exists => TRUE);


-- Test Results table (tracks individual test execution results)
CREATE TABLE IF NOT EXISTS test_result (
    id BIGSERIAL PRIMARY KEY,
    repository_id VARCHAR(255) NOT NULL,
    commit_sha VARCHAR(255) NOT NULL,
    test_name VARCHAR(500) NOT NULL,
    test_class VARCHAR(500) NOT NULL,
    status VARCHAR(50) NOT NULL,
    execution_time DOUBLE PRECISION DEFAULT 0,
    error_message TEXT,
    stack_trace TEXT,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    build_id VARCHAR(255),
    branch VARCHAR(255),
    retry_count INTEGER DEFAULT 0
);

CREATE INDEX idx_result_test ON test_result(test_class, test_name);
CREATE INDEX idx_result_commit ON test_result(commit_sha);
CREATE INDEX idx_result_timestamp ON test_result(timestamp DESC);
CREATE INDEX idx_result_status ON test_result(status);
CREATE INDEX idx_result_repository ON test_result(repository_id);

-- Convert to hypertable
-- SELECT create_hypertable('test_result', 'timestamp', if_not_exists => TRUE);


-- Class-Test Mapping table (links classes to tests that cover them)
CREATE TABLE IF NOT EXISTS class_test_map (
    id BIGSERIAL PRIMARY KEY,
    repository_id VARCHAR(255) NOT NULL,
    commit_sha VARCHAR(255) NOT NULL,
    class_name VARCHAR(500) NOT NULL,
    test_name VARCHAR(500) NOT NULL,
    coverage_percent DOUBLE PRECISION DEFAULT 0,
    lines_covered INTEGER DEFAULT 0,
    total_lines INTEGER DEFAULT 0,
    branches_covered INTEGER DEFAULT 0,
    total_branches INTEGER DEFAULT 0,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_map_class ON class_test_map(class_name);
CREATE INDEX idx_map_test ON class_test_map(test_name);
CREATE INDEX idx_map_commit ON class_test_map(commit_sha);
CREATE INDEX idx_map_repository ON class_test_map(repository_id);


-- Test Flakiness table (tracks test stability over time)
CREATE TABLE IF NOT EXISTS test_flakiness (
    id BIGSERIAL PRIMARY KEY,
    repository_id VARCHAR(255) NOT NULL,
    test_class VARCHAR(500) NOT NULL,
    test_name VARCHAR(500) NOT NULL,
    total_runs INTEGER DEFAULT 0,
    failed_runs INTEGER DEFAULT 0,
    passed_runs INTEGER DEFAULT 0,
    consecutive_failures INTEGER DEFAULT 0,
    flakiness_score DOUBLE PRECISION DEFAULT 0,
    window_start TIMESTAMPTZ,
    window_end TIMESTAMPTZ,
    last_failure TIMESTAMPTZ,
    last_success TIMESTAMPTZ,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(repository_id, test_class, test_name)
);

CREATE INDEX idx_flakiness_test ON test_flakiness(test_class, test_name);
CREATE INDEX idx_flakiness_score ON test_flakiness(flakiness_score DESC);
CREATE INDEX idx_flakiness_repository ON test_flakiness(repository_id);


-- Test Debt table (tracks test coverage debt and recommendations)
CREATE TABLE IF NOT EXISTS test_debt (
    id BIGSERIAL PRIMARY KEY,
    repository_id VARCHAR(255) NOT NULL,
    commit_sha VARCHAR(255) NOT NULL,
    class_name VARCHAR(500) NOT NULL,
    coverage_deficit DOUBLE PRECISION DEFAULT 0,
    uncovered_lines INTEGER DEFAULT 0,
    uncovered_branches INTEGER DEFAULT 0,
    uncovered_methods INTEGER DEFAULT 0,
    mutation_deficit DOUBLE PRECISION DEFAULT 0,
    survived_mutants INTEGER DEFAULT 0,
    flakiness_impact DOUBLE PRECISION DEFAULT 0,
    flaky_test_count INTEGER DEFAULT 0,
    public_methods_without_tests INTEGER DEFAULT 0,
    debt_score DOUBLE PRECISION DEFAULT 0,
    recommendations TEXT,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_debt_class ON test_debt(class_name);
CREATE INDEX idx_debt_commit ON test_debt(commit_sha);
CREATE INDEX idx_debt_score ON test_debt(debt_score DESC);
CREATE INDEX idx_debt_repository ON test_debt(repository_id);


-- Mutation Results table (tracks PIT mutation testing results)
CREATE TABLE IF NOT EXISTS mutation_result (
    id BIGSERIAL PRIMARY KEY,
    repository_id VARCHAR(255) NOT NULL,
    commit_sha VARCHAR(255) NOT NULL,
    class_name VARCHAR(500) NOT NULL,
    method_name VARCHAR(255),
    line_number INTEGER,
    mutator VARCHAR(255),
    mutation_description TEXT,
    status VARCHAR(50) NOT NULL,
    killing_test VARCHAR(500),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_mutation_class ON mutation_result(class_name);
CREATE INDEX idx_mutation_commit ON mutation_result(commit_sha);
CREATE INDEX idx_mutation_status ON mutation_result(status);
CREATE INDEX idx_mutation_repository ON mutation_result(repository_id);

-- Convert to hypertable
-- SELECT create_hypertable('mutation_result', 'timestamp', if_not_exists => TRUE);


