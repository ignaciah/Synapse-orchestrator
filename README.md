┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React/Next.js)                  │
│                    User: Clinician Dashboard                 │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/WebSocket
┌─────────────────────▼───────────────────────────────────────┐
│            Synapse A2A Orchestrator (FastAPI)                │
│  - Natural Language Processing                               │
│  - Agent Coordination                                        │
│  - Reasoning Trace Generation                                │
└─────┬──────────────────┬──────────────────┬────────────────┘
      │ A2A Protocol      │ MCP Protocol     │ FHIR
┌─────▼─────┐      ┌──────▼──────┐    ┌──────▼──────┐
│ Pharmacy  │      │ MedTools    │    │ Synthetic   │
│ Agent     │◄────►│ MCP Server  │    │ FHIR Server │
│ (Mock)    │      │             │    │             │
└───────────┘      └─────────────┘    └─────────────┘

# Synapse-orchestrator
The Problem hospitals face an interoperability paradox. While EHRs (Epic/Cerner ar FHIR-complaiant, AI agents operate in silos. Aradiology agent cannot talk to a pharmcy Agent. Clinicians suffer from Aler Fatigue (noise, non-priority alerts)
