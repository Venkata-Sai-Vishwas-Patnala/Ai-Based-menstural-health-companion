"""
scheduler.py — APScheduler jobs for notifications + email alerts.

Jobs:
  daily_check    08:00 UTC daily  — period, PMS, mood, symptom alerts
  weekly_summary 09:00 UTC Monday — weekly health summary email
"""
from datetime import datetime, timedelta, date
from collections import Counter
from typing import Optional, Tuple
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.models import User, Prediction, Notification, Symptom, Journal, Cycle
from app.services.email_service import (
    send_period_alert,
    send_pms_alert,
    send_weekly_health_summary,
    send_mood_alert,
    send_high_symptom_alert,
)

scheduler = BackgroundScheduler(timezone="UTC")


def _can_notify(db: Session, user_id: int, ntype: str, hours: int = 20) -> bool:
    existing = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.notification_type == ntype,
        Notification.created_at >= datetime.utcnow() - timedelta(hours=hours),
    ).first()
    return existing is None


def _add_notification(db: Session, user_id: int, title: str, message: str, ntype: str):
    db.add(Notification(user_id=user_id, title=title, message=message, notification_type=ntype))


def _email_target(user: User) -> Optional[Tuple[str, str]]:
    if not user.email_notifications:
        return None
    email = user.notify_email or user.email
    name = user.notify_name or user.full_name or user.username
    return (email, name)


def daily_check():
    db: Session = SessionLocal()
    try:
        users = db.query(User).filter(User.is_active == True).all()
        today = date.today()

        for user in users:
            target = _email_target(user)

            # Period & PMS alerts
            pred = (
                db.query(Prediction)
                .filter(Prediction.user_id == user.id)
                .order_by(Prediction.created_at.desc())
                .first()
            )
            if pred:
                days_until = (pred.predicted_start_date - today).days

                # 7 days — PMS alert
                if days_until == 7 and _can_notify(db, user.id, "pms_alert"):
                    msg = "Your period is about a week away. Watch for PMS symptoms and practice self-care."
                    _add_notification(db, user.id, "PMS Alert — 7 Days", msg, "pms_alert")
                    if target:
                        send_pms_alert(target[0], target[1], pred.predicted_start_date)

                # 3, 2, 1 days — countdown alerts with unique messages
                elif days_until in (3, 2, 1) and _can_notify(db, user.id, f"period_alert_{days_until}"):
                    titles = {
                        3: "Period in 3 Days — Prepare Now",
                        2: "Period in 2 Days — Almost Time",
                        1: "Period Tomorrow — Get Ready!",
                    }
                    tips = {
                        3: "Stock up on pads/tampons, prepare a heating pad, and eat iron-rich foods today.",
                        2: "Reduce caffeine and salty foods. Keep pain relief handy. Rest well tonight.",
                        1: "Your period is expected tomorrow. Wear comfortable clothing and keep supplies close.",
                    }
                    _add_notification(db, user.id, titles[days_until], tips[days_until], f"period_alert_{days_until}")
                    if target:
                        send_period_alert(target[0], target[1], pred.predicted_start_date, days_until)

            # Mood alert — avg mood < 4 over last 3 days (minimum 1 entry)
            recent_journals = db.query(Journal).filter(
                Journal.user_id == user.id,
                Journal.entry_date >= today - timedelta(days=3),
                Journal.mood_score.isnot(None),
            ).all()
            if len(recent_journals) >= 1:
                avg_mood = sum(j.mood_score for j in recent_journals) / len(recent_journals)
                if avg_mood < 4 and _can_notify(db, user.id, "mood_alert", hours=48):
                    msg = f"Your average mood score over the last 3 days is {avg_mood:.1f}/10. Take care of yourself."
                    _add_notification(db, user.id, "Low Mood Detected", msg, "mood_alert")
                    if target:
                        send_mood_alert(target[0], target[1], avg_mood, 3)

            # High severity symptom alert — severity >= 8 today
            severe_today = db.query(Symptom).filter(
                Symptom.user_id == user.id,
                Symptom.logged_date == today,
                Symptom.severity >= 8,
            ).first()
            if severe_today and _can_notify(db, user.id, "symptom_alert", hours=12):
                msg = f"You logged {severe_today.symptom_type} with severity {severe_today.severity}/10 today. Consider resting and staying hydrated."
                _add_notification(db, user.id, f"High Severity: {severe_today.symptom_type}", msg, "symptom_alert")
                if target:
                    send_high_symptom_alert(target[0], target[1], severe_today.symptom_type, severe_today.severity)

        db.commit()
    finally:
        db.close()


def weekly_summary():
    db: Session = SessionLocal()
    try:
        users = db.query(User).filter(User.is_active == True).all()

        for user in users:
            target = _email_target(user)
            if not target:
                continue

            cycles = db.query(Cycle).filter(Cycle.user_id == user.id).all()
            symptoms = db.query(Symptom).filter(Symptom.user_id == user.id).all()
            journals = db.query(Journal).filter(Journal.user_id == user.id).all()

            lengths = [c.cycle_length for c in cycles if c.cycle_length]
            avg_cycle = round(sum(lengths) / len(lengths), 1) if lengths else "N/A"
            top_symptoms = [s for s, _ in Counter(s.symptom_type for s in symptoms).most_common(5)]

            summary = {
                "total_cycles": len(cycles),
                "avg_cycle_length": avg_cycle,
                "total_symptoms_logged": len(symptoms),
                "total_journal_entries": len(journals),
                "top_symptoms": top_symptoms,
            }

            if _can_notify(db, user.id, "health_tip", hours=144):
                _add_notification(
                    db, user.id,
                    "Weekly Health Summary",
                    f"You have logged {len(cycles)} cycles and {len(symptoms)} symptoms. Check your email for the full summary.",
                    "health_tip",
                )

            send_weekly_health_summary(target[0], target[1], summary)

        db.commit()
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(daily_check, "cron", hour=8, minute=0, id="daily_check")
    scheduler.add_job(weekly_summary, "cron", day_of_week="mon", hour=9, minute=0, id="weekly_summary")
    scheduler.start()


def stop_scheduler():
    scheduler.shutdown(wait=False)
