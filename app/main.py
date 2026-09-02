from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session

from src.triage_engine import TriageEngine
from src.email_client import authenticate_gmail, fetch_unread_emails
from src.database import engine, Base, get_db
from src.db_models import TriagedTicket
from src.email_client import authenticate_gmail, fetch_unread_emails, get_or_create_label, apply_label_and_mark_read
# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Customer Support Ticket Triage API",
    description="Automated email classification and triage system using NLP and SQLAlchemy.",
    version="1.0.0"
)

# Initialize engine on startup
triage_engine = TriageEngine()

# Pydantic Schemas
class TicketRequest(BaseModel):
    subject: str
    body: str

class TriageResponse(BaseModel):
    id: Optional[int] = None
    subject: str
    category: str
    confidence: float
    cleaned_text: str

class EmailTriageResponse(BaseModel):
    email_id: str
    subject: str
    category: str
    confidence: float

class TicketHistoryResponse(BaseModel):
    id: int
    email_id: Optional[str]
    subject: str
    predicted_category: str
    confidence: float

    class Config:
        from_attributes = True

@app.get("/")
def read_root():
    return {"status": "active", "service": "Customer Support Ticket Triage API"}

@app.post("/triage/classify", response_model=TriageResponse)
def classify_ticket(ticket: TicketRequest, db: Session = Depends(get_db)):
    """Classify a custom ticket, save it to the database, and return results."""
    result = triage_engine.predict(ticket.subject, ticket.body)

    db_ticket = TriagedTicket(
        subject=ticket.subject,
        body=ticket.body,
        cleaned_text=result["cleaned_text"],
        predicted_category=result["category"],
        confidence=result["confidence"]
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)

    return {
        "id": db_ticket.id,
        "subject": ticket.subject,
        "category": result["category"],
        "confidence": result["confidence"],
        "cleaned_text": result["cleaned_text"]
    }

@app.post("/triage/scan-inbox", response_model=List[EmailTriageResponse])
def scan_and_triage_inbox(max_results: int = 5, db: Session = Depends(get_db)):
    """Fetch unread emails, classify them, and store them in the database."""
    try:
        service = authenticate_gmail()
        emails = fetch_unread_emails(service, max_results=max_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gmail API error: {str(e)}")

    triage_results = []
    for email in emails:
        # Check if already processed in database
        existing = db.query(TriagedTicket).filter(TriagedTicket.email_id == email["id"]).first()
        if existing:
            continue

        # AI Engine makes the prediction
        prediction = triage_engine.predict(email.get("subject", ""), email.get("body", ""))

        # 1. Database Persistence
        db_ticket = TriagedTicket(
            email_id=email["id"],
            subject=email.get("subject", ""),
            body=email.get("body", ""),
            cleaned_text=prediction["cleaned_text"],
            predicted_category=prediction["category"],
            confidence=prediction["confidence"]
        )
        db.add(db_ticket)
        db.commit()

        # 2. Automated Gmail Action
        try:
            label_id = get_or_create_label(service, prediction["category"])
            apply_label_and_mark_read(service, email["id"], label_id)
        except Exception as e:
            print(f"Failed to apply Gmail label to {email['id']}: {e}")

        triage_results.append({
            "email_id": email["id"],
            "subject": email["subject"],
            "category": prediction["category"],
            "confidence": prediction["confidence"]
        })

    return triage_results

@app.get("/tickets", response_model=List[TicketHistoryResponse])
def list_tickets(limit: int = 50, db: Session = Depends(get_db)):
    """Retrieve historical triaged tickets from the database."""
    tickets = db.query(TriagedTicket).order_by(TriagedTicket.id.desc()).limit(limit).all()
    return tickets