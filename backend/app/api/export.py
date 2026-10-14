import io
from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from app.database import get_db
from app.models.models import User, Cycle, Symptom, Journal, Prediction
from app.utils.auth import get_current_user
from app.utils.diet import get_cycle_phase, get_diet_for_phase, calculate_cycle_day

router = APIRouter(prefix="/export", tags=["export"])


def _build_pdf(user: User, cycles, symptoms, journals, prediction) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("title", parent=styles["Title"], textColor=colors.HexColor("#e91e8c"))
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], textColor=colors.HexColor("#c2185b"))
    body = styles["Normal"]
    small_body = ParagraphStyle("small_body", parent=styles["BodyText"], fontSize=8, leading=10, wordWrap='CJK')

    def cell_text(value):
        text = str(value or "—")
        if len(text) > 80:
            return Paragraph(text, small_body)
        return text

    story = []
    story.append(Paragraph("🌸 Menstrual Health Report", title_style))
    story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC", body))
    story.append(Paragraph(f"User: {user.full_name or user.username}", body))
    story.append(Spacer(1, 0.5 * cm))

    latest_cycle = cycles[0] if cycles else None
    cycle_day = 1
    if latest_cycle:
        cycle_day = calculate_cycle_day(latest_cycle.start_date, cycle_length=user.average_cycle_length or 28)
    phase = get_cycle_phase(cycle_day)
    symptom_severity = max((s.severity for s in symptoms if s.severity is not None), default=0)
    recommendations = get_diet_for_phase(phase, severity=symptom_severity)

    story.append(Paragraph("Current Health Snapshot", h2))
    if prediction:
        story.append(Paragraph(
            f"Predicted next period: <b>{prediction.predicted_start_date}</b> | "
            f"Confidence: <b>{int((prediction.confidence_score or 0) * 100)}%</b>",
            body,
        ))
    else:
        story.append(Paragraph("No prediction available yet.", body))
    story.append(Paragraph(f"Current cycle day: <b>{cycle_day}</b> | Phase: <b>{phase.title()}</b>", body))
    story.append(Paragraph(f"Diet focus: {recommendations['description']}", body))
    story.append(Paragraph(f"Remedies: {'; '.join(recommendations.get('remedies', [])[:3])}", body))
    story.append(Spacer(1, 0.35 * cm))
    if recommendations.get('daily_advice'):
        story.append(Paragraph("Daily AI Advice", h2))
        story.append(Paragraph(recommendations['daily_advice'], body))
        story.append(Spacer(1, 0.35 * cm))

    story.append(Paragraph("Cycle History", h2))
    if cycles:
        data = [["Start Date", "End Date", "Cycle Length", "Flow"]]
        for c in cycles[:12]:
            data.append([
                cell_text(c.start_date),
                cell_text(c.end_date or "—"),
                cell_text(c.cycle_length or "—"),
                cell_text(c.flow_intensity or "—"),
            ])
        table = Table(data, colWidths=[4 * cm, 4 * cm, 4 * cm, 3 * cm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8bbd0")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fce4ec")]),
        ]))
        story.append(table)
    else:
        story.append(Paragraph("No cycle data logged.", body))
    story.append(Spacer(1, 0.35 * cm))

    story.append(Paragraph("Recent Symptoms", h2))
    if symptoms:
        data = [["Date", "Symptom", "Severity", "AI Advice"]]
        for s in symptoms[:10]:
            data.append([
                cell_text(s.logged_date),
                cell_text(s.symptom_type),
                cell_text(s.severity or "—"),
                cell_text(s.ai_advice or "—"),
            ])
        table = Table(data, colWidths=[2.8 * cm, 3.3 * cm, 2 * cm, 7 * cm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8bbd0")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(table)
    else:
        story.append(Paragraph("No symptoms logged.", body))
    story.append(Spacer(1, 0.35 * cm))

    story.append(Paragraph("Mood Journal Summary", h2))
    if journals:
        data = [["Date", "Mood", "Score", "Energy", "AI Advice"]]
        for j in journals[:8]:
            data.append([
                cell_text(j.entry_date),
                cell_text(j.mood or "—"),
                cell_text(j.mood_score or "—"),
                cell_text(j.energy_level or "—"),
                cell_text(j.ai_advice or "—"),
            ])
        table = Table(data, colWidths=[2.6 * cm, 2.8 * cm, 1.8 * cm, 1.8 * cm, 7.2 * cm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8bbd0")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(table)
    else:
        story.append(Paragraph("No journal entries.", body))
    story.append(Spacer(1, 0.35 * cm))

    story.append(Paragraph("Diet & Wellness Guidance", h2))
    story.append(Paragraph(f"Phase: <b>{phase.title()}</b>", body))
    story.append(Paragraph(f"Hydration: {recommendations.get('hydration', '')}", body))
    story.append(Paragraph(f"Exercise: {recommendations.get('exercise', '')}", body))
    story.append(Paragraph("Recommended foods:", body))
    for item in recommendations.get('foods', [])[:4]:
        story.append(Paragraph(f"• {item['name']} — {item['reason']}", body))
    story.append(Paragraph("Remedies:", body))
    for item in recommendations.get('remedies', [])[:3]:
        story.append(Paragraph(f"• {item}", body))
    story.append(Paragraph("Suggestions:", body))
    for item in recommendations.get('suggestions', [])[:3]:
        story.append(Paragraph(f"• {item}", body))

    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        "⚠️ This report is for personal tracking only and does not constitute medical advice.",
        ParagraphStyle("disclaimer", parent=styles["Italic"], textColor=colors.grey, fontSize=8),
    ))

    doc.build(story)
    return buffer.getvalue()


@router.get("/report")
def export_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cycles = db.query(Cycle).filter(Cycle.user_id == current_user.id).order_by(Cycle.start_date.desc()).all()
    symptoms = db.query(Symptom).filter(Symptom.user_id == current_user.id).order_by(Symptom.logged_date.desc()).all()
    journals = db.query(Journal).filter(Journal.user_id == current_user.id).order_by(Journal.entry_date.desc()).all()
    prediction = db.query(Prediction).filter(Prediction.user_id == current_user.id).order_by(Prediction.created_at.desc()).first()

    pdf_bytes = _build_pdf(current_user, cycles, symptoms, journals, prediction)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=health_report_{current_user.username}.pdf"},
    )
