# BAKAY sistem analizi — 1 Ekim 2026

Mevcut Qwen3.5 9B + LaBSE + Chroma kurulumu çalışıyor; ancak kaynak erişimi
kurumsal danışmanlık için yeterli güvenilirlikte değil. Hibrit arama ve E5-small
deneyi daha iyi erişim gösteriyor. Doğru kaynak verildiğinde de bazı koşulların
atlanması ve belirsiz sorulara açıklama istemeden cevap verilmesi sürüyor.

Bu bir **geliştirme pilotudur**. Sorular daha önce geliştirmede görülen,
iki insan tarafından henüz onaylanmamış 50 taslaktır. Güncel yürürlük ve kurum
istisnaları doğrulanmış değildir; sonuçlar saklı test başarımı değildir.

## Gerçekte ne test edildi?

- 50 soru + her birinin bir farklı söyleyişi: **100 sorgu**.
- 45 cevaplanabilir soru × 2 söyleyiş: retrieval tablosunun paydası **90**.
  Üç açıklama isteme ve iki çekimserlik örneği bu paydaya dahil edilmedi.
- Yerel Chroma koleksiyonunda **39.659 parça**; mevcut LaBSE vektörleri kullanıldı.
- Tam koleksiyonda dense arama, BM25 ve eşit ağırlıklı RRF birleşimi.
- Ayrı **1.983 parçalık** havuzda LaBSE, multilingual-E5-small ve multilingual-MiniLM.
- 12 kritik soruda mevcut Qwen'e canlı indeksten bulunan bağlam verildi;
  aynı 12 soruda iki LLM'ye yalnız referans alıntılarından oluşan ortak bağlam verildi.
  Bunlar birbirinden ayrı deneylerdir. Kullanılan gerçek prompt ve yanıtlar kaydedildi.
- İlk 12 soruda deneyin ilk beş sonucu üretimin `store.query(top_k=5)` sonucu
  ile **12/12 birebir eşleşti**: [kontrol](production-top5-check.json).
  Tam retrieval taraması 50 adaydan ilk 5/10'u kullanır; yaklaşık HNSW aramasında
  diğer 88 sorgunun `n_results=5` sonucuyla eşitliği ayrıca sınanmadı.
- Ham kaynak dosyaları ve alıntılar `scripts.dataset validate --verify-raw`
  ile yeniden doğrulandı: 50 kayıt, 5 kaynak, 21 birim; hepsi `pending_review`.
- `/health` başlangıçta erişilemiyordu; HTTP sunucusunu başlatmadan yerel
  retrieval ve Ollama üzerinden ölçüm yapıldı. Frontend/API uçtan uca yük testi yapılmadı.

Üretim ayarları değişmedi: Qwen3.5 9B, `think=false`, sıcaklık 0,3,
8192 bağlam, 1024 çıktı sınırı, top-k 5, skor eşiği 0,30;
route/rewrite/verify kapalı. Model deneylerinde ayrıca sabit tohum 42 kullanıldı.

## RAG: kaynak erişimi

| Yöntem — tam 39.659 parça | En az bir dayanak ilk 5'te | Tüm dayanaklar ilk 5'te | Alıntı Recall@5 | MRR@10 |
|---|---:|---:|---:|---:|
| LaBSE dense | 27/90 (%30,0) | 16/90 (%17,8) | 0,235 | 0,198 |
| BM25 | 44/90 (%48,9) | 35/90 (%38,9) | 0,437 | 0,344 |
| LaBSE + BM25, RRF | 49/90 (%54,4) | 36/90 (%40,0) | 0,470 | 0,376 |

Hibrit yöntem mevcut dense aramadan daha iyi, fakat tek başına yeterli değil.
BM25'e göre tüm dayanakları bulmada fark yalnız bir sorgu; hibritin kesin
üstünlüğü veya yeterli üretim kalitesi çıkarılamaz.

Söyleyiş hassasiyeti yüksek: dense için orijinal sorularda 18/45 dayanak
erişimi varken varyantlarda 9/45. Hibritte bunlar 28/45 ve 21/45.
Kural düzeyi/işlem bilgisi ve yeniden sıralama ayrıca denenmeli.

**Puanların anlamı:** Unicode/boşluk normalizasyonundan sonra referans alıntının
en az 80 ardışık karakterini taşıyan parça ilgili sayıldı. 80 karakterden kısa
alıntıda aynı belge ve bütün alıntı aranır. Uzun alıntının başka belge kopyaları
da kabul edilir. Tam alıntı kapsaması ayrıca kaydedildi: sırasıyla 12/90,
28/90 ve 26/90 sorguda bütün alıntılar eksiksiz ilk beş parçadaydı.
Bu mekanik etiket, doğru madde/sürüm için uzman değerlendirmesinin yerini tutmaz;
kopya metnin güncel ve uygulanabilir olduğunu da kanıtlamaz.

Alıntı Recall@5, her sorguda bulunan alıntıların o sorgunun beklenen alıntılarına
oranının makro ortalamasıdır. MRR@10 ilk ilgili parçanın ters sırasıdır;
ilk 10'da yoksa sıfırdır. Aynı sorunun iki söyleyişi bağımsız örnek kabul
edilerek istatistiksel anlamlılık hesaplanmadı.

Yalnız kanonik belgeyi kabul eden ilk ölçüm de korunmuştur:
[belgeye özgü ölçüm](document-only-retrieval-metrics.json).
Yukarıdaki tabloda kopya hükümler nedeniyle haksız negatif oluşmasını azaltan
[nihai ölçüm](retrieval-metrics.json) kullanıldı.

## Embedding: aynı havuzda karşılaştırma

| Model | En az bir dayanak ilk 5'te | Tüm dayanaklar ilk 5'te | Alıntı Recall@5 | MRR@10 | Token sınırını aşan parçalar |
|---|---:|---:|---:|---:|---:|
| LaBSE, 768 boyut | 26/90 | 16/90 | 0,230 | 0,192 | 579/1.983 (%29,2), sınır 256 |
| multilingual-E5-small, 384 boyut | 48/90 | 42/90 | 0,498 | 0,378 | 39/1.983 (%2,0), sınır 512 |
| multilingual-MiniLM-L12-v2, 384 boyut | 21/90 | 14/90 | 0,198 | 0,180 | 1.673/1.983 (%84,4), sınır 128 |

Bu kurulumda **E5-small daha güçlü bir aday**. MiniLM mevcut parçalama ve
varsayılan 128-token sınırıyla geride kalıyor. LaBSE'nin çok dilli olması
bu kurumun soru–madde erişiminde en uygun model olduğunu kanıtlamıyor.
LaBSE indeksindeki ilk 10 pilot vektör yeniden üretildi; kosinüs benzerlikleri
yaklaşık 1,0. İncelenen örneklerde yanlış embedding uzayı karışımı görülmedi.

Havuz; beş referans belgenin mevcut indeks parçaları, 100 sorgunun dense/BM25
ilk 10 adayları ve kimlik hash'iyle seçilmiş 1.000 genel parça birleşimidir.
Aynı havuzda normalize vektörler üzerinde tam kosinüs araması yapıldı.
LaBSE belge vektörleri mevcut indeksten okundu; diğer iki modelde belgeler yeniden
kodlandı. Aynı koşul, aynı parçalar ve model revizyonları JSON dosyalarında kayıtlı.
Havuz eski dense/BM25 adaylarıyla oluşturulduğundan seçim yanlılığı vardır;
bu sonuç E5'in tam 39.659 parçada aynı sonucu vereceğini göstermez.
TR dışında dil test edilmedi; KY/RU başarımı için sonuç çıkarılamaz.

E5'te resmî kullanımına uygun `query: ` ve `passage: ` önekleri kullanıldı.
Mevcut `Embedder` bu ayrımı yapmıyor. E5 üretime alınacaksa **yeni ayrı indeks**,
doğru önekler ve yeniden kalibre edilen eşik gerekir; yalnız `.env` değiştirmek
LaBSE vektörleriyle E5 sorgularını karıştırır. Eski 768-boyut koleksiyonu 384-boyut
E5 sorgusuyla uyumlu değildir.
[E5 model kartı](https://huggingface.co/intfloat/multilingual-e5-small),
[LaBSE model kartı](https://huggingface.co/sentence-transformers/LaBSE),
[MiniLM model kartı](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2).

## LLM: gerçek örnek cevaplar

12 soru bilinçli olarak kritik vakalardan seçildi; rastgele veya temsilî model
sıralaması değildir. Oracle deneyinde iki model aynı prompt, kaynak alıntıları,
ayarlar ve tohumla çalıştı. Oracle, yalnız doğru dayanaklar verilen tanısal bir
deneydir; üretimde erişim kalitesi veya tam belgeyi okuma başarımı değildir.

Oracle koşularının uygulama dosyası/yanıt temizliği hash'i aynıdır. Canlı Qwen
koşusu ile oracle koşuları arasında diğer sohbetin hafıza çalışması uygulama
dosyası hash'ini değiştirdi; bu nedenle canlı/oracle karşılaştırması tek kod
sürümüyle yapılmış uçtan uca bir ablation olarak sunulmaz. Sabit prompt'ların
sistem metni hash'i tüm snapshot'larda aynıdır.

| Ortak oracle bağlamı | Qwen3.5 9B | Turkish-Gemma 9B |
|---|---:|---:|
| Tamamlanan istek | 12/12 | 12/12 |
| Medyan generation süresi | 4,11 sn | 14,27 sn |
| p95 generation süresi | 6,61 sn | 21,36 sn |
| Boş/hatalı/kesilmiş cevap | 0/0/0 | 0/0/0 |
| Ham düşünme bloğu | 0/12 | 12/12 |

Süre, ısıtılmış modelin tam Ollama cevabını dönmesidir; API/UI süresi veya ilk
token değildir. Gemma'nın düşünme metni kullanıcıya gösterilmeden temizlenir,
ama üretim süresinde yer tutar. İki model sıralı çalıştı; bazı Qwen oracle
istekleri kısa MiniLM ve üretim top-5 kontrolüyle eşzamanlıydı. Bu küçük koşumun
hız farkı önceki pilotla aynı yönde, fakat hassas kapasite ölçümü değildir.
Canlı Qwen bağlamında ayrı ölçüm medyan 7,85, p95 17,39 sn; 12/12 cevap tamamlandı.

| Soru | Beklenen temel cevap | Qwen, canlı kaynak | Qwen, doğru alıntılar | Gemma, doğru alıntılar |
|---|---|---|---|---|
| Lisans kaydında vekil | Noter vekili + kayıt süresi | Lisansüstü Enstitü kuralını uyguluyor | Noter doğru; süre koşulu eksik | Noter doğru; süre koşulu eksik |
| Yüksek lisans/doktora başvuru ortalaması | 2,00/2,50; daha yüksek program eşiği mümkün | Başvuru maddesi gelmiyor; çekimser | Temel sayılar doğru; istisna ve çevirim eksik | Sayılar doğru; daha yüksek eşik yerine “esnetilebilir” diyor |
| Lisansüstü mazeret sınavı | Sınavların bitiminden itibaren 3 iş günü | Doğru madde gelmiyor; çekimser | 3 iş günü; başlangıcı “tüm süreçler” olarak değiştiriyor | Süre ve başlangıç doğru; rapor/kurul koşulu eksik |
| ALES 55 | Başvuruda beyan; yazılı muafiyeti, sözlü zorunlu | Beyan koşulunu atlıyor | Beyan koşulunu atlıyor | Beyan koşulunu atlıyor |
| “Vize için ne yapmalıyım?” | Ara sınav mı giriş/oturum mu diye sor | Giriş vizesini varsayıyor | Giriş vizesini varsayıyor; bağlam hüküm içermiyor | Kaynakta olmayan 60 gün vizesiz giriş üretiyor |
| “Sınav sonucuna kaç günde itiraz?” | Düzey ve sınav türünü sor | Tek bir 7 gün kuralına indiriyor | Üç süreyi ayırıyor ama soru sormuyor | Soru sormuyor; olmayan “tez dersleri hariç” istisnası ekliyor |

**Karar:** Qwen mevcut yerel varsayılan olarak makul; bu testte Gemma'ya geçmek
güvenilirlik sorununu çözmedi. İki model de tam koşullu cevap ve belirsizlik
davranışında eksik. Daha büyük/düşünmeli model bu çalışmada karşılaştırılmadı;
“doğru/en iyi LLM bulundu” sonucu çıkarılamaz.

36 cevabın tamamı, taslak beklenen cevapları ve soru bazlı gerekçeleri
[örnek soru–cevap paketinde](examples.md). `*.assessment.json` dosyaları
cevap hash'i ve bağlam hash'iyle incelemeyi kaydeder. Kaynak desteği, tüm
`required_points` maddelerinin tamlığı ve answer/clarify/abstain davranışı
ayrıdır; bunlar tek AI değerlendiricinin gözlemidir. Uzman onayı değildir ve
genel “doğruluk yüzdesi” olarak sunulmaz. Bir cevabın temel sayıyı doğru vermesi,
gerekli istisnaları/başlangıç olayını koruduğu anlamına gelmez.

## İndeks ve RAG akışındaki somut kusurlar

1. **Deneme belgesi üretim koleksiyonunda:** `ornek_yonetmelik.txt` iki parça.
   Örnek belge final alt sınırını 50 ve başarı ağırlıklarını 40/60 diye veriyor;
   kaynak bağlı lisans taslağındaki gerçek hükümle karışabilir. Resmî belge
   allowlist'i ve ayrı demo koleksiyonu gerekli. Bu analizde silinmedi.
2. **Kısa cevap kaybı:** hazırlık SSS'nin ham kaynağında burs sorusuna
   “Evet, alabiliyorlar.” cevabı var; mevcut indeks parçasında soru kalmış,
   cevap yok. BAKAY-043'ün kısa referans alıntısı indeks içinde eşleşmiyor.
   HTML temizleyici/parçalama akışı soru ile cevabı birlikte korumalı.
3. **Yinelenen kaynaklar:** lisansüstü yönetmeliğin bağımsız PDF'si ve büyük
   `docs_mevzuattr.pdf` aynı metni taşıyarak top-k yerlerini tüketiyor.
   Pilot havuzda boşluk normalizasyonu sonrası ilk kopya dışındaki 96 parça
   birebir tekrar. Sayfa/madde ve sürüm metadata'sı ile tekilleştirme gerekli.
4. **Kapsamın kaybolması:** 1.000 karakterlik dilimler hükmün başını, öğrenim
   düzeyini veya madde başlığını ayırabiliyor. Bazı sonuçlar kelimenin ortasından
   başlıyor. Token ve madde sınırlarını koruyan parçalama deneyi gerekli.
5. **Skor kapısı kapsam kontrolü değil:** 0,30 eşik, kek tarifi dahil 100 sorgunun
   tamamını geçiriyor. Kek sorusunun skorları 0,467/0,436; anlamı belirsiz
   “vize” sorusu da geçiyor. Benzerlik skoru cevaplanabilirlik/kanıt olasılığı değildir.
6. **Ek düğümler kapalı:** dokümantasyondaki ajansal akışın route/rewrite/verify
   adımları etkin değil. Açılması da ayrıca doğru kaynak, güvenli başarısızlık
   davranışı ve süre testi gerektirir. Mevcut doğrulama hatada `True` döndürüyor;
   açıkken bile doğrulanmış cevap garantisi vermez.

## Deney sınırları ve sonraki karar

Kaynak eşleştirme testleri (6/6) ve ham alıntı/hash doğrulaması geçti.
Üç LLM koşusunun 12'şer prompt/cevap/inceleme hash'i ve üç embedding çıktısının
ortak havuz hash'i yeniden kontrol edildi; hepsi eşleşti.
Model ve retrieval ölçümleri tek koşumdur. Canlı Qwen koşusunun bazı bölümleri
embedding işiyle eşzamanlıydı; süreler kapasite garantisi değildir. Oracle
bağlamı çok daha kısa olduğundan canlı/oracle süre farkı model hız kazancı
olarak yorumlanmamalıdır. Token/s farklı tokenizer'lar arasında eşdeğer değildir.
Isıtma süreleri ana ölçümden ayrıdır; hata/kesilme kayıtları sonuçlardan dışlanmaz.

Öncelik sırası: örnek belge ve tekrarları ayır; SSS kısa cevap kaybını gider;
madde/düzey/sürüm metadata'sını koru; E5 + BM25 + yeniden sıralamayı ayrı tam
indekste dene; açıklama isteme davranışını geliştir; ardından iki bağımsız
uzman incelemesi ve saklı test ile nihai model kararını ver.
E5-large/BGE-M3 veya daha büyük LLM henüz bu çalışmada ölçülmedi.
