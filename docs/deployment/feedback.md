# Geri bildirim ve admin IP — yayın kaydı

18 Ekim 2026: sade geri bildirim formu ve admin IP görünümü canlıya alındı.
İlk geliştirme commitleri `a679b2d` ve `74dfe6e`, GitHub `main` dalındaydı;
canlı `codex/live-progress` dalında bulunmadıkları için sitede görünmüyordu.

## Yayın

- Dal: `codex/feedback-live`.
- Son yayın: `fc11c5055ed09ec977c7de337d96d8923f10da09`, sürüm `0.3.2`.
- Önceki canlı taban: `fd95c7dbaf0ca8a69f51f2199d8556483eb4fd47`.
- Önce geri bildirim `13ccfe3` ile yayımlandı. Oturum sırasında eklenen sürüm
  kuralı uygulanarak VERSION, paket ve kilit dosyası `0.3.2` yapıldı;
  arayüz tekrar derlenip API ile aynı sürüme getirildi.
- Form: Bilgi güncel değil, İlgisiz yanıt, Yanlış cevap ve Diğer. Açıklama
  yalnız Diğer seçilince, ad alanı İsim ekle bağlantısıyla açılır.
- İstemci IP adresi JSON ve SSE sorgularında güvenilir proxy denetimiyle
  kaydedilir. Admin listesi ve ayrıntıları IP, neden, açıklama ve adı gösterir.
  Önceki kayıtlarda bulunmayan IP için Kaydedilmemiş yazılır.

## Doğrulama

- Yerelde ve canlı Linux ortamında 171 backend testi geçti. Üretim arayüzü
  `/api` adresiyle derlendi; aday sayfa ve bağlı varlıklar yayın öncesi denendi.
- Veritabanının çevrimiçi yedeği alındı. Kopyada ek sütun geçişi denendi;
  ilk geçişteki 39 sorgu ve 5 geri bildirim korundu.
- HTTPS ana sayfa, monitor, health ve 10 JS/CSS dosyası 200; özel metrik ve
  stats uçları oturumsuz 401 verdi (15 kontrol).
- Gerçek Chrome oturumunda dört seçenekli form, Diğer açıklaması, isteğe bağlı
  ad ve Kaydedildi sonucu doğrulandı. Aynı sorgunun admin ayrıntısında IP,
  neden, açıklama ve ad görüldü. Test kaydı “Yayın kontrolü” adıyla ve
  “Yayın doğrulama testi; yanıt kalitesi değerlendirmesi değildir.” açıklamasıyla
  bırakıldı; yanıt kalitesi analizi yapılmadı.
- Son `0.3.2` yayını da 171 Linux testini ve 15 HTTPS kontrolünü geçti;
  API ve arayüzün aynı yeni sürümü gösterdiği doğrulandı. Önceki tarayıcı
  test kaydı dahil 40 sorgu ve 6 geri bildirim korundu.
- Backend, frontend, Apache, izleme ve yedekleme timer'ları aktif.
- Yerel kanıtlar: `output/feedback-live/https-checks.json`, `live-form.png`,
  `live-saved.png` ve `live-admin.png`. Görseller ilk işlev yayınına aittir;
  sürüm eşitlemesi `https-checks-v0.3.2.json` ile doğrulandı.

## Geri dönüş

Geri bildirimden önceki kod/arayüz:
`/opt/bakay/runtime/frontend-before-feedback.20261018T122452Z`.
Veritabanı yedeği: `/var/backups/bakay/feedback.20261018T122452Z`.

Her yayında önceki `.next`, Git commit ve dal adı birlikte saklanır.
Son sürüm eşitlemesinin geri dönüş kopyası
`/opt/bakay/runtime/frontend-before-feedback.20261018T123514Z` içindedir;
aynı yol `runtime/feedback-live/rollback-path.txt` dosyasında kayıtlıdır.
Geri dönüşte kod ile arayüz birlikte değiştirilir; eklenen veritabanı sütunları
korunarak yeni geri bildirim kayıtlarının kaybı önlenir.

Son paket SHA256:
`4be4fdd25283ab0ad284980c0e334e226350d02d5f2b2877f81d6314ba15104b`.
Paket ve yayın aracı: yerel `tmp/ktmu-deployment/feedback-live/`,
sunucuda `/opt/bakay/runtime/feedback-live/`.
