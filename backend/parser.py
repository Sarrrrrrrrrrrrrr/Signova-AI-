"""
parser.py — Parser Teks -> Gloss BISINDO untuk Signova AI
==========================================================
Alur: teks mentah -> normalisasi -> pencocokan frasa terpanjang (greedy)
      -> gloss -> lookup kamus klip -> fallback ejaan huruf.

Catatan penting untuk juri/dokumentasi:
- Ini pendekatan rule-based + dictionary untuk MVP. Model ML (seq2seq
  text->gloss) ada di roadmap setelah dataset terkumpul.
- BISINDO punya grammar sendiri; MVP ini melakukan penyederhanaan
  (menghapus kata fungsi) sebagai aproksimasi glossing, divalidasi
  bersama komunitas Tuli.
"""

import json
import re
import unicodedata
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Muat kamus gloss -> file klip
# ---------------------------------------------------------------------------
DICT_PATH = Path(__file__).parent / "dictionary.json"

with open(DICT_PATH, encoding="utf-8") as f:
    DICTIONARY: dict[str, str] = json.load(f)

# Kunci kamus yang terdiri >1 kata, diurutkan dari yang terpanjang
# agar "selamat pagi" tertangkap sebelum "selamat".
PHRASES = sorted(
    (k for k in DICTIONARY if " " in k),
    key=lambda k: len(k.split()),
    reverse=True,
)

# ---------------------------------------------------------------------------
# 2. Normalisasi
# ---------------------------------------------------------------------------
# Kata tidak baku / percakapan -> bentuk baku yang ada di kamus
SLANG_MAP = {
    "gak": "tidak", "ga": "tidak", "nggak": "tidak", "engga": "tidak",
    "udah": "sudah", "udh": "sudah",
    "gimana": "bagaimana", "gmn": "bagaimana",
    "makasih": "terima kasih", "trims": "terima kasih",
    "aja": "saja", "kalo": "kalau", "sy": "saya", "sdh": "sudah",
    "bpk": "bapak", "bu": "ibu", "pak": "bapak",
}

# Kata fungsi yang umumnya tidak diisyaratkan secara terpisah di BISINDO
STOPWORDS = {
    "yang", "di", "ke", "dari", "dan", "atau", "itu", "ini", "para",
    "pada", "dengan", "untuk", "adalah", "ya", "kah", "lah", "pun",
    "si", "sang", "oleh",
}


def normalize(text: str) -> list[str]:
    """Lowercase, buang tanda baca, perbaiki slang, buang stopword."""
    text = unicodedata.normalize("NFKC", text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)          # buang tanda baca
    tokens = text.split()
    tokens = [SLANG_MAP.get(t, t) for t in tokens]     # slang -> baku
    # SLANG_MAP bisa menghasilkan frasa ("terima kasih") -> pecah lagi
    tokens = " ".join(tokens).split()
    tokens = [t for t in tokens if t not in STOPWORDS]
    return tokens


# ---------------------------------------------------------------------------
# 3. Pencocokan frasa terpanjang (greedy longest-match)
# ---------------------------------------------------------------------------
def to_gloss(tokens: list[str]) -> list[str]:
    """
    Gabungkan token menjadi gloss. Frasa multi-kata di kamus
    (mis. "selamat pagi") dicocokkan lebih dulu.
    """
    glosses: list[str] = []
    i = 0
    n = len(tokens)
    while i < n:
        matched = False
        for phrase in PHRASES:
            words = phrase.split()
            if tokens[i : i + len(words)] == words:
                glosses.append(phrase)
                i += len(words)
                matched = True
                break
        if not matched:
            glosses.append(tokens[i])
            i += 1
    return glosses


# ---------------------------------------------------------------------------
# 4. Lookup klip + fallback
# ---------------------------------------------------------------------------
def gloss_to_clips(glosses: list[str]) -> list[dict]:
    """
    Untuk tiap gloss kembalikan dict:
      { gloss, mode: 'video' | 'eja' | 'teks', file | letters }
    - video : klip ada di kamus
    - eja   : tidak ada di kamus tapi alfabetis -> fingerspelling per huruf
    - teks  : mengandung angka/simbol -> tampilkan sebagai teks saja
    """
    result = []
    for g in glosses:
        if g in DICTIONARY:
            result.append({"gloss": g, "mode": "video", "file": DICTIONARY[g]})
        elif g.isalpha():
            letters = [
                {"letter": ch, "file": DICTIONARY.get(f"huruf_{ch}")}
                for ch in g
            ]
            result.append({"gloss": g, "mode": "eja", "letters": letters})
        else:
            result.append({"gloss": g, "mode": "teks"})
    return result


# ---------------------------------------------------------------------------
# API utama yang dipakai main.py
# ---------------------------------------------------------------------------
def translate(text: str) -> dict:
    tokens = normalize(text)
    glosses = to_gloss(tokens)
    clips = gloss_to_clips(glosses)
    coverage = (
        sum(1 for c in clips if c["mode"] == "video") / len(clips)
        if clips else 0.0
    )
    return {
        "input": text,
        "tokens": tokens,
        "gloss": glosses,
        "clips": clips,
        "coverage": round(coverage, 2),   # % gloss yang punya klip video
    }


if __name__ == "__main__":
    # Uji cepat: python parser.py
    import pprint
    pprint.pprint(translate("Selamat pagi, ada yang bisa kami bantu?"))
