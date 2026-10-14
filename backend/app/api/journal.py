from datetime import date, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Journal, Notification
from app.schemas.schemas import JournalCreate, JournalOut
from app.utils.auth import get_current_user
from app.services.email_service import send_mood_alert

router = APIRouter(prefix="/journal", tags=["journal"])


def _build_journal_advice(payload: JournalCreate) -> str:
    mood = (payload.mood or "neutral").lower()
    energy = payload.energy_level or 5
    score = payload.mood_score or 5
    if score <= 3:
        return "Your mood is low right now. Gentle movement, hydration, extra rest, and a supportive check-in can help. If this pattern keeps repeating, consider discussing it with a healthcare professional."
    if energy <= 3:
        return "Your energy feels low, so it may help to keep your routine lighter and prioritize sleep, protein, and a shorter walk. Try reducing overstimulation for the next day or two."
    if "anxious" in mood or "irritable" in mood:
        return "This mood pattern often responds well to calm routines, less caffeine, consistent meals, and some quiet reset time. Journaling and a short walk can help regulate stress."
    if "tired" in mood:
        return "Your energy and mood suggest a lower-demand day is beneficial. Prioritize rest, hydration, and simple meals to support recovery."
    return "This is a balanced mood and energy day. Keep your routine consistent, stay hydrated, and continue tracking early signs of stress or PMS so you can notice patterns sooner."


@router.post("/", response_model=JournalOut, status_code=201)
def create_entry(
    payload: JournalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = Journal(user_id=current_user.id, **payload.model_dump())
    entry.ai_advice = _build_journal_advice(payload)
    db.add(entry)
    db.commit()
    db.refresh(entry)

    # Immediate mood alert — don't wait for scheduler
    if payload.mood_score is not None and payload.mood_score < 4:
        already_notified = db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.notification_type == "mood_alert",
            Notification.created_at >= date.today(),
        ).first()
        if not already_notified:
            msg = f"Your mood score is {payload.mood_score}/10. Take care of yourself."
            db.add(Notification(user_id=current_user.id, title="Low Mood Detected", message=msg, notification_type="mood_alert"))
            db.commit()
            email = current_user.notify_email or current_user.email
            name = current_user.notify_name or current_user.full_name or current_user.username
            if current_user.email_notifications:
                send_mood_alert(email, name, float(payload.mood_score), 1)

    return entry


@router.get("/", response_model=List[JournalOut])
def get_entries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Journal)
        .filter(Journal.user_id == current_user.id)
        .order_by(Journal.entry_date.desc())
        .all()
    )


@router.delete("/{entry_id}", status_code=204)
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = db.query(Journal).filter(Journal.id == entry_id, Journal.user_id == current_user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    db.delete(entry)
    db.commit()
