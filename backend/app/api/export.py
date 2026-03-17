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

router = APIRouter(prefix="/export", tags=["export"])


def _build_pdf(user: User, cycles, symptoms, journals, prediction) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("title", parent=styles["Title"], textColor=colors.HexColor("#e91e8c"))
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], textColor=colors.HexColor("#c2185b"))

    story = []
    story.append(Paragraph("🌸 Menstrual Health Report", title_style))
    story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC", styles["Normal"]))
    story.append(Paragraph(f"User: {user.full_name or user.username}", styles["Normal"]))
    story.append(Spacer(1, 0.5 * cm))

    # Prediction
    story.append(Paragraph("Next Predicted Period", h2))
    if prediction:
        story.append(Paragraph(
            f"Predicted Start: <b>{prediction.predicted_start_date}</b> | "
            f"Confidence: <b>{int((prediction.confidence_score or 0) * 100)}%</b>",
            styles["Normal"],
        ))
    else:
        story.append(Paragraph("No prediction available yet.", styles["Normal"]))
    story.append(Spacer(1, 0.4 * cm))

    # Cycle History
    story.append(Paragraph("Cycle History", h2))
    if cycles:
        data = [["Start Date", "End Date", "Cycle Length", "Flow"]]
        for c in cycles[:12]:
            data.append([
                str(c.start_date),
                str(c.end_date or "—"),
                str(c.cycle_length or "—"),
                c.flow_intensity or "—",
            ])
        t = Table(data, colWidths=[4 * cm, 4 * cm, 4 * cm, 4 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8bbd0")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fce4ec")]),
        ]))
        story.append(t)
    else:
        story.append(Paragraph("No cycle data logged.", styles["Normal"]))
    story.append(Spacer(1, 0.4 * cm))

    # Symptoms
    story.append(Paragraph("Recent Symptoms", h2))
    if symptoms:
        data = [["Date", "Symptom", "Severity"]]
        for s in symptoms[:15]:
            data.append([str(s.logged_date), s.symptom_type, str(s.severity or "—")])
        t = Table(data, colWidths=[4 * cm, 8 * cm, 4 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8bbd0")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(t)
    else:
        story.append(Paragraph("No symptoms logged.", styles["Normal"]))
    story.append(Spacer(1, 0.4 * cm))

    # Mood Journal
    story.append(Paragraph("Mood Journal Summary", h2))
    if journals:
        data = [["Date", "Mood", "Score", "Energy"]]
        for j in journals[:10]:
            data.append([str(j.entry_date), j.mood or "—", str(j.mood_score or "—"), str(j.energy_level or "—")])
        t = Table(data, colWidths=[4 * cm, 4 * cm, 4 * cm, 4 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8bbd0")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(t)
    else:
        story.append(Paragraph("No journal entries.", styles["Normal"]))

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
