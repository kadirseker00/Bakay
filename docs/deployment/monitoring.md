# BAKAI yönetim ve izleme paneli

Panel adresi: **https://bakai.manas.edu.kg/monitor**.
Kullanıcı adı: **adminbakai**. Panel parolası SSH/root parolasından ayrıdır.

## Gösterilen bilgiler

- Bugün / son 7 gün / son 30 gün: sorgu sayıları, ortanca ve %95 yanıt süresi,
  kaynak erişimi / LLM üretimi süreleri, kaynak gösterme oranı ve geri bildirim.
- `/chat` ve `/feedback` isteklerinin HTTP hata oranı ve son hata kodları.
  Sağlık yoklamaları ve panel yenilemeleri kullanıcı istekleri arasında sayılmaz.
- RAM, disk, çekirdek sayısı ve bir dakikalık sistem yükü. RAM, Linux
  `MemAvailable` kullanılarak hesaplanır; dosya önbelleği doğrudan kullanım sayılmaz.
- Backend, frontend ve gerçek HTTPS adresi için dakika başına sağlık ölçümü.
  İki buçuk dakikadan eski ölçümler arayüzde güncel/çalışıyor olarak gösterilmez.
- Son 20 sorgu, soru/yanıt/kaynak ayrıntısı, model, süre ve sorgu maliyeti.
  Ham prompt, düşünme metni, API anahtarı veya parolalar panele gönderilmez.

Tarihler **Asia/Bishkek** saat diliminde; grafik günleri de aynı gün sınırlarına
göre gruplanır. Panel açık ve görünürken 15 saniyede bir yenilenir.

## Maliyet ölçümü

Claude Messages API'nin gerçek `usage` sayaçları, her LLM çağrısı için ayrı
`llm_calls` kaydına alınır. Sohbet hafızası, sorgu yeniden yazma veya doğrulama
ek bir LLM çağrısı yaparsa aynı sorguya bağlanır ve maliyete dahil olur.
Eşzamanlı istekler ContextVar ile ayrılır. Yanıt metni boş dönse bile geçerli
API kullanım sayacı varsa ücret sayılır. HTTP/API hatasında sayaç gelmediyse
maliyet **bilinmiyor** olur; sıfır maliyet varsayılmaz.

12 Ekim 2026 [standart Anthropic API tarifesi](https://platform.claude.com/docs/en/about-claude/pricing):

| Model / giriş uzunluğu | Giriş / milyon | Çıkış / milyon | Önbellek okuma / milyon | 5 dk yazma / milyon | 1 sa yazma / milyon |
|---|---:|---:|---:|---:|---:|
| Haiku 5.5, en çok 100.000 giriş tokenı | $0,10 | $0,50 | $0,01 | $0,125 | $0,20 |
| Haiku 5.5, 100.000'den fazla giriş tokenı | $0,50 | $2,50 | $0,05 | $0,625 | $1,00 |
| Sonnet 5.5 | $2,00 | $10,00 | $0,10 | $2,50 | $4,00 |

Haiku eşik hesabına önbellek okuma/yazma tokenları da dahildir; uzun isteklerde
hem giriş hem çıkış tarifesi yükselir. Çıkış sayacı düşünme tokenlarını da
kaplar; görünür yanıtın uzunluğundan tahmin yapılmaz. Ücret her çağrıda
hesaplanıp tarife sürümüyle saklanır; geçmiş maliyetler sonraki tarifeyle
yeniden hesaplanmaz. Yeni/başka model için tarife tanınmıyorsa maliyet bilinmiyor
olur. Tarife değişince `monitoring.cost_estimate` ve sürüm güncellenmelidir.

Paneldeki USD toplamı **kaydedilmiş sayaçların maliyet tahminidir**, kuruluş
faturası veya kalan kredi değildir. Vergi, indirim, kredi kampanyası veya
sunucu maliyetini içermez. Token sayacı tutulmamış eski sorguların maliyeti
geriye dönük uydurulmaz; kapsanmayan sorgu/çağrı sayısı ayrıca gösterilir.

## Erişim ve parola yönetimi

API metrikleri, sorgu ayrıntıları ve eski `/stats` ucu yönetici oturumu ister.
Parola scrypt ile tuzlu hash olarak saklanır. Oturum imzalı, 8 saatlik,
`HttpOnly`, HTTPS'te `Secure`, `SameSite=Strict` çerezle taşınır. Kullanıcı
parolası localStorage'a yazılmaz. Girişte Origin kontrolü ve IP başına 5 dakika
içinde en fazla 5 deneme vardır. Panel yanıtları `Cache-Control: no-store`
taşır ve sayfa arama motoru indekslemesine kapalıdır.

Root terminalinde panel parolasını ayarlama/değiştirme:

```bash
cd /opt/bakay
backend/.venv/bin/python deploy/configure-monitor.py
systemctl restart bakay-backend
```

Araç parolayı gizli terminal girdisiyle iki kez ister; düz parolayı yazdırmaz
ve kaydetmez. En az 12 karakter ister. Mevcut özel ortamı root 600 izinli olarak
`/var/backups/bakay` altında yedekler; API/model/yol ayarlarını korur. Oturum
sırrını döndürdüğü için önceki panel oturumları yeniden giriş ister.
Panel yapılandırması `/etc/bakay/backend.env` altında, Git dışındadır.

## Sağlık ölçümü ve bakım

```bash
systemctl status bakay-monitor.timer
systemctl start bakay-monitor.service
journalctl -u bakay-monitor.service
```

`bakay-monitor.timer` dakikada bir hafif Python yoklaması başlatır; ayrı model
yüklemez ve LLM çağırmaz. Backend durmuşken de aynı SQLite dosyasına başarısız
sağlık ölçümünü yazabilir. HTTPS sertifikası doğrulanır. 31 günden eski sağlık
ve HTTP olay kayıtları temizlenir; asıl soru/yanıt ve API kullanım kayıtları
silinmez. Mevcut sorgu/geri bildirim tabloları korunur; yeni izleme tabloları
aynı `data/bakay.db` dosyasında oluşturulur.

Sağlık oranı **kaydedilmiş yoklamalar arasında başarılı olanların oranıdır**;
kesintisiz SLA ölçümü olarak yorumlanmaz. Sunucu tamamen kapalıyken içerideki
timer da çalışamaz; harici erişim izleme ve bildirim bu panelden ayrı kurulmalıdır.

Yeni frontend üretim derlemesi `/api` adresiyle hazırlanır. Canlı backend'e
yeni Python bağımlılığı eklenmez. Yayın sırasında eski frontend derlemesi
geri dönüş için saklanır; eski statik dosyalar yeni derlemeye korunarak taşınır.

## Canlı yayın doğrulaması — 12 Ekim 2026

Git üzerinden canlı kod güncellendi; sunucuda 40 backend testi geçti. HTTPS
giriş, 1/7 günlük metrikler, sorgu ayrıntısı ve çıkış doğrulandı. Oturumsuz
metrikler, ayrıntılar ve `/stats` HTTP 401 ve `no-store` dönüyor. Backend,
frontend ve sağlık timer'ı etkin ve açılışta başlatılacak şekilde ayarlı.

Gerçek Haiku 5.5 kontrol sorgusu 5 kaynakla yanıtlandı: 5.440 giriş ve 1.357
çıkış tokenı, tahmini **0,0012225 USD**. İlk sorgu 43,2 sn sürdü (LLM çağrısı
7,1 sn); ilk kaynak erişiminin ısınması süreyi artırdı. Önceki 7 sorgunun
maliyeti bilinmiyor. Başlangıç/ilk sorgu sırasında 5 saniyelik sağlık
zaman aşımı kaydedildi; sonraki backend/frontend/HTTPS yoklaması başarılı.
Yoklama zaman aşımı, sunucunun kesin olarak kapandığı anlamına gelmez.

Önceki frontend derlemesi
`/opt/bakay/runtime/frontend-before-monitor.20261012T170830Z/.next`
altında geri dönüş için korundu. Panel parolası ayrı gizli girişle belirlendi;
yalnız hash ve oturum sırrı root 600 ortam dosyasında saklanıyor.
