# Panelden kullanım sınırları

Yönetim panelindeki **Kullanım koruması → Kullanım sınırlarını düzenle** bölümünden IP
başına dakika/saat, sistem genelinde dakika/son 24 saat ve global/IP başına
eşzamanlı iş sınırları değiştirilebilir. Kaydetme anında sonraki isteklerde
uygulanır; yeniden başlatma gerekmez. Çalışan cevaplar tamamlanır, kullanım
sayaçları sıfırlanmaz. Son 24 saat kayan penceredir; gece yarısında yenilenmez.

İlk kayda kadar `.env` değerleri kullanılır. Panel ayarları SQLite'ta saklanır;
yeniden başlatmada korunur ve `.env` değerlerinin önüne geçer. Başlangıç
değerlerini doldurmak yalnız formu doldurur; ayrıca kaydetmek gerekir.

| Alan | Kabul edilen değer |
|---|---|
| IP / dakika | 1–1.000 |
| IP / saat | 1–10.000, dakika sınırından küçük olamaz |
| Global / dakika | 1–1.000 |
| Global / 24 saat | 1–100.000 |
| Global eşzamanlı | 1–16 |
| IP eşzamanlı | 1–16, global eşzamanlı sınırını aşamaz |

`GET /monitor/rate-limits` oturum gerektirir. `PUT /monitor/rate-limits`
oturuma ek olarak kaynak kontrolü ve güncel `revision` gerektirir; eski sürüm
409 döner. Değişiklik geçmişinde yönetici, zaman ve sınırlar saklanır.
Geri bildirim/giriş kotaları, gövde sınırı ve CAPTCHA bu formdan değişmez.
Kalıcı kota deposu okunamazsa yeni üretim 503 ile durur.

Dağıtım mevcut tek backend worker düzenini kullanır: eşzamanlılık sayacı
worker belleğindedir. Birden çok worker için ortak eşzamanlılık kilidi gerekir.
Zaman pencereli kotalar ve ayarlar SQLite üzerinde atomiktir.
