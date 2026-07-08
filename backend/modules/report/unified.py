# =============================================================================
# unified.py — Decision Intelligence Engine for PetroMind
#
# The most architecturally significant module in PetroMind.
# Receives structured outputs from all three AI services and:
# 1. Synthesises findings across modalities
# 2. Resolves conflicting evidence
# 3. Prioritises actions by risk severity
# 4. Generates unified executive maintenance report
# 5. Exports PDF
#
# This is what separates PetroMind from three separate AI tools.
# =============================================================================

import os
import sys
import time
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from backend.core.llm import get_llm


# =============================================================================
# STATE
# =============================================================================

class DecisionState(TypedDict):
    equipment_name: str
    knowledge_result: Optional[dict]
    prediction_result: Optional[dict]
    vision_result: Optional[dict]
    synthesised_findings: str
    priority_score: int
    recommended_actions: list[str]
    executive_report: str
    report_generated: bool


# =============================================================================
# NODES
# =============================================================================

def synthesise_node(state: DecisionState) -> DecisionState:
    """
    Collects and structures outputs from all three AI modules.
    Identifies overlapping signals across modalities.
    """
    findings = []

    if state.get("knowledge_result"):
        findings.append(
            f"KNOWLEDGE AI FINDINGS:\n"
            f"{state['knowledge_result'].get('answer', 'No findings')}"
        )

    if state.get("prediction_result"):
        pred = state["prediction_result"]
        findings.append(
            f"PREDICTION AI FINDINGS:\n"
            f"Risk Level: {pred.get('risk_level', 'Unknown')}\n"
            f"Failure Probability: "
            f"{pred.get('failure_probability', 0)*100:.1f}%\n"
            f"LLM Analysis: {pred.get('llm_explanation', 'No analysis')}"
        )

    if state.get("vision_result"):
        vis = state["vision_result"]
        findings.append(
            f"VISION AI FINDINGS:\n"
            f"Severity: {vis.get('severity_level', 'Unknown')}\n"
            f"Assessment: "
            f"{vis.get('severity_assessment', 'No assessment')}"
        )

    state["synthesised_findings"] = "\n\n".join(findings)
    return state


def reason_node(state: DecisionState) -> DecisionState:
    """
    Applies LangGraph reasoning across synthesised findings.
    Resolves conflicts, identifies corroborating evidence,
    produces priority score and recommended actions.
    """
    llm = get_llm(temperature=0.0)

    system_prompt = """You are PetroMind Decision Intelligence Engine.

You receive findings from three independent AI systems:
- Knowledge AI (document analysis)
- Prediction AI (sensor anomaly detection)
- Vision AI (equipment image inspection)

Your role is to:
1. Identify corroborating evidence across all three systems
2. Resolve any conflicting findings
3. Assign a priority score (1-10) for maintenance urgency
4. List specific recommended actions in priority order

Priority scoring:
10 = Immediate shutdown required — safety risk
7-9 = Urgent — address within 24 hours
4-6 = Important — address within 1 week
1-3 = Routine — schedule at next maintenance window"""

    user_prompt = f"""Equipment: {state['equipment_name']}

SYNTHESISED FINDINGS FROM ALL AI MODULES:

{state['synthesised_findings']}

Provide:
1. CORROBORATING EVIDENCE: Where do multiple AI systems agree?
2. CONFLICTS: Where do findings differ and which to trust?
3. PRIORITY SCORE (1-10): Overall maintenance urgency
4. RECOMMENDED ACTIONS: Ordered list of specific actions
5. TIME WINDOW: When must action be taken?"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    # Extract priority score
    import re
   score_match = re.search(r'priority.*?(\d+)\s*/\s*10', response.content.lower())
if not score_match:
    score_match = re.search(r'(\d+)\s*/\s*10', response.content[:500])
priority_score = int(score_match.group(1)) if score_match else 8

    state["priority_score"] = priority_score
    state["recommended_actions"] = [response.content]
    return state


def report_node(state: DecisionState) -> DecisionState:
    """
    Generates the final executive maintenance report.
    Structured for multiple audiences — field engineers,
    maintenance managers, and executive stakeholders.
    """
    llm = get_llm(temperature=0.0)

    system_prompt = """You are PetroMind Decision Intelligence Engine.
Generate a professional executive maintenance report.

Format the report as follows:

# PETROMIND MAINTENANCE REPORT
## Equipment: [name]
## Priority: [score]/10 — [CRITICAL/HIGH/MEDIUM/LOW]

### EXECUTIVE SUMMARY
[2-3 sentences for leadership]

### AI ANALYSIS FINDINGS
[Bullet points from each AI module]

### RISK ASSESSMENT
[Overall risk with justification]

### RECOMMENDED ACTIONS
[Numbered, prioritised action list with time windows]

### TECHNICAL DETAILS
[For maintenance engineers]

### COMPLIANCE REFERENCES
[Relevant OSHA/API/IOGP standards]"""

    user_prompt = f"""Generate executive maintenance report for:

Equipment: {state['equipment_name']}
Priority Score: {state['priority_score']}/10

Synthesised AI Findings:
{state['synthesised_findings']}

Reasoning Analysis:
{state['recommended_actions'][0] if state['recommended_actions'] else 'N/A'}"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    state["executive_report"] = response.content
    state["report_generated"] = True
    return state


# =============================================================================
# BUILD DECISION ENGINE
# =============================================================================

def build_decision_engine():
    """
    Builds the LangGraph Decision Intelligence Engine.
    Three-node graph: synthesise → reason → report → END
    """
    graph = StateGraph(DecisionState)
    graph.add_node("synthesise", synthesise_node)
    graph.add_node("reason", reason_node)
    graph.add_node("report", report_node)
    graph.set_entry_point("synthesise")
    graph.add_edge("synthesise", "reason")
    graph.add_edge("reason", "report")
    graph.add_edge("report", END)
    return graph.compile()


# =============================================================================
# MASTER FUNCTION
# =============================================================================

def run_decision_engine(
    equipment_name: str,
    knowledge_result: dict = None,
    prediction_result: dict = None,
    vision_result: dict = None
) -> dict:
    """
    Master function — runs Decision Intelligence Engine.
    Called by /api/report FastAPI route.

    Accepts outputs from any combination of the three AI modules.
    At least one module result required.
    """
    start_time = time.time()

    engine = build_decision_engine()

    initial_state = DecisionState(
        equipment_name=equipment_name,
        knowledge_result=knowledge_result,
        prediction_result=prediction_result,
        vision_result=vision_result,
        synthesised_findings="",
        priority_score=5,
        recommended_actions=[],
        executive_report="",
        report_generated=False
    )

    result = engine.invoke(initial_state)
    latency = round(time.time() - start_time, 2)

    return {
        "equipment_name": equipment_name,
        "priority_score": result["priority_score"],
        "executive_report": result["executive_report"],
        "synthesised_findings": result["synthesised_findings"],
        "latency_seconds": latency,
        "modules_used": [
            m for m, r in [
                ("knowledge_ai", knowledge_result),
                ("prediction_ai", prediction_result),
                ("vision_ai", vision_result)
            ] if r is not None
        ],
        "module": "decision_intelligence_engine"
    }


if __name__ == "__main__":
    print("Testing Decision Intelligence Engine...")
    print("=" * 60)

    # Simulate outputs from all three AI modules
    mock_knowledge = {
        "answer": "According to API 610 Section 8.3, seal failure "
                  "indicators include increased vibration above 6mm "
                  "and pressure fluctuations exceeding 30% of nominal. "
                  "Recommended action: immediate inspection and seal "
                  "replacement within 24 hours.",
        "sources": ["API_610.pdf, Page 47"]
    }

    mock_prediction = {
        "risk_level": "HIGH",
        "failure_probability": 0.95,
        "llm_explanation": "Pump-17 shows critical failure indicators: "
                           "vibration increased 69.23%, pressure spiked "
                           "8.51%, 40 anomalies detected. Bearing failure "
                           "likely within 24-48 hours."
    }

    mock_vision = {
        "severity_level": "HIGH",
        "severity_assessment": "Active corrosion detected on outlet flange "
                               "covering approximately 15% of surface. "
                               "Weld joint shows rust penetration. "
                               "HIGH severity — potential leak point."
    }

    result = run_decision_engine(
        equipment_name="Pump-17",
        knowledge_result=mock_knowledge,
        prediction_result=mock_prediction,
        vision_result=mock_vision
    )

    print(f"\nPriority Score: {result['priority_score']}/10")
    print(f"Modules Used: {result['modules_used']}")
    print(f"Latency: {result['latency_seconds']}s")
    print(f"\nExecutive Report:\n{result['executive_report']}")