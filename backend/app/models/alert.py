from sqlalchemy import Column, String, Float, DateTime, Integer, Text
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    amount = Column(Float, nullable=False)
    fraud_score = Column(Float, nullable=False)
    attack_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    mitre_tag = Column(String, nullable=True)
    source = Column(String, nullable=False)
    ip_address = Column(String, nullable=True)
    account_id = Column(String, nullable=True)
    shap_json = Column(Text, nullable=True)
    status = Column(String, default="open")

    abuse_score = Column(Integer, nullable=True)
    country = Column(String, nullable=True)
    isp = Column(String, nullable=True)