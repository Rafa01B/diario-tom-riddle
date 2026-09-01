from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from schemas import WriteRequest, WriteResponse
from riddle_service import RiddleEngine

app = FastAPI(title="Tom Riddle's Diary API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite conexões locais em qualquer porta do Vite (5173, 5174, etc.)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

riddle_engine = RiddleEngine()

@app.post("/api/write", response_model=WriteResponse, status_code=status.HTTP_200_OK)
def write_to_diary(payload: WriteRequest):
    try:
        reply, easter_egg = riddle_engine.generate_reply(
            message=payload.message,
            history=payload.history
        )
        return WriteResponse(response=reply, easter_egg_triggered=easter_egg)
    except Exception as e:
        print(f"[ERRO NO DIARIO]: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"O diário resistiu à escrita: {str(e)}"
        )