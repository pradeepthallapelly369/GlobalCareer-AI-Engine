"""
colibri-studio FastAPI Backend Application
"""

import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from models_config import TIER_MODELS
from telemetry import get_system_telemetry, get_disk_info
from router import analyze_prompt_complexity
from colibri_driver import ColibriDriver

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_DIR = os.path.join(BASE_DIR, "web")
ENGINE_DIR = os.path.join(BASE_DIR, "engine")

app = FastAPI(title="Colibrì Studio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

driver = ColibriDriver(BASE_DIR)

class RouteRequest(BaseModel):
    prompt: str

class ChatRequest(BaseModel):
    tier: str = "auto"
    prompt: str

@app.get("/api/status")
async def api_status():
    telemetry = get_system_telemetry(ENGINE_DIR)
    return JSONResponse(content=telemetry)

@app.get("/api/tiers")
async def api_tiers():
    disk = get_disk_info("/")
    free_disk_gb = disk["free_gb"]

    tiers_data = {}
    for tid, meta in TIER_MODELS.items():
        data = dict(meta)
        data["is_downloaded"] = driver.is_model_downloaded(tid)
        
        # Real-time hardware capability check
        needed_gb = meta["disk_size_gb"]
        if needed_gb > free_disk_gb:
            data["fits_on_internal_disk"] = False
            data["disk_status_message"] = f"Requires {needed_gb} GB (only {free_disk_gb} GB free on internal NVMe; requires external drive)"
        else:
            data["fits_on_internal_disk"] = True
            data["disk_status_message"] = f"Fits on internal NVMe ({needed_gb} GB needed / {free_disk_gb} GB free)"
        
        tiers_data[tid] = data

    return JSONResponse(content={
        "tiers": tiers_data,
        "free_disk_gb": free_disk_gb
    })

@app.post("/api/route")
async def api_route(req: RouteRequest):
    analysis = analyze_prompt_complexity(req.prompt)
    return JSONResponse(content=analysis)

@app.post("/api/chat")
async def api_chat(req: ChatRequest):
    tier_id = req.tier
    if tier_id == "auto" or not tier_id:
        routing = analyze_prompt_complexity(req.prompt)
        tier_id = routing["selected_tier"]
    
    return StreamingResponse(
        driver.stream_inference(tier_id, req.prompt),
        media_type="text/event-stream"
    )

@app.post("/api/download_guide")
async def api_download_guide(req: Request):
    body = await req.json()
    tier_id = body.get("tier", "tier5")
    tier_info = TIER_MODELS.get(tier_id, TIER_MODELS["tier5"])
    
    model_dir = os.path.join(BASE_DIR, "models", tier_id)
    cmd = f"git clone https://huggingface.co/models/{tier_info['family']}-colibri-int4 {model_dir}"
    
    return JSONResponse(content={
        "tier": tier_id,
        "model_name": tier_info["name"],
        "disk_size_gb": tier_info["disk_size_gb"],
        "target_directory": model_dir,
        "suggested_command": cmd,
        "notes": "Colibrì int4 safetensors model format streamed dynamically by the pure C engine."
    })

# Mount frontend static files
if os.path.isdir(WEB_DIR):
    app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    index_path = os.path.join(WEB_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Colibrì Studio Web UI is loading...</h1>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8088, reload=False)
