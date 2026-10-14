from datetime import date, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import google.generativeai as genai
from app.database import get_db
from app.models.models import User, ChatHistory, Symptom, Journal, Cycle
from app.schemas.schemas import ChatRequest, ChatMessageOut
from app.utils.auth import get_current_user
from app.config import get_settings

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

SYSTEM_PROMPT = """You are a helpful general-purpose AI assistant.
Answer the user's actual question directly, whether it is about health, technology, education, writing, planning, or any other subject.
Give complete, natural answers instead of brief fragments. Explain the point clearly, include practical steps or examples when helpful, and do not stop after the first sentence.
Use clear markdown when it improves readability and provide enough detail to be genuinely useful.
Use the supplied personal context only when it is relevant to the question; do not force unrelated questions into a menstrual-health topic.
For health questions, provide general information, avoid diagnosis, mention important warning signs when appropriate, and end with: _This is general information, not medical advice._"""


def _relative_day_label(target_date: date) -> str:
    delta = (date.today() - target_date).days
    if delta == 0:
        return "today"
    if delta == 1:
        return "yesterday"
    if delta < 7:
        return f"{delta} days ago"
    return f"on {target_date.strftime('%b %d')}"


def _value_for(record, field: str, default=None):
    if isinstance(record, dict):
        return record.get(field, default)
    return getattr(record, field, default)


def build_context_summary(symptoms: list, mood_entries: list, cycles: list | None = None) -> str:
    blocks = []
    if symptoms:
        recent = symptoms[:5]
        symptom_text = ", ".join(
            f"{s['symptom_type']} ({s['severity']}/10, {_relative_day_label(s['logged_date'])})"
            for s in recent
        )
        blocks.append(f"Recent symptoms: {symptom_text}.")
    if mood_entries:
        recent_mood = mood_entries[:3]
        mood_text = ", ".join(
            f"{m['mood']} ({m['mood_score']}/10, {_relative_day_label(m['entry_date'])})"
            for m in recent_mood
        )
        blocks.append(f"Recent mood: {mood_text}.")
    if cycles:
        latest = cycles[0]
        latest_start = _value_for(latest, "start_date")
        flow_intensity = _value_for(latest, "flow_intensity") or "mixed"
        if latest_start:
            blocks.append(
                f"Latest cycle started {_relative_day_label(latest_start)} and the current pattern seems {flow_intensity} flow."
            )
    if not blocks:
        return "The user has no recent symptom, mood, or cycle data yet."
    return " ".join(blocks)


def generate_cycle_ai_guidance(
    cycle_start: date,
    end_date: date | None = None,
    flow_intensity: str | None = None,
    recent_symptoms: list | None = None,
    recent_moods: list | None = None,
) -> str:
    recent_symptoms = recent_symptoms or []
    recent_moods = recent_moods or []
    end_text = f" and ended on {end_date.isoformat()}" if end_date else ""
    flow_text = f" with {flow_intensity or 'mixed'} flow" if flow_intensity else ""

    symptom_list = ", ".join(
        f"{s.get('symptom_type', 'symptom')} ({s.get('severity', 0)}/10)"
        for s in recent_symptoms[:3]
    ) if recent_symptoms else "none logged"
    mood_list = ", ".join(
        f"{m.get('mood', 'Mood')} ({m.get('mood_score', 5)}/10)"
        for m in recent_moods[:3]
    ) if recent_moods else "no recent mood signals"

    prompt = (
        f"A user logged a period start on {cycle_start.isoformat()}{end_text}{flow_text}. "
        f"Recent symptoms: {symptom_list}. "
        f"Recent mood: {mood_list}. "
        "Give 2 compact, empathetic, practical suggestions for their period-related care and recovery in 1 short paragraph."
    )

    settings = get_settings()
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your-gemini-api-key-here":
        fallback = "Stay warm, hydrate consistently, and keep meals simple and iron-rich while your body resets. Gentle movement and a heating pad can help if cramps or fatigue are stronger than usual."
        if flow_intensity and flow_intensity.lower() == "heavy":
            return "Heavy flow needs more rest and hydration; keep iron-rich meals and consider a slower day. A heating pad and regular fluids can help reduce cramps and fatigue."
        return fallback

    try:
        model = _get_gemini_client()
        response = model.generate_content(prompt)
        text = getattr(response, "text", "")
        if text:
            return text.strip()
    except Exception:
        pass

    fallback = "Stay warm, hydrate consistently, and keep meals simple and iron-rich while your body resets. Gentle movement and a heating pad can help if cramps or fatigue are stronger than usual."
    if flow_intensity and flow_intensity.lower() == "heavy":
        return "Heavy flow needs more rest and hydration; keep iron-rich meals and consider a slower day. A heating pad and regular fluids can help reduce cramps and fatigue."
    return fallback


def _get_gemini_client():
    settings = get_settings()
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your-gemini-api-key-here":
        raise HTTPException(status_code=503, detail="Gemini API key not configured. Set GEMINI_API_KEY in .env")

    import os
    configured_model = os.environ.get("GEMINI_MODEL") or settings.GEMINI_MODEL
    model_candidates = []
    for name in [configured_model, "gemini-3.6-flash", "gemini-2.5-flash", "gemini-2.0-flash"]:
        if name and name not in model_candidates:
            model_candidates.append(name)

    generation_config = genai.GenerationConfig(
        max_output_tokens=1024,
        temperature=0.7,
        top_p=0.9,
    )

    last_error = None
    for model_name in model_candidates:
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            return genai.GenerativeModel(
                model_name=model_name,
                system_instruction=SYSTEM_PROMPT,
                generation_config=generation_config,
            )
        except Exception as exc:  # pragma: no cover - defensive fallback for Gemini model rotation
            last_error = exc

    raise HTTPException(status_code=503, detail=(
        f"Gemini models are unavailable right now. Final error: {last_error}"
        if last_error else "Gemini models are unavailable right now."
    ))


@router.post("/ask", response_model=ChatMessageOut)
def ask_chatbot(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    model = _get_gemini_client()

    user_msg = ChatHistory(user_id=current_user.id, role="user", content=payload.message)
    db.add(user_msg)
    db.commit()

    recent_symptoms = (
        db.query(Symptom)
        .filter(Symptom.user_id == current_user.id)
        .order_by(Symptom.logged_date.desc())
        .limit(5)
        .all()
    )
    recent_moods = (
        db.query(Journal)
        .filter(Journal.user_id == current_user.id)
        .order_by(Journal.entry_date.desc())
        .limit(3)
        .all()
    )
    recent_cycles = (
        db.query(Cycle)
        .filter(Cycle.user_id == current_user.id)
        .order_by(Cycle.start_date.desc())
        .limit(3)
        .all()
    )

    ctx = build_context_summary(
        [
            {
                "symptom_type": s.symptom_type,
                "severity": s.severity or 0,
                "logged_date": s.logged_date,
            }
            for s in recent_symptoms
        ],
        [
            {
                "mood": j.mood or "Neutral",
                "mood_score": j.mood_score or 5,
                "entry_date": j.entry_date,
            }
            for j in recent_moods
        ],
        [{"start_date": c.start_date, "flow_intensity": c.flow_intensity} for c in recent_cycles],
    )

    history_rows = (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == current_user.id)
        .order_by(ChatHistory.created_at.desc())
        .limit(20)
        .all()
    )
    gemini_history = []
    for h in reversed(history_rows[1:]):
        gemini_history.append({
            "role": "user" if h.role == "user" else "model",
            "parts": [h.content],
        })

    chat = model.start_chat(history=gemini_history)
    prompt = (
        f"User question: {payload.message}\n\n"
        f"Optional personal context (use only if relevant): {ctx}\n\n"
        "Answer the question completely and naturally. "
        "Give a full, helpful explanation with practical advice, examples, or next steps when relevant. "
        "Do not give a brief fragment or stop after the first idea. "
        "If relevant, include common causes, helpful actions, and warning signs."
    )
    response = chat.send_message(prompt)
    reply = response.text

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
