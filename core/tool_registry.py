"""MCP Box: Advanced Tool Registry with SQLite Backend

This module implements the "MCP Box" concept - a persistent, organized repository
for reusable MCP tools that enables autonomous tool synthesis and cross-project
learning. It provides comprehensive tool lifecycle management with performance
tracking and dependency analysis.
"""

import sqlite3
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging
import uuid

from .models import ToolMetadata, ToolCapability


class MCPBoxRegistry:
    """Advanced tool registry implementing the MCP Box concept
    
    This registry provides:
    - SQLite-backed persistent storage
    - Tool lifecycle management (creation, versioning, deprecation)
    - Performance tracking and analytics
    - Dependency analysis
    - Runtime tool registration/deregistration
    - Cross-project tool reuse
    """
    
    def __init__(self, db_path: str = "data/mcp_box.db"):
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache for frequently accessed tools
        self._tool_cache: Dict[str, ToolMetadata] = {}
        self._capability_index: Dict[str, List[str]] = {}  # capability -> tool_ids
        self._initialized = False
    
    async def _initialize_database(self):
        """Initialize SQLite database with comprehensive schema"""
        async with self._get_connection() as conn:
            await conn.executescript("""
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
            """)
            
            # Insert initial migration record
            await conn.execute("""
                INSERT OR IGNORE INTO migrations (version, description)
                VALUES (1, 'Initial schema creation with comprehensive tool management')
            """)
            
            await conn.commit()
            
        self.logger.info("MCP Box database initialized successfully")
        await self._refresh_cache()
    
    async def _get_connection(self) -> sqlite3.Connection:
        """Get async database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    async def register_tool(self, tool_metadata: ToolMetadata) -> bool:
        """Register a new tool in the MCP Box
        
        Args:
            tool_metadata: Complete tool metadata
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            async with self._get_connection() as conn:
                # Insert tool record
                await conn.execute("""
                    INSERT INTO tools (
                        tool_id, name, description, version, server_url,
                        input_schema, output_schema, created_by, created_at,
                        metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tool_metadata.tool_id,
                    tool_metadata.name,
                    tool_metadata.description,
                    tool_metadata.version,
                    None,  # server_url - to be added later
                    None,  # input_schema - to be added later
                    None,  # output_schema - to be added later
                    tool_metadata.created_by,
                    tool_metadata.created_at.isoformat(),
                    json.dumps(tool_metadata.performance_metrics)
                ))
                
                # Register capabilities
                for capability in tool_metadata.capabilities:
                    capability_id = str(uuid.uuid4())
                    
                    # Insert capability if it doesn't exist
                    await conn.execute("""
                        INSERT OR IGNORE INTO capabilities (capability_id, name, description)
                        VALUES (?, ?, ?)
                    """, (capability_id, capability.name, capability.description))
                    
                    # Get capability ID
                    cursor = await conn.execute(
                        "SELECT capability_id FROM capabilities WHERE name = ?",
                        (capability.name,)
                    )
                    row = await cursor.fetchone()
                    if row:
                        capability_id = row['capability_id']
                    
                    # Link tool to capability
                    await conn.execute("""
                        INSERT INTO tool_capabilities (tool_id, capability_id, strength)
                        VALUES (?, ?, ?)
                    """, (tool_metadata.tool_id, capability_id, capability.strength))
                
                # Register dependencies
                for dep_tool_id in tool_metadata.depends_on:
                    await conn.execute("""
                        INSERT INTO dependencies (dependent_tool_id, dependency_tool_id)
                        VALUES (?, ?)
                    """, (tool_metadata.tool_id, dep_tool_id))
                
                await conn.commit()
            
            # Update cache
            self._tool_cache[tool_metadata.tool_id] = tool_metadata
            await self._update_capability_index(tool_metadata)
            
            self.logger.info(f"Successfully registered tool: {tool_metadata.name} ({tool_metadata.tool_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register tool {tool_metadata.tool_id}: {e}")
            return False
    
    async def find_tools_by_capability(self, capability_name: str, min_strength: float = 0.5) -> List[ToolMetadata]:
        """Find tools that provide a specific capability
        
        Args:
            capability_name: Name of the capability to search for
            min_strength: Minimum strength rating (0.0 to 1.0)
            
        Returns:
            List of tools that provide the capability
        """
        tools = []
        
        try:
            async with self._get_connection() as conn:
                cursor = await conn.execute("""
                    SELECT t.*, tc.strength
                    FROM tools t
                    JOIN tool_capabilities tc ON t.tool_id = tc.tool_id
                    JOIN capabilities c ON tc.capability_id = c.capability_id
                    WHERE c.name = ? AND tc.strength >= ? AND t.deprecated = FALSE
                    ORDER BY tc.strength DESC, t.usage_count DESC
                """, (capability_name, min_strength))
                
                rows = await cursor.fetchall()
                for row in rows:
                    tool = await self._row_to_tool_metadata(row)
                    if tool:
                        tools.append(tool)
        
        except Exception as e:
            self.logger.error(f"Failed to find tools by capability {capability_name}: {e}")
        
        return tools
    
    async def analyze_capability_gap(self, required_capabilities: List[str]) -> Dict[str, Any]:
        """Analyze gaps in available capabilities using stratified negation logic
        
        Args:
            required_capabilities: List of capability names needed
            
        Returns:
            Analysis of capability gaps and recommendations
        """
        analysis = {
            "missing_capabilities": [],
            "weak_capabilities": [],
            "recommendations": [],
            "coverage_score": 0.0
        }
        
        try:
            covered_capabilities = 0
            
            for capability in required_capabilities:
                tools = await self.find_tools_by_capability(capability, min_strength=0.1)
                
                if not tools:
                    analysis["missing_capabilities"].append(capability)
                    analysis["recommendations"].append(
                        f"Create new tool for '{capability}' capability"
                    )
                else:
                    # Check if we have strong tools for this capability
                    strong_tools = [t for t in tools if any(
                        cap.strength >= 0.7 for cap in t.capabilities 
                        if cap.name == capability
                    )]
                    
                    if not strong_tools:
                        analysis["weak_capabilities"].append(capability)
                        analysis["recommendations"].append(
                            f"Improve existing tools for '{capability}' capability"
                        )
                    
                    covered_capabilities += 1
            
            analysis["coverage_score"] = covered_capabilities / len(required_capabilities) if required_capabilities else 1.0
            
        except Exception as e:
            self.logger.error(f"Failed to analyze capability gap: {e}")
        
        return analysis
    
    async def record_tool_usage(self, tool_id: str, project_id: str, duration_ms: float, 
                               success: bool, error_message: Optional[str] = None,
                               additional_metrics: Optional[Dict[str, Any]] = None) -> bool:
        """Record tool usage for performance tracking and analytics
        
        Args:
            tool_id: ID of the tool that was used
            project_id: ID of the project using the tool
            duration_ms: Execution duration in milliseconds
            success: Whether the execution was successful
            error_message: Error message if execution failed
            additional_metrics: Additional performance metrics
            
        Returns:
            True if recorded successfully
        """
        try:
            log_id = str(uuid.uuid4())
            now = datetime.now()
            start_time = now
            end_time = now
            
            async with self._get_connection() as conn:
                # Insert performance log
                await conn.execute("""
                    INSERT INTO performance_logs (
                        log_id, tool_id, project_id, execution_start, execution_end,
                        duration_ms, success, error_message, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    log_id, tool_id, project_id, start_time.isoformat(), end_time.isoformat(),
                    duration_ms, success, error_message, 
                    json.dumps(additional_metrics or {})
                ))
                
                # Update tool statistics
                await conn.execute("""
                    UPDATE tools SET
                        usage_count = usage_count + 1,
                        last_used = ?,
                        success_rate = (
                            SELECT CAST(SUM(CASE WHEN success THEN 1 ELSE 0 END) AS REAL) / COUNT(*)
                            FROM performance_logs
                            WHERE tool_id = ?
                        ),
                        average_duration = (
                            SELECT AVG(duration_ms)
                            FROM performance_logs
                            WHERE tool_id = ?
                        )
                    WHERE tool_id = ?
                """, (now.isoformat(), tool_id, tool_id, tool_id))
                
                await conn.commit()
            
            # Update cache
            if tool_id in self._tool_cache:
                self._tool_cache[tool_id].record_usage(duration_ms / 1000.0, success)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to record tool usage for {tool_id}: {e}")
            return False
    
    async def get_performance_analytics(self, tool_id: Optional[str] = None, 
                                       project_id: Optional[str] = None,
                                       days: int = 30) -> Dict[str, Any]:
        """Get performance analytics for tools
        
        Args:
            tool_id: Specific tool ID to analyze (optional)
            project_id: Specific project ID to analyze (optional)
            days: Number of days to look back
            
        Returns:
            Performance analytics data
        """
        analytics = {
            "total_executions": 0,
            "success_rate": 0.0,
            "average_duration_ms": 0.0,
            "slowest_tools": [],
            "most_used_tools": [],
            "error_patterns": []
        }
        
        try:
            async with self._get_connection() as conn:
                # Build WHERE clause
                where_conditions = ["execution_start >= datetime('now', '-{} days')".format(days)]
                params = []
                
                if tool_id:
                    where_conditions.append("tool_id = ?")
                    params.append(tool_id)
                
                if project_id:
                    where_conditions.append("project_id = ?")
                    params.append(project_id)
                
                where_clause = " AND ".join(where_conditions)
                
                # Get basic statistics
                cursor = await conn.execute(f"""
                    SELECT 
                        COUNT(*) as total_executions,
                        CAST(SUM(CASE WHEN success THEN 1 ELSE 0 END) AS REAL) / COUNT(*) as success_rate,
                        AVG(duration_ms) as avg_duration
                    FROM performance_logs
                    WHERE {where_clause}
                """, params)
                
                row = await cursor.fetchone()
                if row:
                    analytics["total_executions"] = row["total_executions"]
                    analytics["success_rate"] = row["success_rate"] or 0.0
                    analytics["average_duration_ms"] = row["avg_duration"] or 0.0
                
                # Get slowest tools
                cursor = await conn.execute(f"""
                    SELECT t.name, t.tool_id, AVG(pl.duration_ms) as avg_duration
                    FROM performance_logs pl
                    JOIN tools t ON pl.tool_id = t.tool_id
                    WHERE {where_clause}
                    GROUP BY t.tool_id
                    ORDER BY avg_duration DESC
                    LIMIT 10
                """, params)
                
                analytics["slowest_tools"] = [
                    {"name": row["name"], "tool_id": row["tool_id"], "avg_duration_ms": row["avg_duration"]}
                    for row in await cursor.fetchall()
                ]
                
                # Get most used tools
                cursor = await conn.execute(f"""
                    SELECT t.name, t.tool_id, COUNT(*) as usage_count
                    FROM performance_logs pl
                    JOIN tools t ON pl.tool_id = t.tool_id
                    WHERE {where_clause}
                    GROUP BY t.tool_id
                    ORDER BY usage_count DESC
                    LIMIT 10
                """, params)
                
                analytics["most_used_tools"] = [
                    {"name": row["name"], "tool_id": row["tool_id"], "usage_count": row["usage_count"]}
                    for row in await cursor.fetchall()
                ]
        
        except Exception as e:
            self.logger.error(f"Failed to get performance analytics: {e}")
        
        return analytics
    
    async def deprecate_tool(self, tool_id: str, reason: str, replacement_tool_id: Optional[str] = None) -> bool:
        """Deprecate a tool and optionally specify a replacement
        
        Args:
            tool_id: ID of the tool to deprecate
            reason: Reason for deprecation
            replacement_tool_id: Optional ID of replacement tool
            
        Returns:
            True if deprecation successful
        """
        try:
            async with self._get_connection() as conn:
                await conn.execute("""
                    UPDATE tools SET
                        deprecated = TRUE,
                        deprecation_reason = ?,
                        replacement_tool_id = ?
                    WHERE tool_id = ?
                """, (reason, replacement_tool_id, tool_id))
                
                await conn.commit()
            
            # Update cache
            if tool_id in self._tool_cache:
                self._tool_cache[tool_id].deprecated = True
                self._tool_cache[tool_id].deprecation_reason = reason
                self._tool_cache[tool_id].replacement_tool_id = replacement_tool_id
            
            self.logger.info(f"Successfully deprecated tool {tool_id}: {reason}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deprecate tool {tool_id}: {e}")
            return False
    
    async def _row_to_tool_metadata(self, row: sqlite3.Row) -> Optional[ToolMetadata]:
        """Convert database row to ToolMetadata object"""
        try:
            # Get capabilities for this tool
            capabilities = []
            async with self._get_connection() as conn:
                cursor = await conn.execute("""
                    SELECT c.name, c.description, tc.strength
                    FROM capabilities c
                    JOIN tool_capabilities tc ON c.capability_id = tc.capability_id
                    WHERE tc.tool_id = ?
                """, (row["tool_id"],))
                
                cap_rows = await cursor.fetchall()
                for cap_row in cap_rows:
                    capabilities.append(ToolCapability(
                        name=cap_row["name"],
                        description=cap_row["description"],
                        strength=cap_row["strength"]
                    ))
            
            # Get dependencies
            depends_on = []
            async with self._get_connection() as conn:
                cursor = await conn.execute("""
                    SELECT dependency_tool_id
                    FROM dependencies
                    WHERE dependent_tool_id = ?
                """, (row["tool_id"],))
                
                dep_rows = await cursor.fetchall()
                depends_on = [dep_row["dependency_tool_id"] for dep_row in dep_rows]
            
            return ToolMetadata(
                tool_id=row["tool_id"],
                name=row["name"],
                description=row["description"],
                version=row["version"],
                capabilities=capabilities,
                created_by=row["created_by"],
                created_at=datetime.fromisoformat(row["created_at"]),
                last_used=datetime.fromisoformat(row["last_used"]) if row["last_used"] else None,
                usage_count=row["usage_count"],
                success_rate=row["success_rate"],
                average_duration=row["average_duration"],
                performance_metrics=json.loads(row["metadata"]) if row["metadata"] else {},
                deprecated=bool(row["deprecated"]),
                deprecation_reason=row["deprecation_reason"],
                replacement_tool_id=row["replacement_tool_id"],
                depends_on=depends_on
            )
            
        except Exception as e:
            self.logger.error(f"Failed to convert row to ToolMetadata: {e}")
            return None
    
    async def _refresh_cache(self):
        """Refresh in-memory cache from database"""
        try:
            async with self._get_connection() as conn:
                cursor = await conn.execute("SELECT * FROM tools WHERE deprecated = FALSE")
                rows = await cursor.fetchall()
                
                self._tool_cache.clear()
                self._capability_index.clear()
                
                for row in rows:
                    tool = await self._row_to_tool_metadata(row)
                    if tool:
                        self._tool_cache[tool.tool_id] = tool
                        await self._update_capability_index(tool)
        
        except Exception as e:
            self.logger.error(f"Failed to refresh cache: {e}")
    
    async def _update_capability_index(self, tool: ToolMetadata):
        """Update the capability index for fast lookups"""
        for capability in tool.capabilities:
            if capability.name not in self._capability_index:
                self._capability_index[capability.name] = []
            
            if tool.tool_id not in self._capability_index[capability.name]:
                self._capability_index[capability.name].append(tool.tool_id)
    
    async def get_tool_by_id(self, tool_id: str) -> Optional[ToolMetadata]:
        """Get tool by ID, using cache when possible"""
        if tool_id in self._tool_cache:
            return self._tool_cache[tool_id]
        
        try:
            async with self._get_connection() as conn:
                cursor = await conn.execute("SELECT * FROM tools WHERE tool_id = ?", (tool_id,))
                row = await cursor.fetchone()
                
                if row:
                    tool = await self._row_to_tool_metadata(row)
                    if tool:
                        self._tool_cache[tool_id] = tool
                    return tool
        
        except Exception as e:
            self.logger.error(f"Failed to get tool {tool_id}: {e}")
        
        return None
    
    async def list_tools(self, include_deprecated: bool = False, 
                        created_by: Optional[str] = None) -> List[ToolMetadata]:
        """List all tools with optional filtering
        
        Args:
            include_deprecated: Whether to include deprecated tools
            created_by: Filter by creator project ID
            
        Returns:
            List of tool metadata
        """
        tools = []
        
        try:
            conditions = []
            params = []
            
            if not include_deprecated:
                conditions.append("deprecated = FALSE")
            
            if created_by:
                conditions.append("created_by = ?")
                params.append(created_by)
            
            where_clause = ""
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)
            
            async with self._get_connection() as conn:
                cursor = await conn.execute(f"SELECT * FROM tools {where_clause} ORDER BY created_at DESC", params)
                rows = await cursor.fetchall()
                
                for row in rows:
                    tool = await self._row_to_tool_metadata(row)
                    if tool:
                        tools.append(tool)
        
        except Exception as e:
            self.logger.error(f"Failed to list tools: {e}")
        
        return tools