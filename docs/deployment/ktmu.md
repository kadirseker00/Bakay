# KTMÜ yayın hazırlığı

Kod deposu: [kadirseker00/Bakay](https://github.com/kadirseker00/Bakay), dal `main`.
Hedef: `192.168.3.13`, yayın adresi `https://bakai.manas.edu.kg/`.
Hazırlanan çalışma ağacı: **`/home/adminbakai/bakay`**.

Kullanıcı kararı gereği **yayına alma yöneticiye bırakıldı**. Codex yalnız
aktarımı, Linux kurulumunu, localhost kontrollerini ve aşağıdaki yönetici
araçlarını hazırladı. Apache değiştirilmedi; BAKAY servisleri systemd ile
kurulup etkinleştirilmedi. Geçici localhost test süreçleri teslim öncesi kapatılır.

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
- Backend ortamı sunucuda `.env` olarak, izin **600** ile hazırlandı.
  Anahtar Git'e veya frontend'e aktarılmadı. Yönetici hazırlık aracı bu
  dosyayı `/etc/bakay/backend.env` altına taşır.

## Yapılan kontroller — 12 Ekim 2026

`GET http://127.0.0.1:8000/health` HTTP 200: sürüm 0.3.1,
Sonnet 5.5 / LaBSE / 39.659 parça. İlk model yükleme yaklaşık **17,2 sn**.

“Lisansta daha önce aldığım dersleri saydırabilir miyim?” sorusu **40,8 sn**
içinde 5 kaynakla yanıtlandı; yanıtın sonunda gerçek yönetmelik bağlantısı vardı.
Bu süre ilk sorunun BM25 hazırlığını ve üretimi içerir. Backend belleği yaklaşık
**2,5 GB RSS** ölçüldü. 4 GB RAM ile tek backend worker kullanılmalıdır;
eşzamanlı kullanıcı kapasitesi henüz ölçülmedi.

`http://127.0.0.1:3000/` ve CSS HTTP 200. Sonuç dosyası
`runtime/smoke-test.json` altında, Git dışında tutulur.

Apache araçları için shell sözdizimi kontrolü geçti. Mevcut VirtualHost
üzerinde hazırlanan proxy dönüşümü; TLS yollarını ve HTTP yönlendirmesini
koruyor, tekrar uygulandığında aynı sonucu üretiyor. **Root kurulum araçları
çalıştırılmadı**; gerçek systemd/Apache kontrolleri yönetici çalıştırırken yapılır.

## Yöneticinin çalıştıracağı komutlar

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
çalıştırılabilir. Aktif BAKAY servisleri varken hazırlık aracı durur.

`publish-root.sh`, backend/frontend'i **yalnız 127.0.0.1** adresinde başlatır ve
indeks/sayfa kontrolünü yapar. Mevcut Apache dosyasını `/var/backups/bakay/`
altına yedekler; HTTPS VirtualHost içindeki eksik proxy hedeflerini düzeltir.
Sertifika yolları korunur. Apache `configtest`, reload ve HTTPS `/api/health`
kontrolü başarılı olursa servisler açılışta çalışacak şekilde etkinleştirilir.
Apache yüklemesi veya HTTPS kontrolü başarısızsa eski yapılandırma geri yüklenir.

Yönetici ardından tarayıcıdan sohbeti ve kaynak bağlantılarını kontrol eder.
Servis günlükleri: `journalctl -u bakay-backend -u bakay-frontend`.

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
