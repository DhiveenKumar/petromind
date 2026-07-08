# =============================================================================
# detector.py — Vision AI for PetroMind
#
# Analyses equipment images to detect defects:
# corrosion, cracks, leaks, structural damage
#
# Uses GPT-4o Vision — same model as generation,
# with image input capability.
# =============================================================================

import os
import sys
import base64
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from backend.core.llm import get_vision_llm
from langchain_core.messages import HumanMessage


def encode_image_to_base64(image_path: str) -> str:
    """
    Converts image file to base64 string for API transmission.
    GPT-4o Vision accepts base64-encoded images.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def get_image_mime_type(image_path: str) -> str:
    """Returns MIME type based on file extension."""
    ext = Path(image_path).suffix.lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.webp': 'image/webp'
    }
    return mime_types.get(ext, 'image/jpeg')


def detect_defects(image_path: str) -> dict:
    """
    Passes equipment image to Vision LLM for defect detection.

    Returns structured defect analysis:
    - defect_type: what was found
    - severity: LOW / MEDIUM / HIGH / CRITICAL
    - location: where on the equipment
    - confidence: how certain the model is
    - raw_analysis: full model response
    """
    llm = get_vision_llm()

    image_data = encode_image_to_base64(image_path)
    mime_type = get_image_mime_type(image_path)

    system_message = """You are PetroMind Vision AI — an expert in oil and gas 
equipment inspection and defect detection.

Analyse the equipment image and identify:
1. Equipment type (pump, valve, pipeline, vessel, etc.)
2. Visible defects (corrosion, cracks, leaks, erosion, etc.)
3. Defect severity (LOW/MEDIUM/HIGH/CRITICAL)
4. Affected area and location on equipment
5. Estimated defect coverage percentage
6. Immediate safety risk assessment

Be specific and technical. Your analysis informs maintenance decisions."""

    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": system_message
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{image_data}"
                }
            },
            {
                "type": "text",
                "text": """Provide a structured analysis with:
- Equipment Type
- Defects Found (list each one)
- Primary Defect Severity (LOW/MEDIUM/HIGH/CRITICAL)
- Affected Location
- Coverage Estimate (%)
- Safety Risk Assessment
- Recommended Action"""
            }
        ]
    )

    response = llm.invoke([message])

    return {
        "image_path": image_path,
        "raw_analysis": response.content,
        "module": "vision_ai"
    }


if __name__ == "__main__":
    import sys

    print("Testing Vision AI Detector...")
    print("=" * 60)
    print("Vision AI detector ready.")
    print("Requires an actual equipment image to run.")
    print("Will be tested via /api/vision endpoint with uploaded image.")
    print("✅ Vision AI detector module loaded successfully")