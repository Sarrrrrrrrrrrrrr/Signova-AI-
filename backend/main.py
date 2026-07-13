"""
main.py — Backend Signova AI (demo Interpreter: ucapan -> isyarat)
===================================================================
Jalankan:
    pip install fastapi "uvicorn[standard]"
    uvicorn main:app --reload
Lalu buka  http://localhost:8000

Endpoint:
    POST /translate   { "text": "selamat pagi" }
        -> { input, tokens, gloss, clips[], coverage }
    GET  /health      -> cek server hidup
    GET  /videos/...  -> klip isyarat (isi folder videos/ sendiri)
    GET  /            -> frontend demo (frontend/index.html)
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import parser as gloss_parser

BASE = Path(__file__).parent
FRONTEND = BASE.parent / "frontend"
VIDEOS = BASE / "videos"

app = FastAPI(
    title="Signova AI — Demo API",
    description="Penerjemah ucapan/teks ke urutan klip bahasa isyarat BISINDO",
    version="0.1.0",
)

# CORS terbuka untuk memudahkan demo (frontend bisa dari mana saja).
# Untuk produksi, batasi allow_origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500,
                      description="Kalimat Bahasa Indonesia")


@app.post("/translate")
def translate(req: TranslateRequest):
    """Terjemahkan teks menjadi urutan gloss + klip isyarat."""
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=422, detail="Teks kosong.")
    return gloss_parser.translate(text)


@app.get("/health")
def health():
    return {"status": "ok", "vocab_size": len(gloss_parser.DICTIONARY)}


# --- Static: klip video isyarat -------------------------------------------
VIDEOS.mkdir(exist_ok=True)
app.mount("/videos", StaticFiles(directory=VIDEOS), name="videos")


# --- Frontend demo ----------------------------------------------------------
@app.get("/", include_in_schema=False)
def index():
    return FileResponse(FRONTEND / "index.html")
