# BAKAI operasyon koruması

## Alarm ve bildirimler

Yönetici panelindeki **Uyarılar ve yedekler** bölümü sağlık, kaynak kullanımı,
yedekleme ve maliyet alarmını gösterir. `bakay-monitor.timer` dakikada bir ölçer.
Sağlık, RAM (%90), disk (%85), son 15 dakikadaki sunucu hataları ve 192 saatten
eski yedekler üç kötü ölçümde açılır; iki iyi ölçümde kapanır.

Günlük maliyet alarmı **1 USD**: Bişkek 00.00’dan itibaren kaydedilmiş API token
sayaçlarının standart tarifeyle hesaplanan toplamıdır. Fatura/kalan kredi değildir;
bilinmeyen sayaçlar ayrıca uyarılır. Alarm sorguları durdurmaz. Mevcut günlük sorgu
kotası ve eşzamanlı çalışma sınırları ayrıca geçerlidir.

18 Ekim 2026 itibarıyla canlı: **BAKAI <bakai@manas.edu.kg>** göndericisinden
**abdulkadir.seker@manas.edu.kg** adresine AWS SES üzerinden bildirim.
`bakai@manas.edu.kg` kimliği SES `us-east-1` konsolunda **Verified**;
kullanıcı doğrulama bağlantısını açtı. Üniversitenin Google parolası kullanılmaz.

KTMÜ sunucusunda SES SMTP uçlarının 587, 465, 2587 ve 2465 portlarına TCP bağlantısı
zaman aşımına uğradı; üç çözümlenmiş IP ayrı ayrı kontrol edildi.
`https://email.us-east-1.amazonaws.com/` TLS bağlantısı başarılıdır (imzasız kök
istek HTTP 404). Bu nedenle `ALERT_EMAIL_PROVIDER=ses` ile HTTPS/443 üzerinden
AWS SDK kullanılır. SDK otomatik gönderim tekrarı kapalıdır; mevcut kalıcı alarm
kuyruğu aynı yeniden deneme ve düzelme kurallarını uygular.

BAKAI'ye özel, konsol girişi kapalı **bakai-alerts** IAM kullanıcısı ve
**bakai-alerts-send-only** inline politikası oluşturuldu. Yalnız `ses:SendRawEmail`,
`arn:aws:ses:us-east-1:450653396311:identity/bakai@manas.edu.kg` kaynağı,
`ses:FromAddress=bakai@manas.edu.kg` ve `ses:Recipients` yalnız
`abdulkadir.seker@manas.edu.kg` koşulları verildi; grup veya ek politika yoktur.
Tek etkin erişim anahtarı sunucuya bağlandı. Anahtarlar
`ALERT_SES_ACCESS_KEY_ID` ve `ALERT_SES_SECRET_ACCESS_KEY` alanlarında root 0600
özel ortamda tutulur, git'e girmez. Erişim hesabı şu an Moledro AWS hesabıdır;
kuruma devirde SES hesabı/anahtarının da kuruma devri ayrıca planlanmalıdır.
Kimlik doğrulaması yalnız e-posta adresi düzeyindedir; alan adı DKIM/DMARC ayarları
üniversite DNS yöneticisine aittir.

18 Ekim **16.59 Bişkek** test iletisi uygulamanın gerçek SES gönderim yoluyla
AWS tarafından kabul edildi; kullanıcı hedef gelen kutusuna ulaştığını doğruladı.
Sunucuda 15 operasyon testi geçti. Backend yeniden başlatıldı; backend/frontend
ve monitor/yedek timer etkin, son yoklama başarılı, HTTPS health 200 ve oturumsuz
özel metrikler 401. Panel verisi `email_configured=true`, eşik 1 USD ve etkin
alarm yok olarak doğrulandı; geçmişte düzelmiş yedek alarmları gönderilmedi.

Bu yayın, henüz yayına alınmayan geri bildirim değişikliklerini taşımamak için
`7da2402` tabanından ayrılan **codex/ses-alerts** dalındadır; uygulama kodu
`6ffe620` commit’idir. `main` aynı SES kodunu `1127824` ile içerir. Sonraki
yayında bu dal farkı dikkate alınmalı; `main`e geçiş geri bildirim arayüzünün
üretim derlemesini de gerektirir.

Kurulum/güncelleme root oturumunda:

```sh
/opt/bakay/backend/.venv/bin/python /opt/bakay/deploy/configure-operations.py ses
systemctl restart bakay-backend
systemctl start bakay-monitor.service
```

SMTP seçeneği mevcut sağlayıcılar için korunur; SMTP bilgileri varsa:

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

4 Kasım 2026 kullanıcı isteği: **haftada bir, yalnız Drive’da son tam yedek**.
`bakay-backup.timer` her **pazar 02.00 Bişkek** saatinde çalışır. Sunucu kapalıysa
ilk açılışta kaçırılan çalışma telafi edilir. Başarısız işlem 15 dakika sonra
tekrarlanır; iki saatte en çok dört başlangıç. Gecikme eşiği `BACKUP_MAX_AGE_HOURS=192`
(8 gün); haftalık aralık içinde günlük gecikme alarmı oluşmaz.

`/etc/bakay/backup.json` içinde `remote_only=true`: her çalışmada bağımsız bir tam
indeks + uygulama SQLite + yapılandırma paketi oluşturulur. age ile şifreli arşiv
hazırlanırken sunucuda geçici alan kullanılır; düz arşiv oluşturulmaz. Yeni tam
yerel paket tamamlanınca daha eski yerel BAKAI arşivleri ve yan manifestleri
kaldırılır. Aktarım başarısızsa en fazla bu tek tam paket kalır; tekrar denemeler
arşiv biriktirmez.

Drive kopyasının **boyutu ve MD5 değeri doğrulandıktan sonra** yalnız hedef
klasördeki daha eski `BAKAI-index-TARIH.tar.gz.age` / `BAKAI-daily-TARIH.tar.gz.age`
paketleri Drive çöp kutusuna taşınır. Başka dosyalar, alt klasörler, yeni paket
ve daha yeni tarihli dosyalar korunur. Liste/aktarım/hash kontrolü başarısızsa
eski Drive yedekleri silinmez. Temizlik bittiğinde sunucudaki son geçici arşiv de
silinir; başarılı işlem sonunda kalıcı yerel arşiv yoktur. Temizlik başarısızsa
son doğrulanmış aktarım tarihi saklanır, `drive_cleanup` hatası ve yerel tam paket
korunur. Çöp kutusunu kalıcı boşaltma veya tüm klasörü eşitleme yapılmaz.

Yedek dizini `/var/backups/bakai` root 0700, dosyalar 0600. SQLite Online Backup
API ve `integrity_check` kullanılır; indeks dosyalarının önce/sonra parmak izi
değişirse paket yayınlanmaz. Son bir GiB boş alan korunur. İndeksleme sırasında
tekrar denenmelidir. Şifreleme özel anahtarı sunucuda/Drive’da yoktur;
Mac’te `~/.config/bakai-backup/identity.txt` 0600 saklanır. Anahtarın bağımsız güvenli
bir kopyası gerekir. `remote_only` kapalı eski kurulumların günlük/artımlı ve
7 günlük + 2 indeks saklama davranışı geriye uyumluluk için korunur.

```sh
systemctl start bakay-backup.service
systemctl status bakay-backup.service
systemctl list-timers bakay-backup.timer
```

### 4 Kasım 2026 yayın ve bağlantı durumu

Haftalık politika **v0.4.1 / `9999e3b`** ile canlıya alındı. Canlı taban
`c8e05b0` üzerine `codex/weekly-drive-backup` dalı kullanıldı; personel/AXSİS
çalışmaları bu yayına taşınmadı. Linux'ta 211 test, iki ortamda üretim derlemesi,
HTTPS API/arayüz sürüm eşleşmesi, 13 JS/CSS ve özel metriklerin 401 yanıtı geçti.
Sonraki planlı çalışma **8 Kasım 2026 pazar 02.00 Asia/Bishkek**.
Geri dönüş dizini `/var/backups/bakay/weekly-drive.20261104T064221Z`.

Arızanın kesin nedeni rclone ortak istemcisinde Google API **403
RATE_LIMIT_EXCEEDED / defaultPerMinutePerProject**; Drive depolama kotası veya
OAuth token süresi değil. Son doğrulanmış aktarım **2 Kasım 02.17 Bişkek**;
son yerel paket **4 Kasım 02.53 Bişkek**. Mevcut yerel arşivler yaklaşık 1,3 GB.
Yeni gerçek aktarım henüz tamamlanmadığından mevcut arşivler bu aşamada silinmedi.

Kurumsal Google hesabıyla **BAKAI Drive Backup** projesi
(`eminent-quasar-513706-b2`) oluşturuldu ve Drive API etkinleştirildi. OAuth
uygulaması kurum içi olarak, destek/iletişim adresi
`abdulkadir.seker@manas.edu.kg` ile hazırlandı. Google veri politikası kabulü,
özel OAuth istemcisi ve `bakai@manas.edu.kg` Drive izni için kullanıcı onayı
bekleniyor; henüz yeni istemci/token oluşturulmadı. Onaydan sonra bağlantı,
gerçek tam aktarım/hash ve eski uzak/yerel arşiv temizliği doğrulanmalı.
Haftalık alarm eşiği çalışıyor; bu durum bağlantı arızasının giderildiği anlamına gelmez.

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
