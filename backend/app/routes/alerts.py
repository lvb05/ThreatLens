from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.alert import Alert
from app.services.aria_service import analyze_alert
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from fastapi.responses import StreamingResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import json

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])

class AlertCreate(BaseModel):
    amount: float
    fraud_score: float
    attack_type: str
    severity: str
    mitre_tag: Optional[str] = None
    source: Optional[str] = "ml_model"
    ip_address: Optional[str] = None
    account_id: Optional[str] = None
    shap_json: Optional[str] = None

class AlertUpdate(BaseModel):
    status: str  # open, investigating, resolved

@router.get("/")
def get_alerts(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    alerts = db.query(Alert).order_by(Alert.timestamp.desc()).offset(skip).limit(limit).all()
    return {"alerts": alerts, "total": db.query(Alert).count()}

@router.post("/")
def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    db_alert = Alert(**alert.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

@router.get("/{alert_id}")
def get_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.patch("/{alert_id}/status")
def update_alert_status(alert_id: str, update: AlertUpdate, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = update.status
    db.commit()
    db.refresh(alert)
    return alert

@router.post("/{alert_id}/analyze")
def analyze_alert_endpoint(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    analysis = analyze_alert(alert)

    return {"analysis": analysis}

@router.get("/{alert_id}/report")
def export_pdf_report(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("ThreatLens Incident Report", styles["Title"]))
    story.append(Spacer(1, 20))

    fields = [
        ("Alert ID", alert.id),
        ("Timestamp", str(alert.timestamp)),
        ("Attack Type", alert.attack_type),
        ("Amount", f"₹{alert.amount}"),
        ("Fraud Score", str(alert.fraud_score)),
        ("Severity", alert.severity),
        ("MITRE Tag", alert.mitre_tag or "N/A"),
        ("Source", alert.source),
        ("IP Address", alert.ip_address or "N/A"),
        ("Account ID", alert.account_id or "N/A"),
        ("Status", alert.status),
    ]

    for label, value in fields:
        story.append(Paragraph(f"<b>{label}:</b> {value}", styles["BodyText"]))
        story.append(Spacer(1, 8))

    story.append(Spacer(1, 12))
    story.append(Paragraph("SHAP Explanation", styles["Heading2"]))
    story.append(Spacer(1, 8))

    if alert.shap_json:
        try:
            shap_data = json.loads(alert.shap_json)

            for item in shap_data:
                story.append(
                    Paragraph(
                        f"{item['feature']} → {item['shap_value']} ({item['direction']})",
                        styles["BodyText"]
                    )
                )
                story.append(Spacer(1, 6))
        except:
            story.append(Paragraph("Unable to parse SHAP explanation.", styles["BodyText"]))
    else:
        story.append(Paragraph("No SHAP explanation available.", styles["BodyText"]))

    story.append(Spacer(1, 16))
    story.append(Paragraph("ARIA AI Analyst Summary", styles["Heading2"]))
    story.append(Spacer(1, 8))

    from app.services.aria_service import analyze_alert
    analysis = analyze_alert(alert)

    for line in analysis.split("\n"):
        if line.strip():
            story.append(Paragraph(line, styles["BodyText"]))
            story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=ThreatLens_Report_{alert.id}.pdf"
        },
    )