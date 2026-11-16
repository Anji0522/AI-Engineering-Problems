from __future__ import annotations
import os
import sys
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from hardware_reader import SystemHardwareReader
from assistant_agent import HardwareAssistantAgent
from safety_guard import SafetyGuard, SecurityException

app = FastAPI(title="Linux Hardware Q&A Assistant", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

reader = SystemHardwareReader()
agent = HardwareAssistantAgent(reader=reader)

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    query: str
    answer: str
    selected_tools: List[str]
    tool_executions: List[Dict[str, Any]]
    structured_context: Dict[str, Any]

class DirectToolRequest(BaseModel):
    command: List[str]

@app.post("/api/chat", response_model=ChatResponse)
def handle_chat(req: ChatRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    result = agent.answer_query(req.query.strip())
    return result

@app.post("/api/tools/execute")
def direct_tool_execute(req: DirectToolRequest):
    """Allows testing direct tool invocation through the safety guard."""
    try:
        success, output, code = reader.run_safe_command(req.command)
        return {
            "command": " ".join(req.command),
            "success": success,
            "exit_code": code,
            "output": output
        }
    except SecurityException as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.get("/api/system/overview")
def get_system_overview():
    """Returns complete normalized telemetry of the inspected machine."""
    _, lscpu_out, _ = reader.run_safe_command(["lscpu"])
    _, free_out, _ = reader.run_safe_command(["free", "-m"])
    _, lsblk_out, _ = reader.run_safe_command(["lsblk", "-J", "-o", "NAME,SIZE,TYPE,TRAN,MODEL,ROTA,MOUNTPOINT"])
    _, lspci_out, _ = reader.run_safe_command(["lspci"])
    _, dmi_out, _ = reader.run_safe_command(["dmidecode", "-t", "memory"])

    from parsers import HardwareParsers
    return {
        "cpu": HardwareParsers.parse_lscpu(lscpu_out),
        "memory": HardwareParsers.parse_free(free_out),
        "storage": HardwareParsers.parse_lsblk(lsblk_out),
        "pci": HardwareParsers.parse_lspci(lspci_out),
        "memory_slots": HardwareParsers.parse_dmidecode_memory(dmi_out),
        "mode": "Simulation (Dell XPS 15 9520)" if reader.use_mock else "Live Linux System"
    }

# Mount frontend directory for easy web UI preview
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    def serve_frontend():
        return FileResponse(os.path.join(frontend_dir, "index.html"))
