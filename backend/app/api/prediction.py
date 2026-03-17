from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Cycle, Symptom, Journal, Prediction
from app.utils.auth import get_current_user
from app.ml.predictor import predict_next_cycle, train_and_save

router = APIRouter(prefix="/prediction", tags=["prediction"])


def _complete_cycles(cycles: list) -> list:
    """Only cycles with both start_date and end_date."""
    return [c for c in cycles if c.start_date and c.end_date]


def _gather_context(db: Session, user_id: int, cycles: list):
    symptom_stats, mood_stats = [], []
    for i, cycle in enumerate(cycles):
        window_start = cycle.start_date
        window_end = cycles[i + 1].start_date if i + 1 < len(cycles) else None

        sym_q = db.query(func.avg(Symptom.severity).label("avg_severity")).filter(
            Symptom.user_id == user_id, Symptom.logged_date >= window_start,
        )
        if window_end:
            sym_q = sym_q.filter(Symptom.logged_date < window_end)

        mood_q = db.query(func.avg(Journal.mood_score).label("avg_mood")).filter(
            Journal.user_id == user_id, Journal.entry_date >= window_start,
        )
        if window_end:
            mood_q = mood_q.filter(Journal.entry_date < window_end)

        symptom_stats.append({"avg_severity": float(sym_q.first().avg_severity or 0)})
        mood_stats.append({"avg_mood": float(mood_q.first().avg_mood or 0)})

    return symptom_stats, mood_stats


@router.post("/", status_code=201)
def generate_prediction(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    all_cycles = (
        db.query(Cycle)
        .filter(Cycle.user_id == current_user.id)
        .order_by(Cycle.start_date.asc())
        .all()
    )

    complete = _complete_cycles(all_cycles)
    if len(complete) < 2:
        raise HTTPException(
            status_code=400,
            detail=f"Need at least 2 completed cycles to predict. You have {len(complete)}."
        )

    cycles_with_length = [c for c in complete if c.cycle_length is not None]
    if not cycles_with_length:
        raise HTTPException(status_code=400, detail="No valid cycle lengths found.")

    cycle_lengths = [c.cycle_length for c in cycles_with_length]
    period_lengths = [c.period_length for c in cycles_with_length]
    flow_intensities = [c.flow_intensity for c in cycles_with_length]
    symptom_stats, mood_stats = _gather_context(db, current_user.id, cycles_with_length)

    # Use active cycle start if available, else last complete cycle
    active = next((c for c in reversed(all_cycles) if not c.end_date), None)
    last_cycle = active if active and active.start_date > complete[-1].start_date else complete[-1]

    result = predict_next_cycle(
        cycle_lengths=cycle_lengths,
        last_period_start=last_cycle.start_date,
        last_period_length=last_cycle.period_length,
        last_flow=last_cycle.flow_intensity,
        last_symptom_severity=symptom_stats[-1]["avg_severity"] if symptom_stats else 0.0,
        last_mood_score=mood_stats[-1]["avg_mood"] if mood_stats else 0.0,
        average_cycle_length=current_user.average_cycle_length or 28,
    )

    prediction = Prediction(
        user_id=current_user.id,
        predicted_start_date=result["predicted_start_date"],
        predicted_end_date=result["predicted_end_date"],
        predicted_cycle_length=result["predicted_cycle_length"],
        confidence_score=result["confidence_score"],
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return {
        **{c.name: getattr(prediction, c.name) for c in prediction.__table__.columns},
        "confidence_label": result["confidence_label"],
        "avg_cycle_length": result["avg_cycle_length"],
        "last_3_lengths": result["last_3_lengths"],
        "regularity": result["regularity"],
        "std_dev": result["std_dev"],
        "insufficient_data": False,
        "complete_cycles": len(complete),
    }


@router.post("/train")
def train_model(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    all_cycles = (
        db.query(Cycle)
        .filter(Cycle.user_id == current_user.id)
        .order_by(Cycle.start_date.asc())
        .all()
    )
    complete = _complete_cycles(all_cycles)
    cycles_with_length = [c for c in complete if c.cycle_length is not None]
    if len(cycles_with_length) < 4:
        raise HTTPException(
            status_code=400,
            detail=f"Need at least 4 cycles to train. You have {len(cycles_with_length)}.",
        )

    cycle_lengths = [c.cycle_length for c in cycles_with_length]
    period_lengths = [c.period_length for c in cycles_with_length]
    flow_intensities = [c.flow_intensity for c in cycles_with_length]
    symptom_stats, mood_stats = _gather_context(db, current_user.id, cycles_with_length)

    metrics = train_and_save(cycle_lengths, period_lengths, flow_intensities, symptom_stats, mood_stats)
    return {"status": "trained", **metrics}


@router.get("/latest")
def get_latest_prediction(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    all_cycles = (
        db.query(Cycle)
        .filter(Cycle.user_id == current_user.id)
        .order_by(Cycle.start_date.asc())
        .all()
    )
    complete = _complete_cycles(all_cycles)

    if len(complete) < 2:
        return {
            "insufficient_data": True,
            "complete_cycles": len(complete),
        }

    cycles_with_length = [c for c in complete if c.cycle_length is not None]
    if not cycles_with_length:
        return {"insufficient_data": True, "complete_cycles": len(complete)}

    cycle_lengths = [c.cycle_length for c in cycles_with_length]
    period_lengths = [c.period_length for c in cycles_with_length]
    flow_intensities = [c.flow_intensity for c in cycles_with_length]
    symptom_stats, mood_stats = _gather_context(db, current_user.id, cycles_with_length)

    active = next((c for c in reversed(all_cycles) if not c.end_date), None)
    last_cycle = active if active and active.start_date > complete[-1].start_date else complete[-1]

    result = predict_next_cycle(
        cycle_lengths=cycle_lengths,
        last_period_start=last_cycle.start_date,
        last_period_length=last_cycle.period_length,
        last_flow=last_cycle.flow_intensity,
        last_symptom_severity=symptom_stats[-1]["avg_severity"] if symptom_stats else 0.0,
        last_mood_score=mood_stats[-1]["avg_mood"] if mood_stats else 0.0,
        average_cycle_length=current_user.average_cycle_length or 28,
    )

    pred = (
        db.query(Prediction)
        .filter(Prediction.user_id == current_user.id)
        .order_by(Prediction.created_at.desc())
        .first()
    )

    return {
        "predicted_start_date": str(result["predicted_start_date"]),
        "predicted_end_date": str(result["predicted_end_date"]),
        "predicted_cycle_length": result["predicted_cycle_length"],
        "confidence_score": result["confidence_score"],
        "confidence_label": result["confidence_label"],
        "avg_cycle_length": result["avg_cycle_length"],
        "last_3_lengths": result["last_3_lengths"],
        "regularity": result["regularity"],
        "std_dev": result["std_dev"],
        "insufficient_data": False,
        "complete_cycles": len(complete),
        "id": pred.id if pred else None,
        "created_at": str(pred.created_at) if pred else None,
    }
