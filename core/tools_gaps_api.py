from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from core.tool_registry import MCPBoxRegistry
import main

router = APIRouter(prefix="/tools", tags=["tools"])

class GapAnalysisRequest(BaseModel):
    required_capabilities: List[str]

class RecordUsageRequest(BaseModel):
    project_id: str
    duration_ms: float
    success: bool
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@router.post("/gaps", response_model=None)
async def capability_gaps(req: GapAnalysisRequest, registry: MCPBoxRegistry = Depends(lambda: main._registry)):
    analysis = await registry.analyze_capability_gap(req.required_capabilities)
    return analysis

@router.post("/{tool_id}/usage", response_model=None)
async def record_usage(tool_id: str, req: RecordUsageRequest, registry: MCPBoxRegistry = Depends(lambda: main._registry)):
    ok = await registry.record_tool_usage(tool_id, req.project_id, req.duration_ms, req.success, req.error_message, req.metadata)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to record usage")
    return {"status": "ok"}
