from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import google.generativeai as genai
from app.database import get_db
from app.models.models import User, ChatHistory
from app.schemas.schemas import ChatRequest, ChatMessageOut
from app.utils.auth import get_current_user
from app.config import get_settings

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

SYSTEM_PROMPT = """You are a menstrual health assistant.
Rules:
- Maximum 4 sentences OR 3-5 bullet points. Never both.
- Use **bold** for key terms, bullet lists for multiple items.
- Never write long essays or multiple headings.
- End with: _This is general info, not medical advice._"""


def _get_gemini_client():
    settings = get_settings()
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your-gemini-api-key-here":
        raise HTTPException(status_code=503, detail="Gemini API key not configured. Set GEMINI_API_KEY in .env")
    genai.configure(api_key=settings.GEMINI_API_KEY)
    # Ensure model name has no stale prefix issues — use env var directly
    import os
    model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    return genai.GenerativeModel(
        model_name=model_name,
        system_instruction=SYSTEM_PROMPT,
        generation_config=genai.GenerationConfig(max_output_tokens=300),
    )


@router.post("/ask", response_model=ChatMessageOut)
def ask_chatbot(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    model = _get_gemini_client()

    # Save user message first
    user_msg = ChatHistory(user_id=current_user.id, role="user", content=payload.message)
    db.add(user_msg)
    db.commit()

    # Build conversation history for Gemini (last 10 exchanges = 20 messages)
    history_rows = (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == current_user.id)
        .order_by(ChatHistory.created_at.desc())
        .limit(20)
        .all()
    )
    # Gemini expects [{role, parts}] — roles must be "user" / "model"
    gemini_history = []
    for h in reversed(history_rows[1:]):   # skip the message we just saved
        gemini_history.append({
            "role": "user" if h.role == "user" else "model",
            "parts": [h.content],
        })

    chat = model.start_chat(history=gemini_history)
    response = chat.send_message(payload.message)
    reply = response.text

    # Save assistant reply
    assistant_msg = ChatHistory(user_id=current_user.id, role="assistant", content=reply)
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)
    return assistant_msg


@router.delete("/history", status_code=204)
def clear_chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).delete()
    db.commit()


@router.get("/history", response_model=List[ChatMessageOut])
def get_chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == current_user.id)
        .order_by(ChatHistory.created_at.asc())
        .all()
    )
