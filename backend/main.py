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

from roboflow_utils import send_to_roboflow, draw_predictions  # Make sure roboflow.py is in the same folder
from report_generator import generate_report
app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or use ["http://localhost:3000"]
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

        # Save uploaded DICOM file
        with open(temp_path, "wb") as f:
            f.write(contents)

        # Read DICOM
        ds = pydicom.dcmread(temp_path)
        arr = apply_voi_lut(ds.pixel_array, ds)

        if ds.PhotometricInterpretation == "MONOCHROME1":
            arr = np.max(arr) - arr

        arr = arr - np.min(arr)
        arr = arr / np.max(arr)
        arr = (arr * 255).astype(np.uint8)
        
        

        # Save image as PNG for Roboflow
        image = Image.fromarray(arr)
        # Resize image before converting to PNG- reducing latency to upload image to roboflow 
        image = Image.fromarray(arr).resize((512, 512))

        image.save(png_path)

        # 🔍 Call Roboflow API
        predictions = send_to_roboflow(png_path)

        # 🎯 Draw predictions on image
        annotated_img = draw_predictions(png_path, predictions)

        # 🔄 Convert annotated image to base64
        buffered = BytesIO()
        annotated_img.save(buffered, format="PNG")
        annotated_img_b64 = base64.b64encode(buffered.getvalue()).decode()

        # Diagnostic summary
         # 🧠 Generate report
        report = generate_report(predictions)

        return {
            "original_image_b64": annotated_img_b64,
            "diagnostic_report": report
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})
