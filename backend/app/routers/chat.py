from fastapi import APIRouter, HTTPException

from app.schemas import ChatRequest, ChatResponse
from app.claude_client import chat_with_claude

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="message cannot be empty")

    history = [m.model_dump() for m in (request.history or [])]

    try:
        result = await chat_with_claude(request.message, history)
    except Exception as exc:  # noqa: BLE001 - surface a clean error to the frontend
        raise HTTPException(status_code=500, detail=f"Chat failed: {exc}") from exc

    return ChatResponse(reply=result["reply"], tools_used=result["tools_used"])
