# Sürüm geçmişi

Sürümler `MAJOR.MINOR.PATCH` biçiminde tutulur. Yeni özellikler MINOR,
uyumlu hata düzeltmeleri PATCH, kırıcı değişiklikler MAJOR artırır.
`0.x.y` geliştirme aşamasını belirtir. Ana kaynak kökteki `VERSION` dosyasıdır;
frontend paket ve kilit dosyasının sürümleri onunla birlikte güncellenir.
Git sürüm etiketleri `vMAJOR.MINOR.PATCH` biçimindedir.

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
