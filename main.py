import os
from typing import List, Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN", "")
BASE_URL = os.getenv("BASE_URL", "http://100.70.134.107:8001/v1").rstrip("/")
MODEL = os.getenv("MODEL", "Ornith-1.0-9B-4bit plan")

app = FastAPI(title="Murat Karakaya Akademi Sohbet Botu")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str


@app.get("/")
async def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.messages:
        raise HTTPException(status_code=400, detail="Mesaj listesi bos olamaz.")

    payload = {
        "model": req.model or MODEL,
        "messages": [m.model_dump() for m in req.messages],
        "temperature": 0.7,
        "stream": False,
    }

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }

    url = f"{BASE_URL}/chat/completions"

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"LLM servisine ulasilamadi: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Beklenmeyen hata: {e}")

    try:
        reply = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise HTTPException(status_code=502, detail="LLM yaniti islenemedi.")

    return ChatResponse(reply=reply)
