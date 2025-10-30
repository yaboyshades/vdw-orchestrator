# VDW Orchestrator - MCP Integration for Qwen Desktop

## 🎯 What This Is

The **VDW (Vibe-Driven Waterfall) Orchestrator** is now available as an **MCP (Model Context Protocol) server** that works with **Qwen Desktop**!

Transform your unstructured ideas ("vibes") into structured software development plans through natural conversation with Qwen.

## ✨ What You Can Do

- 💭 **Submit a "vibe"** - Describe what you want to build in natural language
- 📋 **Get structured requirements** - System distills your vibe into organized requirements
- 🔄 **Track progress** - See which phase your project is in
- ✅ **Validate outputs** - Approve or request refinement of phase outputs
- 📦 **Access artifacts** - Get all outputs from each development phase

## 🚀 Quick Start (3 Steps)

### 1. Start the VDW API Server

```bash
cd /home/ubuntu/vdw-orchestrator
./start_vdw.sh
```

### 2. Add to Qwen Desktop Config

Add this to your Qwen MCP configuration file:

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

**Config file locations:**
- macOS: `~/Library/Application Support/Qwen/mcp_config.json`
- Linux: `~/.config/Qwen/mcp_config.json`
- Windows: `%APPDATA%\Qwen\mcp_config.json`

### 3. Restart Qwen Desktop

Restart Qwen to load the MCP server, then try:

```
"Use VDW Orchestrator to create a project for building a todo app with React"
```

## 🛠️ Available Tools

| Tool | What It Does | Example |
|------|--------------|---------|
| `vdw_create_project` | Create project from vibe | "Create a VDW project for a blog" |
| `vdw_get_project` | Get project details | "Show me project {id}" |
| `vdw_get_artifacts` | Get all phase outputs | "Get artifacts for {id}" |
| `vdw_validate_phase1` | Approve/reject Phase 1 | "Approve Phase 1 for {id}" |
| `vdw_health_check` | Check if running | "Is VDW running?" |

## 📖 Example Conversation

**You:** "Use VDW to create a project for a real-time chat application"

**Qwen (via vdw_create_project):**
```
✅ VDW Project Created Successfully!

Project ID: 550e8400-e29b-41d4-a716-446655440000

Your vibe has been processed through Phase 1 (Mood & Requirements).
The system has distilled your unstructured idea into structured requirements.
```

**You:** "Show me the project details"

**Qwen (via vdw_get_project):**
```
📊 VDW Project: 550e8400-e29b-41d4-a716-446655440000

Current Phase: PHASE_1_VALIDATION
Original Vibe: real-time chat application

Phase 1: Mood & Requirements
Confidence Score: 0.8

Distilled Requirements:
requirements:
  - id: seg_1
    title: Real-time Chat Core
    content: Build a real-time chat application
    priority: 1
```

## 🏗️ How It Works

```
You → Qwen Desktop → MCP Server → VDW API → Processing

Your "vibe"
    ↓
Conversation Distiller
    ↓
Structured Requirements
    ↓
Phase Agents (1-5)
    ↓
Atoms & Bonds Memory
```

### The VDW 5-Phase Process

1. **Phase 1: Mood & Requirements** ✅ (Working)
   - Distills your vibe into structured requirements
   - Identifies dependencies and priorities
   - Generates validation checklist

2. **Phase 2: Architecture & Design** ⚠️ (Partial)
   - Designs system architecture
   - Creates component diagrams

3. **Phase 3: Technical Specification** ⏳ (Not yet implemented)
   - Detailed technical specs
   - API definitions

4. **Phase 4: Implementation** ⏳ (Not yet implemented)
   - Code generation
   - Implementation plans

5. **Phase 5: Validation & Testing** ⏳ (Not yet implemented)
   - Test plans
   - Quality assurance

## 🔧 Troubleshooting

### MCP server not connecting

```bash
# Check if API is running
curl http://localhost:8000/

# If not, start it
cd /home/ubuntu/vdw-orchestrator
./start_vdw.sh
```

### Test MCP server directly

```bash
cd /home/ubuntu/vdw-orchestrator

# Test initialize
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python3 vdw_mcp_server.py

# Test tools list
echo '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | python3 vdw_mcp_server.py
```

### Check logs

```bash
# API server logs
tail -f /tmp/vdw_server.log

# Check if Redis is running
redis-cli ping
```

## 📚 Documentation

- **Quick Setup:** `QWEN_SETUP.md` - Step-by-step Qwen integration
- **Full Guide:** `MCP_SETUP_GUIDE.md` - Complete technical documentation
- **Test Report:** `TEST_REPORT.md` - System test results
- **Fixes Applied:** `FIXES_APPLIED.md` - All fixes during installation

## 🎓 Understanding "Vibes"

A "vibe" is your unstructured idea or vision. Examples:

❌ **Don't overthink it:**
```
"I need a RESTful API with JWT authentication, PostgreSQL database,
Redis caching, Docker containerization, and CI/CD pipeline..."
```

✅ **Just describe what you want:**
```
"I want to build a blog where people can comment"
"Make me a todo app"
"Real-time chat with rooms"
```

The VDW Orchestrator will structure it for you!

## 🔄 Current Status

| Feature | Status | Notes |
|---------|--------|-------|
| MCP Server | ✅ Working | Fully functional stdio server |
| Phase 1 Processing | ✅ Working | Vibe → Requirements |
| Project Management | ✅ Working | Create, retrieve, validate |
| Memory Storage | ✅ Working | Atoms & Bonds persistence |
| Phase 2-5 | ⏳ Partial | Need implementation |
| Mangle Reasoning | ⚠️ Stub | gRPC server not deployed |

## 🚦 Getting Started Checklist

- [ ] Start Redis: `redis-server --daemonize yes`
- [ ] Start VDW API: `./start_vdw.sh`
- [ ] Verify API: `curl http://localhost:8000/`
- [ ] Add config to Qwen Desktop
- [ ] Restart Qwen Desktop
- [ ] Test: "Use VDW to create a project for..."

## 💡 Pro Tips

1. **Be creative with vibes** - The system handles informal language
2. **Check project status** - Use `vdw_get_project` to see progress
3. **Iterate on requirements** - Reject Phase 1 with feedback to refine
4. **Save project IDs** - You'll need them to access projects later

## 🤝 Contributing

The VDW Orchestrator is open for development:

- **Phase 2-5 agents** need implementation
- **Mangle reasoning engine** needs gRPC deployment
- **Tool synthesis** needs completion
- **Testing** needs expansion

## 📞 Support

If you encounter issues:

1. Check `QWEN_SETUP.md` troubleshooting section
2. Review logs: `tail -f /tmp/vdw_server.log`
3. Test API directly: `curl http://localhost:8000/`
4. Test MCP server: See troubleshooting section above

## 🎉 You're Ready!

Start transforming your vibes into structured development plans with Qwen Desktop!

```
"Use VDW Orchestrator to create a project for [your idea here]"
```

---

**Built with:** FastAPI, Redis, Pydantic, MCP Protocol  
**Compatible with:** Qwen Desktop, Claude Desktop (MCP clients)  
**Version:** 0.1.0
