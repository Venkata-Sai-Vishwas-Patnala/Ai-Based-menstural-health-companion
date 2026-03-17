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


@router.post("/", response_model=JournalOut, status_code=201)
def create_entry(
    payload: JournalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = Journal(user_id=current_user.id, **payload.model_dump())
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
