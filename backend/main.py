from typing import Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from riddle_service import RiddleEngine

app = FastAPI(title="Diário de Tom Riddle API", version="1.0.0")

# Configuração permissiva de CORS para comunicação fluida com a Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialização única da engine para reaproveitamento de conexão
engine = RiddleEngine()


class WriteRequest(BaseModel):
    message: str
    history: Optional[List[Any]] = []


class WriteResponse(BaseModel):
    response: str
    easter_egg: Optional[str] = None


@app.get("/")
def health_check():
    """Rota raiz para status e pings de monitoramento/keep-alive."""
    return {"status": "alive", "artifact": "Diário de Tom Marvolo Riddle (1943)"}


@app.post("/api/write", response_model=WriteResponse)
def write_on_diary(payload: WriteRequest):
    """
    Recebe as palavras inscritas pelo interlocutor,
    delibera e devolve a resposta manuscrita de Riddle.
    """
    try:
        reply, easter_egg = engine.generate_reply(
            message=payload.message,
            history=payload.history
        )
        return WriteResponse(response=reply, easter_egg=easter_egg)
    except Exception as exc:
        print(f"[ERRO NO ENDPOINT /api/write]: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=500,
            detail="As páginas parecem inertes e incapazes de responder."
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)