# VDW Orchestrator - Windows Setup Guide

## Quick Setup for Windows

This guide is specifically for Windows users who want to run VDW Orchestrator with Qwen Desktop.

## Prerequisites

### 1. Python 3.8+
Check if installed:
```powershell
python --version
```

If not installed, download from: https://www.python.org/downloads/

### 2. Redis

**Option A: Install Redis for Windows (Recommended)**

Using Chocolatey:
```powershell
choco install redis-64
```

Or download from: https://github.com/microsoftarchive/redis/releases

**Option B: Use Docker**
```powershell
docker run -d -p 6379:6379 --name redis redis:latest
```

**Option C: Use WSL2**
```powershell
wsl
sudo apt-get update
sudo apt-get install redis-server
redis-server --daemonize yes
```

### 3. Install Dependencies

```powershell
cd C:\Users\YourName\Desktop\vdw-orchestrator-main
pip install -r requirements.txt
```

## Starting the VDW Orchestrator

### Option 1: PowerShell Script (Easiest)

```powershell
.\start_vdw.ps1
```

### Option 2: Manual Start

**Step 1: Start Redis**
```powershell
# If installed via Chocolatey
redis-server

# Or if using Docker
docker start redis

# Or if using WSL2
wsl redis-server --daemonize yes
```

**Step 2: Start VDW API**
```powershell
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Keep this terminal open!

### Option 3: Background Process

```powershell
# Start in background
Start-Process python -ArgumentList "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000" -WindowStyle Hidden

# Check if running
Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing
```

## Verify It's Running

```powershell
# Test the API
Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing | Select-Object -ExpandProperty Content
```

Should return:
```json
{"service":"vdw-orchestrator","status":"ok"}
```

## Configure Qwen Desktop (Windows)

### 1. Find Qwen Config File

The config file location on Windows:
```
%APPDATA%\Qwen\mcp_config.json
```

Full path example:
```
C:\Users\YourName\AppData\Roaming\Qwen\mcp_config.json
```

### 2. Create/Edit Config File

Open PowerShell as Administrator and run:

```powershell
# Create directory if it doesn't exist
New-Item -ItemType Directory -Force -Path "$env:APPDATA\Qwen"

# Open config file in notepad
notepad "$env:APPDATA\Qwen\mcp_config.json"
```

### 3. Add This Configuration

**Important:** Update the path to match your actual installation directory!

```json
{
  "mcpServers": {
    "vdw-orchestrator": {
      "command": "uvx",
      "args": [
        "--from",
        "C:\\Users\\YourName\\Desktop\\vdw-orchestrator-main",
        "vdw_mcp_server.py"
      ],
      "env": {
        "VDW_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

**Replace `C:\\Users\\YourName\\Desktop\\vdw-orchestrator-main` with your actual path!**

To get your path:
```powershell
cd C:\Users\YourName\Desktop\vdw-orchestrator-main
(Get-Location).Path
```

### 4. Install uv/uvx

Qwen Desktop requires `uvx` to run the MCP server:

```powershell
# Install uv
pip install uv

# Verify installation
uvx --version
```

### 5. Restart Qwen Desktop

Close Qwen Desktop completely and restart it.

## Test with Qwen Desktop

Once configured, try in Qwen:

```
"Use VDW Orchestrator to create a project for building a blog platform"
```

Qwen should respond with a project ID and confirmation!

## Troubleshooting

### "Redis connection refused"

**Problem:** Redis not running

**Solution:**
```powershell
# Check if Redis is running
redis-cli ping

# If not, start it
redis-server

# Or with Docker
docker start redis
```

### "Port 8000 already in use"

**Problem:** Another process using port 8000

**Solution:**
```powershell
# Find process using port 8000
Get-NetTCPConnection -LocalPort 8000

# Stop Python processes
Stop-Process -Name python -Force

# Restart VDW
.\start_vdw.ps1
```

### "uvx: command not found"

**Problem:** uv/uvx not installed

**Solution:**
```powershell
pip install uv

# Add to PATH if needed
$env:Path += ";$env:USERPROFILE\AppData\Local\Programs\Python\Python3XX\Scripts"
```

### "Module not found" errors

**Problem:** Missing dependencies

**Solution:**
```powershell
cd C:\Users\YourName\Desktop\vdw-orchestrator-main
pip install -r requirements.txt
pip install httpx  # Specifically for MCP server
```

### Qwen doesn't see the MCP server

**Solutions:**

1. **Check config path is correct:**
```powershell
Test-Path "$env:APPDATA\Qwen\mcp_config.json"
```

2. **Verify JSON syntax** (no trailing commas!)

3. **Check the path in config matches your installation:**
```powershell
# In config file, the path should match this:
(Get-Location).Path
```

4. **Restart Qwen completely** (not just reload)

5. **Check Qwen logs** for MCP errors

### Test MCP Server Directly

```powershell
cd C:\Users\YourName\Desktop\vdw-orchestrator-main

# Test initialize
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python vdw_mcp_server.py

# Test tools list
echo '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | python vdw_mcp_server.py
```

## Windows-Specific Notes

### Firewall

If you get firewall prompts, allow Python to communicate on private networks.

### Antivirus

Some antivirus software may block Redis or Python. Add exceptions if needed.

### WSL2 Alternative

If you prefer Linux, you can run everything in WSL2:

```powershell
# Install WSL2
wsl --install

# Enter WSL
wsl

# Follow Linux setup instructions
cd /mnt/c/Users/YourName/Desktop/vdw-orchestrator-main
./start_vdw.sh
```

Then configure Qwen to use `http://localhost:8000` (works across WSL2/Windows).

## Stopping the Server

```powershell
# Stop Python processes
Stop-Process -Name python -Force

# Stop Redis
Stop-Process -Name redis-server -Force

# Or if using Docker
docker stop redis
```

## Example PowerShell Session

```powershell
# Navigate to directory
cd C:\Users\leama\OneDrive\Desktop\vdw-orchestrator-main

# Install dependencies (first time only)
pip install -r requirements.txt
pip install httpx uv

# Start Redis (if not running)
redis-server

# Start VDW (in new terminal or background)
.\start_vdw.ps1

# Test it
Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing

# Configure Qwen
notepad "$env:APPDATA\Qwen\mcp_config.json"

# Restart Qwen Desktop and test!
```

## Quick Reference

| Task | Command |
|------|---------|
| Start VDW | `.\start_vdw.ps1` |
| Stop VDW | `Stop-Process -Name python -Force` |
| Check status | `Invoke-WebRequest http://localhost:8000/` |
| View logs | `Get-Content $env:TEMP\vdw_server.log -Wait` |
| Start Redis | `redis-server` |
| Test Redis | `redis-cli ping` |
| Edit Qwen config | `notepad "$env:APPDATA\Qwen\mcp_config.json"` |

## Getting Help

1. Check logs: `Get-Content $env:TEMP\vdw_server.log`
2. Test API: `Invoke-WebRequest http://localhost:8000/`
3. Test MCP: `echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python vdw_mcp_server.py`
4. Review this guide's troubleshooting section

## What's Next?

After setup:
1. ✅ VDW API running on http://localhost:8000
2. ✅ Qwen Desktop configured with MCP server
3. ✅ Ready to create projects from "vibes"!

Try in Qwen:
```
"Use VDW Orchestrator to create a project for a todo app"
```

---

**Windows-specific issues?** Check the troubleshooting section above or review the logs!
