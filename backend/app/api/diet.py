from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Cycle, Symptom
from app.utils.auth import get_current_user
from app.utils.diet import get_cycle_phase, get_diet_for_phase, calculate_cycle_day

router = APIRouter(prefix="/diet", tags=["diet"])


@router.get("/")
def get_diet_recommendation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    last_cycle = (
        db.query(Cycle)
        .filter(Cycle.user_id == current_user.id)
        .order_by(Cycle.start_date.desc())
        .first()
    )

    preferred_cycle_length = current_user.average_cycle_length or 28
    if last_cycle:
        cycle_length = last_cycle.cycle_length or preferred_cycle_length
        cycle_day = calculate_cycle_day(last_cycle.start_date, cycle_length=cycle_length)
    else:
        cycle_day = 1
        cycle_length = preferred_cycle_length

    recent_symptoms = (
        db.query(Symptom)
        .filter(Symptom.user_id == current_user.id)
        .order_by(Symptom.logged_date.desc())
        .limit(5)
        .all()
    )
    severity = max((s.severity for s in recent_symptoms if s.severity is not None), default=0)

    phase = get_cycle_phase(cycle_day)
    diet = get_diet_for_phase(phase, severity=severity)

    return {
        "cycle_day": cycle_day,
        "cycle_length": cycle_length,
        "phase": phase,
        "severity": severity,
        "severity_label": diet.get("severity_label", "low"),
        "recommendations": {
            **diet,
            "remedies": diet.get("remedies", []),
            "suggestions": diet.get("suggestions", []),
            "diet_variants": diet.get("diet_variants", []),
        },
    }
