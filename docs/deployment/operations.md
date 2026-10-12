# BAKAI operasyon koruması

## Alarm ve bildirimler

Yönetici panelindeki **Uyarılar ve yedekler** bölümü sağlık, kaynak kullanımı,
yedekleme ve maliyet alarmını gösterir. `bakay-monitor.timer` dakikada bir ölçer.
Sağlık, RAM (%90), disk (%85), son 15 dakikadaki sunucu hataları ve 30 saatten
eski yedekler üç kötü ölçümde açılır; iki iyi ölçümde kapanır.

Günlük maliyet alarmı **1 USD**: Bişkek 00.00’dan itibaren kaydedilmiş API token
sayaçlarının standart tarifeyle hesaplanan toplamıdır. Fatura/kalan kredi değildir;
bilinmeyen sayaçlar ayrıca uyarılır. Alarm sorguları durdurmaz. Mevcut günlük sorgu
kotası ve eşzamanlı çalışma sınırları ayrıca geçerlidir.

SMTP bağlanana kadar panel alarmı çalışır, e-posta gönderilmez. `bakai@manas.edu.kg`
hesabının SMTP sunucusu, TLS yöntemi/portu ve alıcı adresi doğrulanınca root oturumunda:

```sh
/opt/bakay/backend/.venv/bin/python /opt/bakay/deploy/configure-operations.py mail
systemctl restart bakay-backend
systemctl start bakay-monitor.service
```

Parola gizli girişle alınır; `/etc/bakay/backend.env` root:root 0600 kalır.
Yalnız STARTTLS veya TLS bağlantısı, doğrulanan sertifikalar kullanılır. Soru/yanıt
metni veya API anahtarı gönderilmez. Yalnız alarm açılışı ve düzelmesi bildirilir.
Gönderim arızasında kuyruk yeniden denenir; eski, henüz gönderilmemiş alarmlar
geçerliliğini yitirdiyse gönderilmez. SMTP kabulü ile kayıt güncellemesi arasındaki
çökmede nadiren tekrar bildirim oluşabilir.

Bu ölçüm sunucunun içinde çalışır. Sunucu tamamen kapandığında dışarıdan bir erişim
izleyicisi gerekir; içerideki timer o durumda e-posta gönderemez.

## Şüpheli trafik doğrulaması

Turnstile `Managed` widget: **BAKAI**, yalnız `bakai.manas.edu.kg`, pre-clearance
kapalı. DNS taşımak gerekmez. On dakika içinde aynı bağlantıda üç hız ihlali
sonraki kabul edilebilir istekte doğrulama ister. IP bilgisi HMAC ile saklanır;
yeni tabloda düz IP tutulmaz. IPv6 /64 ve ortak ağlar mevcut kota davranışını korur.

Doğrulama kanıtının Cloudflare tarafından kabulü, alan adı ve `bakai_chat` action
sunucuda kontrol edilir. Token tek kullanımlı ve kısa ömürlüdür. Başarılı doğrulama
aynı bağlantıda 30 dakika geçerlidir; hız/saat/gün/eşzamanlılık kotalarını kaldırmaz.
Kullanıcı pencerede doğrulayıp **Doğrula ve soruyu gönder** düğmesine basar; vazgeçerse
sorusu yazı alanında korunur. Sağlayıcı erişilemiyorsa açıklayıcı hata verilir,
LLM çağrısı başlamaz.

Anahtarlar sohbetten veya git üzerinden paylaşılmaz. Root oturumunda:

```sh
/opt/bakay/backend/.venv/bin/python /opt/bakay/deploy/configure-operations.py captcha
systemctl restart bakay-backend
```

[Cloudflare sunucu doğrulaması](https://developers.cloudflare.com/turnstile/get-started/server-side-validation/)
ve [istemci kurulumu](https://developers.cloudflare.com/turnstile/get-started/client-side-rendering/).

## Şifreli yedekleme

`bakay-backup.timer` her gün **03.15 Bişkek** civarında çalışır (en çok 5 dakika
rastgele gecikme). Yedekler `/var/backups/bakai` root 0700 dizininde 0600 tutulur.
`/etc/bakay/backup.json` yalnız **açık age alıcı anahtarını** içerir. Geri yükleme
özel anahtarı sunucuda veya git'te bulunmaz; yöneticinin Mac'inde
`~/.config/bakai-backup/identity.txt` 0600 saklanır. Anahtarın bağımsız güvenli bir
kopyası gerekir; anahtar kaybolursa şifreli yedek açılamaz.

İlk yedek veya indeks değişikliği tam indeks paketi üretir. İndeks değişmezse günlük
paket yalnız tutarlı uygulama SQLite yedeği, veri JSON dosyaları, sürüm ve özel
sunucu yapılandırmasını içerir. Günlük paket manifestteki indeks parmak iziyle aynı
tam indeks paketine bağlıdır. Yalnız günlük paket Chroma indeksini içermez.

SQLite Online Backup API ve `integrity_check` kullanılır. HNSW dosyaları paket
akışı içinde hash'lenir; indeks dosyalarının yedek öncesi/sonrası parmak izi değişirse
paket yayınlanmaz. İndeksleme sırasında tekrar denenmelidir. Şifreli arşiv doğrudan
age akışında oluşur; düz arşiv diske yazılmaz. SQLite/yapılandırma geçici kopyaları
0700 dizinde tutulur, sonunda kaldırılır. Son bir GiB boş alan korunur.

Yerelde en fazla 7 günlük paket ve 2 tam indeks saklanır. Tam indeksi kaldırılan
günlük paketler de kaldırılır; kalan günlük paketlerin eşleşen indeksi korunur. Drive'da otomatik silme, sync
veya purge yoktur. Drive bağlantısı yapılmadan uzak yedek mevcut sayılmaz.

```sh
systemctl start bakay-backup.service
systemctl status bakay-backup.service
systemctl list-timers bakay-backup.timer
```

### Drive bağlantısı (hesap seçildiğinde)

Hesap/klasör henüz seçilmedi; `remote` boş. Sunucuda rclone kuruludur. Tercihen
kuruma ait Google OAuth istemcisi ve yalnız uygulamanın oluşturduğu dosyalara
`drive.file` yetkisi kullanılır. Bu kapsam mevcut keyfî klasörleri okuyamaz; ilgili
hesapta BAKAI-Yedek klasörünü rclone ile oluşturun. OAuth giriş/yetki adımını hesap
sahibi tamamlar. Kullanıcı parolası koda veya sohbet geçmişine yazılmaz.

Rclone yapılandırması `/var/lib/bakai-backup/rclone.conf`, root 0600; üst dizin
root 0700. `/etc/bakay/backup.json` içindeki `remote` örneğin `bakai-drive:BAKAI-Yedek`
olarak ayarlanır. Birinci aktarım tam indeks paketini de yükler. `copyto` sonrasında
uzak dosya boyutu ve MD5 doğrulanmadan başarılı kabul edilmez. Aktarım başarısızsa
yerel yedek korunur; sonraki çalışmada eksik tam indeks önce yüklenir.

[Rclone Drive kapsamları](https://rclone.org/drive/),
[SQLite Online Backup](https://www.sqlite.org/backup.html).

### Geri yükleme provası

Mac'te sunucudaki `.tar.gz.age` dosyasını git dışındaki korumalı bir dizine indirin.
Sunucu özel anahtar gerektirmez. Dosya bütünlüğü, manifest ve SQLite doğrulaması:

```sh
backend/.venv/bin/python deploy/backup.py verify /güvenli/dizin/BAKAI-index-TARIH.tar.gz.age \
  --identity ~/.config/bakai-backup/identity.txt --check-index
```

Varsayılan olarak geçici, üretimden ayrı bir dizine açar ve sonunda kaldırır.
`--check-index` tam pakette Chroma koleksiyonunu açıp kayıt sayısını ve mevcut bir
vektörün en yakın komşusunu doğrular; LLM veya embedding indirmesi yapmaz. Var olan
hedef dizine yazmayı, arşivde yol kaçışını/symlink'i ve bozulmuş şifreli dosyayı reddeder.

Gerçek kurtarmada önce tam paket yeni bir hedefe açılır. Günlük paket **başka yeni**
bir hedefe açılıp manifest parmak izleri karşılaştırılır; doğrulanmış günlük SQLite
ve yapılandırmalar durdurulmuş uygulamanın kurtarma dizinine yönetici tarafından
aktarılır. Aktif üretim Chroma dizinine arşiv açmayın. `last_restore_test_at` yalnız
başarılı gerçek prova sonrası güncellenir.

## Doğrulama

Yerel backend: **150 test**. Next.js üretim derlemesi başarılı. Yeni testler alarm
geçişi/düzelme, Bişkek gün sınırı, eksik maliyet, TLS/kuyruk/yeniden deneme, CAPTCHA
alan adı/action/kotalar ve gerçek age şifreleme/geri yükleme/bozulma senaryolarını kapsar.
13 Ekim 2026 canlı kurulum: Cloudflare BAKAI widget'ı oluşturuldu ve özel anahtar
sunucuda bağlandı. Siteverify, geçersiz test token'ı için `invalid-input-response`
döndürdü; eksik/geçersiz token HTTP 403 aldı, LLM/daily üretim kotası tüketmedi.

İlk tam şifreli paket **426.628.437 bayt** (yaklaşık 407 MiB), 31 dosya.
Mac'te ayrı geçici dizinde açıldı: arşivin SHA-256 değeri, age doğrulaması, manifest,
SQLite bütünlüğü ve **39.659 parça** üzerinden en yakın komşu sorgusu başarılı.
Özel anahtar sunucuya gönderilmedi. Şifreli test kopyası Mac'te git dışındaki
`~/.config/bakai-backup/archives/` dizininde saklandı. Sunucu health HTTP 200,
Haiku 5.5 ve 39.659 parça doğrulandı. SMTP hesabı ve Drive bağlantısı bekleniyor.
