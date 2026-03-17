from collections import Counter
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Cycle, Symptom, Journal, Prediction
from app.utils.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _get_phase(cycle_day: int, cycle_length: int) -> dict:
    period_len = 5
    ovulation_day = cycle_length - 14
    if cycle_day <= period_len:
        return {"phase": "Menstrual", "day_in_phase": cycle_day, "color": "#e91e8c",
                "description": "Your period is active. Rest, stay warm, and stay hydrated.",
                "tips": ["Apply heat to lower abdomen for cramps", "Eat iron-rich foods like spinach and lentils", "Light walks can ease bloating", "Stay hydrated with warm fluids"]}
    elif cycle_day <= ovulation_day - 2:
        return {"phase": "Follicular", "day_in_phase": cycle_day - period_len, "color": "#ff9800",
                "description": "Energy is rising. Great time for exercise and new activities.",
                "tips": ["Good time for high-intensity workouts", "Focus on protein-rich foods", "Your skin may look clearer now", "Creativity and focus are at a peak"]}
    elif cycle_day <= ovulation_day + 2:
        return {"phase": "Ovulation", "day_in_phase": cycle_day - (ovulation_day - 2), "color": "#4caf50",
                "description": "Peak energy and fertility window. You may feel your best.",
                "tips": ["Energy and libido are highest", "Great time for social activities", "Eat antioxidant-rich foods", "Track any ovulation symptoms"]}
    else:
        return {"phase": "Luteal", "day_in_phase": cycle_day - (ovulation_day + 2), "color": "#9c27b0",
                "description": "PMS may begin. Prioritise sleep and reduce stress.",
                "tips": ["Reduce caffeine and sugar", "Magnesium helps with mood swings", "Prioritise 8 hours of sleep", "Gentle yoga or stretching helps"]}


@router.get("/period-status")
def get_period_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()
    cycles = (
        db.query(Cycle)
        .filter(Cycle.user_id == current_user.id)
        .order_by(Cycle.start_date.desc())
        .all()
    )
    if not cycles:
        return {"status": "no_data"}

    latest = cycles[0]
    cycle_day = (today - latest.start_date).days + 1
    avg_cycle = current_user.average_cycle_length or 28

    # Check if currently on period
    on_period = False
    period_day = None
    if latest.end_date:
        on_period = latest.start_date <= today <= latest.end_date
        period_day = (today - latest.start_date).days + 1 if on_period else None
    elif cycle_day <= 7:  # no end_date logged, assume ~5 day period
        on_period = cycle_day <= 5
        period_day = cycle_day if on_period else None

    # Get prediction
    pred = (
        db.query(Prediction)
        .filter(Prediction.user_id == current_user.id)
        .order_by(Prediction.created_at.desc())
        .first()
    )
    if pred:
        days_until_next = (pred.predicted_start_date - today).days
    elif len(cycles) >= 2:
        days_until_next = avg_cycle - cycle_day
    else:
        days_until_next = None

    phase = _get_phase(cycle_day, avg_cycle)

    return {
        "status": "on_period" if on_period else "tracking",
        "on_period": on_period,
        "period_day": period_day,
        "cycle_day": cycle_day,
        "phase": phase,
        "days_until_next": days_until_next,
        "last_period_start": str(latest.start_date),
    }


@router.get("/")
def get_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cycles = (
        db.query(Cycle)
        .filter(Cycle.user_id == current_user.id)
        .order_by(Cycle.start_date.asc())
        .all()
    )
    symptoms = db.query(Symptom).filter(Symptom.user_id == current_user.id).all()
    journals = db.query(Journal).filter(Journal.user_id == current_user.id).all()

    # Cycle length trend
    cycle_trend = [
        {"date": str(c.start_date), "cycle_length": c.cycle_length}
        for c in cycles if c.cycle_length and 21 <= c.cycle_length <= 45
    ]

    # Symptom frequency
    symptom_counts = Counter(s.symptom_type for s in symptoms)
    symptom_freq = [{"symptom": k, "count": v} for k, v in symptom_counts.most_common(10)]

    # Mood trend
    mood_trend = [
        {"date": str(j.entry_date), "mood_score": j.mood_score, "mood": j.mood}
        for j in sorted(journals, key=lambda x: x.entry_date)
        if j.mood_score
    ]

    # Summary stats — only physiologically valid lengths
    lengths = [c.cycle_length for c in cycles if c.cycle_length and 21 <= c.cycle_length <= 45]
    summary = {
        "total_cycles": len(cycles),
        "avg_cycle_length": round(sum(lengths) / len(lengths), 1) if lengths else None,
        "min_cycle_length": min(lengths) if lengths else None,
        "max_cycle_length": max(lengths) if lengths else None,
        "total_symptoms_logged": len(symptoms),
        "total_journal_entries": len(journals),
    }

    return {
        "summary": summary,
        "cycle_trend": cycle_trend,
        "symptom_frequency": symptom_freq,
        "mood_trend": mood_trend,
    }
