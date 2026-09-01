from pydantic import BaseModel, Field
from typing import List, Optional

class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' ou 'assistant'")
    content: str = Field(..., min_length=1, max_length=1000)

class WriteRequest(BaseModel):
    session_id: str = Field(..., description="Identificador único da sessão/diário")
    message: str = Field(..., min_length=1, max_length=500)
    history: Optional[List[ChatMessage]] = Field(default_factory=list)

class WriteResponse(BaseModel):
    response: str
    easter_egg_triggered: Optional[str] = None