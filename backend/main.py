from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from riddle_service import RiddleEngine

app = FastAPI(title="Tom Riddle's Diary API")

# Permite que o frontend na Vercel acesse a API sem bloqueios de segurança
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = RiddleEngine()

class ChatMessage(BaseModel):
    role: str
    content: str

class WriteRequest(BaseModel):
    session_id: str
    message: str
    history: Optional[List[ChatMessage]] = []

class WriteResponse(BaseModel):
    response: str
    easter_egg_triggered: Optional[str] = None

@app.get("/")
def read_root():
    return {"status": "ok", "message": "O Diário de Tom Riddle está ativo."}

@app.post("/api/write", response_model=WriteResponse)
def write_in_diary(payload: WriteRequest):
    try:
        reply, easter_egg = engine.generate_reply(payload.message, payload.history)
        return WriteResponse(response=reply, easter_egg_triggered=easter_egg)
    except Exception as e:
        print(f"[ERRO NO DIARIO]: {e}")
        raise HTTPException(status_code=500, detail="Algo perturbou a magia destas páginas...")