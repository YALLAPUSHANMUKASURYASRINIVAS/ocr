from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

import numpy as np
import cv2
import tempfile
import os

from gtts import gTTS
from deep_translator import GoogleTranslator
import pytesseract

# =========================
# IMPORTANT (Docker FIX)
# =========================
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# =========================
# INIT
# =========================

app = FastAPI()

# 🔥 CORS (Flutter Web fix)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# OCR FUNCTION
# =========================

def run_ocr(img):
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Improve OCR quality
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

        # Optional: resize for better accuracy
        gray = cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)

        # Telugu OCR
        text = pytesseract.image_to_string(gray, lang='tel')

        return text.strip()

    except Exception as e:
        return f"OCR Error: {str(e)}"

# =========================
# REQUEST MODEL
# =========================

class TTSRequest(BaseModel):
    text: str
    target_language: str

# =========================
# ROUTES
# =========================

@app.get("/")
def home():
    return {
        "status": "running",
        "ocr": "tesseract",
        "language": "telugu",
        "tesseract_path": pytesseract.pytesseract.tesseract_cmd
    }

# 🔥 Preflight fix
@app.options("/ocr-translate")
def options_ocr():
    return {"status": "ok"}

@app.post("/ocr-translate")
async def ocr_translate(file: UploadFile = File(...), target_language: str = "en"):
    try:
        contents = await file.read()

        # Decode image
        img = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image")

        # OCR
        text = run_ocr(img)

        # Translation
        try:
            translated = GoogleTranslator(
                source="auto",
                target=target_language
            ).translate(text)
        except Exception:
            translated = "Translation failed"

        return {
            "ocr_text": text,
            "translated": translated
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tts")
def tts(req: TTSRequest):
    try:
        if not req.text:
            raise HTTPException(status_code=400, detail="Text is empty")

        tts_audio = gTTS(text=req.text, lang=req.target_language)

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts_audio.save(tmp.name)

        return FileResponse(tmp.name, media_type="audio/mpeg")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
