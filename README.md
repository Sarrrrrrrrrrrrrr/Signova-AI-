# Signova AI — Demo Penerjemah Dua Arah BISINDO

## Cara menjalankan
```bash
cd backend
pip install -r ../requirements.txt
uvicorn main:app --reload
```
Buka http://localhost:8000 (pakai Chrome agar mic Web Speech API jalan).

## Arsitektur (sesuai UML sequence)
mic -> Web Speech API (id-ID) -> POST /translate -> parser.py
(normalisasi -> gloss -> lookup dictionary.json) -> urutan klip
-> frontend memutar klip berurutan. Gloss tanpa klip -> ejaan huruf
atau teks besar (demo tidak pernah error).

## Struktur
- backend/main.py        — FastAPI: /translate, /health, static /videos, frontend
- backend/parser.py      — normalisasi + greedy phrase match + fallback eja
- backend/dictionary.json— kamus gloss -> nama klip (35 frasa + 26 huruf)
- backend/videos/        — isi klip .mp4 di sini (lihat BACA_SAYA.txt)
- frontend/index.html    — SPA satu berkas, 6 tampilan via hash routing
  (vanilla HTML/CSS/JS, tanpa build):
  - `#/` landing (hero + maskot Nova), `#/masuk` & `#/daftar` (mock visual,
    TANPA auth nyata — pekerjaan masa depan), `#/dashboard` (kartu fitur +
    placeholder Riwayat/Pengaturan), `#/interpreter`, `#/hearme`.
  - **Interpreter** (suara/teks -> isyarat): mic Web Speech id-ID, live caption,
    chip gloss, cakupan kamus, kecepatan avatar (playbackRate video sungguhan),
    panggung gelap dengan maskot robot **Nova** (SVG, 4 state).
  - **HearMe** (isyarat -> suara): kamera nyata (getUserMedia), overlay 21 titik
    tangan, label isyarat + keyakinan, keluaran suara (Speech Synthesis id-ID),
    riwayat frasa per sesi. Pengenalan isyarat masih **simulasi demo** (berlabel
    jujur di UI); antarmuka recognizer siap ditukar dengan `POST /recognize`.
  - Aksesibilitas: kontras AA, fokus keyboard (navigasi hash memindahkan fokus
    ke judul), status ikon+teks+warna, prefers-reduced-motion + tombol
    "kurangi animasi".
  - Dependensi eksternal hanya Google Fonts (Inter) + ikon Lucide (CDN).
- frontend/assets/       — PNG maskot/logo opsional (lihat BACA_SAYA.txt);
  tanpa PNG, SVG Nova bawaan yang tampil
- frontend/index.legacy.html — UI lama (cadangan sebelum redesain)

## Uji cepat tanpa browser
```bash
cd backend && python parser.py
curl -X POST localhost:8000/translate -H "Content-Type: application/json" \
     -d '{"text":"Selamat pagi, saya mau daftar periksa"}'
```
