from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Cycle, Symptom, Journal
from app.schemas.schemas import CycleCreate, CycleOut
from app.utils.auth import get_current_user

router = APIRouter(prefix="/cycle", tags=["cycle"])

SANE_MIN, SANE_MAX = 21, 45


def _validate_period_entry(db: Session, user_id: int, payload: CycleCreate) -> None:
    today = date.today()
    if payload.start_date > today:
        raise HTTPException(status_code=400, detail="Period start date cannot be in the future")
    if payload.end_date and payload.end_date > today:
        raise HTTPException(status_code=400, detail="Period end date cannot be in the future")
    if payload.end_date and payload.end_date < payload.start_date:
        raise HTTPException(status_code=400, detail="end_date cannot be before start_date")

    new_start = payload.start_date
    new_end = payload.end_date or payload.start_date

    existing = (
        db.query(Cycle)
        .filter(Cycle.user_id == user_id)
        .order_by(Cycle.start_date.desc())
        .all()
    )

    for cycle in existing:
        existing_start = cycle.start_date
        existing_end = cycle.end_date or cycle.start_date

        if new_start == existing_start:
            raise HTTPException(status_code=400, detail="This period start date already exists")

        if max(new_start, existing_start) <= min(new_end, existing_end):
            raise HTTPException(status_code=400, detail="This period overlaps an existing logged cycle")

        days_since_previous = (new_start - existing_start).days
        if 0 < days_since_previous < 21:
            raise HTTPException(status_code=400, detail="A new period entry is too close to a recently logged cycle")

        if new_start > existing_start and (new_start - existing_end).days < 21 and cycle.end_date is not None:
            raise HTTPException(status_code=400, detail="The new period is too close to the previous cycle end date")


@router.post("/", response_model=CycleOut, status_code=201)
def log_cycle(
    payload: CycleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _validate_period_entry(db, current_user.id, payload)

    period_length = None
    if payload.end_date:
        period_length = (payload.end_date - payload.start_date).days + 1
    if period_length is not None and (period_length < 2 or period_length > 14):
        raise HTTPException(status_code=400, detail="Period length looks invalid. Use a realistic range of 2-14 days.")

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

    cycle = Cycle(
        user_id=current_user.id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        flow_intensity=payload.flow_intensity,
        notes=payload.notes,
        period_length=period_length,
        cycle_length=None,
        ai_advice=None,
    )
    db.add(cycle)
    db.flush()

    all_cycles = (
        db.query(Cycle)
        .filter(Cycle.user_id == current_user.id)
        .order_by(Cycle.start_date.asc())
        .all()
    )
    for i, c in enumerate(all_cycles):
        if i + 1 < len(all_cycles):
            c.cycle_length = (all_cycles[i + 1].start_date - c.start_date).days
        else:
            c.cycle_length = None

    db.commit()
    db.refresh(cycle)
    return cycle


@router.get("/", response_model=List[CycleOut])
def get_cycles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Cycle)
        .filter(Cycle.user_id == current_user.id)
        .order_by(Cycle.start_date.desc())
        .all()
    )


@router.delete("/{cycle_id}", status_code=204)
def delete_cycle(
    cycle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cycle = db.query(Cycle).filter(Cycle.id == cycle_id, Cycle.user_id == current_user.id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    db.delete(cycle)
    db.commit()
