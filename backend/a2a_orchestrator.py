from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import httpx
import json
from openai import OpenAI  # or use Gemini API
import os

app = FastAPI(title="Synapse A2A Orchestrator")

# Configuration
MCP_SERVER_URL = "http://localhost:8001"
PHARMACY_AGENT_URL = "http://localhost:8002"
SCHEDULING_AGENT_URL = "http://localhost:8003"

class ClinicalQuery(BaseModel):
    query: str
    patient_id: str

class AgentResponse(BaseModel):
    answer: str
    reasoning_trace: List[Dict[str, Any]]
    actions_taken: List[str]

# LLM Client (using free Gemini or local model)
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),  # Or use Groq for free tier
    base_url="https://api.groq.com/openai/v1"  # Groq has free Llama models
)

@app.post("/orchestrate", response_model=AgentResponse)
async def orchestrate(query: ClinicalQuery):
    reasoning_trace = []
    actions_taken = []
    
    # Step 1: Parse intent with LLM
    llm_response = client.chat.completions.create(
        model="mixtral-8x7b-32768",  # Free tier model
        messages=[
            {"role": "system", "content": "Extract intent from clinical query. Return JSON with 'intent' and 'required_data' fields."},
            {"role": "user", "content": query.query}
        ],
        temperature=0.1
    )
    
    intent_data = json.loads(llm_response.choices[0].message.content)
    reasoning_trace.append({
        "step": "Intent Parsing",
        "output": intent_data,
        "timestamp": datetime.now().isoformat()
    })
    
    # Step 2: Call MCP Tools
    async with httpx.AsyncClient() as client:
        triage_response = await client.post(
            f"{MCP_SERVER_URL}/mcp/triage_scanner",
            params={"patient_id": query.patient_id}
        )
        triage_data = triage_response.json()
        actions_taken.append(f"Called Triage Scanner: {triage_data['reasoning']}")
        reasoning_trace.append({
            "step": "MCP: Triage Scanner",
            "result": triage_data["data"],
            "reasoning": triage_data["reasoning"]
        })
    
    # Step 3: A2A Collaboration with other agents
    async with httpx.AsyncClient() as client:
        # Call Pharmacy Agent
        pharmacy_response = await client.post(
            f"{PHARMACY_AGENT_URL}/agent/medications",
            json={"patient_id": query.patient_id}
        )
        actions_taken.append("Coordinated with Pharmacy Agent via A2A")
        
        # Call Scheduling Agent
        scheduling_response = await client.post(
            f"{SCHEDULING_AGENT_URL}/agent/schedule_followup",
            json={"priority": triage_data["data"].get("alerts", [])}
        )
        actions_taken.append("Coordinated with Scheduling Agent via A2A")
    
    # Step 4: Synthesize final answer with reasoning
    final_prompt = f"""
    Patient ID: {query.patient_id}
    Clinical Query: {query.query}
    
    Triage Results: {json.dumps(triage_data['data'])}
    Pharmacy Recommendations: {pharmacy_response.json()}
    Scheduling: {scheduling_response.json()}
    
    Generate a concise clinical answer with:
    1. The recommendation (Yes/No/Requires Review)
    2. Key clinical findings
    3. Required actions
    4. Risk assessment
    
    Format as JSON.
    """
    
    final_llm = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[{"role": "user", "content": final_prompt}],
        temperature=0.2
    )
    
    final_answer = json.loads(final_llm.choices[0].message.content)
    
    return AgentResponse(
        answer=final_answer.get("recommendation", "Requires manual review"),
        reasoning_trace=reasoning_trace,
        actions_taken=actions_taken
    )

if __name__ == "__main__":
    import uvicorn
    from datetime import datetime
    uvicorn.run(app, host="0.0.0.0", port=8000)
