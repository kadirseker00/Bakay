# KTMÜ canlı kurulum ve işletim

Kod deposu: [kadirseker00/Bakay](https://github.com/kadirseker00/Bakay), dal `main`.

Ürün adı **BAKAI**. [Hakkında sayfası](https://bakai.manas.edu.kg/hakkinda),
adın kökenini, KTMÜ BAP proje numarasını ve proje yürütücüsü/geliştirici bilgisini açıklar.
Hedef: `192.168.3.13`, yayın adresi `https://bakai.manas.edu.kg/`.
Kurulu çalışma ağacı: **`/opt/bakay`**.

Yönetim paneli: **`/monitor`**. Erişim, metrikler, API maliyet hesabı ve bakım:
[izleme paneli rehberi](monitoring.md).

**12 Ekim 2026'da kullanıcının açık isteğiyle canlıya alındı.** Root SSH erişimi
doğrulandı; hazırlanan ağaç `/home/adminbakai/bakay` konumundan `/opt/bakay`
altına taşındı. Backend ve frontend systemd servisleri kuruldu, başlatıldı ve
sunucu açılışında çalışacak şekilde etkinleştirildi. Apache HTTPS proxy hedefleri
güncellendi; HTTP adresi HTTPS'e yönleniyor. Backend ve frontend yalnız
`127.0.0.1:8000` / `127.0.0.1:3000` adreslerinde dinliyor.

**Canlı LLM: Claude Haiku 5.5 (`claude-haiku-5-5`)**, Anthropic API üzerinden.
12 Ekim 2026'da kullanıcının isteğiyle Sonnet'ten Haiku'ya geçildi. Önceki
Haiku pilotunda denenmiş `adaptive` / `medium` düşünme ayarı ve 4096 çıktı
tokenı bütçesi kullanılıyor. Belge araması LaBSE ve aynı 39.659 parçalı indekste.

## Sunucuda hazır olanlar

- Ubuntu 24.04 / Python 3.12 / x86_64; 8 vCPU ve yaklaşık 4 GB RAM.
- Kullanıcının disk genişletmesi doğrulandı: kök birim yaklaşık 18 GB;
  aktarım öncesi 9,5 GB, bütün hazırlıklar sonrası yaklaşık 4 GB boş alan.
- Chroma `ktmu_docs`: **39.659 parça**, yaklaşık 715 MB. İndeks ve 13 kaynak
  haritasının SHA256 değerleri yerel kaynakla birebir eşleşti.
- LaBSE cache'i yaklaşık 1,8 GB. Yerel model revizyonu
  `836121a0533e5664b21c7aacc5d22951f2b8b25b` sunucuya taşındı.
- Node **22.23.3**, resmi dağıtım SHA256 değeriyle doğrulandı.
- Python **CPU PyTorch 2.12.0+cpu**, Chroma 1.5.9 ve sentence-transformers 5.6.0.
  `pip check` geçti. Tam Linux paket sürümleri `deploy/requirements-linux.txt`
  içinde; çevrimdışı kurulum wheel'leri `runtime/wheels/` altında hazır.
- Frontend **Next.js 15.5.27 / PostCSS 8.5.29**. Ayrı yerel derleme ve
  üretim npm denetimi (0 açık) geçti; sunucuda da Node 22 ile derlendi.
  `NEXT_PUBLIC_API_URL=/api` derleme içine yerleşti.
- Backend ortamı `/etc/bakay/backend.env` altında root'a ait **600** izinli
  dosyada. Anahtar Git'e veya frontend'e aktarılmadı; çalışma ağacındaki `.env`
  kopyası kaldırıldı. Model cache'i `/var/lib/bakay/huggingface` altında.

## İlk kurulum kontrolleri — 12 Ekim 2026, Sonnet

`GET http://127.0.0.1:8000/health` HTTP 200: sürüm 0.3.1,
Sonnet 5.5 / LaBSE / 39.659 parça. İlk model yükleme yaklaşık **17,2 sn**.

“Lisansta daha önce aldığım dersleri saydırabilir miyim?” sorusu **40,8 sn**
içinde 5 kaynakla yanıtlandı; yanıtın sonunda gerçek yönetmelik bağlantısı vardı.
Bu süre ilk sorunun BM25 hazırlığını ve üretimi içerir. Backend belleği yaklaşık
**2,5 GB RSS** ölçüldü. 4 GB RAM ile tek backend worker kullanılmalıdır;
eşzamanlı kullanıcı kapasitesi henüz ölçülmedi.

`http://127.0.0.1:3000/` ve CSS HTTP 200. Sonuç dosyası
`runtime/smoke-test.json` altında, Git dışında tutulur.

Root kurulum ve yayın araçları çalıştırıldı. `pip check`, systemd birim doğrulaması
ve Apache `configtest` geçti; mevcut TLS yolları korundu. Mac üzerinden gerçek
alan adıyla HTTPS sayfası, `/api/health` ve CSS HTTP 200 döndü; sertifika doğrulaması
başarılı. İki BAKAI servisi `active` / `enabled`, yeniden başlama sayıları 0.
Canlı HTTP sonuçları `runtime/live-check.json` altında saklanır.

Canlı tarayıcıda aynı ders saydırma sorusu **53,0 sn** içinde yanıtlandı;
5 kaynak parçası ve yönetmelik PDF bağlantısı görüntülendi. PDF HTTP 200 döndü.
Bu kontrol yeniden başlayan backend'in ilk sohbetini içerir; yük testi değildir.

Yayın öncesi Apache yedeği:
`/var/backups/bakay/bakai.conf.20261012T110658Z`.

## Haiku geçiş kontrolü — 12 Ekim 2026

HTTPS `/api/health` HTTP 200: `claude-haiku-5-5` / LaBSE / 39.659 parça.
Kaynaklı ders saydırma denemesi HTTP 200, 5 kaynak ve yönetmelik PDF bağlantısıyla
tamamlandı. İlk sorgu toplam **54,8 sn**: soğuk kaynak erişimi **44,4 sn**,
Haiku üretimi **10,1 sn**. Bu tek sorgu yük veya genel kalite testi değildir.
Kayıtlar `runtime/haiku-health.json`, `runtime/haiku-chat.json` ve
`runtime/haiku-verification.json` altında, Git dışında.

Geçiş öncesi özel ortam yedeği, root'a ait 600 izinli
`/var/backups/bakay/backend.env.before-haiku.20261012T111435Z` dosyasında.
Gerçek API anahtarı örnek ayarlara veya Git'e eklenmedi.

## Güncelleme ve günlükler

Root oturumunda kod güncellemesi:

```bash
git -C /opt/bakay pull --ff-only origin main
```

Frontend kodu veya kilit dosyası değişirse Node 22 ile `NEXT_PUBLIC_API_URL=/api`
verilerek yeniden üretim derlemesi yapılmalıdır. Python bağımlılıkları değişirse
Linux kilit dosyası ve wheel'ler güncellenmelidir. Yalnız `git pull` çalışan
servisleri yeniden başlatmaz; hazır güncelleme sonrası ilgili servis yeniden
başlatılır. Servis günlükleri:

```bash
journalctl -u bakay-backend -u bakay-frontend
systemctl status bakay-backend bakay-frontend
```

## İlk kurulum araçları

Aşağıdaki adımlar bu sunucuda tamamlandı. Yeni kurulum veya kurtarma için
korunurlar; çalışan kurulumda `prepare-root.sh` tekrar çalıştırılmaz.

Verilen `root` parolası root hesabında oturum açmak içindir.
`adminbakai` üzerinden `sudo` normalde adminbakai'nin kendi parolasını ister.
Root hesabıyla giriş yaptıktan sonra:

```bash
# İstenirse hazırlık öncesi kodu Git'ten güncelle:
runuser -u adminbakai -- git -C /home/adminbakai/bakay pull --ff-only origin main

# Hazırlanmış ağacı /opt/bakay altına taşır; yayını açmaz:
bash /home/adminbakai/bakay/deploy/prepare-root.sh

# Yönetici yayına alma kararı verdiğinde:
bash /opt/bakay/deploy/publish-root.sh
```

`prepare-root.sh`, `bakay` servis kullanıcısını oluşturur; repo/veriyi **taşıyarak**
diskte ikinci model/indeks kopyası oluşturmaz. LaBSE cache'ini
`/var/lib/bakay/huggingface` altına taşır, anahtarı root'a ait 600 izinli
`/etc/bakay/backend.env` dosyasına geçirir ve çalışma ağacındaki anahtar kopyasını
kaldırır. Mutlak yolları değişen venv'i doğrulanmış Linux wheel'lerinden yeniden
kurar. Servis dosyalarını ve izinleri hazırlar; servisleri başlatmaz.
Kısmen tamamlanan hazırlık `/opt/bakay/deploy/prepare-root.sh` üzerinden yeniden
çalıştırılabilir. Aktif BAKAI servisleri varken hazırlık aracı durur.

`publish-root.sh`, backend/frontend'i **yalnız 127.0.0.1** adresinde başlatır ve
indeks/sayfa kontrolünü yapar. Mevcut Apache dosyasını `/var/backups/bakay/`
altına yedekler; HTTPS VirtualHost içindeki eksik proxy hedeflerini düzeltir.
Sertifika yolları korunur. Apache `configtest`, reload ve HTTPS `/api/health`
kontrolü başarılı olursa servisler açılışta çalışacak şekilde etkinleştirilir.
Apache yüklemesi veya HTTPS kontrolü başarısızsa eski yapılandırma geri yüklenir.

Yayın sonrasında tarayıcıdan sohbet ve kaynak bağlantıları kontrol edilir.

## Git ve büyük dosyalar

Git'te kod, kurulum araçları, sürüm/kilit dosyaları ve bu rehber bulunur.
İndeks, ham belgeler, kaynak haritaları, model cache'i, `.venv`, `node_modules`,
`.next`, `runtime/` ve gerçek `.env` Git dışında kalır. Sunucuda `git pull`
bu verileri silmez; `git clean -x` gibi yok sayılan dosyaları da silen komutlar
kullanılmamalıdır. Veri güncellemeleri yazıcılar kapalıyken ayrı aktarılır.

GitHub normal Git depolarında tek dosyada **100 MiB** sınırı uygular.
Chroma SQLite dosyası yaklaşık 546 MB olduğundan Git'e eklenmez.
Bu aktarım için Git LFS gerekmiyor; büyük çalışma verisi sunucuda zaten hazırdır.
[GitHub dosya sınırları](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).

Proxy/derleme kaynakları: [Apache mod_proxy](https://httpd.apache.org/docs/2.4/mod/mod_proxy.html),
[Next.js ortam değişkenleri](https://nextjs.org/docs/app/guides/environment-variables).
Güvenlik güncellemesi kaynakları: [Next.js](https://github.com/vercel/next.js/security/advisories/GHSA-2xp9-vwfh-vxw4),
[PostCSS](https://github.com/postcss/postcss/security/advisories/GHSA-fxqj-rqcc-2cmp).
