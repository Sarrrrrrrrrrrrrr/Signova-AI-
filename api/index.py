"""
api/index.py — Entry point serverless Vercel.
=============================================
Vercel menjalankan FastAPI sebagai function (bukan uvicorn persisten).
File ini hanya mengekspos `app` dari backend/main.py tanpa mengubahnya;
routing / dan /videos ditangani statis lewat vercel.json.
Untuk pengembangan lokal tetap pakai: uvicorn main:app --reload (dari backend/).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from main import app  # noqa: E402,F401
