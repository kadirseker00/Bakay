# Haiku 5.5 pilot sonucu — 9 Ekim 2026

Haiku, BAKAY'da maliyeti belirgin biçimde azaltan bir aday. Düşünme açık
`adaptive/medium` ayarında 12 kritik sorudan 10'unda kaynakla uyumlu ve tam
yanıt üretildi; önceki Sonnet koşusunda 11/12. Düşünme kapalı ayar daha hızlı
ve ucuz, ancak aynı incelemede 8/12. Karmaşık mevzuatta Sonnet'i korumak,
Haiku'yu basit kurumsal sorular için değerlendirmek daha uygun görünüyor.
Bu yönlendirme henüz uygulanmadı; yerel uygulama Sonnet kullanmaya devam ediyor.

**Geliştirme pilotu:** Önceki Sonnet pilotunun aynı 30 üretim kaynaklı sorusu
ve 12 referans alıntılı kritik sorusu, iki Haiku ayarında çalıştırıldı.
84 ücretli Haiku isteği tamamlandı. Kaynaklar ve prompt'lar değiştirilmedi;
herhangi bir referans cevap modele verilmedi. Sorular geliştirmede görülmüş,
etiketleri insan onayı bekleyen taslaklardır. İnceleme tek Codex incelemesidir,
kör veya bağımsız gold testi değildir; sonuç genel doğruluk oranı değildir.

## Üretimden bulunan kaynaklarla 30 soru

| Ölçüm | Sonnet 5.5 | Haiku adaptive/medium | Haiku disabled/high |
|---|---:|---:|---:|
| Tamamlanan istek | 30/30 | 30/30 | 30/30 |
| Ortanca üretim süresi | 6,04 sn | 7,65 sn | 3,64 sn |
| p95 üretim süresi | 9,65 sn | 13,05 sn | 5,02 sn |
| 10 saniyeden kısa üretim | 29/30 | 19/30 | 30/30 |
| Hata / boş / kesilen yanıt | 0/0/0 | 0/0/0 | 0/0/0 |
| Giriş tokenı | 130.244 | 130.304 | 130.244 |
| Çıktı tokenı, düşünme dahil | 22.537 | 50.462 | 17.312 |
| Düşünme tokenı | 0 | 30.622 | 0 |
| Kayıtlı API maliyet tahmini | 0,485858 USD | 0,0382614 USD | 0,0216804 USD |
| Bu tüketimle 1.000 yanıt tahmini | 16,20 USD | 1,28 USD | 0,72 USD |

[Düşünme açık ölçümler](adaptive/retrieved/metrics.json),
[yanıt dökümü](adaptive/retrieved/answers.md),
[düşünme kapalı ölçümler](retrieved/metrics.json),
[yanıt dökümü](retrieved/answers.md).

Haiku'nun giriş/çıkış birim fiyatı bu kısa prompt'larda Sonnet'in 1/20'si.
Gerçek tasarruf, düşünme ve yanıt uzunluğuna bağlı: bu 30 soruda adaptive
yaklaşık **12,7 kat**, disabled yaklaşık **22,4 kat** ucuz oldu.
Düşünme tokenları çıktı olarak ücretlendirildi; kullanıcıya gösterilmez.
1.000 yanıt tahmini bu pilotun ortalamasının ölçeklenmesidir, sabit ücret değildir.

Süreler tam LLM yanıtının dönmesine kadardır; retrieval/arayüz veya ilk token
süresi değildir. Sonnet kayıtları önceki koşudan yeniden kullanıldı.
Haiku'nun dört koşusu birbirinden sonra çalıştı. Bu ölçümler kontrollü
kapasite testi veya her ortam için model hızı iddiası değildir.

## Referans alıntılarla 12 kritik soru

Cevaplar önceki Sonnet/Qwen incelemesindeki kaynak ve ölçütlerle tek tek
karşılaştırıldı. Kaynakların güncel yürürlüğü uzman tarafından doğrulanmış
değildir. Tamlık; gerekli koşullar, istisnalar ve belirsizlikte açıklama
isteme davranışını kapsar. Kaynak uyumu; eklenen iddiaların verilen
alıntılarla desteklenmesini kapsar. Atıf ölçütü yanlış başlık kullanmayı
denetler; hiç başlık anılmayan yanıtta ayrıca sunum eksikliği not edilir.

| Ölçüm | Sonnet 5.5 | Haiku adaptive/medium | Haiku disabled/high |
|---|---:|---:|---:|
| Tamamlanan istek | 12/12 | 12/12 | 12/12 |
| Ortanca üretim süresi | 3,58 sn | 4,97 sn | 2,62 sn |
| Kaynakla uyumlu yanıt | 12/12 | 12/12 | 10/12 |
| Gerekli koşulları/davranışı tam karşılayan yanıt | 11/12 | 10/12 | 9/12 |
| Hem kaynakla uyumlu hem tam yanıt | 11/12 | 10/12 | 8/12 |
| Hata / boş / kesilen yanıt | 0/0/0 | 0/0/0 | 0/0/0 |
| Kayıtlı API maliyet tahmini | 0,086486 USD | 0,0071597 USD | 0,0041223 USD |

[Adaptive ölçümler](adaptive/oracle/metrics.json),
[karşılıklı cevaplar](adaptive/oracle/answers.md),
[inceleme gerekçeleri](haiku-oracle.review.json);
[disabled ölçümler](oracle/metrics.json),
[karşılıklı cevaplar](oracle/answers.md),
[inceleme gerekçeleri](haiku-direct-oracle.review.json).
İncelemelerde cevap ve prompt SHA-256 değerleri korunur.

| Örnek | Adaptive/medium | Disabled/high |
|---|---|---|
| Lisans mazeret sınavı, BAKAY-014 | Süre, evrak, sağlık/diğer mazeret ayrımı ve kurul kabulü birlikte | Süre, evrak ve kurul kabulü var; sağlık raporunu genel zorunluluk gibi başlatması sunum kusuru |
| ALES yazılı/sözlü muafiyeti, BAKAY-025 | 55/eşdeğer, beyan, yazılı muafiyeti ve zorunlu sözlü doğru | Temel şartlar doğru; başta kesin muafiyet bilgisi yok diyor ve muafiyetin uygulanmasını alıntıda bulunmayan ek enstitü değerlendirmesine bağlıyor |
| Sınav itirazı, BAKAY-045 | Düzeyi sorup ayrıntıyı bekletiyor, fakat ders sınavı/tez savunması ayrımını sormuyor | Düzeyi soruyor; sınav türünü sormadan lisans/lisansüstü ders sürelerini veriyor |
| Belirsiz “vize”, BAKAY-046 | Giriş vizesini varsayıyor; anlam netleştirmesi eksik | Giriş vizesini varsayıyor; anlam netleştirmesi eksik |
| Tekrar dersinde devam, BAKAY-049 | Önceden devamı sağlama koşulu ve bireysel uygulamalı ders istisnası korunuyor | Lisans muafiyetini bütün başarısız tekrar derslerine genelliyor; önceki devam koşulunu atlıyor |

30 üretim kaynaklı soruda ayrıca q08 dikkat çekti: disabled yanıtı ilk
cümlede hazırlığı 2/4 yıllık sürelere dahil sayıp devamında “Hazırlık + 2/4 yıl”
diyor; kaynakta hazırlık sonrası dört yıl da verilmişti. Adaptive doğru biçimde
hazırlığın eklendiğini aktardı. q19'da iki Haiku ayarı da burslu programdaki
2,50 koşulunu genel yüksek lisans kabul şartından ayırdı; yanlış kaynak
erişimi yüzünden genel başvuru eşiği yine belirlenemedi. Disabled'ın q30
kişisel not sorusuna genel not itirazı ayrıntısı eklemesi gereksiz konu genişlemesi.
Bu 30 cevabın tamamına uzman kalite puanı verilmedi.

## Ayar, maliyet ve doğrulama

Sonnet `between_tools/high`, 2048 çıktı tokenı; Haiku araçsız koşusu
`disabled/high`, 2048 çıktı tokenı; Haiku düşünme açık koşusu
`adaptive/medium`, 4096 çıktı tokenıyla çalıştı. Adaptive'ın düşünme tokenları
da bütçeye dahil olduğundan üst sınır artırıldı. Prompt'lar aynı, düşünme
modu/çaba/bütçe aynı değildir; bu pratik ayar pilotudur. Örnekleme ve servis
şablonları da tam kontrol edilmez. [Tekrar komutları ve sınırlar](README.md).

- Haiku adaptive 42 istek: **0,0454211 USD**.
- Haiku disabled 42 istek: **0,0258027 USD**.
- Bu denemedeki toplam 84 Haiku isteği: **0,0712238 USD**, yaklaşık **7,1 cent**.
- Önceki 42 nihai Sonnet isteği karşılaştırma için kullanıldı; yeniden ücretli
  Sonnet çağrısı yapılmadı. Onların kayıtlı tahmini **0,572344 USD**.
- İstek hatası, boş yanıt, çıktı sınırında kesilme veya otomatik tekrar olmadı.
- API'nin döndürdüğü kullanım sayaçları [9 Ekim tarifesiyle](https://platform.claude.com/docs/en/about-claude/pricing)
  hesaplandı. Bütün prompt'lar 100.000-token Haiku sınırının altında;
  önbellek, araç, bölge primi veya Batch API kullanılmadı. Bu toplam fatura
  veya kalan kredi bakiyesi iddiası değildir.
- **13 ilgili backend testi** geçti: Haiku düşünme kapalı isteği, fiyat
  eşiğinde önbellek tokenlarının dahil edilmesi, iki önbellek süresi, Sonnet
  tarifesi, istek biçimi, hata/tekrar ve snapshot/ayar bütünlüğü kapsandı.
- Dört koşunun 84 cevabı ve iki inceleme dosyası, kaynak/prompt/cevap
  hash'leri ve kayıtlı kullanım/maliyet bakımından doğrulandı.
- API anahtarı `.env` içinde, git dışında tutuldu; yeni bağımlılık eklenmedi.
  Canlı uygulamanın model ayarı değiştirilmedi.

## Kullanım önerisi

Maliyet öncelikliyse Haiku adaptive/medium daha dengeli aday: bu seçilmiş
kritik soru paketinde disabled'a göre iki ek yanıtı doğru/tam aktardı,
42 isteğin toplamında Sonnet'ten yaklaşık **12,6 kat ucuz** oldu.
Sonnet bu pilotta hem daha hızlı hem kritik sorularda biraz daha iyi.
Basit SSS için Haiku, birden fazla koşul/istisna içeren mevzuat için Sonnet
yaklaşımı değerlendirilebilir; yönlendirme ve saklı test henüz yok.
Mevcut retrieval hataları ve belirsiz “vize” sorusu yalnız model değişimiyle
çözülmedi. Kalite kararı için bağımsız insan incelemesi gerekir.
