from typing import List, Optional, Literal
from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    # Optional short history so the frontend can support multi-turn conversations.
    history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    reply: str
    tools_used: List[str] = []


class TransactionOut(BaseModel):
    id: int
    date: str
    merchant: str
    category: str
    amount: float
    description: Optional[str] = None
