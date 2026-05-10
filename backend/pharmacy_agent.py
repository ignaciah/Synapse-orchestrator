from fastapi import FastAPI
from pydantic import BaseModel
import random

app = FastAPI()

class PatientRequest(BaseModel):
    patient_id: str

@app.post("/agent/medications")
async def get_medications(request: PatientRequest):
    """Mock pharmacy agent responding to A2A protocol"""
    medications = {
        "patient-1": ["Lisinopril 10mg", "Metformin 500mg"],
        "patient-2": ["Warfarin 5mg", "Aspirin 81mg"],
        "patient-3": ["Atorvastatin 20mg", "Levothyroxine 50mcg"]
    }
    
    meds = medications.get(request.patient_id, ["No active prescriptions"])
    
    return {
        "agent": "Pharmacy Agent",
        "patient_id": request.patient_id,
        "medications": meds,
        "interaction_risk": "High" if "Warfarin" in meds and "Aspirin" in meds else "Low"
    }
