from typing import List, Dict, Optional
import openai
import os

def generate_report(predictions: List[Dict], use_llm: bool = False, OPENAI_API_KEY: Optional[str] = None) -> str:
    """
    Generate a diagnostic report.
    If use_llm is True and an OpenAI API key is provided, it uses GPT-4 to generate a clinical report.
    Otherwise, it falls back to a rule-based summary.
    """

    if not predictions:
        return (
            "No radiographic abnormalities were detected in the dental X-ray. "
            "The image appears within normal limits. Routine dental check-ups are recommended."
        )

    if use_llm and OPENAI_API_KEY:
        try:
            openai.api_key = OPENAI_API_KEY

            metadata = {
                "num_detections": len(predictions),
                "classes": list(set(pred.get("class_name", "Unknown") for pred in predictions)),
            }

            prompt = f"""
You are a dental radiologist. Based on the image annotations provided below (which include detected pathologies), write a concise diagnostic report in clinical language.

Annotations:
{predictions}

Write a brief paragraph highlighting:
- Detected pathologies
- Location if possible (e.g., upper left molar)
- Clinical advice (optional)
"""

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=250
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"⚠️ LLM generation failed: {e}. Falling back to rule-based summary."

    # Fallback: Rule-based summary
    findings = []
    for pred in predictions:
        label = pred.get("class_name", "an abnormality")
        confidence = pred.get("confidence", 0)
        bbox = pred.get("bbox", {})
        x = bbox.get("x", "unknown")
        y = bbox.get("y", "unknown")

        # Estimate position
        quadrant = "upper" if y != "unknown" and y < 500 else "lower"
        side = "left" if x != "unknown" and x < 750 else "right"
        location = f"{quadrant} {side} quadrant"

        findings.append(f"{label.replace('_', ' ')} in the {location} (confidence {confidence:.2f})")

    report = (
        "Dental radiographic analysis indicates the following findings:\n"
        + "; ".join(findings) + ".\n"
        "A detailed clinical examination is advised to confirm the diagnosis and determine appropriate treatment."
    )
    return report
