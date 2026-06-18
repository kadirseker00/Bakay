# BAKAY — Yapılacaklar ve Araştırma Yol Haritası

> Bu belge, BAKAY projesinin **kalan işlerini** akademik (BAP projesi + Scopus
> indeksli yayın) bakış açısıyla düzenler. Mevcut durum: İP1–İP5'in tamamının
> uçtan uca çalışan ilk sürümü hazırdır ("ince dilim" yaklaşımı). Bundan sonraki
> aşama, her katmanı **ölçülebilir biçimde güçlendirmek** ve sonuçları
> karşılaştırmalı deneylere dönüştürmektir.

**Proje:** KTMÜ BAP, GAP-A, 01/01/2026 – 31/12/2026 (12 ay)
**Yürütücü:** Yrd. Doç. Dr. Abdulkadir Şeker (KTMÜ, Bilgisayar Mühendisliği)
**Son güncelleme:** 2026-06-18

---

## 1. Genel durum özeti

| İP | İçerik | Mevcut durum | Kalan iş (özet) |
|----|--------|--------------|-----------------|
| İP1 | Veri toplama / temizleme / segmentasyon | 🟢 statik çalışıyor | Kapsamı genişlet, periyodik tarama, PII denetimi |
| İP2 | Embedding modeli seçimi & karşılaştırma | 🟡 iskelet | Karşılaştırmalı deney (LaBSE/e5/BERTurk/XLM-R) |
| İP3 | Retrieval katmanı | 🟢 Chroma çalışıyor | FAISS/ES hibrit (BM25+dense), yeniden sıralama |
| İP4 | Generation (LLM) | 🟢 Turkish-Gemma 9B | Düşük gecikmeli instruct model, çoklu LLM karşılaştırması |
| İP5 | API + arayüz + dağıtım | 🟢 FastAPI + Next.js | Dağıtım, kimlik/erişim, gözlemlenebilirlik |
| **İP6** | **Çok-dillilik (Kırgızca / Rusça)** | 🔴 yok | Kırgızca belge + soru-cevap + değerlendirme |
| — | **Bilimsel çıktı (görev #6)** | 🟡 telemetri hazır | Değerlendirme seti + metrikler + makale |

Öncelik sırası: **(A) Değerlendirme altyapısı → (B) İP4 gecikme sorunu →
(C) İP2/İP3 karşılaştırmaları → (D) Kırgızca dil desteği → (E) makale.**
Değerlendirme altyapısı önce gelmeli; çünkü diğer tüm iyileştirmelerin "daha iyi"
olduğunu ancak ölçerek iddia edebiliriz.

---

## 2. Bilimsel çıktı: değerlendirme protokolü (öncelik #1)

Makalenin gövdesi burası. Hedef: BAKAY'ın tasarım kararlarını (embedding, vektör
DB, LLM, ajansal düğümler) **tekrarlanabilir** bir protokolle karşılaştırmak.

### 2.1 Değerlendirme veri seti
- [ ] KTMÜ belgelerinden **altın soru-cevap seti** oluştur (≈100–200 soru).
  - Her madde: `soru`, `beklenen_yanıt`, `dayanak_belge`, `dayanak_paragraf`,
    `kategori` (yönetmelik/takvim/burs/kayıt…), `kapsam_içi mi?`, `dil` (TR/KY/RU).
  - **Kapsam-dışı** (alakasız) sorular ekle — yönlendirme/abstain ölçümü için.
- [ ] Soru üretimini iki kaynaktan dengele: (a) gerçek/temsilî öğrenci soruları,
  (b) belgelerden türetilmiş. Tek kaynağa bağımlılık yanlılık yaratır.
- [ ] Seti `data/eval/` altında sürümle (CSV/JSONL); ek bağımsız değerlendirici
  ile **anlaşma (inter-annotator agreement)** notu düş.

### 2.2 Metrikler
- [ ] **Retrieval:** Recall@5, MRR@10, nDCG@10, Hit@k.
- [ ] **Generation:** dayanak doğruluğu (faithfulness/groundedness), yanıt
  doğruluğu (exact/semantik), **halüsinasyon oranı**, abstain isabeti.
- [ ] **Sistem:** uçtan uca gecikme (p50/p95), düğüm başına gecikme,
  token/saniye, bellek. → Form hedefi **<10 sn**; raporla.
- [ ] **Dil kırılımı:** tüm metrikleri TR ve KY için ayrı raporla (Bölüm 9).
- [ ] Mümkünse otomatik + insan değerlendirmesini birlikte raporla
  (LLM-as-judge'ı insan örneğiyle kalibre et).

### 2.3 Deney koşum altyapısı
- [ ] `app/eval/` modülü: veri setini oku → her konfigürasyonu koştur →
  metrikleri hesapla → tablo/şekil üret.
- [ ] Her koşumu telemetri (`app/telemetry.py`, JSONL+SQLite) ile eşleştir;
  konfigürasyon (embedding, top-k, LLM, ajansal düğümler, dil) kayda geçsin.
- [ ] Sonuçları yeniden üretilebilir kıl: sabit tohum, sürümlenmiş veri,
  konfigürasyon dosyası → `docs/experiments/` altında rapor.

---

## 3. İP4 — Generation: gecikme sorunu (öncelik #2)

> **Bilinen kısıt:** Mevcut tek yerel model `Turkish-Gemma-9b-T1` bir *reasoning*
> modelidir; her yanıttan önce `<think>` bloğu üretir, yanıt süresi ~15–24 sn.
> `think=false` ve prompt talimatıyla susturulamadı. Form hedefi <10 sn.

- [ ] **Akıl yürütmeyen (instruct) yerel model** ekle ve ölç: Mistral 7B,
  Llama-3 8B, Qwen2 7B (Ollama). Gecikme/kalite dengesini karşılaştır.
- [ ] LLM sağlayıcı katmanını (`app/rag/llm.py`) çoklu-model karşılaştırması
  için parametrik tut; `LLM_PROVIDER`/`OLLAMA_MODEL` zaten pluggable.
- [ ] **Gemini kısıtını belgele:** Bişkek'ten `403 PERMISSION_DENIED` (Kırgızistan
  ücretsiz katman dışı). Kod duruyor ama erişilemiyor → makalede "yerel-öncelikli
  mimari" gerekçesi olarak yaz.
- [ ] Streaming yanıt (token token) ile algılanan gecikmeyi düşür.
- [ ] Yerel GPU/donanım profilini netleştir ve raporla (şu an Mac/Metal,
  ~29 tok/s @ 9B Q4). Dağıtım hedef donanımını belirle.

---

## 4. İP2 — Embedding karşılaştırması (öncelik #3)

> **Bilinen kısıt:** LaBSE kosinüs skorları kapsam-içi/dışı ayrımında güvenilmez
> (alakasız "hava durumu" 0.39 > meşru "yatay geçiş" 0.36). Skor-kapısı tek başına
> zayıf.

- [ ] Karşılaştırılacak modeller: **LaBSE, multilingual-e5, BERTurk, XLM-R**
  (+ değerlendirilebilirse Instructor / Türkçe-özel modeller).
- [ ] Her model için Bölüm 2.2 retrieval metriklerini hesapla; Türkçe morfoloji
  ve kapsam-dışı ayrımındaki davranışı ayrıca raporla.
- [ ] **Kırgızca/Rusça dil kapsamı:** aday embedding modellerinin KY/RU desteğini
  ölç (LaBSE ve XLM-R bu dilleri kapsar; BERTurk kapsamaz) → İP6 ile bağlantılı.
- [ ] Embedding değişiminin **skor-kapısı eşiğine** etkisini ölç → daha iyi
  embedding, LLM-yönlendirmeye (`AGENT_ROUTE`) olan ihtiyacı azaltıyor mu?

---

## 5. İP3 — Retrieval katmanı

- [ ] **Hibrit retrieval:** BM25 (sözlük) + dense (embedding) birleşimi;
  Elasticsearch veya hafif BM25 + ChromaDB.
- [ ] Vektör DB karşılaştırması: ChromaDB vs FAISS (hız/bellek/ölçek).
- [ ] **Yeniden sıralama (re-ranking):** cross-encoder ile ilk-k'yı yeniden sırala;
  Recall ve dayanak doğruluğuna etkisini ölç.
- [ ] `top_k`, chunk boyutu/örtüşmesi gibi hiperparametreleri değerlendirme
  setinde tara (ablation).

---

## 6. İP1 — Veri katmanı

- [ ] Belge kapsamını genişlet: tüm güncel yönetmelik/yönerge/takvim/prosedürler.
- [ ] **Periyodik tarama:** akademik takvim gibi değişen belgeler için yeniden
  indeksleme (zamanlanmış crawl + fark tespiti).
- [ ] **PII denetimini sürdür:** burs PDF'leri öğrenci isim listesi → indeks dışı.
  `--exclude` filtresini belge ekledikçe gözden geçir.
- [ ] Türkçe temizleme/normalize (NFC) ve paragraf segmentasyonunun kenar
  durumlarını (tablolar, çok sütunlu PDF, dipnot) iyileştir.
- [ ] Belge sürümleme/tarih meta verisi → "şu tarihte geçerli" yanıtlar.

---

## 7. İP5 — API, arayüz, dağıtım

- [ ] **Dağıtım:** KTMÜ erişilebilir bir ortama kur (yerel sunucu/GPU); reverse
  proxy, HTTPS, ortam ayrımı (geliştirme/üretim).
- [ ] Kimlik doğrulama / erişim denetimi (kurumsal kullanım için).
- [ ] Gözlemlenebilirlik: telemetri panosu (gecikme, skor, kapsam-dışı oranı,
  geri bildirim).
- [ ] Arayüz: kaynak/skor gösterimi (mevcut) üzerine geri bildirim toplama
  (👍/👎), yanıt akışı (streaming), erişilebilirlik.
- [ ] **Arayüz dil seçimi (TR/KY/RU):** yanıt ve arayüz dilini kullanıcı seçebilsin
  → İP6 ile bağlantılı.
- [ ] Ajansal düğümlerin (`AGENT_ROUTE/REWRITE/VERIFY`) maliyet-fayda dengesini
  değerlendirme setinde ölçüp varsayılanları gözden geçir.

---

## 8. İP6 — Çok-dillilik: Kırgızca (ve Rusça)

> **Gerekçe:** KTMÜ iki dilli (Türkçe + **Kırgızca**) bir üniversitedir; birçok
> resmî belge ve öğrenci sorusu Kırgızca (kimi zaman Rusça) olabilir. Mevcut BAKAY
> uçtan uca **yalnızca Türkçe** kuruludur: LaBSE çok-dilli olsa da prompt'lar,
> temizleme/normalize, değerlendirme seti ve LLM (Turkish-Gemma) hep TR odaklıdır.
> Bu yüzden Kırgızca, ayrı ve ölçülebilir bir iş paketi olarak ele alınır.

### 8.1 Veri (İP1 ile)
- [ ] KTMÜ'nün **Kırgızca belgelerini** topla ve etiketle (`dil=ky`); Türkçe/Kırgızca
  eş belge çiftleri varsa eşleştir (paralel değerlendirme imkânı).
- [ ] Temizleme/normalize'i Kırgız Kiril alfabesi için doğrula (Cyrillic Unicode,
  KY'ye özgü harfler **ң, ү, ө**; NFC); gerekirse Rusça için de.

### 8.2 Retrieval & embedding (İP2/İP3 ile)
- [ ] Aday embedding modellerinin **Kırgızca** başarımını değerlendirme setinde ölç
  (LaBSE/XLM-R/e5 KY'yi kapsar; BERTurk kapsamaz — karşılaştırmada belirt).
- [ ] **Diller-arası retrieval:** Kırgızca soru → Türkçe belge (ve tersi) erişimini
  ölç; kurumsal belgeler tek dilde olabileceğinden bu pratikte önemli.

### 8.3 Generation (İP4 ile)
- [ ] Kırgızca üretim için LLM seçeneklerini değerlendir (Turkish-Gemma Kırgızca'da
  zayıf olabilir; çok-dilli Llama-3/Qwen2 alternatiflerini ölç).
- [ ] **Dil tutarlılığı:** yanıt, sorunun dilinde olmalı (soru KY → yanıt KY);
  prompt ve değerlendirmeye dil-tutarlılığı kontrolü ekle.

### 8.4 Değerlendirme (Bölüm 2 ile)
- [ ] Değerlendirme setine **Kırgızca soru-cevap** alt kümesi ekle (`dil=ky`).
- [ ] Tüm metrikleri **TR vs KY kırılımıyla** raporla → makalede "çok-dilli,
  düşük-kaynaklı kurumsal RAG" katkısı olarak öne çık.

### 8.5 Arayüz (İP5 ile)
- [ ] Arayüzde dil seçimi ve dile göre yer/biçim (tarih, sayı) yerelleştirmesi.

---

## 9. Yayın / dokümantasyon

- [ ] **Makale taslağı (Scopus indeksli dergi):** sistem mimarisi + karşılaştırmalı
  deneyler (embedding × retrieval × LLM × ajansal düğümler × **dil**).
  - Anlatı: düşük kaynaklı, çok kısıtlı (bölge erişim engeli, yerel donanım) bir
    ortamda **kaynak gösteren, doğrulanabilir, çok-dilli (TR/KY)** kurumsal RAG.
- [ ] Sonuç tabloları/şekilleri `app/eval/` çıktısından otomatik üret →
  yeniden üretilebilirlik.
- [ ] Etik/PII ve veri kullanım notu (kurumsal belgeler, öğrenci verisi dışlama).
- [ ] BAP ara/sonuç raporuyla iş paketi durumlarını hizala.

---

## 10. Sürdürülen kısıtlar (karar günlüğü)

Bu kararlar koddan görünmez; deney tasarımını ve makale gerekçesini doğrudan
etkilediği için burada izlenir:

1. **Gemini bölge engeli** → yerel Ollama; mimari pluggable, Gemini kodu rezervde.
2. **Reasoning modeli gecikmesi** (T1, `<think>`, ~15–24 sn) → instruct modele geçiş İP4'te.
3. **LaBSE skor-kapısı güvenilmez** → İP2 embedding karşılaştırması + `AGENT_ROUTE`.
4. **PII** → burs/öğrenci listesi belgeleri indeks dışı.
5. **Donanım profili** netleştirilecek (yerel GPU vs Mac/Metal) — dağıtım kararını belirler.
6. **Tek-dilli (TR) kuruluş** → Kırgızca/Rusça İP6'da ele alınacak (iki dilli üniversite).
