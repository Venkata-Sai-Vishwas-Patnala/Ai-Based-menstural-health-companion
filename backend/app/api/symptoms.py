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


@router.post("/", response_model=SymptomOut, status_code=201)
def log_symptom(
    payload: SymptomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    symptom = Symptom(user_id=current_user.id, **payload.model_dump())
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
