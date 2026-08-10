import os
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from model_connector import ModelConnector
from agent_engine import AetherMindAgent
from tools.system_tool import get_system_stats

app = FastAPI(title="AetherMind 70B Local Agent Platform", version="1.0.0")

# Setup static files directory
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Shared state
connector = ModelConnector(base_url="http://localhost:11434", model_name="qwen2.5-coder:32b")
agent = AetherMindAgent(connector)

class ModelConfig(BaseModel):
    base_url: str
    model_name: str

@app.get("/")
async def get_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h2>AetherMind 70B Engine Server Running. UI file index.html loading...</h2>")

@app.get("/api/system")
async def get_system_info():
    """Get live system stats (CPU, RAM, GPU VRAM)."""
    return get_system_stats()

@app.post("/api/config")
async def update_config(cfg: ModelConfig):
    """Update local inference endpoint and model name."""
    connector.set_config(cfg.base_url, cfg.model_name)
    return {"status": "success", "base_url": connector.base_url, "model_name": connector.model_name}

@app.get("/api/config")
async def get_config():
    return {"base_url": connector.base_url, "model_name": connector.model_name}

@app.websocket("/ws/task")
async def websocket_task_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        request = json.loads(data)
        task_prompt = request.get("task", "")
        cwd = request.get("cwd", os.getcwd())

        if not task_prompt:
            await websocket.send_text(json.dumps({"type": "error", "data": "No task provided."}))
            await websocket.close()
            return

        async for event in agent.run_task_stream(task_prompt, cwd=cwd):
            await websocket.send_text(json.dumps(event))

        await websocket.send_text(json.dumps({"type": "complete"}))
    except WebSocketDisconnect:
        print("[AetherMind] WebSocket Client disconnected.")
    except Exception as e:
        await websocket.send_text(json.dumps({"type": "error", "data": str(e)}))
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=7860, reload=True)
