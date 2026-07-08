# ⚡ PetroMind — Enterprise AI Platform for Oil & Gas

> A five-layer enterprise AI platform combining Agentic RAG, Time Series anomaly detection, and Vision AI — unified by a Decision Intelligence Engine that synthesises findings across all three modalities into prioritised maintenance recommendations.

[![Live API](https://img.shields.io/badge/Live%20API-GCP%20Cloud%20Run-blue)](https://petromind-642904158062.us-central1.run.app/docs)
[![Python](https://img.shields.io/badge/Python-3.12-green)](https://python.org)
[![GCP](https://img.shields.io/badge/GCP-Cloud%20Run-orange)](https://cloud.google.com/run)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-purple)](https://github.com/langchain-ai/langgraph)

---

## 🎯 Problem Statement

Oil and gas maintenance teams rely on three disconnected processes — searching technical documents, reviewing sensor logs, and inspecting equipment photos — each producing separate findings that a supervisor must manually cross-reference to make a decision.

**PetroMind unifies all three** into a single platform where one Decision Intelligence Engine synthesises findings across modalities into one prioritised action plan.

---

## 🏗️ Architecture

PetroMind AI Platform
        Enterprise AI for Oil & Gas Operations
                     │
              FastAPI Backend
                     │
            LangGraph Orchestrator
                     │

────────────────── Data Layer ──────────────────
Technical Documents · Sensor CSV · Images
│
────────────────── AI Layer ────────────────────
Knowledge AI      Prediction AI      Vision AI
(Qdrant RAG)     (Anomaly + LLM)   (Vision + LLM)
│
──────────────── Decision Layer ────────────────
Decision Intelligence Engine
│
──────────────── Output Layer ──────────────────
Executive Maintenance Report

---

## 🚀 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **LLM** | GPT-4o (pluggable interface) | Generation across all modules |
| **Vector DB** | Qdrant | Self-hosted semantic search |
| **Agent** | LangGraph | Multi-node orchestration |
| **Time Series** | Statistical anomaly detection | Sensor pattern recognition |
| **Vision** | GPT-4o Vision | Equipment defect detection |
| **Backend** | FastAPI | REST API, async |
| **Container** | Docker (multi-stage) | Packaging |
| **Registry** | GCP Artifact Registry | Image storage |
| **Hosting** | GCP Cloud Run | Serverless deployment |
| **Auth** | RBAC | Role-based access control |

---

## 🤖 Three AI Modules

**Knowledge AI** — Agentic RAG
- Qdrant vector database, 568 chunks from 3 technical documents
- LangGraph retrieve → generate flow
- Every answer cited by document and page number

**Prediction AI** — Time Series + LLM Explanation
- Statistical anomaly detection (Z-score) across sensor readings
- LLM translates mathematical findings into engineering explanation
- Example: 95% failure probability, vibration +69%, bearing failure predicted within 24-48 hours

**Vision AI** — Defect Detection + LLM Severity
- GPT-4o Vision identifies corrosion, cracks, structural damage
- LLM severity reasoner produces maintenance recommendations with compliance citations (API/OSHA/IOGP)

---

## 🧠 Decision Intelligence Engine

Three-node LangGraph workflow that receives outputs from all three AI modules and:

1. **Synthesises** findings across modalities
2. **Reasons** — identifies corroborating evidence, resolves conflicts
3. **Reports** — generates executive maintenance report with priority score (1-10)

Example: Pump-17 test combining all three modules produced a priority score of 8/10 with six ranked actions and citations to API 610, OSHA 1910, and IOGP 434.

---

## ⚙️ Key Design Decisions

**Pluggable LLM interface**
A single `get_llm()` function reads `LLM_PROVIDER` from environment and returns a LangChain-compatible model. Switching between GPT-4o, Gemini, Claude, or local Llama requires zero code changes.

**Qdrant over Azure AI Search**
Deliberately different from OilMind — self-hosted vector database running as a Docker sidecar, demonstrating both managed and self-hosted retrieval patterns.

**RBAC — User → Role → Permission → Module**
Three roles: field engineer (operational access), maintenance manager (reports + approval), administrator (full config access).

**Serverless deployment**
GCP Cloud Run with `min-instances=0` — genuinely zero idle cost, scales up on demand.

---

## 📁 Project Structure

petromind/
├── backend/
│   ├── api/                    # FastAPI routes
│   ├── core/
│   │   ├── config.py           # Centralised settings
│   │   ├── llm.py              # Pluggable LLM interface
│   │   └── rbac.py             # Role-based access control
│   ├── modules/
│   │   ├── knowledge/          # RAG — Qdrant + LangGraph
│   │   ├── prediction/         # Anomaly detection + LLM
│   │   ├── vision/              # Defect detection + LLM
│   │   └── report/             # Decision Intelligence Engine
│   └── main.py                 # FastAPI entry point
├── corpus/raw/                 # Source PDFs
├── Dockerfile
├── docker-compose.yml
└── .github/workflows/

---

## 🔒 Security

- All secrets via environment variables, never hardcoded
- RBAC enforced at endpoint level via FastAPI dependency injection
- No credentials in Docker images

---

## 📝 License

Portfolio project. Not for public distribution.