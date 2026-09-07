# BAKAY: Kaynak Bağlı Veri ve Gold İnceleme Protokolü

## Teslim edilen ilk paket

7 Eylül 2026: [50 soruluk inceleme paketi](review-packet.md), [asıl JSON](../../../data/eval/v1/dataset.json),
[JSON Schema](../../../data/eval/v1/schema.json) ve [kaynak doğrulama sonucu](validation.json).
Teknik testler, canlı Qwen yanıtları ve açık kalite kusurları: [teslim kontrolü](verification.md).
Paket 45 yanıt, 3 açıklama isteme, 2 yanıt vermekten kaçınma örneği içerir.
49 soruda belge alıntısı vardır; kalan bir soru kurumsal kapsam dışı davranışı ölçer.
İki yönetmelik ve üç resmî SSS sayfasının toplam 21 sayfa/bölüm görüntüsü metin olarak sabitlenmiştir.

**50 kaydın tamamı Codex taslağıdır. İnsan onayı yoktur. Bu paket gold değildir.**
Güncel yürürlük, belge değişiklik zinciri ve programlara özgü istisnalar henüz uzman tarafından
doğrulanmadı. Cevaplar yalnız arşivlenen kaynak sürümüne göre önerilmiştir; canlı başvuru tavsiyesi değildir.
Başlıkta “Yeni” yazması veya PDF içindeki tek bir değişiklik tarihi güncellik kanıtı sayılmaz.

Ham PDF/HTML dosyaları Git dışında kalır. Kaynak başlıkları, yerel göreli yollar, tarama haritasından
alınmış resmî URL'ler ve dosya SHA-256 özetleri `evidence.json` içinde bulunur. Her dayanakta PDF'nin
fiziksel sayfası ile basılı sayfa numarası ayrıdır; HTML'de sahte sayfa numarası kullanılmaz.
Alıntılar NFC ve boşluk normalizasyonundan sonra ham metinle birebir eşleşir. Bu teknik eşleşme,
cevabın anlam olarak doğru veya hâlen yürürlükte olduğunu **kanıtlamaz**.

Bu küçük paket aday/kayıt, ders, sınav, devam, not, lisansüstü kabul ve anlam ayrımına ağırlık verir.
Burslar ve barınma yalnız sınırlı örneklerle temsil edilir. Güncel takvim, kontenjan, ücret tutarları,
personel işlemleri, gerçek öğrenci sorguları ve Kırgızca/Rusça henüz kapsanmıyor.

## Şema ve inceleme

Her soru; `question`, `paraphrases`, `answer`, `required_points`, `forbidden_claims`, `citations`,
`behavior`, `category`, `scope` ve `group_ids` taşır. Her alıntı `evidence_id`, madde/SSS konumu ve
birebir kaynak metnini içerir. Beklenen maddeler puanlama kontrol listesidir; otomatik anahtar sözcük
eşleşmesiyle doğruluk puanı verilmez. Açıklama isteme/kaçınma cevaplarının sözcüğü sözcüğüne aynı
olması gerekmez; davranış ve gerekçe doğru olmalıdır.

JSON'da yazılmayan inceleme alanlarının güvenli varsayılanları şemada açıktır:

| Alan | Varsayılan |
|---|---|
| `status` | `pending_review` |
| `split` | `unassigned` |
| `exposure` | `development_exposed` |
| `author` | `codex_draft` |
| `reviews` | boş liste |

İnceleme sırası:

1. Kurumdan yetkili bir uzman belge sürümünü, kapsamını, ilgili istisnaları ve uygulanabilirliğini kontrol eder.
2. Veri sorumlusu kural ailelerini bölümleme için gözden geçirir; bölüm ataması onaydan **önce** yapılır.
3. İki farklı insan soruyu ve kaynakları bağımsız değerlendirir. İlk puanlamada birbirinin kararını görmez.
4. `required_points` ve alıntılar bütün cevabı destekliyor mu, olumsuz iddialar gerçekten yanlış mı incelenir.
5. Anlaşmazlıkta `revise`/`reject` kaydı korunur; düzeltme ve yeniden inceleme gerekir. Gerekirse üçüncü uzman karar verir.
6. Onay veren her insan kendi sabit kimliği, zaman damgası, `kind=human`, `decision=approve`,
   `source_version_checked=true`, açıklama ve inceleme paketindeki `content_sha256` ile kayıt ekler.
7. İki geçerli onaydan sonra veri sorumlusu `status=approved` yapar; doğrulama ve dışa aktarma tekrar çalışır.

Onay özeti soru, cevap, alıntılar, kapsam, kural ailesi, bölüm ve bütün kaynak görüntüsüne bağlıdır.
Bunlardan biri değişirse eski onay yeni içeriğe taşınmaz. İnsan başına aynı içerik için son karar
geçerlidir; mevcut insan kararları içinde ret/düzeltme veya kaynak kontrolü eksikliği varsa dışa
aktarma engellenir. Yapay zekâ incelemesi insan onay sayısına katılmaz.
Bu yerel dosya sistemi kimlik doğrulamalı bir onay servisi değildir: kişilerin gerçekten bağımsız
uzmanlar olduğunu kurum/veri sorumlusu doğrulamalıdır. Ajanlar kendi kararlarını `human` diye kaydedemez.

Kayıt durumu ile kaynak güncelliği farklıdır. `approved`, belirtilen **arşiv sürümüne** ait cevabın
onaylandığını ifade eder; otomatik olarak “2026'da güncel politika” anlamına gelmez. Güncel politika
testi için geçerlilik tarihleri doğrulanmış yeni bir sürüm gerekir.

## Sızıntısız bölümleme

Bu 50 soru hazırlanırken görülmüştür; önceki 30 model karşılaştırma sorusu da görülmüştür.
İkisi de bağımsız test seti olarak sunulamaz. `development_exposed` kayıtların `test` bölümüne
atanmasını şema reddeder. `exposure` etiketini sırf test oluşturmak için değiştirmek kabul edilmez.
İlk 50 soru, uzman onayından sonra **dev** olarak kullanılsın; ayrı eğitim verisi hazırlansın.

Hedef ilk gold büyüklüğü: 100 geliştirme + 200 gerçekten saklı test sorusu. Bu bir hedeftir,
bugün tamamlanmış sayı değildir. LoRA train verisi ayrıca hazırlanır ve bu 300 değerlendirme
sorusuyla aynı kural/parafraz ailesinden örnek içermez. Test seti model/prompt geliştiren ajanın
erişmediği yerde tutulmalı; bu repoya açık test cevapları eklenmemeli.

`group_ids` aynı maddeyi veya ilişkili kararları ölçen bütün varyantları bir arada tutar.
Bir kayıt birden fazla aileyi bağlayabilir; bu durumda bağlı ailelerin tamamı aynı bölümde kalır.
Örneğin BAKAY-005, 034 ve 049 devam kurallarını, BAKAY-017, 037, 038 ve 045 itirazları paylaşır.
Rastgele satır bölmek yasaktır. Araç aynı grup etiketini farklı bölümlerde görürse hata verir.
Fakat semantik benzerliği veya eksik/yanlış grup etiketini kendiliğinden keşfetmez; insan kontrolü gerekir.
Normalleştirilmiş birebir soru/varyant tekrarları otomatik yakalanır.

Kaynak belgenin RAG indeksinde bulunması veri sızıntısı değildir; bu sistemin bilgi kaynağıdır.
Test sorusu, referans cevabı veya aynı kuralın eğitim amacıyla üretilmiş yakın varyantının geliştirmede
kullanılması ayrı bir sızıntı riskidir. Eski 30 soru ile yeni train/dev adayları da elle çapraz taranmalıdır.

## Kullanım

Komutlar `backend/` içinden, mevcut `.venv` ile çalışır. Yeni bağımlılık gerekmez.

```bash
.venv/bin/python -m scripts.dataset validate
.venv/bin/python -m scripts.dataset validate --verify-raw
.venv/bin/python -m unittest discover -s tests -v

# Yeni dosya adı kullanın; araç mevcut incelemeyi/raporu ezmez.
.venv/bin/python -m scripts.dataset review --output ../docs/evaluation/gold-v1/review-next.md
.venv/bin/python -m scripts.dataset schema --output /tmp/bakay-schema-next.json

# Şu an başarısız olması beklenir: onaylı/bölümlenmiş veri henüz yok.
.venv/bin/python -m scripts.dataset export --purpose evaluation --split dev --output /tmp/bakay-approved-dev.jsonl
.venv/bin/python -m scripts.dataset export --purpose lora --split train --output /tmp/bakay-approved-train.jsonl
```

`snapshot` yalnız ilk kaynak görüntüsünü oluşturur; mevcut `evidence.json` dosyasını değiştirmez.
Yeni belge sürümü için yeni veri klasörü ve `--data` seçeneği kullanılmalıdır. Normal `validate`
Git'teki kaynak görüntüsüyle çalışır; `--verify-raw` ayrıca yerel orijinal dosyaları ve sayfa metinlerini
tekrar kontrol eder. Orijinal dosyaların olmadığı makinede normal doğrulama yapılabilir, ham doğrulama yapılamaz.

LoRA dışa aktarma yalnız `train` kabul eder ve seçili bölümde tek bir onaysız/reddedilmiş kayıt varsa
tamamını reddeder. Çıktı kaynak bağlamı + soru + onaylı cevaptan oluşan mesaj formatıdır. Bu sadece
veri çıkış kapısıdır: eğitim betiği, GPU eğitimi, adapter veya RAFT deney sonucu üretilmemiştir.

## Değerlendirme kuralları

Retrieval ve generation ayrı ölçülür. Kaynakları sabit tutulan generation deneyi ile canlı indeks
deneyi aynı sonuç tablosunda birleştirilmez. BAKAY-048'in “tutar yok” etiketi yalnız bu kaynak paketine
aittir; canlı indeks güncel ücret belgesi bulursa cevaplanabilirlik etiketi yeniden değerlendirilir.

- Retrieval: doğru belge + ilgili maddeye erişim, Recall@5, MRR@10; yakın ama yanlış düzeydeki madde negatif sayılır.
- Cevap: gerekli noktaların tamlığı, kaynakça doğruluğu, yanlış kapsam/istisna/sayı ve ek kaynaksız iddialar ayrı işaretlenir.
- Davranış: answer/clarify/abstain kararının doğruluğu. Eksik kaynak ile kapsam dışı istek ayrı raporlanır.
- Dil: anlaşılır Türkçe, gereksiz teknik dosya adı veya ham düşünme bloğu bulunmaması.
- Süre: soğuk/sıcak başlangıç ayrımı, p50/p95, hata/timeout, kullanılan model etiketi ve model digest'i.
- İnsan uyumu: bağımsız ilk kararlar saklanır; uzlaşma sonrası puan ile ilk değerlendiriciler arası uyum ayrı raporlanır.

Otomatik LLM yargıcı ileride insan etiketleriyle kalibre edilebilir; bugünkü testler cevap kalitesine
yüzdelik puan üretmez. Teknik doğrulama geçmesi “50 doğru cevap” veya “halüsinasyon yok” anlamına gelmez.

## Sonraki araştırma işleri

1. **Gold:** iki uzman incelemesi, güncel belge zinciri, gerçek öğrenci sorgularının kişisel veriden arındırılması,
   konu/dil dengesi ve saklı test oluşturma. İlk 50 soru bunun başlangıç paketidir.
2. **Erişim kalitesi:** mevcut Qwen + LaBSE tabanı üzerinde BM25/dense birleşimi ve yeniden sıralamayı
   aynı onaylı dev setinde karşılaştırma. Önceki pilotta kaynak kapsamı önemli bir sınırdı.
3. **LoRA/QLoRA:** onaylı, ayrı train kümesiyle kaynak kullanma, açıklama isteme ve kaçınma davranışlarını
   öğretme. Değişen mevzuat tarih/tutarlarını modele ezberletmek hedef değil. Bağlamlı örnekler, ilgili ve
   yanıltıcı kaynaklar; taban Qwen ile adapter'lı modelin aynı değerlendirmesi. Eğitimden önce donanım,
   bellek, model lisansı ve eğitim çerçevesi uyumu ayrıca doğrulanacak.
4. **Knowledge graph pilotu:** `Program`, `ÖğrenimDüzeyi`, `İşlem`, `Kural`, `İstisna`, `Birim`, `BelgeSürümü`
   düğümleri; `uygulanır`, `gerektirir`, `istisnasıdır`, `yetkilidir`, `dayanır` ilişkileri. Her kuralda
   kapsam, süre birimi (gün/iş günü/ay), başlangıç olayı, belge hash'i, madde ve geçerlilik bilgisi tutulmalı.
   İlk örnek itiraz akışı olabilir: düzey + sınav türü -> uygulanabilir kural -> süre + yetkili birim.
   Tam GraphRAG'a geçmeden bu dar grafiğin düz RAG'a göre faydası ölçülmeli. Bu turda graph indeksi kurulmadı.
5. **Terim ve anlam katmanı:** ÖİDB/Öğrenci İşleri, ÇAP/çift anadal, yurt/öğrenci evi, GANO/genel ortalama
   kontrollü eşlemeleri; burs üst kavramı ve burs türleri alt kavramları; vize=ara sınav ile giriş vizesi
   farklı anlam kimlikleri. “Her yakın sözcüğü sorguya ekleme” yapılmamalı. Belirsizlikte anlamı sorma
   davranışı BAKAY-045/046/047'de taslak olarak ölçülüyor; üretim sorgu genişletmesi henüz eklenmedi.

Qwen varsayılanı ve ilk veri altyapısı hazır; insan onayı, saklı test, LoRA eğitimi ve graph entegrasyonu
ayrı tamamlanma koşulları olan açık işlerdir.
