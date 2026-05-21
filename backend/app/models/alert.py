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
    severity = Column(String, nullable=False)   # low, medium, high, critical
    mitre_tag = Column(String, nullable=True)
    status = Column(String, default="open")     # open, investigating, resolved
    source = Column(String, default="ml_model") # ml_model, wazuh
    shap_json = Column(Text, nullable=True)      # top 3 SHAP features as JSON
    ip_address = Column(String, nullable=True)
    account_id = Column(String, nullable=True)
    abuse_score = Column(Integer, nullable=True) # AbuseIPDB score Phase 4