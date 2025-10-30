# VDW Orchestrator - Qwen Desktop Setup Guide

## Quick Start for Qwen Desktop

This guide shows you how to configure the VDW Orchestrator as an MCP server in Qwen Desktop.

## Prerequisites

✅ **Python 3.8+** (installed)  
✅ **uv/uvx** (installed)  
✅ **Redis** (will be started automatically)  
✅ **Qwen Desktop** (with MCP support)

## Step 1: Start the VDW Orchestrator API

The MCP server communicates with the VDW Orchestrator REST API, so you need to start it first.

### Option A: Quick Start (Recommended)

```bash
cd /home/ubuntu/vdw-orchestrator
./start_vdw.sh
```

This script will:
- Start Redis if not running
- Start the VDW API server on port 8000
- Verify everything is working

### Option B: Manual Start

```bash
# Start Redis
redis-server --daemonize yes

# Start VDW Orchestrator
cd /home/ubuntu/vdw-orchestrator
python3.11 -m uvicorn main:app --host 0.0.0.0 --port 8000 &
```

### Verify It's Running

```bash
curl http://localhost:8000/
# Should return: {"service":"vdw-orchestrator","status":"ok"}
```

## Step 2: Configure Qwen Desktop

Add this configuration to your Qwen Desktop MCP settings:

```json
{
  "mcpServers": {
    "vdw-orchestrator": {
      "command": "uvx",
      "args": [
        "--from",
        "/home/ubuntu/vdw-orchestrator",
        "vdw_mcp_server.py"
      ],
      "env": {
        "VDW_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

### Where to Add This Config

The location depends on your Qwen Desktop version:

**macOS:**
```
~/Library/Application Support/Qwen/mcp_config.json
```

**Linux:**
```
~/.config/Qwen/mcp_config.json
```

**Windows:**
```
%APPDATA%\Qwen\mcp_config.json
```

## Step 3: Restart Qwen Desktop

After adding the configuration, restart Qwen Desktop to load the MCP server.

## Step 4: Test It!

In Qwen Desktop, try these commands:

### Example 1: Create a Project
```
Use VDW Orchestrator to create a project for building a real-time chat application
```

Qwen will call `vdw_create_project` and return:
```
✅ VDW Project Created Successfully!

Project ID: abc-123-def-456

Your vibe has been processed through Phase 1 (Mood & Requirements).
The system has distilled your unstructured idea into structured requirements.
```

### Example 2: Get Project Details
```
Show me the details of VDW project abc-123-def-456
```

Qwen will call `vdw_get_project` and show:
- Current phase
- Original vibe
- Distilled requirements in YAML format
- Validation checklist

### Example 3: Check Health
```
Check if VDW Orchestrator is running
```

Qwen will call `vdw_health_check` and confirm the service status.

## Available MCP Tools

| Tool | Description | Example Usage |
|------|-------------|---------------|
| `vdw_create_project` | Create project from vibe | "Create a VDW project for a blog platform" |
| `vdw_get_project` | Get project details | "Show me VDW project {id}" |
| `vdw_get_artifacts` | Get all phase outputs | "Get artifacts for VDW project {id}" |
| `vdw_validate_phase1` | Approve/reject Phase 1 | "Approve Phase 1 for project {id}" |
| `vdw_health_check` | Check service health | "Is VDW Orchestrator running?" |

## How It Works

```
┌─────────────────┐
│  Qwen Desktop   │  You: "Create a VDW project for a todo app"
└────────┬────────┘
         │ MCP Protocol (stdio)
         ▼
┌─────────────────┐
│ vdw_mcp_server  │  Translates MCP → HTTP
│   (uvx runs)    │
└────────┬────────┘
         │ HTTP REST API
         ▼
┌─────────────────┐
│ VDW Orchestrator│  Processes your "vibe"
│   (FastAPI)     │
└────────┬────────┘
         │
    ┌────┴────┬──────────┐
    ▼         ▼          ▼
┌──────┐ ┌────────┐ ┌────────┐
│Redis │ │ Memory │ │ Agents │
└──────┘ └────────┘ └────────┘
```

### The VDW Process

1. **You provide a "vibe"** - Unstructured idea (e.g., "I want a chat app")
2. **Phase 1: Mood & Requirements** - System distills into structured requirements
3. **Phase 2: Architecture** - Designs system architecture (partial)
4. **Phase 3: Specification** - Creates technical specs (not yet implemented)
5. **Phase 4: Implementation** - Generates code (not yet implemented)
6. **Phase 5: Validation** - Tests and validates (not yet implemented)

Currently, **Phase 1 is fully working** and will process your vibe into structured requirements!

## Troubleshooting

### "Connection refused" error

**Problem:** MCP server can't reach the API

**Solution:**
```bash
# Check if API is running
curl http://localhost:8000/

# If not, start it
cd /home/ubuntu/vdw-orchestrator
./start_vdw.sh
```

### "uvx: command not found"

**Problem:** uv/uvx not installed

**Solution:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or use pip
pip install uv
```

### "httpx is required" error

**Problem:** Missing Python dependency

**Solution:**
```bash
cd /home/ubuntu/vdw-orchestrator
pip3 install httpx
```

### Qwen doesn't see the MCP server

**Problem:** Configuration not loaded

**Solutions:**
1. Check config file location is correct
2. Verify JSON syntax (no trailing commas!)
3. Restart Qwen Desktop completely
4. Check Qwen logs for MCP server errors

### Test the MCP server directly

You can test the MCP server without Qwen:

```bash
cd /home/ubuntu/vdw-orchestrator

# Test with echo
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python3 vdw_mcp_server.py

# Should return initialization response
```

## Advanced Configuration

### Change API URL

If your VDW API is running on a different host/port:

```json
{
  "mcpServers": {
    "vdw-orchestrator": {
      "command": "uvx",
      "args": ["--from", "/home/ubuntu/vdw-orchestrator", "vdw_mcp_server.py"],
      "env": {
        "VDW_API_URL": "http://your-host:your-port"
      }
    }
  }
}
```

### Run API on Remote Server

If you want to run the API on a remote server:

1. Start the API on the remote server:
```bash
ssh user@remote-server
cd /home/ubuntu/vdw-orchestrator
./start_vdw.sh
```

2. Update Qwen config with remote URL:
```json
"VDW_API_URL": "http://remote-server:8000"
```

## Example Workflow

Here's a complete example of using VDW Orchestrator through Qwen:

**Step 1: Create Project**
```
You: "Use VDW to create a project for a blog platform with comments and user auth"

Qwen: ✅ VDW Project Created!
      Project ID: 550e8400-e29b-41d4-a716-446655440000
```

**Step 2: Review Requirements**
```
You: "Show me the project details"

Qwen: 📊 VDW Project: 550e8400-e29b-41d4-a716-446655440000
      Current Phase: PHASE_1_VALIDATION
      
      Phase 1: Mood & Requirements
      Confidence Score: 0.8
      
      Distilled Requirements:
      requirements:
        - id: seg_1
          title: Blog Platform Core
          content: Build a blog platform with comments and user authentication
          priority: 1
```

**Step 3: Approve and Continue**
```
You: "Approve Phase 1 for this project"

Qwen: ✅ Phase 1 Approved!
      Transitioning to Phase 2 (Architecture & Design)...
```

## What's Next?

After setup, you can:

1. ✅ Create projects from natural language "vibes"
2. ✅ Get structured requirements automatically
3. ✅ Review and validate Phase 1 outputs
4. ⏳ Phase 2-5 (coming soon - need implementation)

## Resources

- **Test Report:** `TEST_REPORT.md`
- **Fixes Applied:** `FIXES_APPLIED.md`
- **Full Setup Guide:** `MCP_SETUP_GUIDE.md`
- **API Docs:** http://localhost:8000/docs (when running)

## Support

If you encounter issues:

1. Check the API logs: `tail -f /tmp/vdw_server.log`
2. Test the API directly: `curl http://localhost:8000/`
3. Test the MCP server: `echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python3 vdw_mcp_server.py`
4. Review this guide's troubleshooting section

---

**Ready to transform your vibes into structured development plans!** 🚀
