from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.triage_engine import TriageEngine
from src.email_client import authenticate_gmail, fetch_unread_emails

app = FastAPI(
    title="Customer Support Ticket Triage API",
    description="Automated email classification and triage system using NLP.",
    version="1.0.0"
)

# Initialize engine on startup
triage_engine = TriageEngine()

# Pydantic Schemas
class TicketRequest(BaseModel):
    subject: str
    body: str

class TriageResponse(BaseModel):
    subject: str
    category: str
    confidence: float
    cleaned_text: str

class EmailTriageResponse(BaseModel):
    email_id: str
    subject: str
    category: str
    confidence: float

@app.get("/")
def read_root():
    return {"status": "active", "service": "Customer Support Ticket Triage API"}

@app.post("/triage/classify", response_model=TriageResponse)
def classify_ticket(ticket: TicketRequest):
    """Classify a custom support ticket provided in request body."""
    result = triage_engine.predict(ticket.subject, ticket.body)
    return {
        "subject": ticket.subject,
        "category": result["category"],
        "confidence": result["confidence"],
        "cleaned_text": result["cleaned_text"]
    }

@app.post("/triage/scan-inbox", response_model=List[EmailTriageResponse])
def scan_and_triage_inbox(max_results: int = 5):
    """Fetch unread emails from Gmail and classify each into queues."""
    try:
        service = authenticate_gmail()
        emails = fetch_unread_emails(service, max_results=max_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gmail API error: {str(e)}")

    triage_results = []
    for email in emails:
        prediction = triage_engine.predict(email.get("subject", ""), email.get("body", ""))
        triage_results.append({
            "email_id": email["id"],
            "subject": email["subject"],
            "category": prediction["category"],
            "confidence": prediction["confidence"]
        })

    return triage_results