from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pydicom
from pydicom.pixel_data_handlers.util import apply_voi_lut
from PIL import Image
import numpy as np
import base64
from io import BytesIO
import os
import aiofiles

from roboflow_utils import send_to_roboflow, draw_predictions
from report_generator import generate_report

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload-dicom/")
async def upload_dicom(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        os.makedirs("temp", exist_ok=True)
        temp_path = f"temp/{file.filename}"
        png_path = temp_path.replace(".dcm", ".png")

        # Async write DICOM file to disk for faster IO
        async with aiofiles.open(temp_path, "wb") as f:
            await f.write(contents)

        ds = pydicom.dcmread(temp_path)
        arr = apply_voi_lut(ds.pixel_array, ds)

        if ds.PhotometricInterpretation == "MONOCHROME1":
            arr = np.max(arr) - arr

        arr = arr - np.min(arr)
        arr = arr / np.max(arr)
        arr = (arr * 255).astype(np.uint8)

        # Create PIL Image once and resize once to 512x512 (reduce upload size)
        image = Image.fromarray(arr).resize((256, 256))
        image.save(png_path)

        # Roboflow API call - async for non-blocking
        predictions = await send_to_roboflow(png_path)

        # Draw bounding boxes on the resized image
        annotated_img = draw_predictions(png_path, predictions)

        # Encode to base64 for frontend
        buffered = BytesIO()
        annotated_img.save(buffered, format="PNG")
        annotated_img_b64 = base64.b64encode(buffered.getvalue()).decode()

        report = generate_report(predictions)

        return {
            "original_image_b64": annotated_img_b64,
            "diagnostic_report": report
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})
