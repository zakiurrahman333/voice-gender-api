from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import shutil
import torch
import uuid
import os
from model import ECAPA_gender

app = FastAPI(
    title="Voice Gender Classifier API",
    description="API that predicts gender from .wav audio files using ECAPA-TDNN model.",
    version="1.0.0"
)

# Load model once at startup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = ECAPA_gender.from_pretrained("JaesungHuh/voice-gender-classifier")
model.to(device)
model.eval()
print(f"Model loaded on device: {device}")

@app.get("/")
async def root():
    return {"message": "Welcome to the Voice Gender Classifier API!"}

@app.post("/predict")
async def predict_gender(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".wav"):
        raise HTTPException(status_code=400, detail="Only .wav audio files are supported.")

    try:
        temp_file = f"temp_{uuid.uuid4().hex}.wav"
        contents = await file.read()  # ✅ Read file contents properly
        with open(temp_file, "wb") as buffer:
            buffer.write(contents)

        gender = model.predict(temp_file, device=device)
        os.remove(temp_file)

        return JSONResponse({"gender": gender})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
