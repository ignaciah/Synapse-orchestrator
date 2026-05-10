from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import asyncio
from datetime import datetime

# MCP Protocol Implementation
app = FastAPI(title="MedTools MCP Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load synthetic data
with open("data/synthetic_ehr.json", "r") as f:
    EHR_DATA = json.load(f)

class MCPToolCall(BaseModel):
    tool: str
    parameters: Dict[str, Any]

class MCPResponse(BaseModel):
    success: bool
    data: Any
    reasoning: str

# Tool 1: Triage Scanner
@app.post("/mcp/triage_scanner", response_model=MCPResponse)
async def triage_scanner(patient_id: str):
    """Analyzes patient vitals and returns risk flags"""
    patient_obs = [obs for obs in EHR_DATA["observations"] 
                   if obs["subject"]["reference"] == f"Patient/{patient_id}"]
    
    alerts = []
    for obs in patient_obs:
        code = obs["code"]["coding"][0]["code"]
        if code == "4548-4":  # HbA1c
            value = obs.get("valueQuantity", {}).get("value", 0)
            if value > 8.0:
                alerts.append(f"⚠️ Critical: HbA1c {value}% indicates poor diabetes control")
            elif value > 7.0:
                alerts.append(f"📊 Warning: Elevated HbA1c {value}%")
    
    return MCPResponse(
        success=True,
        data={"alerts": alerts, "total_obs": len(patient_obs)},
        reasoning=f"Scanned {len(patient_obs)} observations. Found {len(alerts)} clinically significant flags."
    )

# Tool 2: Interaction Checker
@app.post("/mcp/interaction_checker")
async def interaction_checker(medications: List[str]):
    """Checks for dangerous drug interactions"""
    dangerous_pairs = {
        ("Warfarin", "Aspirin"): "Increased bleeding risk",
        ("Lisinopril", "Spironolactone"): "Hyperkalemia risk",
        ("Metformin", "Contrast dye"): "Lactic acidosis risk"
    }
    
    interactions = []
    for med in medications:
        for (drug1, drug2), warning in dangerous_pairs.items():
            if med in drug1 or med in drug2:
                other = drug2 if med in drug1 else drug1
                if other in medications:
                    interactions.append(f"🚨 {warning}: {drug1} + {drug2}")
    
    return MCPResponse(
        success=True,
        data={"interactions": interactions, "is_safe": len(interactions) == 0},
        reasoning=f"Checked {len(medications)} medications. Found {len(interactions)} potential interactions."
    )

# Tool 3: Social Determinants
@app.post("/mcp/social_determinants")
async def social_determinants(patient_id: str):
    """Calculates social risk factors"""
    patient = next((p for p in EHR_DATA["patients"] if p["id"] == patient_id), None)
    if not patient:
        raise HTTPException(404, "Patient not found")
    
    address = patient["address"][0]
    risk_factors = []
    
    # Simulate geographic risk scoring
    if address["postalCode"][0] in ["1", "2", "3"]:
        risk_factors.append("📍 High transportation barrier area")
    if address["city"] in ["Boston", "Seattle"]:
        risk_factors.append("🏥 Excellent healthcare access")
    
    return MCPResponse(
        success=True,
        data={"risk_factors": risk_factors, "score": len(risk_factors)},
        reasoning=f"Analyzed patient location in {address['city']}. {len(risk_factors)} social risks identified."
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80
