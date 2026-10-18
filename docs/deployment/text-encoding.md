# Üniversite adı karakter düzeltmesi

18 Ekim 2026: kullanıcının açık isteğiyle **0.3.3 canlıya alındı**.
Canlı commit `61e183134b619d49ef081d30b8d849d878e38229`, yayın dalı
`codex/text-encoding-live`. Taban, geri bildirim/IP yayını v0.3.2 `fc11c50`.

## Hatanın kaynağı ve kapsam

`data/raw/web/docs_ogrenci_el_kitabi_kilavuz_2010_tr.pdf` dosyasının PDF
metadatasındaki başlık `Kırgızistan-Tьrkiye Manas Ьniversitesi`.
Eski indeks bu başlığı taşıdığı için modelin prompt'una ve kaynak kartlarına da
bozuk yazım gidiyordu.

`repair_turkish_encoding`, yalnız bilinen Türkçe Türkiye/üniversite kökleri
ve Türkçe eklerindeki Kiril `ь` / `Ь` harflerini `ü` / `Ü` yapar.
Kırgızca/Rusça kelimeler, hükümler ve belge adresleri korunur.
Yeni metin/başlık çıkarımı ile mevcut indeksin hibrit ve salt vektör erişimi
aynı düzeltmeyi uygular. Chroma verisi değiştirilmez; yeniden indeksleme gerekmez.

## Hazırlık

- Ana düzeltme: `4dfb700`; ayrı yayın dalı `codex/text-encoding-live`.
- Yerelde 177 backend testi ve `/api` adresiyle 0.3.3 üretim derlemesi geçti.
- Altı regresyon testi: büyük/küçük harf ve ekler, geçerli Kiril metinleri,
  PDF metadata, mevcut hibrit indeksin prompt/atıf/bağlantı yolu ve vektör arama.
- Arayüz paketi SHA256:
  `3f477c6691e18f35f763bc8dc347a673cb721b6bd5d3aa9b5663c7fee94771e9`.
- Yayın aracı ve doğrulama betiği `tmp/ktmu-deployment/text-encoding-live/`
  altında; özel ortam, veri ve anahtarlar pakete dahil değil.

## Canlı doğrulama

- Linux ortamında 177 test geçti. Aday arayüz ve JS/CSS dosyaları yayından
  önce ayrı portta doğrulandı; API ve arayüz HTTPS üzerinden 0.3.3 gösteriyor.
- Haiku 5.5, 39.659 parça ve iki uygulama servisi sağlıklı; yeniden başlama
  sayıları 0. Apache, izleme ve yedekleme timer'ları aktif.
- HTTPS üzerinden 10 JS/CSS dosyası 200, özel metrikler oturumsuz 401.
- İlk kaynaklı kütüphane sorusu 5 kaynakla 55,99 saniyede tamamlandı;
  bu ilk sorgu soğuk indeks açılışını içerir. Gösterilen belge bağlantısı 200.
- Hatanın olduğu öğrenci el kitabını getiren “Aynı anda iki örgün lisans kaydı
  mümkün mü?” sorusu 9.096 ms içinde 5 kaynakla yanıtlandı. İlk kaynak başlığı
  ve yanıttaki atıf **Kırgızistan-Türkiye Manas Üniversitesi** olarak doğru.
- Kontrol sorgusu `ee1f0bade5a54420a30d971e2872283b`; canlı SQLite kaydında
  prompt, yanıt ve kaynak JSON'unda doğru başlık, sıfır bozuk yazım doğrulandı.
- Kanıtlar Git dışındaki `output/text-encoding-live/` altında:
  `answer.json`, `verification.json`, `booklet-answer.json`,
  `booklet-verification.json`.

Geri dönüş kopyası:
`/opt/bakay/runtime/frontend-before-text-encoding.20261018T123717Z`.
Önceki kod `codex/feedback-live`, `fc11c5055ed09ec977c7de337d96d8923f10da09`.
Özel ortam ve indeks değiştirilmedi. Açık eski sekmelerin statik dosyaları korundu.
