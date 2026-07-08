# =============================================================================
# main.py — FastAPI Application Entry Point for PetroMind
#
# Wires all AI modules into REST API endpoints.
# Every endpoint tested via Swagger UI before React frontend.
#
# API Groups:
#   /api/knowledge/*   — Knowledge AI (RAG + Qdrant)
#   /api/prediction/*  — Prediction AI (Transformer + LLM)
#   /api/vision/*      — Vision AI (Vision LLM + Severity)
#   /api/report/*      — Decision Intelligence Engine
#   /api/auth/*        — RBAC
#   /health            — System health check
# =============================================================================

import os
import sys
import time
import tempfile
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

sys.path.append(os.path.dirname(__file__))
from backend.core.config import validate_config
from backend.core.rbac import get_current_user, User, Role
from backend.core.llm import get_llm_provider_info


# =============================================================================
# STARTUP
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_config()
    print("✅ PetroMind API ready")
    yield
    print("PetroMind API shutting down")


# =============================================================================
# APP
# =============================================================================

app = FastAPI(
    title="PetroMind AI Platform",
    description="""
Enterprise AI Platform for Oil & Gas Operations.

Three AI capabilities unified under one platform:
- **Knowledge AI** — Agentic RAG on technical documentation
- **Prediction AI** — Time Series anomaly detection + LLM explanation
- **Vision AI** — Equipment defect detection + severity reasoning
- **Decision Intelligence Engine** — Unified maintenance report

Architecture: 5-layer enterprise platform (Data → AI → Decision → Output → Evaluation)
    """,
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# REQUEST / RESPONSE MODELS
# =============================================================================

class KnowledgeRequest(BaseModel):
    query: str
    include_trace: bool = False


class DecisionRequest(BaseModel):
    equipment_name: str
    knowledge_result: Optional[dict] = None
    prediction_result: Optional[dict] = None
    vision_result: Optional[dict] = None


# =============================================================================
# HEALTH
# =============================================================================

@app.get("/", tags=["Health"])
async def root():
    return {"status": "running", "service": "PetroMind AI Platform"}


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Readiness check — verifies all AI services are reachable.
    Used by GCP Cloud Run health probes and monitoring dashboard.
    """
    start = time.time()

    services = {}

    # Check Qdrant
    try:
        from qdrant_client import QdrantClient
        from backend.core.config import QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        count = client.count(collection_name=QDRANT_COLLECTION)
        services["qdrant"] = {
            "status": "healthy",
            "chunks": count.count
        }
    except Exception as e:
        services["qdrant"] = {"status": "unhealthy", "error": str(e)}

    # Check LLM
    try:
        llm_info = get_llm_provider_info()
        services["llm"] = {
            "status": "healthy",
            "provider": llm_info["provider"],
            "model": llm_info["model"]
        }
    except Exception as e:
        services["llm"] = {"status": "unhealthy", "error": str(e)}

    overall = "healthy" if all(
        s["status"] == "healthy" for s in services.values()
    ) else "degraded"

    return {
        "status": overall,
        "services": services,
        "latency_ms": round((time.time() - start) * 1000, 2),
        "version": "1.0.0"
    }


# =============================================================================
# KNOWLEDGE AI
# =============================================================================

@app.post("/api/knowledge/query", tags=["Knowledge AI"])
async def knowledge_query(
    request: KnowledgeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Query the Knowledge AI module with a natural language question.
    Returns cited answer from oil & gas technical documentation.
    """
    try:
        from backend.modules.knowledge.agent import run_knowledge_query
        result = run_knowledge_query(request.query)
        result["user"] = current_user.username
        result["role"] = current_user.role.value
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# PREDICTION AI
# =============================================================================

@app.post("/api/prediction/analyse", tags=["Prediction AI"])
async def prediction_analyse(
    equipment_name: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload equipment sensor CSV for anomaly detection.
    Returns risk level, failure probability, and LLM explanation.
    """
    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".csv"
        ) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        from backend.modules.prediction.explainer import (
            run_prediction_with_explanation
        )
        result = run_prediction_with_explanation(tmp_path, equipment_name)
        os.unlink(tmp_path)
        result["user"] = current_user.username
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/prediction/sample", tags=["Prediction AI"])
async def prediction_sample(
    current_user: User = Depends(get_current_user)
):
    """
    Generate synthetic sensor data and run prediction.
    Used for demo purposes when no real CSV is available.
    """
    try:
        import numpy as np
        import pandas as pd

        np.random.seed(42)
        n = 200
        timestamps = pd.date_range('2024-01-01', periods=n, freq='h')
        pressure = 150 + np.random.normal(0, 5, n)
        temperature = 180 + np.random.normal(0, 8, n)
        vibration = 2.5 + np.random.normal(0, 0.3, n)
        pressure[150:170] += 45
        vibration[160:180] += 3.5
        temperature[140:160] -= 25

        df = pd.DataFrame({
            'timestamp': timestamps,
            'pressure_psi': pressure,
            'temperature_f': temperature,
            'vibration_mm': vibration
        })

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".csv"
        ) as tmp:
            df.to_csv(tmp.name, index=False)
            tmp_path = tmp.name

        from backend.modules.prediction.explainer import (
            run_prediction_with_explanation
        )
        result = run_prediction_with_explanation(
            tmp_path, "Pump-17 (Sample)"
        )
        os.unlink(tmp_path)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# VISION AI
# =============================================================================

@app.post("/api/vision/analyse", tags=["Vision AI"])
async def vision_analyse(
    equipment_name: str = Form(...),
    file: UploadFile = File(...),
    sensor_context: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """
    Upload equipment image for defect detection.
    Returns severity assessment and maintenance recommendations.
    """
    try:
        suffix = "." + file.filename.split(".")[-1]
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=suffix
        ) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        from backend.modules.vision.severity import run_vision_analysis
        result = run_vision_analysis(
            tmp_path, equipment_name, sensor_context
        )
        os.unlink(tmp_path)
        result["user"] = current_user.username
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# DECISION INTELLIGENCE ENGINE
# =============================================================================

@app.post("/api/report/generate", tags=["Decision Intelligence Engine"])
async def generate_report(
    request: DecisionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Runs the Decision Intelligence Engine.
    Synthesises outputs from Knowledge AI, Prediction AI, Vision AI.
    Returns unified executive maintenance report.
    """
    if not any([
        request.knowledge_result,
        request.prediction_result,
        request.vision_result
    ]):
        raise HTTPException(
            status_code=400,
            detail="At least one AI module result required"
        )

    try:
        from backend.modules.report.unified import run_decision_engine
        result = run_decision_engine(
            equipment_name=request.equipment_name,
            knowledge_result=request.knowledge_result,
            prediction_result=request.prediction_result,
            vision_result=request.vision_result
        )
        result["user"] = current_user.username
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# AUTH
# =============================================================================

@app.get("/api/auth/me", tags=["Auth"])
async def get_me(current_user: User = Depends(get_current_user)):
    """Returns current user profile and permissions."""
    return current_user.to_dict()


@app.get("/api/auth/roles", tags=["Auth"])
async def get_roles():
    """Returns RBAC role summary for admin monitoring."""
    from backend.core.rbac import get_role_summary
    return get_role_summary()


# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )