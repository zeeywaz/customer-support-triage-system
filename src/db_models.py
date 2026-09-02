from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from src.database import Base

class TriagedTicket(Base):
    __tablename__ = "triaged_tickets"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String(100), unique=True, index=True, nullable=True)
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=True)
    cleaned_text = Column(Text, nullable=True)
    predicted_category = Column(String(100), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)