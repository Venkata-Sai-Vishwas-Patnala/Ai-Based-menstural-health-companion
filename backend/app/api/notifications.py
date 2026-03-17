from typing import List
from collections import Counter
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Notification, Cycle, Symptom, Journal
from app.schemas.schemas import NotificationOut
from app.utils.auth import get_current_user
from app.services.email_service import send_weekly_health_summary

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=List[NotificationOut])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )


@router.put("/{notification_id}/read", response_model=NotificationOut)
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    n = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    ).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    n.is_read = True
    db.commit()
    db.refresh(n)
    return n


@router.post("/test-email")
def send_test_email(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    email = current_user.notify_email or current_user.email
    name = current_user.notify_name or current_user.full_name or current_user.username

    cycles = db.query(Cycle).filter(Cycle.user_id == current_user.id).all()
    symptoms = db.query(Symptom).filter(Symptom.user_id == current_user.id).all()
    journals = db.query(Journal).filter(Journal.user_id == current_user.id).all()
    lengths = [c.cycle_length for c in cycles if c.cycle_length]

    summary = {
        "total_cycles": len(cycles),
        "avg_cycle_length": round(sum(lengths) / len(lengths), 1) if lengths else "N/A",
        "total_symptoms_logged": len(symptoms),
        "total_journal_entries": len(journals),
        "top_symptoms": [s for s, _ in Counter(s.symptom_type for s in symptoms).most_common(5)],
    }

    sent = send_weekly_health_summary(email, name, summary)
    if sent:
        return {"status": "sent", "to": email}
    return {"status": "failed", "detail": "Check SMTP_USER and SMTP_PASSWORD in .env"}
