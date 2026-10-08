# Sonnet 5.5 pilot sonucu — 9 Ekim 2026

Yerel BAKAY uygulaması Claude Sonnet 5.5'e bağlandı ve canlı sohbetle
doğrulandı. Pilot, daha güçlü modelin kaynakları yorumlama ve koşulları tam
aktarma bakımından yararlı olduğuna işaret ediyor. Eksik veya yanlış kaynak
erişimi ve belirsiz soru davranışı için ayrıca çalışma gerekiyor.

**Geliştirme pilotu:** 30 üretim kaynaklı soru ve doğru referans alıntıları
verilen 12 kritik soru. İki model her koşulda aynı prompt metni ve kaynakları
kullandı. Sorular geliştirmede görülmüş, etiketleri insan onayı bekleyen
taslaklardır. Sonuç bağımsız gold testi veya genel doğruluk yüzdesi değildir.

## Yanıt üretimi

| Ölçüm | Qwen3.5 9B | Sonnet 5.5 |
|---|---:|---:|
| Üretimden bulunan kaynaklarla tamamlanan istek | 30/30 | 30/30 |
| Ortanca üretim süresi | 13,21 sn | 6,04 sn |
| p95 üretim süresi | 20,94 sn | 9,65 sn |
| 10 saniyeden kısa üretim | 11/30 | 29/30 |
| Boş yanıt / API hatası | 0/0 | 0/0 |
| Çıktı sınırında kesilen yanıt | 1/30 | 0/30 |
| Ortalama çıktı tokenı | 300,7 | 751,2 |
| Kayıtlı API maliyet tahmini | — | 0,485858 USD |

[Ham karşılıklı yanıtlar](retrieved/answers.md), [ölçümler](retrieved/metrics.json).
Qwen yerel Apple M3 Max/Ollama'da, Sonnet bulut API'sinde çalıştı. Süreler
tam yanıtın dönmesine kadardır; retrieval, arayüz veya ilk token süresi değildir.
İki karşılaştırma modeli ardışık çalıştı. Qwen koşusu sırasında iki canlı
Sonnet sohbet üretimi ve teknik kontroller yapıldı; süreler kontrollü kapasite
ya da evrensel model hızı iddiası olarak yorumlanmamalıdır.

Qwen sıcaklık 0,3, tohum 42, `think=false`, 8192 bağlam ve 1024 çıktı
tokenıyla çalıştı. Sonnet `between_tools`, `effort=high`, 2048 çıktı tokenıyla
çalıştı; özel sıcaklık/top_p/top_k gönderilmedi. Tokenizer, servis şablonu ve
çıktı bütçeleri farklıdır. Sonnet daha uzun cevaplar üretiyor; bu çalışma
eşit bütçeli bir model ağırlığı karşılaştırması değildir.

İlk Sonnet 1024-token koşusunda 10/30 yanıt kesildi. Sonuçlar
`sonnet-retrieved.*` dosyalarında korunur; son tablo yeni
`sonnet-retrieved-2k.*` koşusunu kullanır. Varsayılan Sonnet çıktı bütçesi
bu nedenle 2048'e çıkarıldı. Ek ücretli ısıtma veya otomatik tekrar yapılmadı.

## Doğru kaynaklarla 12 kritik soru

Bu koşulda yalnız doğrulanabilir arşiv alıntıları verilir. Kaynakların güncel
yürürlüğü doğrulanmış değildir. Cevaplar Codex tarafından tek tek alıntılarla
karşılaştırıldı; tek yapay zekâ incelemesidir, insan uzman onayı değildir.

| Ölçüm | Qwen3.5 9B | Sonnet 5.5 |
|---|---:|---:|
| Tamamlanan istek | 12/12 | 12/12 |
| Ortanca üretim süresi | 6,37 sn | 3,58 sn |
| Kaynakla uyumlu yanıt | 10/12 | 12/12 |
| Gerekli koşulları/davranışı tam karşılayan yanıt | 7/12 | 11/12 |
| Hem kaynakla uyumlu hem tam yanıt | 6/12 | 11/12 |
| Kesilen / boş / hatalı istek | 0/0/0 | 0/0/0 |
| Kayıtlı API maliyet tahmini | — | 0,086486 USD |

[Cevap dökümü](oracle/answers.md), [ölçümler](oracle/metrics.json),
[Qwen incelemesi](qwen-oracle.review.json), [Sonnet incelemesi](sonnet-oracle.review.json).
İnceleme dosyalarında gerekçeler, cevap ve prompt SHA-256 değerleri vardır.
Küçük ve seçilmiş 12 soru üzerinde anlamlılık veya genellenebilir üstünlük
iddiası yapılmadı. Kaynak atfı ölçütü yanlış başlığa atıf yapmayı denetler;
Qwen BAKAY-001 gibi bir başlığı açıkça anmayan yanıtların atıf sunumu ayrıca
zayıf olarak not edilmiştir. Açık Türkçe puanı yazım kusursuzluğu değildir.

| Örnek | Qwen | Sonnet |
|---|---|---|
| Lisans mazeret sınavı, BAKAY-014 | Süre/evrak doğru; kurulca mazeretin kabul edilmesi eksik | Süre/evrak ve Birim Yönetim Kurulu kabulü birlikte |
| Lisansüstü mazeret, BAKAY-036 | 3 iş günü ve başlangıç doğru; rapor/kurul koşulu eksik | Süre, başlangıç ve rapor/kurul ayrımı birlikte |
| Tekrar dersinde devam, BAKAY-049 | Lisansta devamsızlıktan kalınca da muafiyet varmış gibi ifade; kaynakta olmayan komisyon ekliyor | Devamı önceden sağlama koşulu ve bireysel uygulamalı ders istisnası korunuyor |
| Sınav itirazı, BAKAY-045 | Süreleri ayırıyor; düzey/sınav türünü sormuyor | Süreleri ayırıyor ve düzey/sınav türünü soruyor; ayrıntıları açıklamadan önce soru sorma kuralına tam uymuyor |
| Belirsiz “vize”, BAKAY-046 | Bilgi yok diyor; anlamı netleştirmiyor | Giriş/oturum vizesini varsayıyor; anlamı netleştirmiyor |

Üretimden bulunan kaynaklarda da fark görüldü: q08'de Qwen hazırlığı
programın 2/4 yıllık süresine dahil gibi aktardı; Sonnet hazırlığın program
süresine ek olduğunu belirtti. q19'da Qwen özel burslu kabuldeki 2,50
eşiğini genel kabul şartına uyguladı; Sonnet programları ayırıp genel
başvuru şartını bu kaynaklarda bulamadığını söyledi. Buna rağmen ilgisiz
Erasmus ve personel başvuru koşullarını da uzun yanıtına eklemesi istenmiyor.
30 üretim kaynaklı yanıtın tümü için uzman doğruluk puanı verilmedi.

## Canlı uygulama

`/health`, `anthropic / claude-sonnet-5-5` ve 39.659 parça bildirdi;
backend ve frontend HTTP 200 döndü. [Canlı yanıtlar](live.json) ve
[tam kaynak/prompt kayıtları](live.contexts.json) saklandı.

- “Başka kurumdan aldığım dersi saydırabilir miyim?” sorusunda mevcut
  kaynaklı ön cevap/öğrenim düzeyi kapısı çalıştı; bu adım LLM üretimi değildir.
- “Lisans için soruyorum.” takibinde Sonnet doğru konuyu korudu; 5 yıl,
  en az CC, AKTS/içerik uygunluğu, toplam AKTS'nin en fazla 1/3'ü, belge
  ekleri, Bölüm Başkanlığı ve kurul/onay süreçlerini birlikte aktardı.
- Öğrenci e-postasının ilk şifresi sorusunda kütüphane platformu üyelik
  şifrelerini öğrenci e-postası şifresi gibi göstermedi; kaynakta prosedür
  bulunmadığını söyledi. Doğru prosedürün kaynaklara eklenmesi hâlâ gerekli.

## Maliyet ve teknik doğrulama

42 nihai Sonnet isteği: **0,572344 USD**. İlk 1024-token teşhis koşusu:
**0,485922 USD**. Kayıtlı deney toplamı: **1,058266 USD**.
Canlı sohbetteki iki ek üretimin kullanım sayaçları mevcut üretim
telemetrisinde tutulmadığı için bu toplama dahil değildir; kuruluş faturası
veya kalan kredi bakiyesi iddiası yapılmıyor. Team API kredisi kullanıcıdaki
fatura kaydına göre 7 Kasım 2026'da sona eriyor.

- Sonnet API model erişimi HTTP 200; gerçek üretimler ve aynı girdili
  karşılaştırma tamamlandı. API anahtarı `.env` içinde, git dışında.
- **103 backend testi** geçti; gerçek HTTP istek biçimi, düşünme/metin
  ayrımı, anahtar eksikliği, hata sonrası durma, kaldığı yerden devam,
  kaynak/ayar bütünlüğü, kullanım/maliyet ve model sağlık bilgisi sınandı.
- 50 taslak kaydın 5 ham kaynak/21 alıntı birimi hash ile doğrulandı;
  `pending_review` durumları korundu. Yanıtlar ve inceleme hash'leri kontrol edildi.
- Yeni Python bağımlılığı gerekmedi; mevcut `httpx` ile resmi Messages API
  kullanıldı. Sonnet diğer sağlayıcılarla aynı `generate(prompt)` arayüzünde.

## Sonraki kalite işi

Sonnet yerel uygulamada pilot sağlayıcı olarak kullanılıyor. Kaynak erişimi
iyileştirilmeden genel kabul koşulu, yurt belgesi ve e-posta ilk şifresi gibi
eksik bağlamlı sorular tamamen çözülmüyor. Eğitim ücreti sorusunda Orhun
programının özel kuralından genel harç varlığına yapılan çıkarım da yanıltıcı
olabilir. Belirsiz vize/sınav sorularında açık anlam/düzey sorusu ve yanıttaki
gereksiz konu genişlemesi ayrıca düzeltilmeli. Nihai kurum doğruluğu için
bağımsız insan incelemesi ve ayrı saklı test gerekiyor.
