from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Cycle
from app.schemas.schemas import CycleCreate, CycleOut
from app.utils.auth import get_current_user

router = APIRouter(prefix="/cycle", tags=["cycle"])

SANE_MIN, SANE_MAX = 21, 45


@router.post("/", response_model=CycleOut, status_code=201)
def log_cycle(
    payload: CycleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.end_date and payload.end_date < payload.start_date:
        raise HTTPException(status_code=400, detail="end_date cannot be before start_date")

    period_length = None
    if payload.end_date:
        period_length = (payload.end_date - payload.start_date).days + 1

    cycle = Cycle(
        user_id=current_user.id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        flow_intensity=payload.flow_intensity,
        notes=payload.notes,
        period_length=period_length,
        cycle_length=None,
    )
    db.add(cycle)
    db.flush()  # get the new row into the session without committing

    # Recalculate cycle_length for ALL user cycles sorted by start_date.
    # cycle_length[i] = start_date[i+1] - start_date[i]
    # The most recent cycle always has cycle_length=NULL (next start unknown).
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
            c.cycle_length = None  # most recent — unknown until next cycle logged

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
