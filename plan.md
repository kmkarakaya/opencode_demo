# Plan: Web Tabanlı Sohbet Botu (FastAPI)

## Genel Bakış
Google.com arama motoru arayüzüne benzer, çok basit bir web tabanlı sohbet botu.
OpenAI API uyumlu bir LLM servisine bağlanır. Arayüzde "Murat Karakaya Akademi" imzası bulunur.

## Konum
`C:\Users\KMK\opencode demo\`

## Dosya Yapısı
- `main.py` — FastAPI sunucusu (uvicorn, port 2026)
  - `GET /` → `static/index.html` servis eder
  - `POST /api/chat` → OpenAI uyumlu `/v1/chat/completions` endpoint'ine istek
    - Base URL: `http://100.70.134.107:8001/v1`
    - Model: `Ornith-1.0-9B-4bit`
    - Token: `.env` içindeki `API_TOKEN` (Bearer header)
    - Çoklu mesaj geçmişi: gövdeden gelen `messages` dizisi olduğu gibi iletilir
    - Tek yanıt (streaming değil, basitlik için)
- `.env` — `API_TOKEN=24081969`, `BASE_URL=http://100.70.134.107:8001/v1`, `MODEL=Ornith-1.0-9B-4bit plan`
- `requirements.txt` — `fastapi`, `uvicorn`, `python-dotenv`, `httpx`
- `static/index.html` — Google benzeri arayüz:
  - Ortada başlık "Murat Karakaya Akademi" + arama/soru çubuğu
  - Soru girilince sohbet ekranına geçiş
  - Markdown render (marked.js CDN) + basit CSS
  - Sohbet balonları, geçmiş korunur

## LLM Yapılandırması
- Base URL: `http://100.70.134.107:8001/v1`
- Token/Password: `24081969`
- LLM: `Ornith-1.0-9B-4bit plan`

## Çalıştırma
```
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 2026
```
Tarayıcıda: `http://localhost:2026`

## Kullanıcı Tercihleri (Onaylanan)
- Teknoloji: FastAPI
- Token saklama: `.env` dosyası
- Sohbet geçmişi: Çoklu mesaj geçmişi (context korunur)
- Arayüz: Google başlangıç ekranı (logo + çubuk, tıklayınca sohbet)
- Çıkış formatı: Markdown desteği
- Port: 2026
- Konum: Bulunulan klasörde `opencode demo`
