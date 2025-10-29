-- Migration 001: Initial MCP Box Schema
-- This creates the comprehensive tool management schema
-- Version: 1
-- Description: Initial schema creation with comprehensive tool management

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Core tools table with comprehensive metadata
CREATE TABLE tools (
    tool_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    version TEXT NOT NULL DEFAULT '1.0.0',
    server_url TEXT,
    input_schema TEXT, -- JSON string
    output_schema TEXT, -- JSON string
    created_by TEXT NOT NULL, -- project_id that created this tool
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    success_rate REAL DEFAULT 1.0,
    average_duration REAL DEFAULT 0.0,
    deprecated BOOLEAN DEFAULT FALSE,
    deprecation_reason TEXT,
    replacement_tool_id TEXT,
    metadata TEXT, -- JSON string for additional metadata
    FOREIGN KEY (replacement_tool_id) REFERENCES tools(tool_id)
);

-- Capabilities that tools can provide
CREATE TABLE capabilities (
    capability_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Junction table linking tools to capabilities with strength ratings
CREATE TABLE tool_capabilities (
    tool_id TEXT,
    capability_id TEXT,
    strength REAL DEFAULT 1.0 CHECK (strength >= 0.0 AND strength <= 1.0),
    confidence REAL DEFAULT 1.0 CHECK (confidence >= 0.0 AND confidence <= 1.0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (tool_id, capability_id),
    FOREIGN KEY (tool_id) REFERENCES tools(tool_id) ON DELETE CASCADE,
    FOREIGN KEY (capability_id) REFERENCES capabilities(capability_id)
);

-- Tool dependencies and relationships
CREATE TABLE dependencies (
    dependent_tool_id TEXT,
    dependency_tool_id TEXT,
    dependency_type TEXT DEFAULT 'requires', -- 'requires', 'optional', 'conflicts'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (dependent_tool_id, dependency_tool_id),
    FOREIGN KEY (dependent_tool_id) REFERENCES tools(tool_id) ON DELETE CASCADE,
    FOREIGN KEY (dependency_tool_id) REFERENCES tools(tool_id)
);

-- Security vulnerability tracking
CREATE TABLE vulnerabilities (
    vulnerability_id TEXT PRIMARY KEY,
    tool_id TEXT NOT NULL,
    severity TEXT NOT NULL, -- 'low', 'medium', 'high', 'critical'
    description TEXT NOT NULL,
    cve_id TEXT,
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    patched_at TIMESTAMP,
    patched_in_version TEXT,
    FOREIGN KEY (tool_id) REFERENCES tools(tool_id) ON DELETE CASCADE
);

-- Performance logs for analytics and optimization
CREATE TABLE performance_logs (
    log_id TEXT PRIMARY KEY,
    tool_id TEXT NOT NULL,
    project_id TEXT,
    execution_start TIMESTAMP NOT NULL,
    execution_end TIMESTAMP NOT NULL,
    duration_ms REAL NOT NULL,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    input_size_bytes INTEGER,
    output_size_bytes INTEGER,
    memory_usage_mb REAL,
    cpu_usage_percent REAL,
    metadata TEXT, -- JSON string for additional metrics
    FOREIGN KEY (tool_id) REFERENCES tools(tool_id) ON DELETE CASCADE
);

-- Performance indexes
CREATE INDEX idx_tools_created_by ON tools(created_by);
CREATE INDEX idx_tools_deprecated ON tools(deprecated);
CREATE INDEX idx_tools_last_used ON tools(last_used);
CREATE INDEX idx_tools_usage_count ON tools(usage_count DESC);

CREATE INDEX idx_capabilities_name ON capabilities(name);
CREATE INDEX idx_capabilities_category ON capabilities(category);

CREATE INDEX idx_tool_capabilities_capability ON tool_capabilities(capability_id);
CREATE INDEX idx_tool_capabilities_strength ON tool_capabilities(strength DESC);

CREATE INDEX idx_dependencies_dependent ON dependencies(dependent_tool_id);
CREATE INDEX idx_dependencies_dependency ON dependencies(dependency_tool_id);

CREATE INDEX idx_performance_logs_tool ON performance_logs(tool_id);
CREATE INDEX idx_performance_logs_project ON performance_logs(project_id);
CREATE INDEX idx_performance_logs_duration ON performance_logs(duration_ms);
CREATE INDEX idx_performance_logs_success ON performance_logs(success);

CREATE INDEX idx_vulnerabilities_tool ON vulnerabilities(tool_id);
CREATE INDEX idx_vulnerabilities_severity ON vulnerabilities(severity);

-- Insert common capabilities that VDW phases might need
INSERT INTO capabilities (capability_id, name, description, category) VALUES
('cap-requirement-analysis', 'requirement-analysis', 'Analyze and structure requirements', 'analysis'),
('cap-architecture-design', 'architecture-design', 'Design system architecture', 'design'),
('cap-code-generation', 'code-generation', 'Generate source code', 'development'),
('cap-testing', 'testing', 'Execute tests and validations', 'quality-assurance'),
('cap-documentation', 'documentation', 'Generate documentation', 'documentation'),
('cap-api-integration', 'api-integration', 'Integrate with external APIs', 'integration'),
('cap-database-design', 'database-design', 'Design database schemas', 'data-modeling'),
('cap-security-analysis', 'security-analysis', 'Analyze security vulnerabilities', 'security'),
('cap-performance-testing', 'performance-testing', 'Test system performance', 'performance'),
('cap-deployment', 'deployment', 'Deploy applications', 'operations'),
('cap-monitoring', 'monitoring', 'Monitor system health', 'operations'),
('cap-logging', 'logging', 'Structured logging and analytics', 'observability'),
('cap-web-scraping', 'web-scraping', 'Extract data from websites', 'data-extraction'),
('cap-file-processing', 'file-processing', 'Process various file formats', 'file-management'),
('cap-email-sending', 'email-sending', 'Send emails and notifications', 'communication'),
('cap-report-generation', 'report-generation', 'Generate reports and summaries', 'reporting');

-- Update database version
PRAGMA user_version = 1;