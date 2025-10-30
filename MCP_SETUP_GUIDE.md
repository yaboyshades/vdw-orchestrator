# VDW Orchestrator - MCP Server Setup Guide for Qwen Desktop

## Overview

The VDW Orchestrator can be used as an MCP (Model Context Protocol) server with Qwen Desktop. Currently, the system is implemented as a **FastAPI REST API** rather than a native MCP stdio server, but it can still be integrated with MCP-compatible clients.

## Architecture

```
┌─────────────────┐
│  Qwen Desktop   │
│   (MCP Client)  │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  VDW Orchestr.  │
│  FastAPI Server │
│   (Port 8000)   │
└────────┬────────┘
         │
    ┌────┴────┬──────────┐
    ▼         ▼          ▼
┌──────┐ ┌────────┐ ┌────────┐
│Redis │ │ Memory │ │ Mangle │
│      │ │ Store  │ │(stub)  │
└──────┘ └────────┘ └────────┘
```

## Current Implementation Status

### ✅ Available (REST API)
- **Project Management**: Create and manage VDW projects
- **Phase 1 Processing**: Vibe distillation and requirements extraction
- **State Management**: Phase transitions and validation
- **Memory Storage**: Atoms and Bonds persistence
- **Tool Registry**: MCP Box for tool management

### ⚠️ Not Yet Available (Native MCP)
- **stdio MCP Server**: Not implemented (uses HTTP instead)
- **MCP Tool Definitions**: Need to be exposed via MCP protocol
- **Direct MCP Integration**: Requires wrapper or adapter

## Setup Options

### Option 1: REST API Integration (Current)

The VDW Orchestrator runs as a REST API that can be accessed via HTTP.

#### 1. Start the Server

```bash
# Navigate to the repository
cd /home/ubuntu/vdw-orchestrator

# Ensure Redis is running
redis-server --daemonize yes

# Start the VDW Orchestrator
python3.11 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

#### 2. Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /` | GET | Health check |
| `POST /projects` | POST | Create new VDW project |
| `GET /projects/{id}` | GET | Get project details |
| `GET /projects/{id}/artifacts` | GET | Get project artifacts |
| `POST /projects/{id}/validate/phase-1` | POST | Validate Phase 1 |
| `GET /tools` | GET | List available tools |
| `POST /tools` | POST | Register new tool |

#### 3. Example Usage

**Create a Project:**
```bash
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{
    "vibe": "I want to build a real-time chat application with WebSockets"
  }'
```

**Response:**
```json
{
  "project_id": "10e200a9-4e06-4fb0-bee4-bcb016144925"
}
```

**Get Project Details:**
```bash
curl http://localhost:8000/projects/10e200a9-4e06-4fb0-bee4-bcb016144925
```

### Option 2: Create MCP Wrapper (Recommended for Qwen Desktop)

To use with Qwen Desktop's MCP client, you'll need to create an MCP stdio wrapper.

#### Create MCP Server Wrapper

Create a file `mcp_wrapper.py`:

```python
#!/usr/bin/env python3.11
"""MCP stdio wrapper for VDW Orchestrator"""

import sys
import json
import asyncio
import httpx
from typing import Any, Dict

# MCP Server base URL
BASE_URL = "http://localhost:8000"

async def handle_mcp_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP protocol requests and forward to REST API"""
    
    method = request.get("method")
    params = request.get("params", {})
    
    async with httpx.AsyncClient() as client:
        if method == "tools/list":
            # Return available VDW tools
            return {
                "tools": [
                    {
                        "name": "vdw_create_project",
                        "description": "Create a new VDW project from a vibe",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "vibe": {
                                    "type": "string",
                                    "description": "Unstructured description of what you want to build"
                                }
                            },
                            "required": ["vibe"]
                        }
                    },
                    {
                        "name": "vdw_get_project",
                        "description": "Get details of a VDW project",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_id": {
                                    "type": "string",
                                    "description": "Project ID"
                                }
                            },
                            "required": ["project_id"]
                        }
                    },
                    {
                        "name": "vdw_get_artifacts",
                        "description": "Get all artifacts from a VDW project",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_id": {
                                    "type": "string",
                                    "description": "Project ID"
                                }
                            },
                            "required": ["project_id"]
                        }
                    }
                ]
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "vdw_create_project":
                response = await client.post(
                    f"{BASE_URL}/projects",
                    json={"vibe": arguments["vibe"]}
                )
                return {"content": [{"type": "text", "text": response.text}]}
            
            elif tool_name == "vdw_get_project":
                response = await client.get(
                    f"{BASE_URL}/projects/{arguments['project_id']}"
                )
                return {"content": [{"type": "text", "text": response.text}]}
            
            elif tool_name == "vdw_get_artifacts":
                response = await client.get(
                    f"{BASE_URL}/projects/{arguments['project_id']}/artifacts"
                )
                return {"content": [{"type": "text", "text": response.text}]}
        
        return {"error": "Unknown method"}

async def main():
    """Main MCP stdio loop"""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line)
            response = await handle_mcp_request(request)
            
            print(json.dumps(response))
            sys.stdout.flush()
            
        except Exception as e:
            error_response = {"error": str(e)}
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())
```

#### Make it executable:
```bash
chmod +x mcp_wrapper.py
```

### Option 3: Use Meta-Review MCP Server

The repository includes a more advanced MCP server in `reasoning/meta_review/mcp_server.py` that provides meta-review capabilities. This could be adapted for full VDW integration.

## Qwen Desktop Configuration

### For REST API (Option 1)

In Qwen Desktop, you would configure it to make HTTP requests to the VDW Orchestrator API endpoints.

### For MCP Wrapper (Option 2)

Add to your Qwen Desktop MCP configuration:

```json
{
  "mcpServers": {
    "vdw-orchestrator": {
      "command": "python3.11",
      "args": ["/home/ubuntu/vdw-orchestrator/mcp_wrapper.py"],
      "env": {
        "VDW_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

## How the VDW Orchestrator Works

### 1. **Vibe Input** (Phase 1: Mood)
User provides an unstructured "vibe" describing what they want to build.

**Example:**
```
"I want to build a real-time chat application with WebSockets"
```

### 2. **Conversation Distillation**
The system processes the vibe through the ConversationDistiller:
- Parses into logical segments
- Identifies dependencies
- Generates structured requirements
- Creates validation checklist

**Output:**
```yaml
requirements:
  - id: seg_1
    title: Requirement 1
    content: Build a real-time chat application with WebSockets
    priority: 1
```

### 3. **Phase Progression**
The orchestrator manages progression through 5 phases:
1. **Phase 1: Mood & Requirements** ✅ (Working)
2. **Phase 2: Architecture & Design** ⚠️ (Partial)
3. **Phase 3: Technical Specification** ❌ (Not implemented)
4. **Phase 4: Implementation** ❌ (Not implemented)
5. **Phase 5: Validation & Testing** ❌ (Not implemented)

### 4. **State Machine**
Manages valid transitions between phases with validation gates.

### 5. **Memory Store (Atoms & Bonds)**
All artifacts are stored as:
- **Atoms**: Individual knowledge units (project data, phase outputs)
- **Bonds**: Relationships between atoms

## Testing the Integration

### 1. Start the Server
```bash
cd /home/ubuntu/vdw-orchestrator
redis-server --daemonize yes
python3.11 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. Test with curl
```bash
# Health check
curl http://localhost:8000/

# Create project
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{"vibe": "Build a todo app with React"}'

# Get project (replace with actual ID)
curl http://localhost:8000/projects/{project_id}
```

### 3. Test with Qwen Desktop
Once configured, you can use natural language:
```
"Use VDW Orchestrator to create a project for building a blog platform"
```

## Troubleshooting

### Server won't start
- Check if Redis is running: `redis-cli ping`
- Check port 8000 is available: `lsof -i :8000`
- Check logs: `tail -f /tmp/server.log`

### Connection refused
- Ensure server is running on correct host/port
- Check firewall settings
- Verify BASE_URL in wrapper script

### No response from tools
- Check server logs for errors
- Verify JSON format of requests
- Ensure all dependencies are installed

## Next Steps

To fully integrate with Qwen Desktop as a native MCP server:

1. **Implement MCP stdio protocol** in main.py
2. **Add MCP tool definitions** for all VDW operations
3. **Complete remaining phase agents** (3, 4, 5)
4. **Deploy Mangle reasoning engine**
5. **Add streaming support** for long-running operations
6. **Implement progress notifications**

## Resources

- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [VDW Orchestrator Documentation](./docs/)
- [Test Report](./TEST_REPORT.md)
- [Fixes Applied](./FIXES_APPLIED.md)
