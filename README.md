# BAKAY — Bütünleşik Akıllı Kurumsal Asistan Yazılımı

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
| İP4 | Generation (RAG) — LLM seçimi | 🟢 yerel Türkçe Gemma 9B |
| İP5 | API + web arayüzü + dağıtım | 🟢 FastAPI + Next.js sohbet |

## Başlangıç teknik kararları (değiştirilebilir, kod pluggable)

| Konu | Başlangıç | Sonra (makale karşılaştırması) |
|------|-----------|-------------------------------|
| LLM | Gemini API | Mistral 7B, Llama-3, Qwen2 (yerel) |
| Embedding | LaBSE / multilingual-e5 | BERTurk, XLM-R, Instructor |
| Vektör DB | ChromaDB | FAISS, Elasticsearch (BM25+hybrid) |
| Backend | FastAPI | — |
| Frontend | Next.js | — |

---

## Kurulum

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp ../.env.example ../.env   # ve GEMINI_API_KEY değerini gir
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
