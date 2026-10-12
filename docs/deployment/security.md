# BAKAI hız sınırları ve kötüye kullanım koruması

Ücretli LLM ve küçük sunucunun kaynakları için kademeli koruma uygulanır.
Kotalar kayan zaman aralığıdır; dakika/saat başında topluca sıfırlanmaz.

| Koruma | Varsayılan sınır | Ortam değişkeni |
|---|---|---|
| Sohbet / IP | 10 istek / 60 saniye | `RATE_CHAT_PER_MINUTE` |
| Sohbet / IP | 120 istek / 1 saat | `RATE_CHAT_PER_HOUR` |
| Sohbet / tüm IP'ler | 30 istek / 60 saniye | `RATE_CHAT_GLOBAL_PER_MINUTE` |
| Başlatılan sorgu / tüm IP'ler | 1.000 sorgu / son 24 saat | `RATE_CHAT_GLOBAL_PER_DAY` |
| Aynı anda çalışan sorgu | 2 toplam, 2 / IP | `RATE_CHAT_CONCURRENT`, `RATE_CHAT_CONCURRENT_PER_IP` |
| JSON gövdesi | 128 KiB | `RATE_MAX_BODY_BYTES` |
| Uygulamada gövde okuma | 10 saniye, en çok 16 okuyucu | `RATE_BODY_TIMEOUT` |
| Panel girişi | 5 / IP / 5 dakika; 30 toplam / dakika | Sabit |
| Geri bildirim | 30 / IP / dakika; 120 toplam / dakika | Sabit |

Kampüs veya yurt NAT bağlantısındaki kullanıcılar aynı IP kotasını paylaşır.
IPv6 adres değiştirme ile sınırın aşılmasını azaltmak için aynı /64 ağ tek
istemci sayılır; IPv4 ve IPv4-mapped IPv6 aynı kimliğe bağlanır. Bunlar kullanıcı
hesabı kotaları değildir. Gerçek kullanım ve engelleme sayıları izlenerek
üniversitenin ortak IP'leri için gerekirse sınırlar yükseltilmelidir.

## İstek reddi ve maliyet

Hız/kota/yoğunluk sınırında HTTP **429**, `Retry-After` ve `Cache-Control:
no-store` döner. Sohbet ekranı bekleme süresini gösterir; otomatik yeniden
deneme yapmaz. Büyük gövde 413, yavaş gövde 408, sıkıştırılmış gövde 415 ile
durdurulur. `top_k` 1–8, soru 2.000 karakter, geçmiş 12 mesaj × 2.000 karakter
ve geri bildirim açıklaması 2.000 karakterle sınırlıdır.

IP ve global dakika kotası doğrulamadan önce alınır; geçersiz JSON/şema da
bu kotaya girer. Günlük kota ise yalnız şeması geçerli, eşzamanlı çalışma
izni almış sorgu başlatılırken alınır. Reddedilmiş veya sıraya giremeyen
istek LLM çağırmaz, günlük kotayı tüketmez. Başlatıldıktan sonra başarısız
olan sorgu günlük kotada kalır; bir sorgu hafıza/yeniden yazma nedeniyle
birden fazla LLM çağrısı yapabilir. Bu sınır USD bütçesi veya sağlayıcı kredi
limiti değildir; gerçek maliyet panelin API maliyetleri bölümünden izlenir.

Kotalar SQLite `rate_hits` tablosunda atomik kontrol/yazma ile tutulur.
Canlıdaki kalıcı oturum sırrı ve aynı veritabanıyla servis yeniden başladığında
kotalar korunur. Depoya erişilemiyorsa yeni sorgu 503 ile durur. Panel parolası
aracı oturum sırrını döndürdüğünde IP kimlikleri ve dolayısıyla IP kotaları
yenilenir; global kotalar aynı veritabanında korunur.

Çalışan iş sayacı gerçek senkron worker işinin ömrünü izler; HTTP istemcisinin
bağlantıyı bırakması kotayı erken serbest bırakmaz. Eşzamanlılık ve gövde
okuyucu sayacı süreç içindedir. Canlı systemd **bir Uvicorn worker** kullanır;
birden çok worker/sunucuya geçmeden önce bu sayaçlar paylaşılan bir depoya
taşınmalıdır. Kalıcı istek kotaları çoklu SQLite bağlantısında atomiktir.

## Apache ve gerçek istemci IP'si

Backend yalnız `127.0.0.1:8000` üzerinden çalışır, Uvicorn proxy başlıklarını
yalnız `127.0.0.1` kaynağından kabul eder. HTTPS VirtualHost, kullanıcıdan gelen
`X-Forwarded-For` ve `Forwarded` başlıklarını siler. `ProxyAddHeaders On` gerçek
bağlantı IP'sini ekler. Uygulama yalnız ASGI `request.client` bilgisini kullanır;
istek başlıklarındaki IP'yi kendisi okumaz.

`deploy/apache-proxy.inc` API için `LimitRequestBody 131072`, VirtualHost için
`RequestReadTimeout header=20-40,MinRate=500 body=10-20,MinRate=500` içerir.
`reqtimeout` modülü etkin olmalıdır. Gövde sınırı değiştirilirse Apache ve
uygulama değeri birlikte değiştirilmelidir. Apache yapılandırması yedeklenip
`apache2ctl configtest` başarılı olduktan sonra yeniden yüklenir. TLS yolları
ve diğer VirtualHost'lar korunur.

Resmî kaynaklar: [Apache proxy başlıkları](https://httpd.apache.org/docs/2.4/mod/mod_proxy.html#proxyaddheaders),
[istek zaman aşımı](https://httpd.apache.org/docs/2.4/mod/mod_reqtimeout.html),
[gövde sınırı](https://httpd.apache.org/docs/2.4/mod/core.html#limitrequestbody),
[FastAPI güvenilir proxy](https://fastapi.tiangolo.com/advanced/behind-a-proxy/).

## Panel ve kayıtlar

Yönetici panelindeki **Kullanım koruması** bölümünde IP sınırları, son 24 saat
sorgu kotası, çalışan iş sayısı ve seçilen dönemde engellenen istekler görünür.
Veri yalnız yönetici oturumuyla `/monitor/metrics` üzerinden okunabilir.
Rate tablolarında düz IP yerine amaç ayrımlı HMAC özeti saklanır; soru/gövde
kaydedilmez. Apache'nin mevcut erişim logları ayrı olarak IP tutabilir.

Reddedilen istekler tek tek HTTP olayına yazılmaz; dakika/uç/neden bazında
toplanarak beş saniyede bir SQLite'a aktarılır. Normal kapanışta aktarım yapılır;
beklenmeyen çökmede son beş saniyelik engelleme sayacı kaybolabilir. Yazma
hatasında bellek kuyruğu 256 anahtarla sınırlıdır. Engelleme kayıtları 31 gün
tutulur. Apache'nin uygulamaya ulaşmadan durdurduğu istekler panel sayacına
dahil değildir. Bilinmeyen sorguya geri bildirim yazılmaz; aynı sorguya yeniden
oy verildiğinde yeni satır eklemek yerine mevcut oy güncellenir.

Bu katman uygulama kötüye kullanımını ve ücretli çağrı sayısını sınırlar.
Dağıtık saldırıyla ağın/Apache bağlantı kapasitesinin doldurulması için üniversite
ağında ayrıca DDoS/WAF koruması gerekir; bu uygulama her botu ayırt etmez.

## Doğrulama

`backend/` içinde `.venv/bin/python -m unittest discover -s tests` çalıştırılır.
`tests/test_abuse.py` kalıcı ve atomik kotaları, IPv6/başlık taklitlerini,
eşzamanlılık ve günlük bütçe ayrımını, büyük/parçalı/yavaş gövdeleri, disk
hatasını, geri bildirim spamini ve özel panel sayaçlarını doğrular.
Ücretli çağrı yapmadan canlı rate testi: güvenilir localhost üzerinden ayrı
test IP'siyle boş soru gönderilir; ilk 10 istek 422, 11. istek 429 olmalıdır.
Bu test üretim sorgu kotasını tüketmez.
