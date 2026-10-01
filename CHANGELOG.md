# Sürüm geçmişi

Sürümler `MAJOR.MINOR.PATCH` biçiminde tutulur. Yeni özellikler MINOR,
uyumlu hata düzeltmeleri PATCH, kırıcı değişiklikler MAJOR artırır.
`0.x.y` geliştirme aşamasını belirtir. Ana kaynak kökteki `VERSION` dosyasıdır;
frontend paket ve kilit dosyasının sürümleri onunla birlikte güncellenir.
Git sürüm etiketleri `vMAJOR.MINOR.PATCH` biçimindedir.

## 0.3.0 — 2026-10-01

- DomainRAG yönteminin Türkçe KTMÜ uyarlaması: 106 geliştirme senaryosu ve
  21 kaynak sayfa/bölümü; soru/cevap/kaynak/geçmiş alanları ve izlenebilir hash'ler.
- Sohbet, yapılandırılmış bilgi, sadakat, gürültü, güncellik ve çoklu belge pilotları.
- Paket üretimi, kaynak doğrulama, canlı erişim ölçümü ve mevcut model karşılaştırma
  aracına sabit bağlam hazırlama komutları.
- Taslak etiketleri korunur; referans cevaplar prompt'a, train/saklı test kayıtları
  geliştirme paketine veya soru-cevaplar üretim indeksine taşınmaz.

Doğrulama: 87 backend testi ve ham kaynak hash kontrolü. 94 cevaplanabilir
geliştirme sorgusunda en az bir alıntı ilk 5'te 69/94, bütün alıntılar 58/94.
Altı Qwen sabit bağlam deneyi tamamlandı; yanlış şart/istisna aktarımı bulguları
`docs/evaluation/domainrag-tr-v1/` altında kaydedildi. Bunlar gold doğruluk skoru değildir.

## 0.2.2 — 2026-10-01

- Yanıtın kısa sonucundan sonra temel şartları ayrı maddelerde sun.
- Süre, asgari not, kredi/AKTS sınırı, içerik uygunluğu ve gerekli belgelerin
  kritik değerlerini kalın vurgula; şartları parantez içine gömme.
- Kaynaktaki alt/üst sınırların yönünü ve ilgili koşulları koruma talimatı eklendi.
- Süre, asgari harf notu ve oranlar mevcut cevap metninden otomatik kalınlaştırılır;
  sayı/hüküm değiştirilmez, mevcut Markdown ve bağlantılar korunur.

Doğrulama: 78 backend testi; canlı iki ders saydırma cevabında süre/not vurgusu
ve maddeli sunum, API/arayüz 0.2.2. Bir takip cevabında 1/3 şartı eksildi;
vurgu adımı eksik hükmü geri getirmez. Ayrıntılar `docs/answer-presentation.md`.

## 0.2.1 — 2026-10-01

- Öğrenim düzeyi belirsizken önce ilgili hükmün kısa, tam ilk cümlesini
  kaynak başlığı, madde ve kapsamıyla göster; ardından öğrenim düzeyini sor.
- Başlık soru terimleriyle eşleşmiyorsa, cümle kesilmiş/uzunsa veya sayısal
  şart içeriyorsa ön cevap vermeden açıklama iste. Alıntı için LLM çağrısı yapılmaz.
- Kısa düzey seçimi, ön cevapla birlikte de ilk kullanıcı sorusunu korur.

Doğrulama: 75 backend testi; iki genel ders saydırma sorusunda Madde 25
ön cevabı ve lisans takip sorusunda doğru kaynak; API/arayüz sürümü 0.2.1.
Koşulların eksiksiz aktarılması henüz garanti edilmez.

## 0.2.0 — 2026-10-01

- Aynı sohbet içinde son altı turdan bağlam çözümü, tarayıcı geçmişi ve yeni sohbet.
- LaBSE + BM25 hibrit erişim, Türkçe önekler ve aynı metinlerin tekilleştirilmesi.
- Öğrenim düzeyi belirsizliğinde kapsam açıklaması ve kısa kapsam seçiminin ilk soruyla birleştirilmesi.
- Kesilmiş kaynak parçalarının komşularla tamamlanması.
- Ders saydırma regresyonları, RAG/model ölçümleri ve üniversite veri kümesi araştırması.
- Uygulama adının altında sürüm gösterimi; API ve arayüzün ortak sürüm kaynağı.

Doğrulama: 69 backend testi; ders saydırma için 8/8 hedef ilk beşte.
90 geliştirme sorgusunda hedef alıntı erişimi 27/90 → 65/90.
Bu ölçümler insan onaylı cevap doğruluğu değildir; üretimde koşul eksiltme kusurları sürer.

## 0.1.0 — önceki geliştirme sürümü

- Kaynak gösteren kurumsal soru-cevap API'si ve Next.js arayüzü.
- ChromaDB/LaBSE erişimi, yerel Qwen3.5 9B ve Turkish-Gemma karşılaştırmaları.
- Aday öğrenci rehberi ve kaynak bağlı değerlendirme taslakları.
