from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from core.orchestrator import VDWOrchestrator
import main

router = APIRouter()

class CreateProjectRequest(BaseModel):
    vibe: str

class ValidateRequest(BaseModel):
    approved: bool
    feedback: Optional[str] = None

@router.post("/projects", response_model=None)
async def create_project(req: CreateProjectRequest, orchestrator: VDWOrchestrator = Depends(lambda: main._orchestrator)):
    project_id = await orchestrator.submit_new_project(req.vibe)
    return {"project_id": project_id}

@router.get("/projects/{project_id}", response_model=None)
async def get_project(project_id: str, orchestrator: VDWOrchestrator = Depends(lambda: main._orchestrator)):
    ctx = orchestrator.projects.get(project_id)
    if not ctx:
        raise HTTPException(status_code=404, detail="Project not found")
    return ctx.model_dump()

@router.get("/projects/{project_id}/artifacts", response_model=None)
async def get_artifacts(project_id: str, orchestrator: VDWOrchestrator = Depends(lambda: main._orchestrator)):
    ctx = orchestrator.projects.get(project_id)
    if not ctx:
        raise HTTPException(status_code=404, detail="Project not found")
    artifacts = {
        "phase_1_output": ctx.phase_1_output,
        "phase_2_output": ctx.phase_2_output,
        "phase_3_output": ctx.phase_3_output,
        "phase_4_output": ctx.phase_4_output,
        "phase_5_output": ctx.phase_5_output,
    }
    return artifacts

@router.post("/projects/{project_id}/validate/phase-1", response_model=None)
async def approve_phase_1(project_id: str, req: ValidateRequest, orchestrator: VDWOrchestrator = Depends(lambda: main._orchestrator)):
    if not req.approved:
        # simple rejection loop: re-run Phase 1 with feedback noted
        await orchestrator.approve_phase_1(project_id, feedback=req.feedback or "Re-run requested")
        return {"status": "re-run", "message": "Phase 1 re-run initiated"}
    await orchestrator.approve_phase_1(project_id, req.feedback)
    return {"status": "ok"}
