#!/bin/bash
# VDW Orchestrator - Quick Start Script

set -e

echo "🚀 Starting VDW Orchestrator..."
echo ""

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "📦 Starting Redis..."
    redis-server --daemonize yes
    sleep 2
    echo "✅ Redis started"
else
    echo "✅ Redis already running"
fi

# Check if server is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Server already running on port 8000"
    echo "   To restart, run: pkill -f 'uvicorn main:app' && ./start_vdw.sh"
    exit 1
fi

# Start the VDW Orchestrator
echo "🎯 Starting VDW Orchestrator API server..."
cd /home/ubuntu/vdw-orchestrator
python3.11 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/vdw_server.log 2>&1 &
SERVER_PID=$!

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 3

# Check if server is running
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ VDW Orchestrator is running!"
    echo ""
    echo "📊 Server Status:"
    curl -s http://localhost:8000/ | python3.11 -m json.tool
    echo ""
    echo "🔗 API Endpoints:"
    echo "   - Health: http://localhost:8000/"
    echo "   - Docs: http://localhost:8000/docs"
    echo "   - Create Project: POST http://localhost:8000/projects"
    echo ""
    echo "📝 Logs: tail -f /tmp/vdw_server.log"
    echo "🛑 Stop: pkill -f 'uvicorn main:app'"
    echo ""
    echo "🎉 Ready to use with Qwen Desktop!"
    echo "   Configure MCP: python3.11 /home/ubuntu/vdw-orchestrator/mcp_wrapper.py"
else
    echo "❌ Failed to start server"
    echo "Check logs: tail -f /tmp/vdw_server.log"
    exit 1
fi
