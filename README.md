# Murat Karakaya Akademi Sohbet Botu

Basit, tek sayfalık bir **web tabanlı sohbet botu**. FastAPI ile yazılmış bir sunucu,
Google benzeri bir açılış ekranı sunar ve kullanıcı mesajlarını **OpenAI uyumlu bir LLM
backend**'ine iletir. Sohbet geçmişi korunur ve bot yanıtları Markdown olarak render edilir.

> Örnek/demo proje ("opencode demo"). Arayüz ve dokümantasyon Türkçe'dir.

## Özellikler

- Google tarzı açılış ekranı → sohbet ekranı geçişi
- OpenAI uyumlu LLM'e proxy (`/v1/chat/completions`)
- Çok mesajlı sohbet bağlamı (conversation history) korunur
- Arayüzden model seçimi (dropdown)
- Bot yanıtları Markdown olarak gösterilir (kod blokları, tablolar vb.)
- Hata ve bağlantı kopması durumunda satır içi uyarı

## Teknoloji

| Katman | Araç |
|--------|------|
| Backend | FastAPI + Uvicorn, `httpx` (async HTTP), `python-dotenv` |
| Frontend | Vanilla HTML/CSS/JS, [marked.js](https://github.com/markedjs/marked) (CDN) |
| LLM | OpenAI uyumlu `/v1` sunucusu (llama.cpp / MLX tarzı) |

## Dosya Yapısı

```
opencode demo/
├── main.py              # FastAPI sunucusu + LLM proxy (/api/chat)
├── plan.md              # Türkçe tasarım dokümanı
├── requirements.txt     # Bağımlılıklar
├── .env                 # Yapılandırma (gizli — commit edilmez)
├── .gitignore
├── static/
│   └── index.html       # Tek sayfalık arayüz (home + chat)
└── tests/
    └── test_llm_connection.py  # LLM backend bağlantı testleri (pytest)
```

### `main.py`
- `.env` yüklenir (`load_dotenv`).
- Yapılandırma: `API_TOKEN`, `BASE_URL`, `MODEL`.
- Rotalar:
  - `GET /` → `static/index.html` servis eder.
  - `POST /api/chat` → `{ messages, model? }` alır, LLM'e iletir, `{ reply }` döner.
- LLM çağrısı: `POST {BASE_URL}/chat/completions`, `Authorization: Bearer {API_TOKEN}`,
  `temperature: 0.7`, `stream: False`.
- Hata kodları: boş mesaj → `400`, upstream hatası → `502`, beklenmeyen → `500`.

### `static/index.html`
- **Home:** Renkli "Murat Karakaya Akademi" logosu, yuvarlak arama kutusu, kredi satırı.
- **Chat:** Üst bar (marka + model seçici + "Ana ekrana dön"), mesaj listesi, girdi çubuğu.
- Akış: `history` dizisi tüm konuşmayı tutar; her gönderimde tüm geçmiş `/api/chat`'e
  yollanır, yanıt `marked.parse()` ile Markdown olarak basılır.

## Yapılandırma (`.env`)

`.env` dosyasında üç anahtar bulunur (gerçek değerler gizlidir, commit edilmez):

| Anahtar | Açıklama |
|---------|----------|
| `API_TOKEN` | LLM kimlik doğrulama bearer token'ı |
| `BASE_URL`  | LLM API taban URL'i (ör. `http://100.70.134.107:8001/v1`) |
| `MODEL`     | Varsayılan model adı |

> **Not:** `main.py` içindeki hardcoded fallback `"Ornith-1.0-9B-4bit plan"` ile
> `.env`/`plan.md`'teki `Ornith-1.0-9B-4bit` arasında küçük bir isim farkı vardır.
> Çalışma zamanında `.env` değeri önceliklidir. Arayüzden seçilebilen modeller:
> `gemma-4-12B-it-MLX-8bit`, `Qwen3.6-35B-A3B-MLX-8bit`, `gemma-4-26B-A4B-it-MLX-8bit`.

## Çalıştırma

```bash
# 1. Bağımlılıkları kur
pip install -r requirements.txt

# 2. .env dosyasını ayarla (API_TOKEN, BASE_URL, MODEL)
#    Gerçek token'ı commit etmeyin.

# 3. Sunucuyu başlat
uvicorn main:app --host 0.0.0.0 --port 2026

# 4. Tarayıcıda aç
#    http://localhost:2026
```

## Kullanım Akışı

1. Kullanıcı Google tarzı açılış ekranında sorusunu yazar ve gönderir.
2. Uygulama sohbet ekranına geçer ve ilk mesajı yollar.
3. Her yeni mesaj geçmişe eklenir; tüm geçmiş `/api/chat`'e gönderilir.
4. Sunucu LLM'den (`/v1/chat/completions`) yanıtı alır ve döndürür.
5. Arayüz yanıtı Markdown olarak sohbet balonunda gösterir; bağlam korunur.
6. Kullanıcı modeli dropdown'dan değiştirebilir veya "Ana ekrana dön" ile çıkabilir.

## Testler

```bash
pytest tests/test_llm_connection.py
```

LLM backend bağlantısını doğrular: ortam değişkenleri mevcut mu, `/models`
ve `/chat/completions` uçları beklenen yanıtları veriyor mu (geçersiz model → 404,
geçersiz token → 401).
