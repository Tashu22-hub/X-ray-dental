import os
import requests
from typing import Dict, Any, List
from dotenv import load_dotenv
from PIL import Image, ImageDraw

import asyncio
import aiofiles

load_dotenv()

ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
ROBOFLOW_MODEL_URL = "https://detect.roboflow.com/adr/6"

async def send_to_roboflow(image_path: str, confidence=0.3, overlap=0.5) -> List[Dict[str, Any]]:
    if not ROBOFLOW_API_KEY:
        raise ValueError("ROBOFLOW_API_KEY environment variable not set.")

    params = {
        "api_key": ROBOFLOW_API_KEY,
        "confidence": confidence,
        "overlap": overlap,
    }

    # Read image file asynchronously
    async with aiofiles.open(image_path, "rb") as f:
        image_bytes = await f.read()

    # Use run_in_executor to avoid blocking event loop on requests.post (which is sync)
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: requests.post(ROBOFLOW_MODEL_URL, params=params, files={"file": image_bytes})
    )

    try:
        response.raise_for_status()
        response_json = response.json()
        print("📦 Roboflow raw response:", response_json)
        return response_json.get("predictions", [])
    except requests.exceptions.RequestException as e:
        print(f"[Roboflow API Error] {e}")
        return []

def draw_predictions(image_path: str, predictions: List[Dict[str, Any]]) -> Image.Image:
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    for pred in predictions:
        x = pred["x"]
        y = pred["y"]
        width = pred["width"]
        height = pred["height"]
        class_name = pred["class"]
        confidence = pred["confidence"]

        left = x - width / 2
        top = y - height / 2
        right = x + width / 2
        bottom = y + height / 2

        draw.rectangle([left, top, right, bottom], outline="red", width=2)
        label = f"{class_name} ({confidence:.2f})"
        draw.text((left + 4, top + 4), label, fill="red")

    return image
