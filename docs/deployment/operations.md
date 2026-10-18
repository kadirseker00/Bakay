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

`bakay-backup.timer` her gün **02.00 Bişkek** saatinde çalışır; rastgele gecikme
kapalıdır. Sunucu o sırada kapalıysa ilk açılışta kaçırılan çalışma telafi edilir.
Başarısız işlem 15 dakika sonra yeniden denenir; iki saatte toplam en çok dört
servis başlangıcına izin verilir. Yerel yedek aktarım başarısızlığında korunur.
Yedekler `/var/backups/bakai` root 0700 dizininde 0600 tutulur.
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

### Drive bağlantısı — 18 Ekim 2026

Hesap: **bakai@manas.edu.kg**. Kullanıcının mevcut
[bakai_backup klasörü](https://drive.google.com/drive/folders/1z0-L4EhRdJC-RJ2AiN5Ihus40zmIbWxj)
hedef olarak seçildi. OAuth hesabı Google Drive API üzerinden doğrulandı.

Rclone yapılandırması `/var/lib/bakai-backup/rclone.conf`, root 0600; üst dizin
root 0700. `bakai-drive` uzak hedefinde `root_folder_id` paylaşılan klasörün
kimliğine sabitlendi, `/etc/bakay/backup.json` içindeki `remote` değeri
`bakai-drive:`. Böylece aynı adlı başka klasörler aktarım hedefini değiştirmez.

İlk denenen `drive.file` kapsamı uygulamanın oluşturduğu dosyalara izin verir;
kullanıcının önceden oluşturduğu bu klasöre erişemedi. Daha geniş `drive` kapsamı
kullanıcı tarafından Google ekranında onaylandı. **Bu Google izni klasörle
sınırlı değildir**; klasör sınırı rclone yapılandırmasındadır. Uygulama Google
parolasını almaz, erişim/yenileme tokenlarını özel yapılandırmada saklar.

OAuth bağlantı yapılandırması da şifreli günlük yedeğe dahildir. Geri yükleme
özel anahtarı sunucuya veya Drive'a gönderilmez.

Birinci aktarım eşleşen tam indeks paketini de yükler. `copyto` sonrasında uzak
dosya boyutu ve MD5 doğrulanmadan başarılı kabul edilmez. Aktarım başarısızsa
yerel yedek korunur; sonraki çalışmada eksik tam indeks önce yüklenir. Drive'da
silme/sync/purge yapılmaz. İlk denemede ortak rclone Google istemcisinin API
istek kotası 403 verdi; veri kaybı olmadı, aktarım yeniden denendi ve tam indeks/günlük paketi
18 Ekim 2026 14.10 Bişkek itibarıyla boyut/MD5 kontrolünden geçti. Yeniden
denemeler arasına 60 saniye bekleme eklendi. Bu kota
Drive depolama kotasından ayrıdır. Tekrarlayan hata halinde kurumun kendi
Google OAuth istemcisine geçilmelidir.

[Rclone Drive kapsamları ve kendi istemcisi](https://rclone.org/drive/),
[SQLite Online Backup](https://www.sqlite.org/backup.html).

### 18 Ekim canlı doğrulaması

Saat ayarı sunucuda yüklendi ve `systemd-analyze verify` geçti. Bir sonraki
çalışma **19 Ekim 2026 02.00 Asia/Bishkek**; servis hataları 15 dakika sonra
sınırlı sayıda yeniden denenir. Son günlük aktarım **18 Ekim 14.28 Bişkek**
itibarıyla başarılı; paket 605.387 bayt, boyut/MD5 doğrulandı ve hata durumu temizlendi.
Ortak Google istemcisinin kotası aralıklı hata verdiği için yeniden deneme korunur;
kota tekrarlarsa kuruma ait OAuth istemcisi gereklidir.

Drive'daki tam indeks paketi doğrudan Drive'dan Mac'e tekrar indirildi:
426.865.206 bayt, MD5 `d3d98d816ff9481588928097d9bc38c2`;
SHA-256 sunucunun paket manifestiyle aynı. Ayrı geçici dizine age ile açıldı,
31 dosyanın manifesti, SQLite bütünlüğü ve **39.659 parça** üzerinde en yakın
komşu sorgusu geçti. `last_restore_test_at` ancak bu gerçek provadan sonra
18 Ekim 2026 08.28 UTC olarak güncellendi. Özel anahtar Mac'te kaldı.

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
Haiku 5.5 ve 39.659 parça doğrulandı. Bu ilk kurulum tarihinde SMTP hesabı ve Drive bağlantısı bekleniyordu; Drive için 18 Ekim güncellemesi yukarıdadır.
