"""
seed_data.py — populate the database with realistic synthetic training data.

Usage (from backend/ directory, venv active):
    python scripts/seed_data.py --user-email you@example.com --cycles 24

What it creates
───────────────
  • 24 cycles  (configurable) with realistic length variation
  • 3–6 symptom logs per cycle
  • 1 journal entry every 2–3 days
  • Runs the ML trainer after seeding

Realistic distributions used
─────────────────────────────
  Cycle length  : Normal(28, 2.5) clamped to [21, 45]
  Period length : Normal(5, 1)    clamped to [2, 8]
  Flow          : weighted random light/medium/heavy
  Symptoms      : drawn from a realistic pool with phase-aware severity
  Mood          : correlated with cycle phase (lower during menstrual/luteal)
"""
import argparse
import random
import sys
import os
from datetime import date, timedelta
from pathlib import Path

# Allow running from repo root or backend/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.models import Base, User, Cycle, Symptom, Journal
from app.utils.auth import hash_password
from app.ml.predictor import train_and_save

# ── helpers ───────────────────────────────────────────────────────────────────

SYMPTOM_POOL = {
    "menstrual":  [("Cramps", 6, 3), ("Fatigue", 5, 2), ("Bloating", 5, 2), ("Back pain", 4, 2)],
    "follicular": [("Headache", 3, 2), ("Acne", 3, 2), ("Fatigue", 2, 1)],
    "ovulation":  [("Breast tenderness", 4, 2), ("Bloating", 3, 2), ("Mood swings", 3, 2)],
    "luteal":     [("Mood swings", 6, 2), ("Bloating", 5, 2), ("Fatigue", 5, 2), ("Insomnia", 4, 2), ("Cramps", 3, 2)],
}

MOODS = {
    "menstrual":  ("Tired",    4, 3),
    "follicular": ("Energetic", 7, 2),
    "ovulation":  ("Happy",    8, 1),
    "luteal":     ("Anxious",  5, 2),
}

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def cycle_phase(day: int) -> str:
    if day <= 5:   return "menstrual"
    if day <= 13:  return "follicular"
    if day <= 16:  return "ovulation"
    return "luteal"

def rand_cycle_length() -> int:
    return clamp(int(random.gauss(28, 2.5)), 21, 45)

def rand_period_length() -> int:
    return clamp(int(random.gauss(5, 1)), 2, 8)

def rand_flow() -> str:
    return random.choices(["light", "medium", "heavy"], weights=[25, 55, 20])[0]


# ── main seeder ───────────────────────────────────────────────────────────────

def seed(user_email: str, n_cycles: int, db: Session):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        print(f"  User '{user_email}' not found - creating demo account")
        user = User(
            email=user_email,
            username=user_email.split("@")[0],
            hashed_password=hash_password("Demo1234!"),
            full_name="Demo User",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Start ~2 years ago
    current_start = date.today() - timedelta(days=n_cycles * 28 + 30)
    cycle_lengths_logged = []

    for i in range(n_cycles):
        cl = rand_cycle_length()
        pl = rand_period_length()
        end = current_start + timedelta(days=pl - 1)

        cycle = Cycle(
            user_id=user.id,
            start_date=current_start,
            end_date=end,
            cycle_length=cl if i > 0 else None,   # first cycle has no prior
            period_length=pl,
            flow_intensity=rand_flow(),
        )
        db.add(cycle)
        db.flush()

        if i > 0:
            cycle_lengths_logged.append(cl)

        # ── symptoms (3–6 per cycle) ──────────────────────────────────────
        n_sym = random.randint(3, 6)
        for _ in range(n_sym):
            day_offset = random.randint(0, cl - 1)
            sym_date = current_start + timedelta(days=day_offset)
            phase = cycle_phase(day_offset + 1)
            pool = SYMPTOM_POOL[phase]
            sym_name, base_sev, sev_std = random.choice(pool)
            severity = clamp(int(random.gauss(base_sev, sev_std)), 1, 10)
            db.add(Symptom(
                user_id=user.id,
                logged_date=sym_date,
                symptom_type=sym_name,
                severity=severity,
            ))

        # ── journal entries (every 2–3 days) ─────────────────────────────
        j_day = 0
        while j_day < cl:
            j_date = current_start + timedelta(days=j_day)
            phase = cycle_phase(j_day + 1)
            mood_name, base_score, score_std = MOODS[phase]
            mood_score = clamp(int(random.gauss(base_score, score_std)), 1, 10)
            energy = clamp(int(random.gauss(base_score - 1, score_std)), 1, 10)
            db.add(Journal(
                user_id=user.id,
                entry_date=j_date,
                mood=mood_name,
                mood_score=mood_score,
                energy_level=energy,
                content=f"Day {j_day + 1} of cycle — feeling {mood_name.lower()}.",
            ))
            j_day += random.randint(2, 3)

        current_start += timedelta(days=cl)

    db.commit()
    print(f"  Seeded {n_cycles} cycles, symptoms, and journal entries for '{user_email}'")
    return cycle_lengths_logged


def run_training(cycle_lengths: list[int]):
    if len(cycle_lengths) >= 4:
        metrics = train_and_save(cycle_lengths)
        print(f"  Model trained — samples: {metrics['samples_trained']}")
    else:
        print("  Not enough cycles to train ML model (need >= 4)")


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed menstrual health training data")
    parser.add_argument("--user-email", default="demo@example.com", help="Target user email")
    parser.add_argument("--cycles", type=int, default=24, help="Number of cycles to generate")
    args = parser.parse_args()

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        print(f"Seeding {args.cycles} cycles for {args.user_email} ...")
        lengths = seed(args.user_email, args.cycles, db)
        print("Training ML model ...")
        run_training(lengths)
        print("Done. You can now log in and generate predictions.")
    finally:
        db.close()
