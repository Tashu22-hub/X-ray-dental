import os
import requests
import openai
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# ======== Load Environment Variables ========
load_dotenv()
roboflow_api_key = os.getenv("ROBOFLOW_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

if not roboflow_api_key or not openai.api_key:
    raise ValueError("API keys not set in .env file")

# ======== Constants ========
image_dir = r"C:\Users\DELL\OneDrive\DICom_converter\dcm_images\png_images"
endpoint = f"https://detect.roboflow.com/adr/6?api_key={roboflow_api_key}&confidence=0.3&overlap=0.5"

# ======== Process Images ========
for filename in os.listdir(image_dir):
    if filename.lower().endswith(".png"):
        image_path = os.path.join(image_dir, filename)
        print(f"\nProcessing: {filename}")

        # Load Image
        image = Image.open(image_path)

        # Send to Roboflow
        with open(image_path, "rb") as image_file:
            response = requests.post(endpoint, files={"image": image_file})
        data = response.json()
        predictions = data.get("predictions", [])

        # Draw Bounding Boxes
        draw = ImageDraw.Draw(image)
        for pred in predictions:
            x, y = pred["x"], pred["y"]
            w, h = pred["width"], pred["height"]
            x0, y0 = x - w / 2, y - h / 2
            x1, y1 = x + w / 2, y + h / 2
            label = pred["class"]
            confidence = pred["confidence"]
            draw.rectangle([x0, y0, x1, y1], outline="red", width=2)
            draw.text((x0, y0), f"{label} ({confidence:.2f})", fill="red")

        # Create annotation summary for LLM
        annotation_text = "\n".join([
            f"- {p['class']} with {p['confidence']*100:.1f}% confidence at (x={p['x']}, y={p['y']})"
            for p in predictions
        ])

        # ======== Diagnostic Report via OpenAI ========
        if predictions:
            prompt = f"""
You are a dental radiologist. Based on the following image annotations (which include detected pathologies), write a concise diagnostic report in clinical language.

Annotations:
{annotation_text}

Output a brief paragraph highlighting:
- Detected pathologies
- Location if possible (e.g., upper left molar)
- Optional clinical advice
"""
            try:
                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a professional dental radiologist."},
                        {"role": "user", "content": prompt}
                    ]
                )
                report = completion.choices[0].message.content.strip()
            except Exception as e:
                report = f"Error generating report: {e}"
        else:
            report = "No pathologies detected."

        # ======== Display Results Side-by-Side ========
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
        ax1.imshow(image)
        ax1.axis('off')
        ax1.set_title(f"Predictions: {filename}")

        ax2.text(0, 1, report, fontsize=12, verticalalignment='top', wrap=True)
        ax2.axis('off')
        ax2.set_title("Diagnostic Report")

        plt.tight_layout()
        plt.show()
