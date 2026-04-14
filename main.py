from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import numpy as np
import cv2
import tempfile
from gtts import gTTS
from deep_translator import GoogleTranslator
from pydantic import BaseModel
import pytesseract

# =========================
# INIT
# =========================

app = FastAPI()

# 🔥 CORS FIX (VERY IMPORTANT FOR FLUTTER WEB)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# OCR FUNCTION (TESSERACT)
# =========================

def run_ocr(img):
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Improve quality
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

        # Telugu OCR
        text = pytesseract.image_to_string(gray, lang='tel')

        return text.strip()
    except Exception as e:
        return f"OCR Error: {e}"

# =========================
# REQUEST MODEL
# =========================

class TTSRequest(BaseModel):
    text: str
    target_language: str

# =========================
# API ROUTES
# =========================

@app.get("/")
def home():
    return {
        "status": "running",
        "ocr": "tesseract",
        "language": "telugu"
    }

# 🔥 IMPORTANT (Fixes browser preflight)
@app.options("/ocr-translate")
def options_ocr():
    return {"status": "ok"}

@app.post("/ocr-translate")
async def ocr_translate(file: UploadFile = File(...), target_language: str = "en"):
    try:
        contents = await file.read()

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
        except:
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
        tts_audio = gTTS(text=req.text, lang=req.target_language)

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts_audio.save(tmp.name)

        return FileResponse(tmp.name, media_type="audio/mpeg")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
