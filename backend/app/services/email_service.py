"""
email_service.py — sends HTML health update emails via SMTP.

To use Gmail:
  1. Enable 2FA on your Google account
  2. Google Account > Security > App Passwords > generate one
  3. Put it in SMTP_PASSWORD in .env
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date


def _send(to_email: str, to_name: str, subject: str, html_body: str) -> bool:
    from app.config import get_settings
    s = get_settings()
    if not s.SMTP_USER or not s.SMTP_PASSWORD:
        print("[Email] SMTP not configured — skipping send")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.SMTP_FROM_NAME} <{s.SMTP_USER}>"
        msg["To"] = f"{to_name} <{to_email}>"
        msg.attach(MIMEText(html_body, "html"))
        with smtplib.SMTP(s.SMTP_HOST, s.SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(s.SMTP_USER, s.SMTP_PASSWORD)
            server.sendmail(s.SMTP_USER, to_email, msg.as_string())
        print(f"[Email] Sent '{subject}' to {to_email}")
        return True
    except Exception as e:
        print(f"[Email] Failed to send to {to_email}: {e}")
        return False


def _base_template(title: str, content: str) -> str:
    return f"""
    <html><body style="font-family:Segoe UI,sans-serif;background:#fff5f8;margin:0;padding:0;">
    <div style="max-width:560px;margin:32px auto;background:white;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(233,30,140,0.1);">
      <div style="background:linear-gradient(135deg,#e91e8c,#9c27b0);padding:28px 32px;">
        <h1 style="color:white;margin:0;font-size:1.4rem;">MenstrualAI Health</h1>
        <p style="color:rgba(255,255,255,0.85);margin:4px 0 0;font-size:0.9rem;">{title}</p>
      </div>
      <div style="padding:28px 32px;">{content}</div>
      <div style="padding:16px 32px;background:#fff5f8;border-top:1px solid #f0d0dc;">
        <p style="color:#9e9e9e;font-size:0.75rem;margin:0;">
          This is general health information only — not medical advice.
          Always consult a qualified healthcare professional for medical concerns.
        </p>
      </div>
    </div>
    </body></html>
    """


def send_period_alert(to_email: str, to_name: str, predicted_date: date, days_until: int) -> bool:
    day_content = {
        3: {
            "color": "#e91e8c", "bg": "#fff5f8", "heading": "Period in 3 Days — Prepare Now",
            "tips": [
                "Stock up on pads, tampons, or menstrual cup",
                "Prepare a heating pad for cramps",
                "Eat iron-rich foods: spinach, lentils, red meat",
                "Brew ginger or chamomile tea in advance",
            ]
        },
        2: {
            "color": "#d81b60", "bg": "#fce4ec", "heading": "Period in 2 Days — Almost Time",
            "tips": [
                "Reduce caffeine and salty foods to minimise bloating",
                "Keep ibuprofen or pain relief handy",
                "Wear comfortable, dark clothing tomorrow",
                "Rest well tonight — good sleep reduces cramp severity",
            ]
        },
        1: {
            "color": "#c2185b", "bg": "#f8bbd0", "heading": "Period Tomorrow — Get Ready!",
            "tips": [
                "Keep your period supplies in your bag today",
                "Avoid heavy exercise — opt for light yoga or walking",
                "Stay warm and hydrated throughout the day",
                "Take pain relief at first sign of cramps",
            ]
        },
    }
    d = day_content.get(days_until, day_content[3])
    tips_html = "".join(f'<li>{t}</li>' for t in d['tips'])
    content = f"""
    <p style="color:#2d2d2d;">Hi <strong>{to_name}</strong>,</p>
    <div style="background:{d['bg']};border-left:4px solid {d['color']};border-radius:8px;padding:16px 20px;margin:16px 0;">
      <p style="margin:0;font-size:1.1rem;font-weight:600;color:{d['color']};">{d['heading']}</p>
      <p style="margin:8px 0 0;color:#757575;">Predicted date: <strong>{predicted_date.strftime('%B %d, %Y')}</strong></p>
    </div>
    <ul style="color:#555;line-height:2;">{tips_html}</ul>
    """
    return _send(to_email, to_name, f"🔴 Period Alert — {days_until} day{'s' if days_until > 1 else ''} away", _base_template(d['heading'], content))


def send_pms_alert(to_email: str, to_name: str, predicted_date: date) -> bool:
    content = f"""
    <p style="color:#2d2d2d;">Hi <strong>{to_name}</strong>,</p>
    <div style="background:#f3e5f5;border-left:4px solid #9c27b0;border-radius:8px;padding:16px 20px;margin:16px 0;">
      <p style="margin:0;font-size:1.1rem;font-weight:600;color:#7b1fa2;">PMS Window Approaching</p>
      <p style="margin:8px 0 0;color:#757575;">Your period is expected around <strong>{predicted_date.strftime('%B %d, %Y')}</strong></p>
    </div>
    <p style="color:#2d2d2d;">Tips for the luteal phase:</p>
    <ul style="color:#555;line-height:2;">
      <li>Increase magnesium intake (dark chocolate, nuts, leafy greens)</li>
      <li>Reduce caffeine and alcohol</li>
      <li>Prioritise sleep - aim for 8 hours</li>
      <li>Light exercise like yoga or walking helps mood</li>
      <li>Track mood swings and energy in your journal</li>
    </ul>
    """
    return _send(to_email, to_name, "PMS Alert - Take care of yourself", _base_template("PMS Reminder", content))


def send_weekly_health_summary(to_email: str, to_name: str, summary: dict) -> bool:
    cycles_logged = summary.get("total_cycles", 0)
    avg_cycle = summary.get("avg_cycle_length", "N/A")
    symptoms_logged = summary.get("total_symptoms_logged", 0)
    journals_logged = summary.get("total_journal_entries", 0)
    top_symptoms = summary.get("top_symptoms", [])

    sym_html = "".join(
        f'<span style="background:#f8bbd0;color:#c2185b;padding:3px 10px;border-radius:20px;'
        f'font-size:0.8rem;margin:2px;display:inline-block;">{s}</span>'
        for s in top_symptoms[:5]
    ) or "<em style='color:#9e9e9e;'>None logged</em>"

    content = f"""
    <p style="color:#2d2d2d;">Hi <strong>{to_name}</strong>, here is your weekly health summary:</p>
    <table width="100%" cellpadding="0" cellspacing="8" style="margin:16px 0;">
      <tr>
        <td width="50%" style="background:#fff5f8;border-radius:8px;padding:14px;text-align:center;">
          <div style="font-size:1.6rem;font-weight:700;color:#e91e8c;">{cycles_logged}</div>
          <div style="font-size:0.8rem;color:#757575;">Cycles Logged</div>
        </td>
        <td width="50%" style="background:#fff5f8;border-radius:8px;padding:14px;text-align:center;">
          <div style="font-size:1.6rem;font-weight:700;color:#e91e8c;">{avg_cycle}</div>
          <div style="font-size:0.8rem;color:#757575;">Avg Cycle Length</div>
        </td>
      </tr>
      <tr>
        <td style="background:#fff5f8;border-radius:8px;padding:14px;text-align:center;">
          <div style="font-size:1.6rem;font-weight:700;color:#9c27b0;">{symptoms_logged}</div>
          <div style="font-size:0.8rem;color:#757575;">Symptoms Logged</div>
        </td>
        <td style="background:#fff5f8;border-radius:8px;padding:14px;text-align:center;">
          <div style="font-size:1.6rem;font-weight:700;color:#9c27b0;">{journals_logged}</div>
          <div style="font-size:0.8rem;color:#757575;">Journal Entries</div>
        </td>
      </tr>
    </table>
    <p style="color:#2d2d2d;margin-top:16px;"><strong>Most frequent symptoms:</strong></p>
    <div style="margin:8px 0 16px;">{sym_html}</div>
    <p style="color:#757575;font-size:0.9rem;">Keep tracking consistently for better predictions!</p>
    """
    return _send(to_email, to_name, "Your Weekly Health Summary", _base_template("Weekly Summary", content))


def send_mood_alert(to_email: str, to_name: str, avg_mood: float, days: int) -> bool:
    content = f"""
    <p style="color:#2d2d2d;">Hi <strong>{to_name}</strong>,</p>
    <div style="background:#fff3e0;border-left:4px solid #ff9800;border-radius:8px;padding:16px 20px;margin:16px 0;">
      <p style="margin:0;font-size:1.1rem;font-weight:600;color:#e65100;">Low Mood Detected</p>
      <p style="margin:8px 0 0;color:#757575;">
        Your average mood score over the last {days} days is <strong>{avg_mood:.1f}/10</strong>.
      </p>
    </div>
    <p style="color:#2d2d2d;">Some things that may help:</p>
    <ul style="color:#555;line-height:2;">
      <li>Gentle exercise - even a 20-minute walk boosts serotonin</li>
      <li>Magnesium-rich foods: dark chocolate, almonds, spinach</li>
      <li>Limit caffeine and alcohol which worsen mood dips</li>
      <li>Talk to someone you trust or journal your feelings</li>
      <li>If low mood persists, consider speaking to a healthcare professional</li>
    </ul>
    """
    return _send(to_email, to_name, "Health Check - Low Mood Alert", _base_template("Mood Alert", content))


def send_high_symptom_alert(to_email: str, to_name: str, symptom: str, severity: int) -> bool:
    content = f"""
    <p style="color:#2d2d2d;">Hi <strong>{to_name}</strong>,</p>
    <div style="background:#ffebee;border-left:4px solid #f44336;border-radius:8px;padding:16px 20px;margin:16px 0;">
      <p style="margin:0;font-size:1.1rem;font-weight:600;color:#c62828;">High Severity Symptom Logged</p>
      <p style="margin:8px 0 0;color:#757575;">
        You logged <strong>{symptom}</strong> with severity <strong>{severity}/10</strong>.
      </p>
    </div>
    <p style="color:#2d2d2d;">Immediate relief tips:</p>
    <ul style="color:#555;line-height:2;">
      <li>Apply a heating pad to the lower abdomen</li>
      <li>Try ginger or turmeric tea for inflammation</li>
      <li>Over-the-counter ibuprofen can help with cramps</li>
      <li>Rest and stay hydrated</li>
      <li>If severity is consistently above 8, consult your doctor</li>
    </ul>
    """
    return _send(to_email, to_name, f"Symptom Alert - High {symptom} Severity", _base_template("Symptom Alert", content))
