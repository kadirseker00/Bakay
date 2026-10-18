# Canlı aşamalar — yayın kaydı

18 Ekim 2026: kullanıcı onayıyla **yayın tamamlandı**. Kullanıcının yeniden
açtığı SSH kontrol bağlantısıyla temiz canlı taban doğrulandı ve
`fd95c7dbaf0ca8a69f51f2199d8556483eb4fd47` sürümüne geçildi.

- Aday arayüzün ana sayfası ve bağlı JS/CSS dosyaları HTTP 200 verdi.
- Canlı Linux ortamında 165 test geçti; backend, frontend, Apache ve
  izleme/yedekleme timer'ları aktif.
- Gerçek HTTPS isteğinde ilk aşama **0,16 saniyede**, beş kaynaklı sonuç
  **53,86 saniyede** ulaştı. Arşiv açılışı, arama, karşılaştırma, değerlendirme,
  yanıt hazırlama ve bitiş bildirimleri sonuçtan önce ayrı ayrı alındı.
- HTTPS ana sayfa ve sağlık ucu 200, özel metrikler oturumsuz 401 verdi.
- HTTPS üzerindeki 10 JS/CSS dosyası ve yanıtta gösterilen resmî PDF HTTP 200
  verdi.
- Tarayıcıda yeni ana örnek, yanıt beklerken sade aşama metinleri, tamamlanan
  adımlar ve kaynaklı sonuç doğrulandı.
- Kanıtlar: yerel `output/live-progress/live-events.json`, `live-verification.json`
  ve `live-answer.json`.

Geri dönüş kopyası:
`/opt/bakay/runtime/frontend-before-progress.20261018T121312Z`.
Önceki `.next`, kod dalı ve commit bilgisi burada saklanır. Önceki kod
`codex/ses-alerts`, `06ba71a1f9bb372939294b12cf92f9684532cfb6`.

## Hazırlanan sürüm

- Ana geliştirme: `fc43159` ve `d097348` (`main` üzerinde GitHub'a gönderildi).
- Yayın dalı: `codex/live-progress`, `fd95c7d`.
- Taban: son kayıtlı canlı `codex/ses-alerts`, `06ba71a1`.
- Bu dalda yalnız gerçek işlem aşamaları, sade dil, kitap animasyonu, süre/
  tamamlanan adımlar ve arama örnekleri var. Bekleyen geri bildirim değişiklikleri
  alınmadı. Canlı tabanda olmayan istemci IP bağlamı bağımlılığı kaldırıldı.
- Yayın dalında 165 test ve `/api` adresiyle üretim derlemesi geçti.
- Geliştirme dalında 171 test ve ayrıca 6 ağ/karakter bölünmesi, hata, yarım
  yanıt ve JSON uyumluluk kontrolü geçti. Tarayıcıda aşamalar sonuçtan önce
  görüntülendi; örnek veriyle 39 saniyelik istek sonuçlandı.

Yerel paket: `tmp/ktmu-deployment/live-progress/frontend-next.tar.gz`.
SHA256: `0f61b716a4cbfd87e7dbc6afe2f8870c4aaf523ed0927f4542ee717e12482a37`.
Yayın aracı: `tmp/ktmu-deployment/live-progress/publish.sh`; Bash sözdizimi geçti.
Derleme ve paket Git dışında, kaynak sürüm GitHub'da tutulur.

## Uygulanan yayın akışı

1. `/opt/bakay` kod sürümü, değişiklik durumu, disk ve servisler salt okunur
   doğrulanır. Canlı sürüm beklenenden farklıysa yayın aracı değişiklik yapmadan
   durur; paket mevcut sürüme göre yeniden değerlendirilir.
2. Paket ve yayın aracı `/opt/bakay/runtime/live-progress/` içine aktarılır;
   SHA256 eşleştirilir.
3. Araç aday arayüzü 127.0.0.1:3007 üzerinde dener; anasayfa ve JS/CSS dosyalarını
   kontrol eder. Kod geçişinden sonra Linux testlerini çalıştırır.
4. Önceki `.next` ve kod kimliği geri dönüş için saklanır. Servisler yeni sürüme
   geçirilir; hata olursa önceki kod ve arayüz geri alınır.
5. Gerçek HTTPS üzerinden durum bildirimlerinin yanıt bitmeden geldiği ölçülür;
   kaynaklı sonuç, belge bağlantısı, anasayfa/JS/CSS ve özel metriklerin 401
   koruması doğrulanır. Tarayıcıda canlı aşamalar ve animasyon gözlenir.

Özel ortam, API anahtarı, indeks ve model önbelleği bu pakete dahil değildir.
Apache ayarı değiştirilmedi; gerçek HTTPS akışında tamponlama olmadığı doğrulandı.
