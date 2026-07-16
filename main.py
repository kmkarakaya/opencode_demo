import os
from typing import List, Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uuid
from datetime import datetime, timezone

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
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str


class SessionMeta(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str


class SessionCreate(BaseModel):
    title: Optional[str] = None


class SessionMessages(BaseModel):
    messages: List[Message]


SESSIONS: dict[str, dict] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.get("/")
async def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/api/sessions", response_model=List[SessionMeta])
async def list_sessions():
    return [
        SessionMeta(
            id=sid,
            title=data["title"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )
        for sid, data in sorted(SESSIONS.items(), key=lambda kv: kv[1]["updated_at"], reverse=True)
    ]


@app.post("/api/sessions", response_model=SessionMeta)
async def create_session(body: SessionCreate):
    sid = str(uuid.uuid4())
    now = _now()
    SESSIONS[sid] = {
        "title": body.title or "Yeni Sohbet",
        "created_at": now,
        "updated_at": now,
        "messages": [],
    }
    return SessionMeta(id=sid, title=SESSIONS[sid]["title"], created_at=now, updated_at=now)


@app.get("/api/sessions/{sid}", response_model=SessionMessages)
async def get_session(sid: str):
    if sid not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session bulunamadi.")
    return SessionMessages(messages=SESSIONS[sid]["messages"])


@app.delete("/api/sessions/{sid}")
async def delete_session(sid: str):
    if sid not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session bulunamadi.")
    del SESSIONS[sid]
    return {"ok": True}


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

    if req.session_id and req.session_id in SESSIONS:
        sess = SESSIONS[req.session_id]
        sess["messages"] = [m.model_dump() for m in req.messages] + [
            {"role": "assistant", "content": reply}
        ]
        if sess["title"] == "Yeni Sohbet" and req.messages:
            sess["title"] = req.messages[0].content[:40]
        sess["updated_at"] = _now()

    return ChatResponse(reply=reply)
