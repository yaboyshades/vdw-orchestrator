from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from core.orchestrator import VDWOrchestrator

router = APIRouter()

class CreateProjectRequest(BaseModel):
    vibe: str

class ValidateRequest(BaseModel):
    approved: bool
    feedback: Optional[str] = None

@router.post("/projects")
async def create_project(req: CreateProjectRequest, orchestrator: VDWOrchestrator):
    project_id = await orchestrator.submit_new_project(req.vibe)
    return {"project_id": project_id}

@router.post("/projects/{project_id}/validate/phase-1")
async def approve_phase_1(project_id: str, req: ValidateRequest, orchestrator: VDWOrchestrator):
    if not req.approved:
        raise HTTPException(status_code=400, detail="Rejection loop not implemented yet")
    await orchestrator.approve_phase_1(project_id, req.feedback)
    return {"status": "ok"}
