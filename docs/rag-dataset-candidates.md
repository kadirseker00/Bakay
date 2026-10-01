# BAKAY için üniversite RAG veri kümesi ve bilgi grafiği adayları

İnceleme tarihi: 2026-10-01. Kaynak sayfalarına ek olarak indirilebilir dosya listeleri ve örnek kayıtların şemaları kontrol edildi. Bu araştırmada KTMÜ kurallarını içeren hazır, eğitilmiş bir üniversite asistanı bulunmadı. Aşağıdaki kaynaklar farklı amaçlara hizmet ediyor: eğitim örnekleri, değerlendirme verisi, belge külliyatı veya mimari örnek.

## Öncelikli adaylar

| Kaynak | Gerçekte sunulan içerik | BAKAY için kullanım | Sınır / yayımlanan lisans bilgisi |
|---|---|---|---|
| [DomainRAG](https://arxiv.org/abs/2406.05654) / [işlenmiş dosyalar](https://huggingface.co/datasets/RUC-NLPIR/FlashRAG_datasets/tree/main/domainrag) | Çin'deki üniversite kabulüne ilişkin Çince sorular, cevaplar, geçmiş ve kaynak referansları; HTML/metin külliyatı | Üniversite RAG değerlendirmesinin tasarımı için en yakın aday | FlashRAG sürümü 485 test örneği; eğitim bölümü yok. Birleştirilmiş veri kartında CC-BY-SA-4.0 yazıyor; özgün kaynağın koşulları ayrıca korunmalı |
| [WikiRAG-TR](https://huggingface.co/datasets/Metin/WikiRAG-TR) | Türkçe Wikipedia temelli 5.999 kayıt: 5.725 sentetik soru-cevap, 274 olumsuz örnek; karışık bağlamlar içinde hedef metin işaretleniyor | Kaynağa bağlı cevap ve kaynakta cevap yokken bunu söyleme davranışı için eğitim adayı | Üniversite yönetmeliklerini öğretmez. Kartta Apache-2.0; sentetik cevaplar gözden geçirilmeli |
| [KG-RAGdataset](https://github.com/KREML0/KG-RAGdataset) | Bilgisayar organizasyonu, ağlar ve işletim sistemleri ders kitapları; GraphML grafikler, varlık/ilişki depoları ve Çince soru-cevap dosyaları | Hazır bilgi grafiği dosya biçimini ve graph + QA eşleşmesini inceleme | İdari mevzuat yerine ders içeriği. Depoda açık lisans dosyası ve GitHub API'de lisans tespit edilmedi |
| [HCMUT üniversite bilgi grafiği çalışması](https://arxiv.org/abs/2404.09296) | Gerçek üniversitede yönetmelik, SSS, web, LMS ve API verilerini birleştiren KG/QA mimarisi | KTMÜ için kurum, işlem, ders ve mevzuat ilişkilerini modelleme örneği | Vietnamca kurum örneği; araştırmada kamuya açık indirilebilir grafik/QA sürümü doğrulanamadı |

### DomainRAG dosya kontrolü

[FlashRAG](https://github.com/RUC-NLPIR/FlashRAG) üniversite kabul alanını ve test örneği sayısını belgeliyor. `domainrag/test.jsonl` ilk kaydında `question`, `golden_answers`, `metadata` alanları mevcut; metadata içinde `task`, `query`, `history`, `positive_reference` bulunuyor. Aynı yayında `retrieval-corpus/domainrag_html_corpus.jsonl` ve `domainrag_text_corpus.jsonl` dosyaları var. [Özgün proje](https://github.com/ShootingWong/DomainRAG) ayrıca külliyat bağlantılarını sunuyor.

Makale konuşma geçmişi, yapılandırılmış bilgi, kaynağa sadakat, ilgisiz bağlam, zamana bağlı bilgiler ve birden çok belgeyle çalışma yeteneklerini değerlendiriyor. Bunlar BAKAY'ın kapsam ve eski/yeni yönetmelik sorunlarına uygun değerlendirme eksenleri. Çin üniversitesinin cevapları KTMÜ'nün doğrusu olarak indekslenmemeli. Test bölümü eğitimde kullanılmamalı.

Kontrol edilen Hugging Face revizyonu: `bcafb8dd07d453be3cbeeeb3f78be1841bddf92c`.

### WikiRAG-TR dosya kontrolü

Gerçek kayıt şeması: `id`, `question`, `answer`, `context`, `is_negative_response`, `number_of_articles`, `ctx_split_points`, `correct_intro_idx`. `data/train.csv` ve veri görüntüleyicisinin örnek satırları erişilebilir. Tek bir train bölümü yayımlanmış; BAKAY deneyinde konu ve belge bazında ayrılmış eğitim/doğrulama/test grupları oluşturulmalı. Aynı Wikipedia maddesinin farklı sorularını farklı gruplara dağıtmak sızıntı doğurur.

Kontrol edilen revizyon: `ce6af3f7cbc8fceab80c821038af9caf346eb20b`.

### KG-RAGdataset dosya kontrolü

Depo ağacında gerçek `.graphml` dosyaları ve JSON varlık/ilişki depoları var. `QA dataset/qa_from_llms/Computer_Organization/computer_bus_qs_prety.jsonl` örneği 200 kayıt içeriyor; alanlar `id`, `type`, `question`, `answer_label`, `answer_explain`, `answer`. Ders içeriklerine ait çoktan seçmeli örnekler. Hazır vektör dosyaları BAKAY'ın LaBSE modeliyle doğrudan uyumlu kabul edilemez; metinler seçilen modelle yeniden gömülmeli. Açık kullanım izni netleşmeden bu veriyi BAKAY eğitim paketinin parçası yapmak uygun bir seçim olmaz.

## Daha sınırlı adaylar ve doğrulama bulguları

- [UQB](https://huggingface.co/datasets/UIAIC/UQB), [İsfahan Üniversitesi RAG çalışması](https://arxiv.org/abs/2411.06237) ile ilişkili Farsça kaynak. Yayımlanan `UQB.json` dosyası incelendi: yalnızca `contexts` altında 452 metin var; soru ve cevap alanları yok. Mevcut sürüm hazır QA eğitim/değerlendirme paketi olarak kullanılamaz. Kartta Apache-2.0. Revizyon: `ada56f9cb2e82eca413e2ed4ce0dbe633d1206df`.
- [RAGPulse](https://github.com/flashserve/RAGPulse), çalışan bir üniversite RAG servisinin iş yükü izleri. Metinlerin yerini hash kimlikleri alıyor; cevap üretimini öğretmek için açık soru/cevap metinleri sunmuyor. Gecikme, önbellek ve sunucu yükü deneyleri için anlamlı.
- [Türkçe RAG-Instruct](https://huggingface.co/datasets/akdeniz27/rag_instruct_turkish), genel alan RAG-Instruct verisinin Türkçe çevirisi; 34.567 kayıt. Üniversite bilgisi yerine davranış eğitimi adayı. HF API'de lisans değeri bulunmadı; çeviri/etiket kalitesi ayrıca incelenmeli. Revizyon: `3bfa0db197999d838293a820de45aeb39eb88c84`.

## BAKAY için önerilen kullanım

İlk tercih, DomainRAG'ın değerlendirme yaklaşımını kendi KTMÜ belgelerimize uyarlamak. WikiRAG-TR ise kaynak metinle cevap ilişkisinin korunmasını öğreten ayrı bir eğitim deneyine uygundur. Eğitimin başarı ölçütü, daha önce eğitimde görülmeyen ve uzmanların kaynak sürümünü doğruladığı KTMÜ soruları olmalı. Harici üniversite kuralları kurumsal bilgi deposuna eklenmemeli.

Bilgi grafiği için hazır ders grafiğini aktarmak yerine KTMÜ mevzuatından küçük bir pilot daha uygun. Ders saydırma örneğinde ilişki şeması:

```text
Ders saydırma → dayanak → Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği / Madde 25
Madde 25 → kapsam → ilk kez kayıt olan önlisans/lisans öğrencisi
Madde 25 → başvuru yeri → bölüm başkanlığı
Madde 25 → belgeler → transkript + ders içerikleri
Madde 25 → koşullar → son 5 yıl, en az CC, uygun AKTS ve içerik
Madde 25 → kredi üst sınırı → programın üçte biri
Madde 25 → karar → bölüm akademik kurulu + ilgili birim yönetim kurulu
```

Bu şema bir uygulama önerisidir; grafiğe dönüştürülüp sisteme eklenmedi. Her ilişki belge URL'si, PDF sayfası, madde, alıntı ve sürümle izlenmeli; lisansüstü hükümler ayrı düğümlerde tutulmalı. [LightRAG](https://github.com/HKUDS/LightRAG) ve [GraphRAG](https://github.com/microsoft/graphrag) uygulama araçlarıdır, hazır üniversite veri kümeleri değildir.

Ders saydırma hatasında kaynak zaten mevcut olduğundan ilk çözüm eğitim değil, erişim ve kapsam düzeltmesiydi. Sonuçlar `docs/course-transfer-retrieval.md` ve JSON raporunda kayıtlı.
