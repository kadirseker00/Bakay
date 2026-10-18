<div align="center">

<img src="docs/brand/bakay-logo-v3.png" alt="BAKAI logo" width="160" />

# BAKAI — KTMÜ Kurumsal Bilgi Asistanı

**Kırgızistan-Türkiye Manas Üniversitesi (KTMÜ) için RAG tabanlı, kaynak gösteren kurumsal bilgi asistanı**

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js%2015-frontend-000000?logo=nextdotjs&logoColor=white)
![LLM](https://img.shields.io/badge/LLM-Qwen3.5%209B-168A73)
![Status](https://img.shields.io/badge/durum-geli%C5%9Ftirme%20a%C5%9Famas%C4%B1-yellow)
![License](https://img.shields.io/badge/lisans-%C3%BCcretsiz%20(%C5%9Fimdilik)-brightgreen)

</div>

> Kırgızistan-Türkiye Manas Üniversitesi (KTMÜ) için RAG (Retrieval-Augmented
> Generation) tabanlı, kaynak gösteren ve doğrulanabilir kurumsal bilgi asistanı.

BAKAI; üniversitenin yönetmelik, yönerge, akademik takvim, burs/kayıt prosedürü
gibi resmi belgelerini anlamlandırır ve kullanıcının Türkçe sorularına **kaynağıyla
birlikte** yanıt verir.

Sürüm kökteki `VERSION` dosyasında `MAJOR.MINOR.PATCH` biçiminde tutulur;
API ve arayüz bu dosyadan okur. Sürüm artırılırken `frontend/package.json` ve
`frontend/package-lock.json` da eşitlenir; değişiklikler [CHANGELOG.md](CHANGELOG.md)
dosyasına eklenir. Arayüz yapılandırması sürümü başlangıç/derleme anında okuduğu
için sürüm değişikliğinden sonra servisler yeniden başlatılır veya yeniden derlenir.
Canlıya çıkan her yeni committe sürüm artırılır; varsayılan artış PATCH'tir.
Yeni numara mevcut canlı sürümden büyük olmalı; yayın sonunda API ve arayüzde
aynı sürümün göründüğü doğrulanmalıdır. Aynı commitin tekrar yayını sürüm artırmaz.

---

## Ürün adı ve BAP projesi

**BAKAI** ürün adı, Manas Destanı’ndaki bilge danışman **Bakay** karakterinden
esinlenir. BAP başvurusundaki ilk ad **BAKAY**, aynı zamanda
**Bütünleşik Akıllı Kurumsal Asistan Yazılımı** kısaltmasıdır. Yeni ürün yazımı,
projenin bu kültürel kökenini ve kurumsal bilgiye rehberlik etme amacını korur.

Uygulama, **Kırgızistan-Türkiye Manas Üniversitesi Bilimsel Araştırma Projeleri
(BAP)** kapsamında geliştirilmiştir.

- Proje numarası: **KTMU-BAP-2026.FB.05**
- Resmî proje adı: **BAKAY: RAG Destekli Kurumsal Bilgi Erişim ve Danışma Sistemi**
- Proje yürütücüsü ve web uygulamasının geliştiricisi: **Yrd. Doç. Dr. Abdulkadir Şeker**
- Birim: KTMÜ Mühendislik Fakültesi, Bilgisayar Mühendisliği Bölümü
- Kamuya açık açıklama: [BAKAI hakkında](https://bakai.manas.edu.kg/hakkinda)

İsim ve yürütücü bilgisi BAP başvuru formuna; proje numarası ilk gelişme raporuna
dayanır. Resmî başvuru/rapor adları tarihsel kayıt olarak korunur.

## Geliştirme stratejisi: "ince dilim"

İş paketlerini sırayla (önce TÜM veri, sonra TÜM model...) bitirmek yerine, önce
**uçtan uca çalışan küçük bir BAKAI** kuruyoruz: birkaç gerçek belgeyle soru-cevap
veren, kaynak gösteren bir demo. Sonra her katmanı tek tek güçlendiriyoruz. Hem
ürün hem de makale için gereken karşılaştırmalı deneyler aynı koddan çıkacak.

## İş paketleri (formdan)

| İP | İçerik | Durum |
|----|--------|-------|
| İP1 | Veri toplama, temizleme, paragraf segmentasyonu | 🟢 çalışıyor (statik) |
| İP2 | Embedding modeli seçimi & karşılaştırma | 🟡 iskelet |
| İP3 | Retrieval katmanı (FAISS / Chroma / ES hybrid) | 🟢 Chroma çalışıyor |
| İP4 | Generation (RAG) — LLM seçimi | 🟢 Qwen3.5 9B (yerel) |
| İP5 | API + web arayüzü + dağıtım | 🟢 FastAPI + Next.js sohbet |

## Başlangıç teknik kararları (değiştirilebilir, kod pluggable)

| Konu | Mevcut | Sonra (makale karşılaştırması) |
|------|--------|-------------------------------|
| LLM | **Qwen3.5 9B** (yerel, Ollama üzerinden) | Turkish-Gemma 9B, onaylı veriyle LoRA |
| Embedding | LaBSE / multilingual-e5 | BERTurk, XLM-R, Instructor |
| Vektör DB | ChromaDB | FAISS, Elasticsearch (BM25+hybrid) |
| Backend | FastAPI | — |
| Frontend | Next.js | — |

> **LLM notu:** Başlangıçta Gemini API planlanmıştı, ancak bölge erişim engeli
> nedeniyle kullanılamadı. Yerel varsayılan artık **Qwen3.5 9B**; Turkish-Gemma 9B
> karşılaştırma modeli olarak korunuyor. [30 soruluk pilot karşılaştırma](docs/evaluation/2026-09-07/report.md)
> model seçiminin gerekçesini ve sınırlılıklarını içerir; bu çalışma insan onaylı gold test değildir.
> `LLM_PROVIDER` ile sağlayıcı değiştirilebilir.

### Kaynak bağlı soru-cevap verisi

[İlk 50 soruluk uzman inceleme paketi](docs/evaluation/gold-v1/review-packet.md) hazırdır.
Tamamı insan onayı bekleyen taslaktır; gold test veya LoRA eğitim verisi değildir.
[Protokol](docs/evaluation/gold-v1/README.md), kaynak hash'leri, JSON Schema ve doğrulama araçları
`data/eval/v1/` ile `backend/evaluation/dataset.py` içinde sürümlenir.
İki güncel insan onayı olmadan gold/LoRA dışa aktarımı engellenir.

[DomainRAG yönteminin Türkçe KTMÜ uyarlaması](docs/evaluation/domainrag-tr-v1/README.md)
106 geliştirme senaryosu ve 21 kaynak bölümünü mevcut ölçüm araçlarına bağlar.
Konuşma takibi, yapılandırılmış bilgi, kaynak sadakati, yanıltıcı bağlam,
güncellik ve çoklu belge senaryoları içerir. Çince kurum verisi bilgi deposuna
aktarılmaz; bu paket gold veya model eğitimi değildir.

---

## Kurulum

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp ../.env.example ../.env
```

LLM için yerel **Qwen3.5 9B** modelini Ollama ile çalıştırın
(GPU önerilir):

```bash
# Ollama kurulu değilse: https://ollama.com/download
ollama pull qwen3.5:9b

# .env içinde:
#   LLM_PROVIDER=ollama
#   OLLAMA_MODEL=qwen3.5:9b
```

## Kullanım (uçtan uca demo)

Claude Sonnet API seçeneği için proje kökündeki `.env` dosyasına
`ANTHROPIC_API_KEY` ekleyin ve `LLM_PROVIDER=anthropic` ayarlayın.
Model `ANTHROPIC_MODEL=claude-sonnet-5-5` ile seçilir; sağlayıcı değiştikten
sonra backend yeniden başlatılır. Sabit kaynaklı karşılaştırma, sağlayıcıyı
değiştirmeden [Sonnet pilot komutlarıyla](docs/evaluation/2026-10-09-sonnet/README.md)
çalıştırılabilir. API anahtarı backend'de kalır; frontend'e aktarılmaz.

```bash
# 1) Belgeleri topla: KTMÜ sitesini tara (HTML + PDF -> data/raw/web/)
#    veya elindeki dosyaları data/raw/ içine elle koy.
python -m app.ingest.crawl --seed https://www.manas.edu.kg --max-pages 100

# 2) İndeksle (temizle → parçala → embed → Chroma'ya yaz)
python -m app.ingest.run

# 3) API'yi başlat
uvicorn app.main:app --reload

# 4) Soru sor
curl -X POST localhost:8000/chat -H "content-type: application/json" \
  -d '{"question": "Bütünleme sınavına kimler girebilir?"}'
```

## Web arayüzü (frontend)

KTMÜ sunucusu için [aktarım ve kurulum rehberi](docs/deployment/ktmu.md)
ile `deploy/` altında Apache, systemd ve backend ortam örnekleri bulunur.
Sunucuda frontend `NEXT_PUBLIC_API_URL=/api` ile derlenir.

```bash
cd frontend
npm install
npm run dev        # http://localhost:3000
```

Backend (`localhost:8000`) çalışırken arayüzü tarayıcıda açın. Arayüz, her yanıtın
altında dayandığı **kaynak belgeleri** ve benzerlik skorunu gösterir.

## Ajansal akış (agentic flow)

BAKAI basit `retrieve→generate` yerine modüler ajansal bir akış kullanır
(`docs/reference/` altındaki referans desenden uyarlandı):

```
Soru → [0] Yönlendirme → [1] Sorgu yeniden yazma → [2] Retrieval
     → [3] Yeterlilik kapısı → [4] Grounded üretim → [5] Dayanak doğrulama → Yanıt
```

Düğümler `.env` ile açılır/kapanır. **Skor kapısı bedavadır** (ekstra LLM yok);
**LLM-ağırlıklı düğümler latency ekler**, bu yüzden varsayılan kapalıdır:

| Düğüm | .env değişkeni | Varsayılan | Maliyet |
|-------|----------------|-----------|---------|
| Kapsam yönlendirme | `AGENT_ROUTE` | kapalı | 1 LLM çağrısı |
| Sorgu yeniden yazma | `AGENT_REWRITE` | kapalı | 1 LLM çağrısı |
| Yeterlilik kapısı | `SCORE_THRESHOLD` | 0.30 | bedava |
| Dayanak doğrulama | `AGENT_VERIFY` | kapalı | 1 LLM çağrısı |

> Not: Mutlak kosinüs skoruyla kapsam ayrımı LaBSE'de güvenilmezdir (alakasız soru
> meşru sorudan yüksek skor alabilir). Güvenilir yönlendirme için `AGENT_ROUTE`
> (LLM) kullanın; embedding karşılaştırması İP2'de bu sorunu ele alır.

## Dizin yapısı

```
backend/app/
  config.py          # tüm ayarlar (.env'den)
  main.py            # FastAPI uygulaması
  schemas.py         # istek/yanıt modelleri
  rag/
    embeddings.py    # pluggable embedding sağlayıcı
    vectorstore.py   # ChromaDB sarmalayıcı
    llm.py           # pluggable LLM (Claude / Gemini / yerel Ollama)
    pipeline.py      # RAG orkestrasyonu (retrieve → prompt → generate)
  ingest/
    crawl.py         # KTMÜ web/PDF toplayıcı (nazik, robots'a uyan tarayıcı)
    loaders.py       # PDF / HTML / metin yükleyiciler
    clean.py         # Türkçe temizleme & normalize (NFC)
    chunk.py         # paragraf bazlı parçalama
    run.py           # indeksleme komut satırı aracı
data/
  raw/ processed/ chroma/
```

---

## Lisans

BAKAI şu an **ücretsiz** olarak geliştiriliyor ve KTMÜ kapsamındaki akademik/araştırma
kullanımına açıktır. İleriki sürümlerde ürünleşme durumunda **ücretli bir lisansa**
geçilebilir. Kullanım koşulları netleştikçe burası güncellenecektir; ticari kullanım
için lütfen proje sahibiyle iletişime geçin.

© 2026 BAKAI — Abdulkadir Şeker, KTMÜ Bilgisayar Mühendisliği.
