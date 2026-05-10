from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timedelta

app = FastAPI()

class ScheduleRequest(BaseModel):
    priority: list

@app.post("/agent/schedule_followup")
async def schedule_followup(request: ScheduleRequest):
    """Mock scheduling agent"""
    urgency = "URGENT" if any("Critical" in alert for alert in request.priority) else "ROUTINE"
    
    date = datetime.now() + timedelta(days=1 if urgency == "URGENT" else 7)
    
    return {
        "agent": "Scheduling Agent",
        "appointment_date": date.isoformat(),
        "urgency": urgency,
        "instructions": "Call patient to confirm" if urgency == "URGENT" else "SMS reminder sent"
    }
