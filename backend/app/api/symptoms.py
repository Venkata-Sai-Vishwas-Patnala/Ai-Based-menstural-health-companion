from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Symptom, Notification
from app.schemas.schemas import SymptomCreate, SymptomOut
from app.utils.auth import get_current_user
from app.services.email_service import send_high_symptom_alert

router = APIRouter(prefix="/symptoms", tags=["symptoms"])


def _build_symptom_advice(payload: SymptomCreate) -> str:
    severity = payload.severity or 5
    name = payload.symptom_type.lower()
    if severity >= 8:
        return f"This is a high-severity {payload.symptom_type.lower()} log. Rest, hydrate well, and consider a warm compress or gentle movement. If it continues for more than a day or worsens, contact a clinician."
    if "cramp" in name or "pain" in name:
        return f"Your {payload.symptom_type.lower()} log is recent. A heating pad, stretching, and magnesium-rich foods may help. Avoid heavy exertion until it settles."
    if "bloat" in name or "swelling" in name:
        return "Your bloating is likely manageable with hydration, gentle walks, and lower-sodium meals. Try limiting caffeine and salty snacks for a few hours."
    if "headache" in name:
        return "A recent headache can ease with hydration, rest, and avoiding excess caffeine or screens. Keep your room cool and dark if it is still bothering you."
    if "fatigue" in name:
        return "This fatigue pattern suggests your body may need more rest right now. Try a lighter day, prioritize sleep, and keep meals regular and protein-rich."
    if "mood" in name or "anxious" in name:
        return "Mood-linked symptoms are often easier to manage with rest, calm routines, and a little extra support. Journaling and a short walk can help regulate stress."
    return f"This {payload.symptom_type.lower()} entry is useful context. Watch for patterns over the next few days and combine rest, hydration, and routine checks with your cycle tracker."


@router.post("/", response_model=SymptomOut, status_code=201)
def log_symptom(
    payload: SymptomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    symptom = Symptom(user_id=current_user.id, **payload.model_dump())
    symptom.ai_advice = _build_symptom_advice(payload)
    db.add(symptom)
    db.commit()
    db.refresh(symptom)

    # Immediate high severity alert — don't wait for scheduler
    if payload.severity is not None and payload.severity >= 8:
        already_notified = db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.notification_type == "symptom_alert",
            Notification.created_at >= date.today(),
        ).first()
        if not already_notified:
            msg = f"You logged {payload.symptom_type} with severity {payload.severity}/10. Rest and stay hydrated."
            db.add(Notification(user_id=current_user.id, title=f"High Severity: {payload.symptom_type}", message=msg, notification_type="symptom_alert"))
            db.commit()
            email = current_user.notify_email or current_user.email
            name = current_user.notify_name or current_user.full_name or current_user.username
            if current_user.email_notifications:
                send_high_symptom_alert(email, name, payload.symptom_type, payload.severity)

    return symptom


@router.get("/", response_model=List[SymptomOut])
def get_symptoms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Symptom)
        .filter(Symptom.user_id == current_user.id)
        .order_by(Symptom.logged_date.desc())
        .all()
    )


@router.delete("/{symptom_id}", status_code=204)
def delete_symptom(
    symptom_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    s = db.query(Symptom).filter(Symptom.id == symptom_id, Symptom.user_id == current_user.id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Symptom not found")
    db.delete(s)
    db.commit()
