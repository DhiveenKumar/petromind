# =============================================================================
# transformer.py — Time Series Anomaly Detection for PetroMind
#
# Uses statistical anomaly detection on equipment sensor data.
# Detects pressure drops, vibration spikes, temperature deviations.
#
# Architecture:
# CSV sensor data → preprocessing → anomaly detection
# → structured output for LLM explanation layer
# =============================================================================

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))


def load_sensor_data(file_path: str) -> pd.DataFrame:
    """
    Loads sensor CSV file.
    Expected columns: timestamp, pressure_psi, temperature_f, vibration_mm
    """
    df = pd.read_csv(file_path)

    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)

    print(f"✅ Loaded {len(df)} sensor readings")
    print(f"   Columns: {list(df.columns)}")
    return df


def detect_anomalies(df: pd.DataFrame) -> dict:
    """
    Statistical anomaly detection using Z-score method.
    Identifies readings that deviate significantly from normal.

    Why Z-score?
    Simple, interpretable, and effective for sensor data.
    A reading with Z-score > 3 is more than 3 standard deviations
    from the mean — statistically unusual and worth investigating.

    In production: replace with Hugging Face Time Series Transformer
    for more sophisticated pattern recognition across longer sequences.
    """
    sensor_columns = [
        col for col in df.columns
        if col != 'timestamp' and df[col].dtype in ['float64', 'int64']
    ]

    anomalies = {}
    summary = {}

    for col in sensor_columns:
        values = df[col].values
        mean = np.mean(values)
        std = np.std(values)

        if std == 0:
            continue

        z_scores = np.abs((values - mean) / std)
        anomaly_indices = np.where(z_scores > 2.5)[0]

        # Calculate trend — last 20% vs first 20%
        n = len(values)
        early = np.mean(values[:n//5]) if n >= 5 else mean
        recent = np.mean(values[-(n//5):]) if n >= 5 else mean
        trend_pct = ((recent - early) / early * 100) if early != 0 else 0

        anomalies[col] = {
            "anomaly_count": len(anomaly_indices),
            "anomaly_indices": anomaly_indices.tolist()[:10],
            "mean": round(float(mean), 3),
            "std": round(float(std), 3),
            "max_z_score": round(float(np.max(z_scores)), 3),
            "trend_percent": round(float(trend_pct), 2)
        }

        summary[col] = {
            "mean": round(float(mean), 3),
            "std": round(float(std), 3),
            "min": round(float(np.min(values)), 3),
            "max": round(float(np.max(values)), 3),
            "anomaly_count": len(anomaly_indices),
            "trend_percent": round(float(trend_pct), 2),
            "status": "ANOMALY" if len(anomaly_indices) > 0 else "NORMAL"
        }

    # Overall risk score
    total_anomalies = sum(a["anomaly_count"] for a in anomalies.values())
    max_z = max(
        (a["max_z_score"] for a in anomalies.values()),
        default=0
    )

    if max_z > 4 or total_anomalies > 20:
        risk_level = "HIGH"
        failure_probability = min(0.95, total_anomalies / len(df) * 10)
    elif max_z > 3 or total_anomalies > 10:
        risk_level = "MEDIUM"
        failure_probability = min(0.60, total_anomalies / len(df) * 5)
    else:
        risk_level = "LOW"
        failure_probability = min(0.20, total_anomalies / len(df) * 2)

    return {
        "sensor_summary": summary,
        "anomaly_details": anomalies,
        "risk_level": risk_level,
        "failure_probability": round(failure_probability, 3),
        "total_anomalies": total_anomalies,
        "readings_analysed": len(df)
    }


def generate_sensor_report(analysis: dict) -> str:
    """
    Formats analysis results into structured text
    for the LLM explanation layer.
    """
    lines = []
    lines.append("SENSOR ANALYSIS REPORT")
    lines.append("=" * 40)
    lines.append(f"Risk Level: {analysis['risk_level']}")
    lines.append(
        f"Failure Probability: "
        f"{analysis['failure_probability']*100:.1f}%"
    )
    lines.append(
        f"Total Anomalies: {analysis['total_anomalies']} "
        f"in {analysis['readings_analysed']} readings"
    )
    lines.append("")

    for sensor, stats in analysis["sensor_summary"].items():
        lines.append(f"Sensor: {sensor}")
        lines.append(f"  Status: {stats['status']}")
        lines.append(f"  Mean: {stats['mean']}")
        lines.append(f"  Range: {stats['min']} — {stats['max']}")
        lines.append(f"  Anomalies: {stats['anomaly_count']}")
        trend = stats['trend_percent']
        direction = "↑" if trend > 0 else "↓"
        lines.append(f"  Trend: {direction} {abs(trend)}%")
        lines.append("")

    return "\n".join(lines)


def run_prediction(file_path: str) -> dict:
    """
    Master function — runs complete prediction pipeline.
    Called by /api/prediction FastAPI route.
    Returns structured output for LLM explanation + Decision Engine.
    """
    df = load_sensor_data(file_path)
    analysis = detect_anomalies(df)
    report_text = generate_sensor_report(analysis)

    return {
        "analysis": analysis,
        "report_text": report_text,
        "module": "prediction_ai"
    }


if __name__ == "__main__":
    import json

    # Generate synthetic test data
    np.random.seed(42)
    n = 200
    timestamps = pd.date_range('2024-01-01', periods=n, freq='h')

    pressure = 150 + np.random.normal(0, 5, n)
    temperature = 180 + np.random.normal(0, 8, n)
    vibration = 2.5 + np.random.normal(0, 0.3, n)

    # Inject anomalies
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

    print("Testing Prediction AI Module...")
    print("=" * 60)

    result = run_prediction(test_file)

    print(result["report_text"])
    print(f"Risk Level: {result['analysis']['risk_level']}")
    print(
        f"Failure Probability: "
        f"{result['analysis']['failure_probability']*100:.1f}%"
    )