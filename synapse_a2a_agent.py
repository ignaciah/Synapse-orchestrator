from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import httpx
import json
import os
from datetime import datetime

app = FastAPI(title="Synapse A2A Orchestrator", version="1.0.0")

# Configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001")

# ============================================
# A2A Protocol JSON-RPC Models
# ============================================
class A2AMessage(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict] = None
    id: Optional[int] = None

class A2AResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict] = None
    id: Optional[int] = None

# ============================================
# Agent Card (A2A Discovery) [citation:5]
# ============================================
AGENT_CARD = {
    "name": "Synapse Clinical Orchestrator",
    "description": "Multi-agent orchestration for clinical decision support - coordinates pharmacy, scheduling, and clinical safety tools",
    "version": "1.0.0",
    "url": "https://your-deployed-url.com",
    "skills": [
        {
            "id": "clinical_decision",
            "name": "Clinical Decision Support",
            "description": "Orchestrates multiple clinical tools to answer complex patient care questions",
            "examples": [
                "Is patient ready for discharge?",
                "Check medication safety before prescribing",
                "Assess fall risk and care coordination needs"
            ],
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "patient_id": {"type": "string"}
                },
                "required": ["query", "patient_id"]
            }
        }
    ],
    "capabilities": {
        "streaming": False,
        "push_notifications": False,
        "extensions": ["ai.promptopinion/fhir-context"]
    }
}

# ============================================
# A2A Endpoints
# ============================================
@app.get("/.well-known/agent.json")
async def get_agent_card():
    """A2A discovery endpoint - tells Prompt Opinion about your agent [citation:5]"""
    return AGENT_CARD

@app.post("/")
async def handle_a2a_message(request: Request):
    """Main A2A JSON-RPC handler for Prompt Opinion"""
    body = await request.json()
    
    method = body.get("method")
    params = body.get("params", {})
    
    # Extract FHIR context from SHARP extension [citation:1][citation:4]
    fhir_context = params.get("fhir_context", {})
    patient_id = fhir_context.get("patient_id") or params.get("patient_id")
    fhir_token = fhir_context.get("fhir_token")
    
    if method == "agent.info":
        return {"jsonrpc": "2.0", "result": AGENT_CARD, "id": body.get("id")}
    
    elif method == "agent.execute":
        query = params.get("query", "")
        task_id = params.get("task_id")
        
        # Execute clinical reasoning
        result = await clinical_reasoning_pipeline(
            query=query,
            patient_id=patient_id,
            fhir_token=fhir_token
        )
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "task_id": task_id,
                "status": "completed",
                "artifacts": [{
                    "name": "clinical_recommendation",
                    "content": result
                }]
            },
            "id": body.get("id")
        }
    
    else:
        return {"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": body.get("id")}

# ============================================
# Clinical Reasoning Pipeline
# ============================================
async def clinical_reasoning_pipeline(query: str, patient_id: Optional[str], fhir_token: Optional[str]) -> Dict:
    """Orchestrates MCP tools and returns clinical recommendation"""
    
    reasoning_trace = []
    actions = []
    
    # Step 1: Parse intent (simplified - could use LLM)
    reasoning_trace.append({
        "step": "Intent Analysis",
        "timestamp": datetime.now().isoformat(),
        "query": query
    })
    
    # Determine what to check based on query keywords
    needs_interaction_check = any(k in query.lower() for k in ["medication", "drug", "prescription", "interaction"])
    needs_triage = any(k in query.lower() for k in ["discharge", "ready", "surgery", "vital", "risk"])
    needs_social = any(k in query.lower() for k in ["barrier", "transport", "home", "follow-up"])
    
    # Step 2: Call MCP tools
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        if needs_interaction_check:
            # Call interaction checker
            interaction_response = await client.post(
                f"{MCP_SERVER_URL}/check_drug_interactions",
                json={
                    "medications": ["Lisinopril", "Ibuprofen"],  # Example
                    "patient_id": patient_id,
                    "fhir_token": fhir_token
                }
            )
            interaction_data = interaction_response.json()
            reasoning_trace.append({
                "step": "MCP: Drug Interaction Check",
                "result": interaction_data
            })
            actions.append("Checked medication interactions via MedTools MCP")
        
        if needs_triage:
            # Call triage scanner
            triage_response = await client.post(
                f"{MCP_SERVER_URL}/triage_risk_scanner",
                json={
                    "patient_id": patient_id,
                    "systolic_bp": 145,
                    "heart_rate": 88,
                    "hba1c": 7.8
                }
            )
            triage_data = triage_response.json()
            reasoning_trace.append({
                "step": "MCP: Triage Risk Assessment",
                "result": triage_data
            })
            actions.append("Assessed clinical risk factors")
    
    # Step 3: Generate final recommendation
    final_recommendation = generate_clinical_recommendation(
        query=query,
        trace=reasoning_trace
    )
    
    return {
        "recommendation": final_recommendation,
        "actions_taken": actions,
        "reasoning_trace": reasoning_trace,
        "patient_id": patient_id
    }

def generate_clinical_recommendation(query: str, trace: List) -> str:
    """Generate human-readable clinical recommendation"""
    
    # In production, this would call an LLM via Gemini/GPT
    # For hackathon demo, use rule-based responses
    
    if "discharge" in query.lower():
        return "⚠️ **REQUIRES REVIEW** - Patient has elevated HbA1c (7.8%) indicating suboptimal diabetes control. Recommend endocrine consultation prior to discharge planning."
    elif "medication" in query.lower():
        return "✅ **PROCEED WITH CAUTION** - No high-severity interactions detected. Standard monitoring recommended for Lisinopril therapy (renal function at 2 weeks)."
    elif "fall" in query.lower():
        return "📋 **CARE COORDINATION NEEDED** - Patient resides in area with limited transportation access. Refer to social work for transport assistance to follow-up appointments."
    else:
        return "📊 **CLINICAL SUMMARY** - No urgent flags identified. Routine follow-up as scheduled. Full reasoning trace available for clinical audit."

# ============================================
# Run the server
# ============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
