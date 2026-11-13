# Dış erişim öncesi güvenlik incelemesi — 13 Kasım 2026

Sonuç: Anahtarın tarayıcıya verildiğine dair bulgu yok. Buna karşılık, genel
erişime açılan sohbet ucunun başka sunuculardan çağrılıp Bakai üzerinden ücretli
yanıt ürettirilmesi mevcut tasarımda mümkündür. Mevcut kotalar bunun hacmini
sınırlar; yetkili kullanıcı ile kota altında kalan otomasyonu ayırt etmez.
Dış erişim öncesinde aşağıdaki öncelikli önlemler tamamlanmalıdır.

## İncelemenin kapsamı ve sınırı

- Yerel kaynak kod, yayın şablonları, frontend kilit dosyası ve son kayıtlı canlı
  commit `6796af5` karşılaştırıldı. Ana erişim/kota/anahtar modülleri aynı.
- Sunucu `192.168.3.13` üzerinde TCP 22 ve 443 bu ağdan zaman aşımına uğradı.
  Etkin Apache kuralları, sistem izinleri, panelde değiştirilen kotalar,
  Cloudflare/WAF durumu ve sağlayıcı harcama limiti bugün canlıdan okunamadı.
- Üretim istekleriyle yük veya açık istismarı testi yapılmadı. Yerel testler
  geçici SQLite ve sahte model kullandı; ücretli LLM çağrısı sıfır.
- Güncel Git dosyalarında Anthropic anahtarı, AWS erişim kimliği ve özel anahtar
  biçimleri tarandı; eşleşme yok. Yerel frontend derlemesinin 19 statik dosyasında
  Anthropic anahtarı biçimi yok. Bu sınırlı desen kontrolüdür; tüm Git geçmişi,
  sunucu logları, Drive erişimleri veya canlı JS dosyaları için garanti değildir.
- Python bağımlılıklarının tam güvenlik taraması ve işletim sistemi yamaları
  bu incelemede doğrulanmadı. Bu rapor sızma testi sertifikası değildir.

## 1. Anahtar ve izinsiz aracı kullanım

`backend/app/rag/llm.py` anahtarı backend ortamından okuyup sabit
`https://api.anthropic.com/v1/messages` adresinin HTTP başlığına ekliyor.
Frontend yalnız Bakai API'sini çağırıyor; `NEXT_PUBLIC` alanlarında sağlayıcı
anahtarı yok. İstek şemasıyla model, sağlayıcı adresi veya API anahtarı seçilemiyor.
Bu, genel amaçlı Anthropic API vekili değildir; dışarıdaki biri Bakai'nin mevcut
RAG hizmetini kendi uygulamasının arkasına koyabilir.

Modelin ortam dosyasını okuyan veya komut çalıştıran araçları yok. Anahtar normal
istem metnine konmuyor. Prompt injection, sunucu sırrını kendiliğinden modelin
erişimine açmaz; yine de yanıt kalitesi ve kaynağın kötüye kullanılması için
güven sınırı testleri gereklidir. Sistem mesajı/veri ayrımı mevcut ve test edildi.

Anahtar gerçekten sızarsa sağlayıcıya doğrudan kullanım mümkün olur; Bakai'nin
IP kotası, CAPTCHA veya günlük sorgu kotası bu doğrudan kullanımda devreye girmez.
Anahtarın iptali/yenilenmesi ve sağlayıcı tarafı bütçe sınırı bu yüzden ayrı
korumalardır. [Anthropic anahtar güvenliği](https://support.claude.com/en/articles/9767949-api-key-best-practices-keep-your-keys-safe-and-secure).

## 2. Öncelikli: anonim otomasyon ve maliyet

`main.py` sohbet ucunda kullanıcı oturumu veya zorunlu başlangıç doğrulaması
aramıyor. `captcha.require`, CAPTCHA ayarlı değilse veya IP henüz şüpheli
işaretlenmediyse hemen dönüyor. Şüphe, IP dakika/saat reddinin tekrarlarıyla
oluşuyor. Yeni IP veya kota altında kalan otomasyon CAPTCHA görmeden çalışabilir.

Yerel doğrulama: CAPTCHA ayarlı, doğrulama fonksiyonu başarısız dönecek şekilde
sahteyken, tokensız iki istek (Origin yok / yabancı Origin) HTTP 200 aldı ve
sahte `pipeline.answer` iki kez çağrıldı. Turnstile doğrulaması hiç çağrılmadı.
Yabancı kaynağa `Access-Control-Allow-Origin` verilmedi; bu tarayıcı sınırıdır,
başka sunucuların HTTP çağrısına kimlik doğrulaması sağlamaz.

Varsayılan kotalar IP başına 30/dakika, 120/saat; toplam 30/dakika,
1.000/son 24 saat; eşzamanlı iş sayısı 2. Bunlar gerçek kısıtlardır fakat saldırgan
diğer kullanıcılardan önce kotayı tüketebilir. Dağıtık IP'ler toplam kotayı aşmasa
da hizmeti meşgul edebilir. Bir soru birden fazla LLM çağrısına yol açabilir.

`ALERT_DAILY_USD=1` yalnız alarmdır. `alerts.py` günlük maliyeti izleyip uyarır;
ücretli çağrıyı durduran dolar bütçesi yok. `generation` kotası dolar yerine soru
sayısını ölçer. [OWASP API4](https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/)
rate limit ve üçüncü taraf harcama sınırlarını birlikte önerir.

Önlem: anonim kullanıcı için ilk ücretli işten önce sunucuda doğrulanan Turnstile
ve kısa süreli imzalı oturum; kullanıcı/oturum + IP + global kotalar birlikte.
Her iş için maksimum token/maliyet rezervasyonuyla atomik uygulama bütçesi,
belirsiz kullanımda güvenli duruş ve sağlayıcı tarafında ayrı proje/workspace
harcama sınırı. İstek bitiminden sonra maliyet kontrolü eşzamanlı aşımı engellemez.
Turnstile otomasyonu zorlaştırır, kullanıcının kimliğini veya hizmetin başka bir
yerde aracılanmayacağını garanti etmez. Daha kuvvetli ayrım gerekirse üniversite
SSO'su ve kullanıcı kotaları gerekir; aday öğrencilere anonim kullanım korunabilir.
[Cloudflare sunucu doğrulaması](https://developers.cloudflare.com/turnstile/get-started/server-side-validation/).

## 3. Bağımlılık uyarıları ve süreç ayrımı

`npm audit --omit=dev --json`: bir kritik paket bulgusu (`next`), iki ilişkili
duyuru; otomatik öneri 15.5.29. Kilitli Next.js 15.5.27.

- [GHSA-2464-fhr4-w9xw](https://github.com/vercel/next.js/security/advisories/GHSA-2464-fhr4-w9xw):
  Linux/glibc görüntü işleme yolunda olası RCE. Üreticinin geçici çözümü
  `sharp >= 0.35.5`; hem yerel hem son canlı commitin kilit dosyası **0.35.5**.
  Dolayısıyla paket uyarısı, mevcut kurulumda kullanılabilir RCE kanıtı değildir.
  Canlıda gerçekten kurulu Sharp sürümü ve optimize görüntü yolu kontrol edilmeli.
- [GHSA-p3m5-59mp-jv5r](https://github.com/vercel/next.js/security/advisories/GHSA-p3m5-59mp-jv5r):
  App Router + en az bir Server Action koşulunda DoS. Mevcut frontend kodunda
  Server Action (`use server`) bulunmadı. Üretici bu özelliği kullanmayan
  uygulamaların etkilenmediğini belirtiyor. Yine de desteklenen yamalı sürüme
  geçiş, temiz üretim derlemesi ve yeniden audit önerilir.

Frontend ve backend systemd şablonlarında aynı `bakay` işletim sistemi hesabını
kullanıyor. Olası frontend kod çalıştırma açığının etkisini sınırlamak için ayrı
hesaplar, ayrı yazma dizinleri ve backend sırlarına erişim ayrımı önerilir.
Root:600 ortam dosyası faydalıdır; aynı kullanıcıyla çalışan süreçler arasındaki
izolasyonun yerini tek başına tutmaz. Canlı süreç/proc erişimleri doğrulanamadı.

## 4. Mevcut iyi önlemler ve ek sıkılaştırma

- Panel: scrypt parola özeti, HMAC imzalı 8 saat oturum, HttpOnly/SameSite Strict,
  HTTPS'te Secure çerez; giriş kotası ve değişikliklerde Origin kontrolü.
  Özel sayaç/soru/golden/yönetim uçları oturum gerektiriyor.
- Yönetici paneli soru/yanıt ve istemci bilgileri içeriyor. Dış erişim için
  panel/API yönetim yolları VPN veya kurum IP'leriyle sınırlandırılmalı;
  paylaşılan ağlarda IP'ye ek güçlü oturum/MFA tercih edilmeli.
- Oturum çıkışı yalnız çerezi siliyor; ele geçirilmiş imzalı token süre bitimine
  kadar tekrar kullanılabilir. Oturum iptali mekanizması iyileştirme adayıdır.
- Backend/frontend loopback'e bağlı; Apache açık forward proxy değil.
  Gelen X-Forwarded-For/Forwarded siliniyor, Uvicorn yalnız localhost proxy'sine
  güveniyor. Yeni dış ters vekil/CDN eklenirse gerçek IP güven zinciri yeniden
  kurulmalı; aksi halde tüm kullanıcılar tek IP kotasında birleşebilir.
- JSON gövde sınırı, yavaş gövde zaman aşımı, geçmiş/soru/top_k sınırları,
  kalıcı atomik SQLite kotaları ve depoda hata halinde ret mevcut.
- Turnstile sunucu denetimi hostname/action doğruluyor; hizmet hatasında 503
  dönüyor. Bunun mevcut CAPTCHA tetiklenme politikasından farkı korunmalı.
- Yedek aracı ortam dosyasını da arşivliyor; **age ile şifreliyor**. Drive
  paylaşımı ve çözme anahtarına kimlerin eriştiği ayrıca kontrol edilmeli.
- OpenAPI/docs varsayılan açık (yerelde `/openapi.json` 200). Kapatmak erişim
  kontrolünün yerini tutmaz; üretimde gereksiz bilgi yüzeyini azaltır.
- Apache/WAF katmanında bağlantı ve istek sınırlaması; TLS, güvenlik başlıkları,
  OS/Python güncellemeleri ve yalnız 443 dış erişimi canlıda doğrulanmalı.
  Turnstile kullanmak alan adının Cloudflare WAF/DDoS arkasında olduğunu göstermez.

## Doğrulama ve yayın kararı

80 mevcut test geçti:

```bash
cd backend
.venv/bin/python -m unittest tests.test_abuse tests.test_operations \
  tests.test_monitoring tests.test_rate_limits tests.test_prompt_injection \
  tests.test_llm tests.test_chat_stream
```

İlk ücretli istek doğrulaması, harcama kesicisi, panelin ağ kısıtı ve bağımlılık
yamaları hazırlanmadan dış erişimi açmayı önermiyorum. Ardından kurum ağından
canlı ayarlar salt okunur doğrulanmalı ve dış ağdan TLS/API/varlık kontrolleri
yapılmalı. DNS kaydının yokluğu tek başına bir güvenlik sınırı değildir.

13 Ekim tarihli `erisime-acma.md` zaten dış DNS'in NXDOMAIN döndüğünü kaydediyor.
Bu inceleme bizim kaydı sildiğimizi veya bilinçli kapattığımızı doğrulamadı.
Uygulama, DNS, firewall, sırlar veya canlı hizmetler bu çalışmada değiştirilmedi.
