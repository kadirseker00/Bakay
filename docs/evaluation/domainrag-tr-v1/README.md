# DomainRAG yönteminin BAKAY entegrasyonu — 0.3.0

1 Ekim 2026. [DomainRAG](https://arxiv.org/abs/2406.05654) üniversite kabulü için
konuşma, yapılandırılmış bilgi, kaynak sadakati, gürültü, zaman ve çoklu belge
yeteneğini değerlendiriyor. BAKAY bu değerlendirme yaklaşımını kendi Türkçe
belgelerine uyarladı. [Yayımlanan veri biçimi](https://huggingface.co/datasets/RUC-NLPIR/FlashRAG_datasets/tree/main/domainrag)
örnek alındı; Çince kurum kuralları, cevapları ve proje kodu kopyalanmadı.

## Paket ve entegrasyon

[Veri paketi](../../../data/eval/domainrag-tr-v1/README.md) 106 senaryo ve 21
kaynak sayfa/bölümü içerir. Mevcut 50 sorunun 100 soru/varyant kaydı korunur;
üzerine aşağıdaki altı geliştirme senaryosu eklenir.

| Senaryo | Ölçülmek istenen davranış |
|---|---|
| DTR-CONV-001 | Yanlış bir önceki asistan cevabını bilgi saymadan “Lisans için” seçimini ders saydırma sorusuna bağlamak |
| DTR-STRUCT-001 | Önlisans/lisans/veterinerlik sürelerini doğru programla eşleştirmek; hazırlık istisnasını korumak |
| DTR-FAITH-001 | Kaynakta 2026-2027 Tıp ücret tutarı yokken sayı uydurmamak |
| DTR-NOISE-001 | Lisans ders saydırma cevabını lisansüstü not ve başka ders yükü pasajlarıyla karıştırmamak |
| DTR-TIME-001 | Arşiv kopyasından 1 Ekim 2026 için kesin yürürlük sonucu çıkarmamak |
| DTR-MULTI-001 | Lisans ve lisansüstü tekrar dersindeki devam kurallarını iki ayrı kaynaktan karşılaştırmak |

Kaynak, sayfa, alıntı ve SHA-256 bağlantıları korunur. `golden_answers` biçimdeki
alan adıdır; cevapların insan onaylı olduğu anlamına gelmez. Bütün kayıtlar
`pending_review`, `development_exposed`, `dev`, `evaluation_draft_only` olarak
etiketlidir. Bu etiketler yeni bir bağımsız test veya eğitim bölümü oluşturmaz.
Temel `data/eval/v1` verisi ve inceleme onayları değiştirilmedi.

`evaluation.domainrag` uyarlama ve bütünlük kontrollerini, `scripts.domainrag`
paket üretimi/doğrulama/erişim ölçümü/model girdisi hazırlamayı sağlar. Sabit
model girdileri mevcut `scripts.compare_models` aracıyla çalışır; yeni bir
embedding, grafik veritabanı veya framework bağımlılığı kurulmadı.

Bu entegrasyon geliştirme ve ölçüm katmanındadır. Model ağırlıkları eğitilmedi;
üretim Chroma koleksiyonuna değerlendirme soruları/cevapları eklenmedi. DomainRAG
bir bilgi grafiği sunmaz; KTMÜ için mevzuat bilgi grafiği ayrı bir sonraki iştir.

## Tekrar çalıştırma

Komutlar `backend/` içinden çalışır. Yeni çıktı dosyası/dizini seçilmeli;
mevcut veri, model cevabı veya inceleme dosyası ezilmez.

```bash
.venv/bin/python -m scripts.domainrag validate --verify-raw
.venv/bin/python -m unittest tests.test_domainrag -v

# Aynı kaynaklardan yeni bir taslak sürümü oluştur.
.venv/bin/python -m scripts.domainrag --bundle ../data/eval/domainrag-tr-next build
.venv/bin/python -m scripts.domainrag --bundle ../data/eval/domainrag-tr-next review --output ../docs/evaluation/domainrag-next-review.md

# Gerçek üretim indeksiyle kaynak erişimi; generation çalıştırmaz.
.venv/bin/python -m scripts.domainrag retrieve --output ../docs/evaluation/domainrag-next-retrieval.json

# Altı tür için kontrollü kaynak bağlamı; referans cevaplar prompt'a eklenmez.
.venv/bin/python -m scripts.domainrag prepare --ids DTR-CONV-001,DTR-STRUCT-001,DTR-FAITH-001,DTR-NOISE-001,DTR-TIME-001,DTR-MULTI-001 --output ../docs/evaluation/domainrag-next.snapshot.json
.venv/bin/python -m scripts.compare_models run --snapshot ../docs/evaluation/domainrag-next.snapshot.json --model qwen3.5:9b --label qwen-domainrag-next --output ../docs/evaluation/domainrag-next
.venv/bin/python -m scripts.compare_models summarize --snapshot ../docs/evaluation/domainrag-next.snapshot.json --results ../docs/evaluation/domainrag-next/qwen-domainrag-next.answers.jsonl --output ../docs/evaluation/domainrag-next/metrics.json
```

## Ölçümün anlamı

[Erişim raporu](retrieval.json) gerçek 39.659 parçalık koleksiyondan ilk 10 sonucu
ve alıntı konumlarını saklar. Konuşma senaryosunda gerçek bağlam çözümü kullanılır;
`metadata.query` aramaya hazır soru olarak geçirilmez. Erişim metrikleri yalnız
`answer` etiketli kayıtlarda hesaplanır; açıklama/kaçınma örnekleri başarı paydasını
şişirmez. Kısa alıntıda belge adı da eşleşmelidir. MRR@10 ilk eşleşen hedef alıntının
sırasını, ortalama alıntı recall@5 ve tam alıntı erişimi ise kapsamı ölçer.

[Sabit model girdisi](pilot.snapshot.json) seçilmiş kaynak sayfalarını kullanır;
yanıltıcı sayfalar pozitif sayfadan önce gösterilir. Güncel yürürlüğü doğrulanmamış
arşiv paketi olduğu açıkça yazılır. Bu deney üretim retrieval/yeterlilik/kapsam
kapılarını veya frontend vurgu adımını ölçmez. Referans cevaplar, beklenen noktalar,
yasak iddialar ve sentetik önceki asistan cevabı yanıt üretim prompt'una taşınmaz.

Her türde tek örnek ve insan onaysız etiketler olduğundan bilimsel genelleme veya
gold başarı iddiası yapılamaz. Çince DomainRAG sonuçlarıyla sayısal karşılaştırma
yapılmadı. Önce [106 kayıtlık inceleme paketi](review.md) ve canlı model cevapları
uzmanlarca kontrol edilmeli; yeni eğitim ve saklı test verisi ayrı hazırlanmalıdır.

## İlk çalışma sonuçları

87 backend testi geçti; kaynak paketi ham PDF/HTML dosyalarının hash'leriyle
doğrulandı. 106 sorgunun 94'ü cevaplanabilir etiketli ve hedef alıntılıdır.
Gerçek indeks aramasında:

| Ölçüm | Sonuç |
|---|---|
| En az bir hedef alıntı ilk 5'te | 69/94 (%73,4) |
| Bütün hedef alıntılar ilk 5'te | 58/94 (%61,7) |
| Soru başına ortalama alıntı recall@5 | 0,674 |
| İlk hedef alıntı MRR@10 | 0,609 |

Altı sabit bağlam senaryosu Qwen3.5 9B ile çalıştı; hata, boş veya kesilmiş
cevap yok. Medyan süre 6,61 saniye, ortalama 8,82 saniyedir.
[Ham cevaplar](qwen-domainrag.answers.jsonl), [okunabilir cevaplar](answers.md),
[çalışma metrikleri](metrics.json) ve [taslak model incelemesi](observations.json)
birlikte saklanır. Bu sayılar cevap doğruluk puanı değildir.

| Senaryo | Kaynakla karşılaştırılan ilk bulgu; insan onayı bekliyor |
|---|---|
| Konuşma | İlk soruyu korudu; 5 yıl, CC ve 1/3 sınırını doğru aktardı. AKTS uygunluğu ve son kurul onayları eksik kaldı. |
| Gürültü | Temel sayısal sınırları korudu; ders saydırma maddesinde bulunmayan danışman onayını şart olarak ekledi. |
| Güncellik | 1 Ekim 2026 için kesin yürürlük iddia etmedi; soruya gereksiz ders saydırma ayrıntıları ekledi. |
| Yapılandırılmış bilgi | 4/8/10 yarıyıl eşleştirmesi ve hazırlık istisnası doğru; kaynak sunumu ve kısalık iyileştirilebilir. |
| Sadakat | Kaynakta olmayan Tıp ücretini uydurmadı; ücret sorusuna gereksiz eğitim süresi ekledi. |
| Çoklu belge | Temel devam ayrımını korudu; izinli öğrencinin mazeret hakkını genel devamsızlık hakkı gibi yanlış genişletti. |

Bu entegrasyon hataları görünür ve tekrar ölçülebilir hâle getirir; tespit edilen
üretim kusurlarını tek başına düzeltmez. Altı ek türün kapsamı genişletilmeli,
koşul/istisna aktarımı ve kaynak sadakati bir sonraki iyileştirmede ele alınmalıdır.
