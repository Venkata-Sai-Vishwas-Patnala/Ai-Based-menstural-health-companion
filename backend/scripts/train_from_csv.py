"""
train_from_csv.py — Train population prior model on FedCycleData dataset.

Feature vector (7 features, must match predictor.py exactly):
  0  prev_cycle_length
  1  avg_last3
  2  std_last3
  3  period_length           (LengthofMenses proxy)
  4  flow_encoded            (MeanBleedingIntensity bucketed: 1/2/3)
  5  avg_symptom_severity    (TotalMensesScore normalised)
  6  avg_mood_score          (0 — not in dataset, filled with 0)

Target: next cycle length (cycle_lengths[i+1])

Usage:
  python scripts/train_from_csv.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_absolute_error

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_CSV = SCRIPT_DIR / "data" / "FedCycleData071012 (2).csv"
DEFAULT_OUT = SCRIPT_DIR.parent / "ml_models" / "cycle_rf_model.joblib"

SANE_MIN, SANE_MAX = 21, 45


def _safe(val, default):
    try:
        v = float(str(val).strip())
        return v if not np.isnan(v) else default
    except (ValueError, TypeError):
        return default


def _flow_encode(intensity: float) -> float:
    """Map MeanBleedingIntensity (continuous) to 1/2/3 buckets."""
    if intensity <= 1.5:
        return 1.0
    if intensity <= 2.5:
        return 2.0
    return 3.0


def build_rows(group: pd.DataFrame):
    df = group.sort_values("CycleNumber").reset_index(drop=True)
    lengths = [_safe(v, None) for v in df["LengthofCycle"]]
    lengths = [v for v in lengths if v is not None and SANE_MIN <= v <= SANE_MAX]

    if len(lengths) < 2:
        return [], []

    rows_X, rows_y = [], []
    for i in range(len(lengths) - 1):
        window = lengths[max(0, i - 2): i + 1]
        avg3 = float(np.mean(window))
        std3 = float(np.std(window)) if len(window) > 1 else 0.0

        period_len = _safe(df.at[i, "LengthofMenses"] if "LengthofMenses" in df.columns else 5, 5)
        flow_raw   = _safe(df.at[i, "MeanBleedingIntensity"] if "MeanBleedingIntensity" in df.columns else 2, 2)
        sym_sev    = _safe(df.at[i, "TotalMensesScore"] if "TotalMensesScore" in df.columns else 0, 0) / 10.0

        rows_X.append([
            float(lengths[i]),   # 0 prev_cycle_length
            avg3,                # 1 avg_last3
            std3,                # 2 std_last3
            period_len,          # 3 period_length
            _flow_encode(flow_raw),  # 4 flow_encoded
            sym_sev,             # 5 avg_symptom_severity
            0.0,                 # 6 avg_mood_score (not in dataset)
        ])
        rows_y.append(float(lengths[i + 1]))

    return rows_X, rows_y


def main():
    csv_path = DEFAULT_CSV
    out_path = DEFAULT_OUT

    if not csv_path.exists():
        print(f"CSV not found: {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)
    df = df[pd.to_numeric(df["LengthofCycle"], errors="coerce").notna()].copy()

    all_X, all_y = [], []
    for _, group in df.groupby("ClientID"):
        X, y = build_rows(group)
        all_X.extend(X)
        all_y.extend(y)

    X_all = np.array(all_X, dtype=float)
    y_all = np.array(all_y, dtype=float)

    print(f"Training pairs: {len(y_all)}")
    print(f"Mean cycle: {y_all.mean():.1f}  Std: {y_all.std():.1f}  Range: {y_all.min():.0f}-{y_all.max():.0f}")

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestRegressor(
            n_estimators=300,
            max_depth=5,
            min_samples_split=2,
            min_samples_leaf=1,
            max_features="sqrt",
            random_state=42,
            n_jobs=-1,
        )),
    ])

    cv = min(5, len(y_all) // 10)
    if cv >= 2:
        scores = cross_val_score(pipeline, X_all, y_all, cv=cv, scoring="neg_mean_absolute_error", n_jobs=-1)
        print(f"CV MAE: {-scores.mean():.2f} ± {scores.std():.2f} days ({cv}-fold)")

    pipeline.fit(X_all, y_all)
    train_mae = mean_absolute_error(y_all, pipeline.predict(X_all))
    print(f"Train MAE: {train_mae:.2f} days")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, out_path)
    print(f"Model saved: {out_path}")


if __name__ == "__main__":
    main()
