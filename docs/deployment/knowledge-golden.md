# Hazır cevaplar, golden dataset ve panelden kotalar — v0.4.0

18 Ekim 2026: kullanıcı canlı yayını istedi. **Paket hazır, sunucuya yayın
henüz yapılmadı.** HTTPS üzerinde mevcut v0.3.3 sağlıklı.
SSH kontrol soketi kapanmış; anahtarla otomatik giriş reddedildi. Kullanıcıdan
mevcut yetkili bağlantıyı yeniden açması istendi; parola istenmedi/kaydedilmedi.

## Hazırlanan yayın

- Yayın commit'i `c8e05b05c3489547569219d64ce6da52cc3cef18`.
- Dal `codex/knowledge-golden-live`; GitHub `main` de bu commit'e ilerletildi.
- Son canlı `61e183134b619d49ef081d30b8d849d878e38229` bu commit'in atasıdır.
  v0.3.2 geri bildirim/IP, v0.3.3 karakter düzeltmesi ve canlı aşamalar korunur.
- VERSION, frontend paket/kilit sürümleri ve CHANGELOG v0.4.0'a eşitlendi.
- Birleştirilmiş sürümde 205 backend testi ve `/api` adresiyle üretim
  derlemesi geçti. SSE istemci IP regresyonu da canlı daldan korundu.
- Arayüz paketi SHA256:
  `9eed91088b2bd12e53cb0d801505793bd2161abb6bf0049f494f72c9d2dbcb4a`.

Git dışındaki yerel `tmp/ktmu-deployment/knowledge-golden-live/` dizini:
`frontend-next.tar.gz`, `publish.sh`, `verify-live.py`, `verify-private.py`.
Özel ortam, anahtarlar, veri, QA veritabanı ve model önbelleği pakette yoktur.

## Yayın ve doğrulama akışı

1. Canlı commit, temiz Git ağacı, servisler ve disk doğrulanır. Beklenmeyen
   tabanda araç değişiklik yapmadan durur.
2. Paket hash'i ve Linux'ta 205 test doğrulanır. SQLite çevrimiçi yedeği
   `/var/backups/bakay/knowledge.<UTC zaman>/` altında root'a özel saklanır.
3. Geçiş yedek kopyada denenir; sorgu/geri bildirim/kota satırları korunur.
   Aday arayüz 127.0.0.1:3008 üzerinde sürüm/JS/CSS/panel özellikleriyle denenir.
4. Önceki kod kimliği ve `.next`,
   `/opt/bakay/runtime/frontend-before-knowledge.<UTC zaman>/` altında korunur.
   Eski statik dosyalar açık sekmeler için yeni derlemeye eklenir.
5. Kod ve arayüz değiştirilir; backend/frontend yeniden başlatılır. Sağlık,
   v0.4.0, Haiku 5.5 ve 39.659 parça doğrulanır. Altı kaynaklı örnek yalnız
   **taslak** olarak eklenir; QA önerileri taşınmaz, otomatik onay verilmez.
6. Hata halinde önceki kod/arayüz geri alınır. Eklenen veritabanı tabloları
   bırakılır; yayın sırasındaki kullanıcı kayıtları geri dönüşte silinmez.
7. HTTPS sayfalar, statik dosyalar ve özel uçların 401 koruması; yetkili panel
   okuması, yabancı Origin reddi, gerçek kaynaklı sohbet ve tarayıcı formu
   doğrulanır. Sonuçlar `output/knowledge-golden-live/` altında saklanır.

Apache, özel ortam, onaylı cevaplar, mevcut kotalar ve indeks bu yayın
aracı tarafından yeniden yapılandırılmaz. Yeni panel ayarları ilk kayda kadar
canlı ortamın mevcut kota değerlerini kullanır.
