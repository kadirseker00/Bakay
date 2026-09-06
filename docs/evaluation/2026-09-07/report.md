# Turkish-Gemma 9B ve Qwen3.5 9B karşılaştırması

7 Eylül 2026, Bişkek. Aynı 30 Türkçe soru ve aynı kaynak parçalarıyla yerel pilot.

Qwen3.5 9B bu kurulumda belirgin biçimde daha hızlıdır. Kaynaksız iddia üretimi
azalmıştır; ancak yanıtların hem tam hem kaynakla uyumlu olması bakımından fark
küçüktür. Bu deney, Qwen'i hatasız ya da genel olarak daha akıllı ilan etmek için
yeterli değildir. Mevcut uygulamanın varsayılan modeli Turkish-Gemma olarak
korunmuştur; Qwen yerel Ollama'ya kurulmuş ve gerçek RAG akışında doğrulanmıştır.

## Sonuçlar

| Ölçüt | Turkish-Gemma 9B | Qwen3.5 9B |
|---|---:|---:|
| Tamamlanan istek | 30/30 | 30/30 |
| Medyan yanıt süresi | 24,81 sn | 7,71 sn |
| p95 yanıt süresi | 63,33 sn | 17,86 sn |
| Ortalama yanıt süresi | 29,03 sn | 8,77 sn |
| 10 saniyeden kısa yanıt | 0/30 | 22/30 |
| Ortalama üretilen token | 587,6 | 168,0 |
| Ortalama üretim hızı | 25,57 token/sn | 32,99 token/sn |
| Çıktı sınırında kesilme | 1 | 0 |
| Boş yanıt / HTTP hatası | 0 / 0 | 0 / 0 |
| Ham yanıtta düşünme bloğu | 30/30 | 0/30 |
| Kaynağa bağlı yanıt | 21/30 | 25/30 |
| Hem kaynağa bağlı hem tam yanıt | 21/30 | 22/30 |
| Doğru kaynak atfı | 24/30 | 24/30 |
| Açık ve tamamlanmış Türkçe | 28/30 | 30/30 |
| Dört inceleme ölçütünün tamamı | 18/30 | 19/30 |

Süreler ısıtılmış modelde **tam yanıtı üretme isteği** içindir; arama, uygulama
sunucusu ve arayüz süresi dahil değildir. Medyanda 3,22 kat, ortalamada 3,31 kat
hız farkı vardır. Qwen'in daha az token üretmesi, farkın önemli bir parçasıdır.
Turkish-Gemma `think=false` verilmesine rağmen ham yanıtta düşünme bloğu
üretmektedir; uygulama bu bloğu sonradan temizler, fakat harcanan süre kalır.
Farklı tokenizer'ların token/s değerleri birebir işlem hızı karşılaştırması değildir.

Kalite satırları **Codex'in tek değerlendirici olarak yaptığı kaynak incelemesi**
sonucudur. Bağımsız insan değerlendirmesi, kör değerlendirme veya istatistiksel
anlamlılık testi değildir. Her puanın gerekçesi soru bazında kaydedilmiştir.
"Açık Türkçe" puanı yazım kusursuzluğu anlamına gelmez; Qwen'de de gereksiz
selamlamalar ve küçük dil hataları vardır.

## Kararı Etkileyen Örnekler

| Soru | Turkish-Gemma | Qwen |
|---|---|---|
| q08: Eğitim süresi ve hazırlık | Hazırlık öğrenim süresine dahil dedi; kaynak tersini söylüyor. | Hazırlığın hariç olduğunu söyledi, fakat hazırlık + 2 yılı toplam 6 yıl yaptı. |
| q20: Yüksek lisansta ALES | Öğretim görevlisi atamasındaki 60 puanı yüksek lisansa uyguladı. | İlgili öğrenci kaynağındaki 55 puan, sözlü sınav ve belge geçerliliklerini doğru ayırdı. |
| q23: Kayıt dondurma | Olmayan madde numarası, başvuru birimi ve azami süre üretti. | Kaynakta prosedür bulunmadığını belirtti; yurt kuralıyla başvuru sürecini ayırdı. |
| q05: Eğitim ücreti | Verilen Tarihçe parçasındaki ücretsiz eğitim bilgisini aktardı. | 200 Som kimlik kartı bedelini kayıt sırasındaki tek maliyet diye sundu. |
| q21: Doktora dil koşulu | Puanları doğru verdi, olmayan belge başlığı kullandı. | Puanları aktardı, fakat sınavı kaynakta olmayan "TYT İngilizce" diye adlandırdı. |
| q24: Devamsızlık | Devam/devamsızlık oranını karıştırdı ve yanıt yarım kaldı. | Kırpılmış %80 hükmünü genelledi, hazırlık ve diğer derece ayrımlarını atladı. |

q26-q30'daki gelecek tarih, olmayan burs, hava durumu, yemek tarifi ve kişisel
not sorularında iki model de istenen bilgiyi uydurmadan çekimser kaldı.

## Kaynak Katmanındaki Bulgular

30 sorunun kaynak kapsamı: 16 tam, 4 kısmi/eski/çelişkili, 10 yanıtsız.
Yanıtsız 10 sorunun 5'i özellikle bilgi yokluğu için tasarlandı. Diğer 5'i gerçek
kurumsal sorular: kesin kayıt belgeleri (q07), yurt belgeleri (q11), yüksek lisans
not ortalaması (q19), lisansüstü süreler (q22), kayıt dondurma prosedürü (q23).
Bu 5 soruda gereken bilgi modele ulaşmadı. Model değişimi bunu düzeltmez.

- q07'nin beş sonucu da kütüphane menüsüydü. HTML menü temizliği ve tekrar
  ayıklama gereksinimi sürüyor.
- q06'da 2012 burs koşulları, q15'te 2015 kütüphane saatleri öne çıktı.
  Kaynak tarihleri ve güncel sürüm önceliği gerekli.
- q05'teki Tarihçe parçası eğitimin ücretsiz olduğunu söylüyor; q08'de gelen
  Genel Bilgiler parçası Tıp Fakültesini hariç tutuyor. Bir cevabın getirilen
  metne sadık olması, güncel kurum bilgisinin eksiksiz olduğu anlamına gelmiyor.
- q20'de öğrenci kabulüyle personel ataması aynı bağlama geldi. Belge türü,
  öğrenci derecesi ve konuya göre yeniden sıralama yararlı olacaktır.
- q24'te cümle ortasından başlayan parça ders türünü kaybediyor. Parça sınırları
  hükmün kapsamını koruyacak biçimde iyileştirilmeli.
- Üretimdeki `score_threshold=0.30` kapısı **30 sorunun tamamını geçiriyordu**;
  hava durumu ve tarif soruları dahil. Bu kapı yeterli bir kapsam kontrolü değil.

## Deney Koşulları

- Donanım: Apple M3 Max, 36 GiB birleşik bellek, macOS 26.6.2; Ollama 0.30.8.
- Her iki model 8.192 bağlamla GPU'da çalıştı. Gemma koşusu tamamlandıktan sonra
  bellekten çıkarıldı, ardından Qwen başlatıldı; eş zamanlı generation yapılmadı.
- Turkish-Gemma: `hf.co/ytu-ce-cosmos/Turkish-Gemma-9b-T1-GGUF:Q4_K_M`,
  ağırlık digest'i `7ea18ec2e6769380dd96b9efe0b55fc41443ef888db031e16dfe189698ca5feb`.
- Qwen: `qwen3.5:9b`, Q4_K_M,
  digest `6488c96fa5faab64bb65cbd30d4289e20e6130ef535a93ef9a49f42eda893ea7`.
  [Ollama model kaydı](https://ollama.com/library/qwen3.5:9b).
- LaBSE, 39.659 Chroma parçası, top-k 5. Bir kez getirilen parçalar iki model
  için aynı sırada kullanıldı. Aynı SYSTEM_PROMPT ve yanıt temizliği uygulandı.
- `temperature=0.3`, `seed=42`, `num_ctx=8192`, `num_predict=1024`, `think=false`.
- Ortak istek ayarları aynıdır; modelle gelen sohbet şablonu ve diğer örnekleme
  varsayılanları farklı olabilir. Bunlar metaveride saklanmıştır. Ölçüm,
  mevcut BAKAY ayarlarıyla doğrudan model değişimini temsil eder; her model
  için ayrı optimize edilmiş en iyi kalite ayarı karşılaştırması değildir.
- Yönlendirme, yeniden yazma, doğrulama ve skor kapısı uygulanmadı; karşılaştırma
  generation katmanını yalıtıyor. Üretimdeki üç LLM düğümü zaten kapalıydı.
- Model başına tek ısıtma isteği ölçüm dışı: Gemma 5,76 sn, Qwen 3,57 sn.
- Her soru model başına bir kez çalıştırıldı. Bilgisayar diğer masaüstü
  uygulamalarına da açıktı; Qwen indirmesi Gemma koşusunun bir bölümünde sürdü.
  Model sırası dengelenmedi. Bu nedenle süreler kontrollü laboratuvar sonucu
  değildir; özellikle p95 için tekrarlı ve sırası dengelenmiş ölçüm gerekir.
- Kaynak anlık görüntüsü SHA-256:
  `ecaeab2501cfc967e4a5c97c1d590291ccd2c8ce4ae9ab762ab12c785ac19851`.

## Uygulama Doğrulaması ve Karar

Karşılaştırmadan sonra `OLLAMA_MODEL=qwen3.5:9b` yalnızca test komutuna verilerek
normal `app.rag.ask` hattı çalıştırıldı. q17'de "3 iş günü" yanıtı doğru
"Vize ve Oturum İşlemleri" kaynağıyla döndü; ölçülen toplam süre 16,64 saniye
(embedding yükleme, arama ve generation dahil), sorgu kimliği
`416d4654ee40419da0a6db6534090782`. Bu ayrı smoke testi 30 soruluk ölçümlere eklenmedi.

Qwen9B hızlı bir alternatif olarak kullanılabilir; ancak mevcut sonuçlarla
otomatik varsayılan değişikliği yapılmadı. Kullanıcının hedefi daha güvenilir
cevapsa sonraki deney, aynı kaynaklarla düşünme modu veya daha büyük bir
Qwen sürümünü karşılaştırmak; buna paralel olarak arama/güncellik sorunlarını
ölçerek düzeltmektir. Bu iki değişken ayrı deneylerde tutulmalıdır.

Ölçüm aracı, 30 soruluk veri seti, kaynak beklentileri ve tekrar çalıştırma
komutları `backend/evaluation/README.md` içinde; bütün girdiler/çıktılar bu
dizinde saklanır:

- `snapshot.json`: Sorular, tam kaynak parçaları ve birebir prompt'lar.
- `gemma.meta.json`, `qwen.meta.json`: Modeller, ayarlar ve sürümler.
- `gemma.answers.jsonl`, `qwen.answers.jsonl`: Ham ve temizlenmiş yanıtlar, süreler.
- `gemma.review.json`, `qwen.review.json`: Soru bazlı inceleme ve gerekçeler.
- `metrics.json`: Otomatik hesaplanan ölçümler ve inceleme sayımları.
- `answers.md`: Yanıtların okunabilir karşılıklı dökümü.
