-- VDW Orchestrator MCP Box Database Schema
-- SQLite schema for comprehensive tool metadata and lifecycle management
-- Supports versioning, performance tracking, and dependency analysis

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Set database version for migrations
PRAGMA user_version = 1;

-- Core tools table
CREATE TABLE IF NOT EXISTS tools (
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

-- Capabilities table
CREATE TABLE IF NOT EXISTS capabilities (
    capability_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tool-capability junction table with strength ratings
CREATE TABLE IF NOT EXISTS tool_capabilities (
    tool_id TEXT,
    capability_id TEXT,
    strength REAL DEFAULT 1.0 CHECK (strength >= 0.0 AND strength <= 1.0),
    confidence REAL DEFAULT 1.0 CHECK (confidence >= 0.0 AND confidence <= 1.0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (tool_id, capability_id),
    FOREIGN KEY (tool_id) REFERENCES tools(tool_id) ON DELETE CASCADE,
    FOREIGN KEY (capability_id) REFERENCES capabilities(capability_id)
);

-- Tool dependencies
CREATE TABLE IF NOT EXISTS dependencies (
    dependent_tool_id TEXT,
    dependency_tool_id TEXT,
    dependency_type TEXT DEFAULT 'requires', -- 'requires', 'optional', 'conflicts'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (dependent_tool_id, dependency_tool_id),
    FOREIGN KEY (dependent_tool_id) REFERENCES tools(tool_id) ON DELETE CASCADE,
    FOREIGN KEY (dependency_tool_id) REFERENCES tools(tool_id)
);

-- Security vulnerabilities tracking
CREATE TABLE IF NOT EXISTS vulnerabilities (
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

-- Performance logs for analytics
CREATE TABLE IF NOT EXISTS performance_logs (
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

-- Migration history
CREATE TABLE IF NOT EXISTS migrations (
    migration_id INTEGER PRIMARY KEY AUTOINCREMENT,
    version INTEGER NOT NULL,
    description TEXT NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_tools_created_by ON tools(created_by);
CREATE INDEX IF NOT EXISTS idx_tools_deprecated ON tools(deprecated);
CREATE INDEX IF NOT EXISTS idx_tools_last_used ON tools(last_used);
CREATE INDEX IF NOT EXISTS idx_capabilities_name ON capabilities(name);
CREATE INDEX IF NOT EXISTS idx_tool_capabilities_capability ON tool_capabilities(capability_id);
CREATE INDEX IF NOT EXISTS idx_performance_logs_tool ON performance_logs(tool_id);
CREATE INDEX IF NOT EXISTS idx_performance_logs_project ON performance_logs(project_id);
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_tool ON vulnerabilities(tool_id);
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_severity ON vulnerabilities(severity);

-- Insert common capabilities
INSERT OR IGNORE INTO capabilities (capability_id, name, description, category) VALUES
('cap-web-scraping', 'web-scraping', 'Extract data from websites', 'data-extraction'),
('cap-api-integration', 'api-integration', 'Integrate with external APIs', 'integration'),
('cap-data-analysis', 'data-analysis', 'Analyze and process data', 'analytics'),
('cap-file-processing', 'file-processing', 'Process various file formats', 'file-management'),
('cap-database-ops', 'database-operations', 'Database CRUD operations', 'data-storage'),
('cap-email-sending', 'email-sending', 'Send emails and notifications', 'communication'),
('cap-code-generation', 'code-generation', 'Generate code snippets', 'development'),
('cap-testing', 'testing', 'Run tests and validations', 'quality-assurance'),
('cap-monitoring', 'monitoring', 'Monitor system health', 'operations'),
('cap-security-scan', 'security-scanning', 'Security vulnerability scanning', 'security');

-- Initial migration record
INSERT OR IGNORE INTO migrations (version, description)
VALUES (1, 'Initial schema creation with comprehensive tool management');