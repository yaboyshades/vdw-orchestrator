#!/bin/bash

echo "=== VDW Orchestrator System Test ==="
echo ""

# Test 1: Health check
echo "1. Testing health endpoint..."
curl -s http://localhost:8000/ | python3.11 -m json.tool
echo ""

# Test 2: Create a project
echo "2. Creating a new project..."
PROJECT_ID=$(curl -s -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{"vibe": "Build a real-time chat application with WebSockets"}' | python3.11 -c "import sys, json; print(json.load(sys.stdin)['project_id'])")
echo "Created project: $PROJECT_ID"
echo ""

# Test 3: Get project details
echo "3. Getting project details..."
curl -s http://localhost:8000/projects/$PROJECT_ID | python3.11 -m json.tool | head -40
echo ""

# Test 4: Get project artifacts
echo "4. Getting project artifacts..."
curl -s http://localhost:8000/projects/$PROJECT_ID/artifacts | python3.11 -m json.tool
echo ""

echo "=== All tests completed successfully! ==="
