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

    on_period = False
    period_day = None
    if latest.end_date:
        on_period = latest.start_date <= today <= latest.end_date
        period_day = (today - latest.start_date).days + 1 if on_period else None
    elif cycle_day <= 7:
        on_period = cycle_day <= 5
        period_day = cycle_day if on_period else None

    pred = (
        db.query(Prediction)
        .filter(Prediction.user_id == current_user.id)
        .order_by(Prediction.created_at.desc())
        .first()
    )
    if pred:
        days_until_next = (pred.predicted_start_date - today).days
    elif len(cycles) >= 2:
        days_until_next = max(0, avg_cycle - cycle_day)
    else:
        days_until_next = None

    phase = _get_phase(cycle_day, avg_cycle)
    ai_tip = latest.ai_advice or (
        "Keep your routine gentle, stay hydrated, and listen to your body for signs of fatigue or bloating."
        if on_period else
        "Track your symptoms consistently and keep your meals steady to help your cycle stay predictable."
    )

    return {
        "status": "on_period" if on_period else "tracking",
        "on_period": on_period,
        "period_day": period_day,
        "cycle_day": cycle_day,
        "phase": phase,
        "days_until_next": days_until_next,
        "last_period_start": str(latest.start_date),
        "ai_tip": ai_tip,
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

    cycle_trend = [
        {"date": str(c.start_date), "cycle_length": c.cycle_length}
        for c in cycles if c.cycle_length and 21 <= c.cycle_length <= 45
    ]

    symptom_counts = Counter(s.symptom_type for s in symptoms)
    symptom_freq = [{"symptom": k, "count": v} for k, v in symptom_counts.most_common(10)]

    mood_trend = [
        {"date": str(j.entry_date), "mood_score": j.mood_score, "mood": j.mood}
        for j in sorted(journals, key=lambda x: x.entry_date)
        if j.mood_score
    ]

    lengths = [c.cycle_length for c in cycles if c.cycle_length and 21 <= c.cycle_length <= 45]
    avg_mood = round(sum(j.mood_score for j in journals if j.mood_score) / len([j for j in journals if j.mood_score]), 1) if any(j.mood_score for j in journals) else None
    avg_severity = round(sum(s.severity for s in symptoms if s.severity is not None) / len([s for s in symptoms if s.severity is not None]), 1) if any(s.severity is not None for s in symptoms) else None
    top_symptom = symptom_counts.most_common(1)[0][0] if symptom_counts else None

    current_phase = "No data"
    cycle_day = None
    status = "No cycle data"
    days_until_next = None
    if cycles:
        latest = cycles[-1]
        cycle_day = (date.today() - latest.start_date).days + 1
        cycle_day = max(1, cycle_day)
        if cycle_day <= 5:
            current_phase = "Menstrual"
        elif cycle_day <= 13:
            current_phase = "Follicular"
        elif cycle_day <= 16:
            current_phase = "Ovulation"
        else:
            current_phase = "Luteal"
        status = "On period" if latest.end_date and latest.start_date <= date.today() <= latest.end_date else "Tracking"
        avg_cycle = current_user.average_cycle_length or 28
        days_until_next = max(0, avg_cycle - cycle_day)

    summary = {
        "total_cycles": len(cycles),
        "avg_cycle_length": round(sum(lengths) / len(lengths), 1) if lengths else None,
        "min_cycle_length": min(lengths) if lengths else None,
        "max_cycle_length": max(lengths) if lengths else None,
        "total_symptoms_logged": len(symptoms),
        "total_journal_entries": len(journals),
        "avg_mood_score": avg_mood,
        "avg_symptom_severity": avg_severity,
        "top_symptom": top_symptom,
        "current_phase": current_phase,
        "cycle_day": cycle_day,
        "status": status,
        "days_until_next": days_until_next,
    }

    return {
        "summary": summary,
        "cycle_trend": cycle_trend,
        "symptom_frequency": symptom_freq,
        "mood_trend": mood_trend,
    }
