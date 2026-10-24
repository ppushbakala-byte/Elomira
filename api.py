
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timezone

app = FastAPI(
    title="Elomira GeoAI API",
    description="GeoAI outdoor activity planning assistant",
    version="1.0.0",
)

class Question(BaseModel):
    question: str
    location: str = "Tirunelveli"
    activity: str = "Outdoor activity"

@app.get("/")
def home():
    return {
        "service": "Elomira GeoAI",
        "status": "online",
        "message": "Elomira API is running"
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(data: Question):
    return {
        "project": "Elomira GeoAI",
        "question": data.question,
        "location": data.location,
        "activity": data.activity,
        "answer": (
            "Elomira received your outdoor activity question. "
            "Check current local weather, air quality, daylight, "
            "and official alerts before deciding. This API demo "
            "does not yet generate an AI-powered assessment."
        ),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": "No hosted language model connected"
    }
