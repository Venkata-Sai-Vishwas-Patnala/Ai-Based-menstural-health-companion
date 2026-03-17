from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Cycle
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

    if last_cycle:
        cycle_day = calculate_cycle_day(last_cycle.start_date)
    else:
        cycle_day = 1

    phase = get_cycle_phase(cycle_day)
    diet = get_diet_for_phase(phase)

    return {
        "cycle_day": cycle_day,
        "phase": phase,
        "recommendations": diet,
    }
