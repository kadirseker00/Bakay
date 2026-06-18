<div align="center">

<img src="docs/brand/bakay-logo-v3.png" alt="BAKAY logo" width="160" />

# BAKAY — Bütünleşik Akıllı Kurumsal Asistan Yazılımı

**Kırgızistan-Türkiye Manas Üniversitesi (KTMÜ) için RAG tabanlı, kaynak gösteren kurumsal bilgi asistanı**

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-frontend-000000?logo=nextdotjs&logoColor=white)
![LLM](https://img.shields.io/badge/LLM-YT%C3%9C%20COSMOS%20Turkish--Gemma%209B-5A4FCF)
![Status](https://img.shields.io/badge/durum-geli%C5%9Ftirme%20a%C5%9Famas%C4%B1-yellow)
![License](https://img.shields.io/badge/lisans-%C3%BCcretsiz%20(%C5%9Fimdilik)-brightgreen)

</div>

> Kırgızistan-Türkiye Manas Üniversitesi (KTMÜ) için RAG (Retrieval-Augmented
> Generation) tabanlı, kaynak gösteren ve doğrulanabilir kurumsal bilgi asistanı.

BAKAY; üniversitenin yönetmelik, yönerge, akademik takvim, burs/kayıt prosedürü
gibi resmi belgelerini anlamlandırır ve kullanıcının Türkçe sorularına **kaynağıyla
birlikte** yanıt verir.

---

## Geliştirme stratejisi: "ince dilim"

İş paketlerini sırayla (önce TÜM veri, sonra TÜM model...) bitirmek yerine, önce
**uçtan uca çalışan küçük bir BAKAY** kuruyoruz: birkaç gerçek belgeyle soru-cevap
veren, kaynak gösteren bir demo. Sonra her katmanı tek tek güçlendiriyoruz. Hem
ürün hem de makale için gereken karşılaştırmalı deneyler aynı koddan çıkacak.

## İş paketleri (formdan)

| İP | İçerik | Durum |
|----|--------|-------|
| İP1 | Veri toplama, temizleme, paragraf segmentasyonu | 🟢 çalışıyor (statik) |
| İP2 | Embedding modeli seçimi & karşılaştırma | 🟡 iskelet |
| İP3 | Retrieval katmanı (FAISS / Chroma / ES hybrid) | 🟢 Chroma çalışıyor |
| İP4 | Generation (RAG) — LLM seçimi | 🟢 YTÜ COSMOS Turkish-Gemma 9B (yerel) |
| İP5 | API + web arayüzü + dağıtım | 🟢 FastAPI + Next.js sohbet |

## Başlangıç teknik kararları (değiştirilebilir, kod pluggable)

| Konu | Mevcut | Sonra (makale karşılaştırması) |
|------|--------|-------------------------------|
| LLM | **YTÜ COSMOS Turkish-Gemma 9B** (yerel, Ollama üzerinden) | Mistral 7B, Llama-3, Qwen2 (yerel) |
| Embedding | LaBSE / multilingual-e5 | BERTurk, XLM-R, Instructor |
| Vektör DB | ChromaDB | FAISS, Elasticsearch (BM25+hybrid) |
| Backend | FastAPI | — |
| Frontend | Next.js | — |

> **LLM notu:** Başlangıçta Gemini API planlanmıştı, ancak bölge erişim engeli
> nedeniyle kullanılamadı. Bunun yerine [YTÜ COSMOS](https://huggingface.co/ytu-ce-cosmos)
> ekibinin Türkçe için ince ayarlı **Turkish-Gemma-9B** modeli yerelde
> (Ollama, GPU) çalıştırılıyor. Kod pluggable: `LLM_PROVIDER` ile sağlayıcı
> değiştirilebilir.

---

## Kurulum

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp ../.env.example ../.env
```

LLM için yerel **YTÜ COSMOS Turkish-Gemma 9B** modelini Ollama ile çalıştırın
(GPU önerilir):

```bash
# Ollama kurulu değilse: https://ollama.com/download
# Modeli Ollama'ya ekleyin (HF: ytu-ce-cosmos/Turkish-Gemma-9b).
# Örn. bir Modelfile ile yerel etiket oluşturup:
ollama create turkish-gemma-9b -f Modelfile

# .env içinde:
#   LLM_PROVIDER=ollama
#   OLLAMA_MODEL=turkish-gemma-9b   # Ollama'da kullandığınız etiket
```

## Kullanım (uçtan uca demo)

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

```bash
cd frontend
npm install
npm run dev        # http://localhost:3000
```

Backend (`localhost:8000`) çalışırken arayüzü tarayıcıda açın. Arayüz, her yanıtın
altında dayandığı **kaynak belgeleri** ve benzerlik skorunu gösterir.

## Ajansal akış (agentic flow)

BAKAY basit `retrieve→generate` yerine modüler ajansal bir akış kullanır
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
    llm.py           # pluggable LLM (Gemini / yerel Ollama)
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

BAKAY şu an **ücretsiz** olarak geliştiriliyor ve KTMÜ kapsamındaki akademik/araştırma
kullanımına açıktır. İleriki sürümlerde ürünleşme durumunda **ücretli bir lisansa**
geçilebilir. Kullanım koşulları netleştikçe burası güncellenecektir; ticari kullanım
için lütfen proje sahibiyle iletişime geçin.

© 2026 BAKAY — Abdulkadir Şeker, KTMÜ Bilgisayar Mühendisliği.
