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
┌──────────────────────────────────────────────────────────────┐
│                   PROMPT OPINION PLATFORM                     │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              FHIR Context Extension (SHARP)            │  │
│  │    Patient data, credentials injected at runtime       │  │
│  └────────────────────────────────────────────────────────┘  │
│                           │                                   │
│  ┌────────────────────────▼────────────────────────────┐    │
│  │         SYNAPSE A2A AGENT (Published)               │    │
│  │    - Registered in Marketplace                       │    │
│  │    - Declares FHIR context capability                │    │
│  │    - Skills: clinical_decision_orchestration         │    │
│  └────────────┬───────────────────────────┬─────────────┘    │
│               │ A2A Protocol               │ MCP Protocol     │
│  ┌────────────▼────────────┐   ┌───────────▼──────────────┐  │
│  │  External Agents        │   │   MedTools MCP Server    │  │
│  │  - Pharmacy Agent       │   │   (Published to          │  │
│  │  - Scheduling Agent     │   │    Marketplace)          │  │
│  └─────────────────────────┘   └──────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘

your-repo/
├── frontend/          # Your Next.js app
│   ├── package.json
│   └── ...
├── backend/           # Your FastAPI A2A Orchestrator
│   ├── main.py
│   ├── requirements.txt
│   └── ...
└── vercel.json


