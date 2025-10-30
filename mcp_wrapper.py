#!/usr/bin/env python3.11
"""MCP stdio wrapper for VDW Orchestrator

This wrapper allows the VDW Orchestrator REST API to be used as an MCP server
via the stdio protocol, making it compatible with MCP clients like Qwen Desktop.
"""

import sys
import json
import asyncio
import httpx
from typing import Any, Dict, List
import os

# MCP Server base URL - can be overridden via environment variable
BASE_URL = os.getenv("VDW_API_URL", "http://localhost:8000")

class VDWMCPWrapper:
    """Wrapper that translates MCP protocol to VDW REST API calls"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = None
    
    async def initialize(self):
        """Initialize the HTTP client"""
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.client:
            await self.client.aclose()
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return MCP tool definitions for VDW Orchestrator"""
        return [
            {
                "name": "vdw_create_project",
                "description": "Create a new VDW (Vibe-Driven Waterfall) project from an unstructured 'vibe'. The system will distill your vibe into structured requirements and begin Phase 1 processing.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "vibe": {
                            "type": "string",
                            "description": "Unstructured description of what you want to build. Be as creative or informal as you like - the system will structure it for you."
                        }
                    },
                    "required": ["vibe"]
                }
            },
            {
                "name": "vdw_get_project",
                "description": "Get complete details of a VDW project including current phase, all outputs, and metadata.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "The unique project ID returned when the project was created"
                        }
                    },
                    "required": ["project_id"]
                }
            },
            {
                "name": "vdw_get_artifacts",
                "description": "Get all phase artifacts (outputs) from a VDW project. Shows what has been produced in each phase.",
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
                "description": "Approve or reject Phase 1 (Mood & Requirements) output and optionally provide feedback for refinement.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "The unique project ID"
                        },
                        "approved": {
                            "type": "boolean",
                            "description": "Whether to approve Phase 1 and move to Phase 2"
                        },
                        "feedback": {
                            "type": "string",
                            "description": "Optional feedback for refinement if not approved"
                        }
                    },
                    "required": ["project_id", "approved"]
                }
            },
            {
                "name": "vdw_health_check",
                "description": "Check if the VDW Orchestrator service is running and healthy.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    async def handle_tools_list(self) -> Dict[str, Any]:
        """Handle tools/list request"""
        return {
            "tools": self.get_tool_definitions()
        }
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        
        try:
            if tool_name == "vdw_create_project":
                response = await self.client.post(
                    f"{self.base_url}/projects",
                    json={"vibe": arguments["vibe"]}
                )
                response.raise_for_status()
                result = response.json()
                
                return {
                    "content": [{
                        "type": "text",
                        "text": f"✅ VDW Project Created!\n\nProject ID: {result['project_id']}\n\nThe system has processed your vibe and completed Phase 1 (Mood & Requirements). Use vdw_get_project with this ID to see the distilled requirements."
                    }]
                }
            
            elif tool_name == "vdw_get_project":
                response = await self.client.get(
                    f"{self.base_url}/projects/{arguments['project_id']}"
                )
                response.raise_for_status()
                result = response.json()
                
                # Format the response nicely
                phase = result.get('current_phase', 'UNKNOWN')
                vibe = result.get('initial_vibe', 'N/A')
                
                text = f"📊 VDW Project Details\n\n"
                text += f"Project ID: {result['project_id']}\n"
                text += f"Current Phase: {phase}\n"
                text += f"Original Vibe: {vibe}\n\n"
                
                if result.get('phase_1_output'):
                    text += "Phase 1 Output (Mood & Requirements):\n"
                    text += f"- Confidence: {result['phase_1_output']['mood_json']['confidence']}\n"
                    text += f"- Requirements YAML:\n{result['phase_1_output']['requirements_yaml']}\n\n"
                
                text += f"\nFull JSON:\n{json.dumps(result, indent=2)}"
                
                return {
                    "content": [{
                        "type": "text",
                        "text": text
                    }]
                }
            
            elif tool_name == "vdw_get_artifacts":
                response = await self.client.get(
                    f"{self.base_url}/projects/{arguments['project_id']}/artifacts"
                )
                response.raise_for_status()
                result = response.json()
                
                text = f"📦 VDW Project Artifacts\n\n"
                
                for phase_num in range(1, 6):
                    phase_key = f"phase_{phase_num}_output"
                    if result.get(phase_key):
                        text += f"✅ Phase {phase_num}: Complete\n"
                    else:
                        text += f"⏳ Phase {phase_num}: Not yet completed\n"
                
                text += f"\n\nFull Artifacts:\n{json.dumps(result, indent=2)}"
                
                return {
                    "content": [{
                        "type": "text",
                        "text": text
                    }]
                }
            
            elif tool_name == "vdw_validate_phase1":
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
                    text = "✅ Phase 1 approved! Moving to Phase 2 (Architecture & Design)..."
                else:
                    text = f"🔄 Phase 1 re-run initiated with feedback: {arguments.get('feedback', 'N/A')}"
                
                return {
                    "content": [{
                        "type": "text",
                        "text": text
                    }]
                }
            
            elif tool_name == "vdw_health_check":
                response = await self.client.get(f"{self.base_url}/")
                response.raise_for_status()
                result = response.json()
                
                return {
                    "content": [{
                        "type": "text",
                        "text": f"✅ VDW Orchestrator is healthy!\n\nService: {result.get('service')}\nStatus: {result.get('status')}"
                    }]
                }
            
            else:
                return {
                    "error": {
                        "code": "UNKNOWN_TOOL",
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
        
        except httpx.HTTPError as e:
            return {
                "error": {
                    "code": "HTTP_ERROR",
                    "message": f"HTTP error calling VDW API: {str(e)}"
                }
            }
        except Exception as e:
            return {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP protocol request"""
        
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "initialize":
            return {
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
            return await self.handle_tools_list()
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            return await self.handle_tool_call(tool_name, arguments)
        
        else:
            return {
                "error": {
                    "code": "METHOD_NOT_FOUND",
                    "message": f"Unknown method: {method}"
                }
            }

async def main():
    """Main MCP stdio loop"""
    
    wrapper = VDWMCPWrapper()
    await wrapper.initialize()
    
    try:
        # Read from stdin line by line (JSON-RPC format)
        while True:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            
            if not line:
                break
            
            try:
                request = json.loads(line.strip())
                response = await wrapper.handle_request(request)
                
                # Write response to stdout
                print(json.dumps(response), flush=True)
                
            except json.JSONDecodeError as e:
                error_response = {
                    "error": {
                        "code": "PARSE_ERROR",
                        "message": f"Invalid JSON: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
            
            except Exception as e:
                error_response = {
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": str(e)
                    }
                }
                print(json.dumps(error_response), flush=True)
    
    finally:
        await wrapper.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
