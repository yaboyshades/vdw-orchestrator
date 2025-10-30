#!/usr/bin/env python3
"""
VDW Orchestrator MCP Server (stdio)

A standalone MCP server that can be run with uvx.
This script can be used independently without installing the full package.

Usage:
    uvx --from /path/to/vdw-orchestrator vdw_mcp_server.py
"""

import sys
import json
import asyncio
import os
from typing import Any, Dict, List

# Try to import httpx, provide helpful error if not available
try:
    import httpx
except ImportError:
    print(json.dumps({
        "error": {
            "code": "MISSING_DEPENDENCY",
            "message": "httpx is required. Install with: pip install httpx"
        }
    }), file=sys.stderr)
    sys.exit(1)

# MCP Server base URL
BASE_URL = os.getenv("VDW_API_URL", "http://localhost:8000")


class VDWMCPServer:
    """MCP Server for VDW Orchestrator"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = None
        self.request_id = 0
    
    async def initialize(self):
        """Initialize the HTTP client"""
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.client:
            await self.client.aclose()
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return MCP tool definitions"""
        return [
            {
                "name": "vdw_create_project",
                "description": "Create a new VDW project from an unstructured 'vibe'. The system distills your idea into structured requirements through Phase 1 (Mood & Requirements) processing.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "vibe": {
                            "type": "string",
                            "description": "Your unstructured idea, vision, or 'vibe' for what you want to build. Be creative - the system will structure it!"
                        }
                    },
                    "required": ["vibe"]
                }
            },
            {
                "name": "vdw_get_project",
                "description": "Retrieve complete details of a VDW project including current phase, distilled requirements, and all phase outputs.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "The unique project ID"
                        }
                    },
                    "required": ["project_id"]
                }
            },
            {
                "name": "vdw_get_artifacts",
                "description": "Get all artifacts produced by each phase of the VDW process.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "The unique project ID"
                        }
                    },
                    "required": ["project_id"]
                }
            },
            {
                "name": "vdw_validate_phase1",
                "description": "Validate and approve Phase 1 output, or provide feedback for refinement.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "The unique project ID"
                        },
                        "approved": {
                            "type": "boolean",
                            "description": "True to approve and advance to Phase 2, False to request refinement"
                        },
                        "feedback": {
                            "type": "string",
                            "description": "Optional feedback if not approved"
                        }
                    },
                    "required": ["project_id", "approved"]
                }
            },
            {
                "name": "vdw_health_check",
                "description": "Check if the VDW Orchestrator API is running and healthy.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call"""
        
        try:
            if name == "vdw_create_project":
                response = await self.client.post(
                    f"{self.base_url}/projects",
                    json={"vibe": arguments["vibe"]}
                )
                response.raise_for_status()
                result = response.json()
                
                return {
                    "content": [{
                        "type": "text",
                        "text": f"✅ VDW Project Created Successfully!\n\n"
                                f"**Project ID:** `{result['project_id']}`\n\n"
                                f"Your vibe has been processed through Phase 1 (Mood & Requirements). "
                                f"The system has distilled your unstructured idea into structured requirements.\n\n"
                                f"Use `vdw_get_project` to see the detailed requirements breakdown."
                    }]
                }
            
            elif name == "vdw_get_project":
                response = await self.client.get(
                    f"{self.base_url}/projects/{arguments['project_id']}"
                )
                response.raise_for_status()
                data = response.json()
                
                text = f"# 📊 VDW Project: {data['project_id']}\n\n"
                text += f"**Current Phase:** {data['current_phase']}\n"
                text += f"**Original Vibe:** {data['initial_vibe']}\n\n"
                
                if data.get('phase_1_output'):
                    p1 = data['phase_1_output']
                    text += f"## Phase 1: Mood & Requirements\n\n"
                    text += f"**Confidence Score:** {p1['mood_json']['confidence']}\n\n"
                    text += f"### Distilled Requirements\n```yaml\n{p1['requirements_yaml']}\n```\n\n"
                    text += f"### Validation Checklist\n"
                    for item in p1['validation_checklist']:
                        text += f"- {item}\n"
                
                return {
                    "content": [{
                        "type": "text",
                        "text": text
                    }]
                }
            
            elif name == "vdw_get_artifacts":
                response = await self.client.get(
                    f"{self.base_url}/projects/{arguments['project_id']}/artifacts"
                )
                response.raise_for_status()
                data = response.json()
                
                text = f"# 📦 VDW Project Artifacts\n\n"
                
                phases = [
                    ("Phase 1: Mood & Requirements", "phase_1_output"),
                    ("Phase 2: Architecture & Design", "phase_2_output"),
                    ("Phase 3: Technical Specification", "phase_3_output"),
                    ("Phase 4: Implementation", "phase_4_output"),
                    ("Phase 5: Validation & Testing", "phase_5_output")
                ]
                
                for phase_name, key in phases:
                    if data.get(key):
                        text += f"✅ **{phase_name}:** Complete\n"
                    else:
                        text += f"⏳ **{phase_name}:** Not yet completed\n"
                
                text += f"\n\n### Completed Artifacts\n\n"
                text += f"```json\n{json.dumps(data, indent=2)}\n```"
                
                return {
                    "content": [{
                        "type": "text",
                        "text": text
                    }]
                }
            
            elif name == "vdw_validate_phase1":
                response = await self.client.post(
                    f"{self.base_url}/projects/{arguments['project_id']}/validate/phase-1",
                    json={
                        "approved": arguments["approved"],
                        "feedback": arguments.get("feedback")
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                if result.get("status") == "ok":
                    text = "✅ **Phase 1 Approved!**\n\nTransitioning to Phase 2 (Architecture & Design)..."
                else:
                    text = f"🔄 **Phase 1 Re-run Initiated**\n\nFeedback: {arguments.get('feedback', 'None provided')}"
                
                return {
                    "content": [{
                        "type": "text",
                        "text": text
                    }]
                }
            
            elif name == "vdw_health_check":
                response = await self.client.get(f"{self.base_url}/")
                response.raise_for_status()
                result = response.json()
                
                return {
                    "content": [{
                        "type": "text",
                        "text": f"✅ **VDW Orchestrator is Healthy**\n\n"
                                f"Service: {result.get('service')}\n"
                                f"Status: {result.get('status')}\n"
                                f"Endpoint: {self.base_url}"
                    }]
                }
            
            else:
                return {
                    "isError": True,
                    "content": [{
                        "type": "text",
                        "text": f"❌ Unknown tool: {name}"
                    }]
                }
        
        except httpx.HTTPStatusError as e:
            return {
                "isError": True,
                "content": [{
                    "type": "text",
                    "text": f"❌ HTTP Error {e.response.status_code}: {e.response.text}"
                }]
            }
        except httpx.RequestError as e:
            return {
                "isError": True,
                "content": [{
                    "type": "text",
                    "text": f"❌ Connection Error: {str(e)}\n\nMake sure the VDW Orchestrator API is running at {self.base_url}"
                }]
            }
        except Exception as e:
            return {
                "isError": True,
                "content": [{
                    "type": "text",
                    "text": f"❌ Error: {str(e)}"
                }]
            }
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP message"""
        
        method = message.get("method")
        params = message.get("params", {})
        msg_id = message.get("id")
        
        response = {"jsonrpc": "2.0", "id": msg_id}
        
        try:
            if method == "initialize":
                response["result"] = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "vdw-orchestrator",
                        "version": "0.1.0"
                    }
                }
            
            elif method == "tools/list":
                response["result"] = {
                    "tools": self.get_tools()
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                response["result"] = await self.call_tool(tool_name, arguments)
            
            else:
                response["error"] = {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
        
        except Exception as e:
            response["error"] = {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        
        return response
    
    async def run(self):
        """Main server loop"""
        await self.initialize()
        
        try:
            async for line in self._read_stdin():
                if not line.strip():
                    continue
                
                try:
                    message = json.loads(line)
                    response = await self.handle_message(message)
                    self._write_stdout(response)
                
                except json.JSONDecodeError as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": f"Parse error: {str(e)}"
                        }
                    }
                    self._write_stdout(error_response)
        
        finally:
            await self.cleanup()
    
    async def _read_stdin(self):
        """Async generator for reading stdin"""
        loop = asyncio.get_event_loop()
        while True:
            line = await loop.run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            yield line
    
    def _write_stdout(self, obj: Dict[str, Any]):
        """Write JSON-RPC response to stdout"""
        print(json.dumps(obj), flush=True)


def main():
    """Entry point"""
    server = VDWMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
