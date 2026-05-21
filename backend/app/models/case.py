from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class Case(Base):
    __tablename__ = "cases"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_id = Column(String, ForeignKey("alerts.id"), nullable=False)
    analyst_name = Column(String, nullable=True)
    status = Column(String, default="open")  # open, investigating, resolved
    notes = Column(Text, nullable=True)
    opened_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    mitre_tag = Column(String, nullable=True)
    playbook_type = Column(String, nullable=True)