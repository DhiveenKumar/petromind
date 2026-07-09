# =============================================================================
# severity.py — LLM Severity Reasoning for Vision AI
#
# Takes raw defect detection output and generates:
# - Severity classification with justification
# - Maintenance recommendation with citations
# - Integration with sensor data if available
# - Autonomous action execution for HIGH/CRITICAL severity
# =============================================================================

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from backend.core.llm import get_llm
from backend.modules.report.tools import get_all_tools
from langchain_core.messages import HumanMessage, SystemMessage


def assess_severity(
    defect_analysis: str,
    equipment_name: str = "Equipment",
    sensor_context: str = None
) -> dict:
    """
    Takes vision defect analysis and generates severity assessment
    with maintenance recommendations.
    """
    llm = get_llm(temperature=0.0)

    sensor_section = ""
    if sensor_context:
        sensor_section = f"""
Additional Sensor Context:
{sensor_context}

Cross-reference the visual defects with the sensor anomalies
to provide a more complete risk assessment.
"""

    system_prompt = """You are PetroMind Vision AI Severity Analyst.

You receive equipment defect analysis from visual inspection
and produce actionable maintenance recommendations.

Your output must be:
- Specific about defect type and location
- Clear on severity and why
- Actionable with time-bound recommendations
- Compliant with oil & gas safety standards (OSHA, API, IOGP)"""

    user_prompt = f"""Equipment: {equipment_name}

Visual Inspection Analysis:
{defect_analysis}
{sensor_section}

Provide a structured severity assessment:

1. SEVERITY CLASSIFICATION
   - Overall severity level (LOW/MEDIUM/HIGH/CRITICAL)
   - Justification based on defect characteristics

2. RISK ASSESSMENT
   - Immediate safety risks
   - Production impact if unaddressed
   - Environmental risk

3. MAINTENANCE RECOMMENDATION
   - Immediate actions required
   - Time window for intervention
   - Maintenance procedure reference (API/OSHA/IOGP standard)

4. PRIORITY SCORE (1-10)
   - 10 = immediate shutdown required
   - 1 = schedule at next planned maintenance"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    severity_level = "MEDIUM"
    response_upper = response.content.upper()
    if "CRITICAL" in response_upper:
        severity_level = "CRITICAL"
    elif "HIGH" in response_upper:
        severity_level = "HIGH"
    elif "LOW" in response_upper:
        severity_level = "LOW"

    import re
    score_match = re.search(r'priority score.*?\*?\*?(\d+)\*?\*?', response.content, re.IGNORECASE)
    priority_score = int(score_match.group(1)) if score_match else 5
    priority_score = min(priority_score, 10)

    return {
        "equipment_name": equipment_name,
        "severity_level": severity_level,
        "severity_assessment": response.content,
        "priority_score": priority_score,
        "has_sensor_context": sensor_context is not None,
        "module": "vision_ai"
    }


def execute_vision_actions(
    equipment_name: str,
    severity_level: str,
    priority_score: int,
    severity_assessment: str
) -> list[dict]:
    """
    Autonomous action execution for Vision AI findings.

    Same tool-calling pattern as the Decision Intelligence Engine —
    the LLM decides which tools to invoke based on severity, not
    hardcoded if-statements. This makes Visual Inspection a genuine
    agentic module, not just a classifier.
    """
    if severity_level not in ["HIGH", "CRITICAL"]:
        return []

    llm = get_llm(temperature=0.0)
    tools = get_all_tools()
    llm_with_tools = llm.bind_tools(tools)

    system_prompt = """You are PetroMind Vision AI's action executor.
Based on the severity assessment, decide which tools to call:

- If severity is HIGH or CRITICAL: call create_maintenance_ticket
- If severity is CRITICAL: also call send_alert with severity CRITICAL
- If severity is HIGH: call send_alert with severity HIGH
- If the assessment mentions specific parts (seal, bearing, gasket,
  flange, impeller): call check_spare_parts_inventory for that part

Only call tools clearly justified by the findings."""

    user_prompt = f"""Equipment: {equipment_name}
Severity: {severity_level}
Priority Score: {priority_score}/10

Severity Assessment:
{severity_assessment[:1500]}

Decide which actions to take and call the appropriate tools."""

    response = llm_with_tools.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    actions_taken = []
    if response.tool_calls:
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            matching_tool = next((t for t in tools if t.name == tool_name), None)
            if matching_tool:
                result = matching_tool.invoke(tool_args)
                actions_taken.append({
                    "tool": tool_name,
                    "args": tool_args,
                    "result": result
                })

    return actions_taken


def run_vision_analysis(
    image_path: str,
    equipment_name: str = "Equipment",
    sensor_context: str = None
) -> dict:
    """
    Master function — runs complete Vision AI pipeline.
    Called by /api/vision FastAPI route.

    Flow:
    Image → Vision LLM detection → LLM severity reasoning
    → autonomous action execution (if HIGH/CRITICAL)
    → structured output for Decision Intelligence Engine
    """
    from backend.modules.vision.detector import detect_defects

    detection = detect_defects(image_path)
    severity = assess_severity(
        defect_analysis=detection["raw_analysis"],
        equipment_name=equipment_name,
        sensor_context=sensor_context
    )

    actions_taken = execute_vision_actions(
        equipment_name=equipment_name,
        severity_level=severity["severity_level"],
        priority_score=severity["priority_score"],
        severity_assessment=severity["severity_assessment"]
    )

    return {
        "equipment_name": equipment_name,
        "raw_detection": detection["raw_analysis"],
        "severity_level": severity["severity_level"],
        "severity_assessment": severity["severity_assessment"],
        "priority_score": severity["priority_score"],
        "actions_taken": actions_taken,
        "has_sensor_context": severity["has_sensor_context"],
        "module": "vision_ai"
    }


if __name__ == "__main__":
    print("Testing Vision AI Severity Module with Action Execution...")
    print("=" * 60)
    print("✅ Vision AI severity module loaded successfully")
    print("Requires equipment image via /api/vision endpoint.")