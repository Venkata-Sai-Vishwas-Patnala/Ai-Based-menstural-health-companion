from datetime import date, timedelta

from app.utils.diet import calculate_cycle_day, get_cycle_phase, get_diet_for_phase
from app.api.chatbot import build_context_summary, SYSTEM_PROMPT


def test_calculate_cycle_day_uses_actual_cycle_length():
    start = date.today() - timedelta(days=12)
    assert calculate_cycle_day(start, cycle_length=30) == 13


def test_phase_changes_are_correct_across_cycle_days():
    assert get_cycle_phase(1) == "menstrual"
    assert get_cycle_phase(6) == "follicular"
    assert get_cycle_phase(14) == "ovulation"
    assert get_cycle_phase(17) == "luteal"


def test_diet_changes_for_high_severity_and_phase():
    plan = get_diet_for_phase("menstrual", severity=9)
    assert plan["severity_label"] == "high"
    assert "extra hydration" in plan["hydration"].lower()
    assert any("heating pad" in item.lower() for item in plan["remedies"])
    assert "daily_advice" in plan
    assert len(plan["daily_advice"]) > 40


def test_build_context_summary_includes_relative_times_and_symptoms():
    symptoms = [
        {"symptom_type": "Cramps", "logged_date": date.today() - timedelta(days=1), "severity": 7},
        {"symptom_type": "Bloating", "logged_date": date.today() - timedelta(days=4), "severity": 5},
    ]
    mood = [{"mood": "Anxious", "mood_score": 3, "entry_date": date.today() - timedelta(days=2)}]

    summary = build_context_summary(symptoms, mood)

    assert "Cramps" in summary
    assert "yesterday" in summary.lower()
    assert "bloating" in summary.lower()
    assert "anxious" in summary.lower()


def test_chatbot_prompt_requires_complete_answers():
    assert "complete" in SYSTEM_PROMPT.lower()
    assert "do not stop after the first sentence" in SYSTEM_PROMPT.lower()


def test_prediction_result_does_not_expose_pattern_stability_text():
    from app.ml.predictor import predict_next_cycle

    result = predict_next_cycle([28, 30, 29, 31], date.today())

    assert "regularity" not in result
    assert "Pattern stable" not in str(result)


def test_phase_diets_have_multiple_prebuilt_options():
    from app.utils.diet import get_diet_for_phase

    for phase in ["menstrual", "follicular", "ovulation", "luteal"]:
        diet = get_diet_for_phase(phase, severity=5)
        assert 10 <= len(diet["diet_variants"]) <= 20
        assert all("foods" in variant and "name" in variant["foods"][0] for variant in diet["diet_variants"])
