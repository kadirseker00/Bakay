# Dış erişim güvenliği — 14 Kasım 2026

## Durum

Canlı `6796af5` / `0.4.3` tabanından ayrı `codex/public-security` dalında
`0.4.4` hazırlandı. Ana çalışma alanındaki marka/araştırma değişiklikleri
bu sürüme taşınmadı. **Henüz canlıya uygulanmadı.**

14 Kasım kontrolünde `192.168.3.13` TCP 22 ve 443 erişilebilir. Kayıtlı SSH
anahtarıyla root girişi `Permission denied (publickey,password)` döndü;
parola denenmedi. Panelin izinli kurum/VPN CIDR listesi de henüz bildirilmedi.

## Tehdit ve sınırlar

Anahtar yalnız backend ortamında kalır. İstemci isteği hedef sağlayıcı URL'sini,
modeli veya genel bir Messages API gövdesini seçemez. Sistem genel amaçlı bir
Anthropic proxy'si değildir; buna rağmen anonim `/chat` hizmeti başka bir
uygulamanın arka ucundan çağrılabilir. CORS ve içerik benzerlik eşiği erişim
kontrolü değildir; Origin de komut satırından taklit edilebilir.

Bu sürüm anahtar çalmadan hizmeti aracı olarak kullanmayı zorlaştırır ve yerel
maliyeti sınırlar. Geçerli CAPTCHA'yı kendi sunucusundan çözen, aynı IP/tarayıcı
başlığını koruyan biri oturum süresince yine istek gönderebilir. Tam kullanıcı
kontrolü gerekiyorsa kurum SSO'su ve doğrulanmış hesap kotaları gerekir.

## Uygulanan kontroller

- `PUBLIC_SECURITY_ENABLED=true`: ilk `/chat` öncesinde `/session` üzerinden
  sunucuda Turnstile doğrulaması. Hostname ve `bakai_chat` action eşleşir;
  eksik ayar/erişilemeyen doğrulama hizmetinde çağrı kabul edilmez.
- Kanıt özeti SQLite'ta atomik, tek kullanımlık tutulur. Sağlayıcının kısa süreli
  tekrar kontrolü gecikse bile eşzamanlı tekrar bir kez doğrulanır.
- 30 dakika süreli imzalı, HttpOnly, Secure (HTTPS), SameSite=Strict çerez.
  HMAC amaç ayrımıyla mevcut panel sırrı kullanılır; yeni API anahtarı gerekmez.
  IP (IPv6 /64), User-Agent özeti ve son kullanma süresi kontrol edilir.
- Oturum başına 30/dakika, 120/saat ek kota. Mevcut IP/global ve gerçek worker
  iş ömrü kotaları ayrıca korunur; yeni çerez almak IP kotasını sıfırlamaz.
- Geri bildirim yalnız geçerli oturumun ürettiği query_id için alınır.
  Bir sorgudan en çok üç farklı düzeltme taslağı açılır; tekrarlar idempotent,
  kontrol ve kayıt aynı SQLite işlemi içindedir. Eski oy güncellemesi korunur.
- Tüm panel API'leri, `/stats` ve API dokümantasyonu uygulamada CIDR kontrolünden
  geçer. Apache ayrıca frontend `/monitor` ve özel `/api/` yollarını sınırlar.
- Next.js `15.5.29`; frontend `bakay-web`, backend `bakay` hesabında çalışır.
  Frontend özel backend/veri/ortam dizinlerine erişemez; `ProtectProc=invisible`
  başka hesaptaki backend proses ortamının okunmasını sınırlar.

## 5 USD günlük yerel harcama kesicisi

`BUDGET_ENABLED=true`, `BUDGET_DAILY_USD=5`. Bildirim eşiği olan
`ALERT_DAILY_USD=1` korunur; erken uyarı ile durdurma farklıdır.

Her Anthropic çağrısından **önce**, hafıza/yeniden yazma/doğrulama çağrıları dahil,
SQLite `BEGIN IMMEDIATE` ile rezervasyon yapılır. Metin UTF-8 bayt sayısı,
protokol payı, çıktı üst sınırı ve bilinen en yüksek tarife ile ihtiyatlı bir
tahmin ayrılır. Bugünkü harcama + kesinleşmemiş rezervasyon + yeni rezervasyon
5 USD'yi aşacaksa sağlayıcıya HTTP isteği gönderilmez.

Kullanım sayacı gelen çağrıda gerçek sayaçlarla yerel tarife hesabına geçilir.
Zaman aşımı, eksik kullanım veya süreç çökmesinde rezervasyon gün sonuna kadar
kalır; restart bütçeyi sıfırlamaz. Beklenmedik fiyat/model veya tahmin aşımı
sonraki ücretli çağrıları kapatır. Yeni/fiyatı bilinmeyen sağlayıcıya geçiş bu
kontrolü sessizce atlayamaz. İlk etkinleştirmede mevcut günün `llm_calls`
tutarı açılışa eklenir; maliyeti bilinmeyen eski kayıt varsa o gün kapalı kalır
ve yönetici incelemesi gerekir. Kayıtları silerek açmak önerilmez.

Gün Bişkek saatiyle 00.00'da değişir; çağrı rezervasyon gününe yazılır. Bu
**yerel ve mevcut tarifeye bağlı bir korumadır, sağlayıcı faturasında mutlak
5 USD garantisi değildir**. Token/fiyat değişimi, farklı gün muhasebesi, vergi
ve aynı anahtarın başka yerde kullanılması yerel sayaçtan bağımsızdır. Ayrı
Anthropic workspace harcama sınırı ikinci savunmadır. Anahtarın kendisi çalınırsa
Bakai kotaları bunu durduramaz; sağlayıcıda iptal/rotasyon gerekir.

Kullanıcıya bütçenin dolduğu ve Bişkek 00.00'dan sonra tekrar deneyebileceği
bildirilir; SSE ve normal HTTP için mesaj korunur. Panelde harcama + ayrılan
tutar, kalan bütçe ve kesinleşmemiş çağrı sayısı gösterilir. Ücretsiz hazır
cevaplar/belge yok yanıtları çalışabilir.

## Sorgulayan kişi hakkında veri

Mevcut sistem IP, zaman, soru/yanıt, kaynak/geçmiş ve maliyet kaydeder;
isteğe bağlı geri bildirim adı kullanıcı beyanıdır. Yeni sürüm yalnız kısa
rastgele oturum kimliği, query_id ilişkisi ve HMAC tarayıcı/IP bağı ekler.
Ham User-Agent, cihaz parmak izi, GPS veya yeni bir kişisel profil eklenmedi.
IP ve User-Agent kişi kimliğini kanıtlamaz; NAT/VPN ve başlık taklidi mümkündür.
Ad-soyad/e-posta ancak beyanla veya doğrulanmış kurum girişinden edinilebilir.
Kesin konum tarayıcı izni gerektirir; güvenlik amacıyla istenmiyor.

## Dağıtım

1. BT ile panel CIDR listesini doğrulayın; tüm özel ağları veya `/0` eklemeyin.
   Listede localhost her zaman kalır; bakım için SSH tüneli kullanılabilir.
2. Canlı git durumunu/commit/sürümünü okuyup yedekleyin. Bu dalı sunucuda çekin;
   canlı son commit `6796af5`'ten ilerlediyse önce farkları birleştirin.
3. `frontend/` içinde `npm ci`, `NEXT_PUBLIC_API_URL=/api npm run build`.
   Çalışan Next.js servisinin aynı `.next` dizininde derleme yapmayın; servisi
   durdurun veya ayrı derleme dizini kullanın. Python testleri ayrı geçici DB'de.
4. Root: `bash deploy/harden-root.sh 'DOĞRULANMIŞ_CIDR,DOĞRULANMIŞ_VPN_CIDR'`.
   Betik mevcut CAPTCHA ve panel sırrını kontrol eder; API anahtarı dahil diğer
   sırları değiştirmeden ortamı günceller. Panelde kullanılacak **aynı** ağları
   backend ve Apache'ye yazar. Önce configtest yapar; servis/ortam/Apache ve
   SQLite kopyasını root-only `/var/backups/bakay/security-*` altında korur.
   Kod, indeks, yedekleme, SES ve model önbelleği silinmez.
5. `systemctl` ve Apache configtest; dışarıdan tokensız JSON/SSE 403 ve sıfır
   LLM çağrısı, gerçek Turnstile + normal soru, yabancı Origin, sahte XFF,
   izin dışından panel/docs 403, izinli ağdan panel girişi doğrulanır.
   API ve arayüzün ikisi de `0.4.4` göstermelidir.

Yeni kurulumda `prepare-root.sh` ayrı frontend hesabını oluşturur; yayın öncesi
`configure-public-security.py --monitor-networks ...` ayrıca çalıştırılmalıdır.
Apache ağ dosyası eksikse configtest başarısız olur; panel herkese açılmaz.

Geri dönüş: root-only yedekteki ortam, Apache ve systemd dosyalarını geri alın;
frontend hesap/dosya grubunu eski servisle eşleştirin, daemon-reload ve servisleri
yeniden başlatın. Uygulama tabanı additive SQLite şemasını yok sayabilir; canlı
DB'yi eski yedekle değiştirerek yeni sorguları kaybetmeyin. Kod geri alınacaksa
önceki canlı committen frontend'i yeniden derleyin. Betik komut hatasında
ortam/servis/Apache geri dönüşünü dener; HTTPS son testi ayrıca zorunludur.

## Doğrulama ve kaynaklar

- 239 uygulama testi + üç dağıtım testi geçti. Yeni testlerde ilk istek,
  sahte/tekrar kanıt, cookie imzası, süre/IP/tarayıcı bağı, JSON/SSE, oturum ve
  IP kotası, feedback sahipliği, eşzamanlı taslak sınırı, panel ağı, eşzamanlı
  bütçe, restart/gün değişimi, bilinmeyen maliyet/fiyat ve sıfır ücretli çağrı
  koşulu denetlendi. Testler geçici DB ve sahte sağlayıcı kullandı.
- Next.js 15.5.29 üretim derlemesi ve npm production audit: 0 açık.
- Gerçek tarayıcıda ayrı yerel QA: ilk doğrulama, doğrulama sonrası yanıt ve
  ikinci soruda CAPTCHA olmadan bütçe mesajı görüldü. Cloudflare'ın resmî test
  widget'ı kullanıldı; gerçek hostname/action kontrolü testte sahtelenmiştir.
  Canlı Cloudflare doğrulamasının testi yerine geçmez.
- OS/Python bağımlılık taraması ve Linux systemd/Apache kurulum doğrulaması,
  root erişimi sağlanınca tamamlanacak; yerel sonuç bunları tamamlanmış saymaz.

Resmî kaynaklar:
[Turnstile sunucu doğrulaması](https://developers.cloudflare.com/turnstile/get-started/server-side-validation/),
[Turnstile test anahtarları](https://developers.cloudflare.com/turnstile/troubleshooting/testing/),
[Anthropic fiyatlandırması](https://platform.claude.com/docs/en/about-claude/pricing),
[Next.js görüntü işleme duyurusu](https://github.com/vercel/next.js/security/advisories/GHSA-2464-fhr4-w9xw),
[Next.js Server Actions DoS duyurusu](https://github.com/vercel/next.js/security/advisories/GHSA-p3m5-59mp-jv5r).
