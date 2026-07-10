"""FastAPI server for the LinguaChat embeddable widget."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Add parent directory so we can import chat_engine
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from chat_engine import get_ai_response, build_system_prompt
from config import DEFAULT_CONFIG

load_dotenv()

app = FastAPI(title="LinguaChat Widget", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HERE = Path(__file__).parent


class ChatRequest(BaseModel):
    config: dict | None = None
    messages: list[dict] = []
    user_input: str


class ChatResponse(BaseModel):
    response: str


@app.get("/api/health")
async def health():
    return JSONResponse({"status": "ok", "version": "1.0.0"})


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not os.getenv("GEMINI_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY not configured on the server.",
        )

    merged_config = {**DEFAULT_CONFIG, "focus_mode": "helpbox"}
    if req.config:
        merged_config.update(req.config)

    try:
        result = get_ai_response(merged_config, req.messages, req.user_input)
        return ChatResponse(response=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def serve_widget():
    return FileResponse(HERE / "embed.html")


# Serve example page and static files
EXAMPLE_DIR = HERE / "example"
if EXAMPLE_DIR.exists():
    app.mount("/example", StaticFiles(directory=str(EXAMPLE_DIR)), name="example")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("WIDGET_PORT", "8000"))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)
