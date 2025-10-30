from fastapi import FastAPI, Depends
import structlog
import logging
import os

from core.event_bus import EventBus
from core.memory_store import MemoryStore
from reasoning.mangle_client import MangleClient
from core.orchestrator import VDWOrchestrator
from core import models  # ensure pydantic models import
from core.api import router as api_router
from core.tools_api import router as tools_router
from core.tools_gaps_api import router as tools_gaps_router
from core.tool_registry import MCPBoxRegistry

logger = structlog.get_logger()

app = FastAPI(title="VDW Orchestrator", version="0.1.0")

# Singletons
_event_bus = EventBus(os.getenv("REDIS_URL", "redis://localhost:6379"))
_memory = MemoryStore(os.getenv("DATABASE_PATH", "data/memory"))
_mangle = MangleClient(os.getenv("MANGLE_SERVER_ADDRESS", "localhost:50051"))
_registry = MCPBoxRegistry(os.getenv("MCP_BOX_DB", "data/mcp_box.db"))
_orchestrator = VDWOrchestrator(_event_bus, _memory, _mangle)

async def get_orchestrator():
    return _orchestrator

async def get_registry():
    return _registry

app.include_router(api_router)
app.include_router(tools_router)
app.include_router(tools_gaps_router)

@app.on_event("startup")
async def startup():
    await _event_bus.connect()
    await _event_bus.start()
    await _mangle.connect()

@app.get("/")
async def root():
    return {"service": "vdw-orchestrator", "status": "ok"}
