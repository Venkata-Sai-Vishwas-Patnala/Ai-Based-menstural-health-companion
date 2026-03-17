"""
Cycle-length predictor — RandomForestRegressor.

Feature vector (7 features, fixed order):
  0  prev_cycle_length       — most recent known cycle length
  1  avg_last3               — rolling mean of last 3 cycles
  2  std_last3               — rolling std  of last 3 cycles (0 if <2)
  3  period_length           — days of bleeding that cycle (5 if unknown)
  4  flow_encoded            — light=1 medium=2 heavy=3 (2 if unknown)
  5  avg_symptom_severity    — 0 if no symptoms logged
  6  avg_mood_score          — 0 if no journal entries

Design notes:
- prev_cycle_length replaces current_cycle_length to eliminate data leakage
- age/bmi removed — not available per-user at prediction time
- Model is always trained fresh on the user's own cycles (never the CSV model)
- Hard clamp 21–45 days enforced at all exit points
"""
from __future__ import annotations

import os
from datetime import date, timedelta
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

MODEL_PATH = Path(os.getenv("MODEL_DIR", "/tmp")) / "cycle_rf_model.joblib"

SANE_MIN = 21
SANE_MAX = 45
GLOBAL_AVG = 28
MIN_CYCLES_FOR_ML = 4   # need ≥4 lengths → 3 training pairs

FLOW_MAP = {"light": 1.0, "medium": 2.0, "heavy": 3.0}


# ── helpers ───────────────────────────────────────────────────────────────────

def _clamp(value: float) -> int:
    return max(SANE_MIN, min(SANE_MAX, int(round(value))))


def _rolling(lengths: list[int], idx: int):
    window = lengths[max(0, idx - 2): idx + 1]
    mean = float(np.mean(window))
    std = float(np.std(window)) if len(window) > 1 else 0.0
    return mean, std


# ── feature builder ───────────────────────────────────────────────────────────

def build_features(
    cycle_lengths: list[int],
    period_lengths: list[int | None] | None = None,
    flow_intensities: list[str | None] | None = None,
    symptom_stats: list[dict] | None = None,
    mood_stats: list[dict] | None = None,
) -> np.ndarray:
    n = len(cycle_lengths)
    period_lengths = period_lengths or [None] * n
    flow_intensities = flow_intensities or [None] * n
    symptom_stats = symptom_stats or [{}] * n
    mood_stats = mood_stats or [{}] * n

    rows = []
    for i in range(n - 1):
        avg3, std3 = _rolling(cycle_lengths, i)
        rows.append([
            float(cycle_lengths[i]),
            avg3,
            std3,
            float(period_lengths[i] or 5),
            float(FLOW_MAP.get(str(flow_intensities[i] or "").lower(), 2)),
            float(symptom_stats[i].get("avg_severity", 0) or 0),
            float(mood_stats[i].get("avg_mood", 0) or 0),
        ])
    return np.array(rows, dtype=float)


def build_prediction_row(
    cycle_lengths: list[int],
    last_period_length: int | None = None,
    last_flow: str | None = None,
    last_symptom_severity: float = 0.0,
    last_mood_score: float = 0.0,
) -> np.ndarray:
    avg3, std3 = _rolling(cycle_lengths, len(cycle_lengths) - 1)
    row = [
        float(cycle_lengths[-1]),
        avg3,
        std3,
        float(last_period_length or 5),
        float(FLOW_MAP.get(str(last_flow or "").lower(), 2)),
        float(last_symptom_severity or 0),
        float(last_mood_score or 0),
    ]
    return np.array([row], dtype=float)


# ── train ─────────────────────────────────────────────────────────────────────

def train_and_save(
    cycle_lengths: list[int],
    period_lengths: list[int | None] | None = None,
    flow_intensities: list[str | None] | None = None,
    symptom_stats: list[dict] | None = None,
    mood_stats: list[dict] | None = None,
) -> dict:
    X = build_features(cycle_lengths, period_lengths, flow_intensities, symptom_stats, mood_stats)
    y = np.array(cycle_lengths[1:], dtype=float)

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestRegressor(
            n_estimators=200,
            max_depth=5,
            min_samples_split=2,
            min_samples_leaf=1,
            random_state=42,
        )),
    ])
    pipeline.fit(X, y)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    return {"samples_trained": len(y)}


# ── confidence ────────────────────────────────────────────────────────────────

def _confidence_label(score: float) -> str:
    if score >= 0.85:
        return "High confidence"
    if score >= 0.65:
        return "Moderate confidence"
    if score >= 0.45:
        return "Low confidence"
    return "Irregular cycle"


# ── predict ───────────────────────────────────────────────────────────────────

def predict_next_cycle(
    cycle_lengths: list[int],
    last_period_start: date,
    last_period_length: int | None = None,
    last_flow: str | None = None,
    last_symptom_severity: float = 0.0,
    last_mood_score: float = 0.0,
    average_cycle_length: int = GLOBAL_AVG,
) -> dict:
    # Clamp any bad stored values
    valid_lengths = [_clamp(l) for l in cycle_lengths if SANE_MIN <= l <= SANE_MAX]

    from statistics import stdev as _std
    std_dev = round(_std(valid_lengths), 1) if len(valid_lengths) >= 2 else 0.0
    regularity = (
        "Your cycle is regular" if std_dev <= 4
        else "Your cycle varies — predictions may be less accurate"
    )

    # ── Fallback: fewer than 3 valid cycles → use rolling mean ───────────────
    if len(valid_lengths) < 3:
        if valid_lengths:
            mean_len = _clamp(np.mean(valid_lengths))
        else:
            mean_len = _clamp(average_cycle_length or GLOBAL_AVG)
        confidence = round(0.35 + 0.05 * len(valid_lengths), 2)

    # ── ML path ───────────────────────────────────────────────────────────────
    else:
        if len(valid_lengths) >= MIN_CYCLES_FOR_ML:
            train_and_save(valid_lengths)

        if MODEL_PATH.exists() and len(valid_lengths) >= MIN_CYCLES_FOR_ML:
            pipeline = joblib.load(MODEL_PATH)
            row = build_prediction_row(
                valid_lengths, last_period_length, last_flow,
                last_symptom_severity, last_mood_score,
            )
            raw = float(pipeline.predict(row)[0])

            rf: RandomForestRegressor = pipeline.named_steps["rf"]
            scaler = pipeline.named_steps["scaler"]
            tree_preds = np.array([t.predict(scaler.transform(row))[0] for t in rf.estimators_])
            std_dev_trees = float(np.std(tree_preds))
            confidence = round(max(0.0, min(1.0, 1.0 - std_dev_trees / 7.0)), 2)
        else:
            raw = float(np.mean(valid_lengths))
            confidence = round(0.5 + 0.03 * len(valid_lengths), 2)

        user_mean = float(np.mean(valid_lengths[-3:]))
        blended = 0.5 * raw + 0.5 * user_mean
        mean_len = _clamp(blended)

    predicted_start = last_period_start + timedelta(days=mean_len)
    predicted_end = predicted_start + timedelta(days=int(last_period_length or 5))

    return {
        "predicted_start_date": predicted_start,
        "predicted_end_date": predicted_end,
        "predicted_cycle_length": mean_len,
        "confidence_score": confidence,
        "confidence_label": _confidence_label(confidence),
        "avg_cycle_length": mean_len,
        "last_3_lengths": valid_lengths[-3:],
        "regularity": regularity,
        "std_dev": std_dev,
    }
