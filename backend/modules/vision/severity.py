# =============================================================================
# severity.py — LLM Severity Reasoning for Vision AI
#
# Takes raw defect detection output and generates:
# - Severity classification with justification
# - Maintenance recommendation with citations
# - Integration with sensor data if available
# =============================================================================

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from backend.core.llm import get_llm
from langchain_core.messages import HumanMessage, SystemMessage


def assess_severity(
    defect_analysis: str,
    equipment_name: str = "Equipment",
    sensor_context: str = None
) -> dict:
    """
    Takes vision defect analysis and generates severity assessment
    with maintenance recommendations.

    Optionally integrates sensor data context from Prediction AI
    for cross-modal reasoning in the Decision Intelligence Engine.
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

    # Extract severity level from response
    severity_level = "MEDIUM"
    response_upper = response.content.upper()
    if "CRITICAL" in response_upper:
        severity_level = "CRITICAL"
    elif "HIGH" in response_upper:
        severity_level = "HIGH"
    elif "LOW" in response_upper:
        severity_level = "LOW"

    return {
        "equipment_name": equipment_name,
        "severity_level": severity_level,
        "severity_assessment": response.content,
        "has_sensor_context": sensor_context is not None,
        "module": "vision_ai"
    }


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
    → structured output for Decision Intelligence Engine
    """
    from backend.modules.vision.detector import detect_defects

    detection = detect_defects(image_path)
    severity = assess_severity(
        defect_analysis=detection["raw_analysis"],
        equipment_name=equipment_name,
        sensor_context=sensor_context
    )

    return {
        "equipment_name": equipment_name,
        "raw_detection": detection["raw_analysis"],
        "severity_level": severity["severity_level"],
        "severity_assessment": severity["severity_assessment"],
        "has_sensor_context": severity["has_sensor_context"],
        "module": "vision_ai"
    }


if __name__ == "__main__":
    print("Testing Vision AI Severity Module...")
    print("=" * 60)
    print("✅ Vision AI severity module loaded successfully")
    print("Requires equipment image via /api/vision endpoint.")