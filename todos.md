# İyileştirme Yol Haritası — Murat Karakaya Akademi Sohbet Botu

3 sub-agent (UI, Security, Functionality) analizine dayalı öncelikli görev listesi.
Efor: Düşük / Orta / Yüksek

---

## Aşama 1 — Kritik Güvenlik (Hemen)
- [ ] **SEC-1** `/api/chat` uç noktasına kimlik doğrulama ekle (basit API key / basic auth) — token'ın ücretsiz proxy olarak kötüye kullanılmasını engeller. (Efor: Düşük-Orta)
- [ ] **SEC-2** Sunucuda model allow-list (beyaz liste) sabitle; istemci `model` gönderse bile yalnızca izin verilenlerden birine izin ver, aksi halde 400. (Efor: Düşük)
- [ ] **SEC-3** Sunucuyu `0.0.0.0` yerine `127.0.0.1`'e bağla (veya Nginx/Caddy arkasına al + TLS + auth). (Efor: Düşük)
- [ ] **SEC-4** Token'ı güçlü rastgele bir değere çevir; boşsa uygulama başlangıcında fail-fast ile dursun. (Efor: Düşük)

## Aşama 2 — Düşük Eforlu Kazanımlar (Hızlı)
### UI
- [ ] **UI-1** Hata balonlarına ayrı `.msg.error` stili; `catch` bloğunda `e.message` kullan. (Efor: Düşük)
- [ ] **UI-2** Animasyonlu "yazıyor" göstergesi (üç nokta CSS animasyonu). (Efor: Düşük)
- [ ] **UI-3** Mobil responsive tasarım (`@media (max-width:600px)`: logo küçült, balon %85, topbar dikey). (Efor: Düşük)
- [ ] **UI-5** Mesaj zaman damgası (HH:MM) ekle. (Efor: Düşük)
- [ ] **UI-6** "Sohbeti temizle" butonu (`history=[]`, mesajları sil). (Efor: Düşük)
### Security
- [ ] **SEC-5** Hata mesajlarını genelleştir; iç detayı (upstream IP/port) yalnızca log'a yaz. (Efor: Düşük)
- [ ] **SEC-6** Girdi doğrulama: `content` max_length, `messages` max_items, `role` Literal kısıtı (Pydantic). (Efor: Düşük)
- [ ] **SEC-7** Timeout'u ayır: connect=5s, read=30-60s. (Efor: Düşük)
### Functionality
- [ ] **FUNC-4** "Sohbeti temizle" butonu (UI-6 ile birlikte). (Efor: Düşük)
- [ ] **FUNC-6** Mesaj/token limiti + Pydantic doğrulama (SEC-6 ile birlikte). (Efor: Düşük)
- [ ] **FUNC-9** Başlangıçta config doğrulaması (BASE_URL/MODEL varlığı). (Efor: Düşük)
- [ ] **FUNC-10** `/health` endpoint'i ekle. (Efor: Düşük)
- [ ] **FUNC-11** Yapılandırılmış loglama (model, durum, süre; hassas içerik loglanmasın). (Efor: Düşük)
- [ ] **FUNC-12** Graceful timeout yönetimi (connect/read ayrımı, dostça mesaj). (Efor: Düşük)
- [ ] **FUNC-13** Sohbeti dışa aktarma (Markdown/JSON indirme). (Efor: Düşük)

## Aşama 3 — Orta Efor
### UI
- [ ] **UI-4** Kod bloklarına "Kopyala" butonu (clipboard API). (Efor: Düşük-Orta)
- [ ] **UI-7** Akıllı scroll (yalnızca en alttaysa otomatik kaydır, değilse "yeni mesaj" oku). (Efor: Orta)
- [ ] **UI-8** Dark mode (`prefers-color-scheme` + CSS değişkenleri). (Efor: Orta)
- [ ] **UI-9** Erişilebilirlik (`aria-live`, `aria-label`, görünür focus). (Efor: Orta)
- [ ] **UI-10** İstek sürerken input'u da disable et (race önleme). (Efor: Düşük)
- [ ] **UI-11** Markdown sanitization (DOMPurify). (Efor: Düşük-Orta)
- [ ] **UI-12** Model değişiminde geri bildirim balonu. (Efor: Düşük)
### Security
- [ ] **SEC-8** Prompt injection koruması: sabit system prompt ekle. (Efor: Orta)
- [ ] **SEC-9** Rate limiting (IP başına dakikada N istek, slowapi/Nginx). (Efor: Orta)
- [ ] **SEC-10** CORS'u yalnızca bilinen frontend origin ile sınırla; asla `*`+credentials. (Efor: Düşük)
### Functionality
- [ ] **FUNC-2** İstek iptali / AbortController ("Durdur" toggle butonu). (Efor: Orta)
- [ ] **FUNC-3** Geçici hatalarda retry (exponential backoff, 429 için Retry-After). (Efor: Orta)
- [ ] **FUNC-7** Daha iyi hata + kısmi yanıt yönetimi (boş content, upstream error.message). (Efor: Düşük)
- [ ] **FUNC-8** Sistem promptu desteği (backend `system_prompt` parametresi). (Efor: Orta)
- [ ] **FUNC-15** Test kapsamı: `/api/chat` birim testleri (TestClient), `pytest` bağımlılığa ekle. (Efor: Orta)

## Aşama 4 — Yüksek Efor
- [ ] **FUNC-1** Streaming (SSE token-token yanıt); backend `stream:True`, frontend `ReadableStream` ile inline render. (Efor: Yüksek)
  - Not: Streaming, FUNC-2 (iptal), FUNC-3 (retry), FUNC-12 (timeout) maddelerinin çoğunu doğal olarak çözer.

## Bakım
- [ ] **SEC-11** Bağımlılıkları `paket==x.y.z` ile sabitle; `pip-audit`/`safety` ile periyodik tarama. (Efor: Düşük)
