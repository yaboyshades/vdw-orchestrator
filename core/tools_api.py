from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from core.tool_registry import MCPBoxRegistry
from core.models import ToolMetadata, ToolCapability

router = APIRouter(prefix="/tools", tags=["tools"])

class CreateToolRequest(BaseModel):
    name: str
    description: str
    capabilities: List[ToolCapability]
    created_by: str
    version: Optional[str] = "1.0.0"

class DeprecateRequest(BaseModel):
    reason: str
    replacement_tool_id: Optional[str] = None

@router.get("")
async def list_tools(registry: MCPBoxRegistry):
    tools = await registry.list_tools()
    return [t.model_dump() for t in tools]

@router.post("")
async def create_tool(req: CreateToolRequest, registry: MCPBoxRegistry):
    meta = ToolMetadata(
        name=req.name,
        description=req.description,
        capabilities=req.capabilities,
        created_by=req.created_by,
        version=req.version,
    )
    ok = await registry.register_tool(meta)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to register tool")
    return meta.model_dump()

@router.get("/{tool_id}")
async def get_tool(tool_id: str, registry: MCPBoxRegistry):
    tool = await registry.get_tool_by_id(tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool.model_dump()

@router.post("/{tool_id}/deprecate")
async def deprecate_tool(tool_id: str, req: DeprecateRequest, registry: MCPBoxRegistry):
    ok = await registry.deprecate_tool(tool_id, req.reason, req.replacement_tool_id)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to deprecate tool")
    return {"status": "ok"}
