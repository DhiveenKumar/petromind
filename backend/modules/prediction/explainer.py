# =============================================================================
# explainer.py — LLM Explanation Layer for Prediction AI
#
# This is what makes PetroMind's Prediction AI different from
# a standard anomaly detection model.
#
# Standard approach: model outputs a number or flag
# PetroMind approach: Transformer detects anomaly →
#                     LLM explains WHY in natural language
#
# Field engineer asks: "Why might Pump-17 fail next week?"
# System answers:     "Vibration increased 69%, pressure
#                      spiked 8.5% — historical pattern
#                      matches seal failure signatures"
# =============================================================================

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from backend.core.llm import get_llm
from backend.modules.prediction.transformer import run_prediction
from langchain_core.messages import HumanMessage, SystemMessage


def explain_prediction(
    analysis: dict,
    report_text: str,
    equipment_name: str = "Equipment"
) -> dict:
    """
    Takes structured anomaly analysis and generates
    natural language explanation using LLM.

    This is the Transformer + LLM combination that
    interviewers find most impressive — two different
    AI techniques working together.
    """
    llm = get_llm(temperature=0.0)

    system_prompt = """You are PetroMind Prediction AI — an expert in 
oil and gas equipment failure analysis.

You receive sensor anomaly analysis reports and explain:
1. What the data shows in plain language
2. Which sensors are most concerning and why
3. What failure mode this pattern suggests
4. What immediate action is recommended
5. Time estimate before potential failure

Be specific about numbers. Reference the actual sensor values.
Keep your response structured and actionable.
This is a safety-critical system — be precise."""

    user_prompt = f"""Equipment: {equipment_name}

Sensor Analysis Report:
{report_text}

Risk Level: {analysis['risk_level']}
Failure Probability: {analysis['failure_probability']*100:.1f}%

Please provide:
1. A plain language explanation of what these sensor readings indicate
2. Which sensor is most concerning and why
3. What failure mode this pattern suggests based on oil & gas engineering knowledge
4. Recommended immediate action
5. Estimated time window before potential failure if unaddressed"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    return {
        "equipment_name": equipment_name,
        "risk_level": analysis["risk_level"],
        "failure_probability": analysis["failure_probability"],
        "llm_explanation": response.content,
        "sensor_summary": analysis["sensor_summary"],
        "total_anomalies": analysis["total_anomalies"],
        "module": "prediction_ai"
    }


def run_prediction_with_explanation(
    file_path: str,
    equipment_name: str = "Equipment"
) -> dict:
    """
    Master function — runs complete Prediction AI pipeline.
    Called by /api/prediction FastAPI route.

    Flow:
    CSV → load → detect anomalies → LLM explanation
    → structured output for Decision Intelligence Engine
    """
    prediction = run_prediction(file_path)
    explanation = explain_prediction(
        analysis=prediction["analysis"],
        report_text=prediction["report_text"],
        equipment_name=equipment_name
    )
    return explanation


if __name__ == "__main__":
    import numpy as np
    import pandas as pd

    # Generate test data with anomalies
    np.random.seed(42)
    n = 200
    timestamps = pd.date_range('2024-01-01', periods=n, freq='h')
    pressure = 150 + np.random.normal(0, 5, n)
    temperature = 180 + np.random.normal(0, 8, n)
    vibration = 2.5 + np.random.normal(0, 0.3, n)

    pressure[150:170] += 45
    vibration[160:180] += 3.5
    temperature[140:160] -= 25

    test_df = pd.DataFrame({
        'timestamp': timestamps,
        'pressure_psi': pressure,
        'temperature_f': temperature,
        'vibration_mm': vibration
    })

    test_file = '/tmp/test_sensors.csv'
    test_df.to_csv(test_file, index=False)

    print("Testing Prediction AI + LLM Explanation...")
    print("=" * 60)

    result = run_prediction_with_explanation(
        test_file,
        equipment_name="Pump-17"
    )

    print(f"\nEquipment: {result['equipment_name']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Failure Probability: {result['failure_probability']*100:.1f}%")
    print(f"\nLLM Explanation:\n{result['llm_explanation']}")