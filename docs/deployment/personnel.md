# Resmî personel rehberi

Kaynak: https://rehber.manas.edu.kg/ . Türkçe birim sayfaları, herkese açık kişi
kartları ve kurumsal iletişim alanları alınır. Fotoğraf, kullanıcı oturumu,
özel dosya veya personel otomasyonundaki kayıtlar toplanmaz. Sayfanın görüntülemek
üzere taşıdığı JSON kart verisi güvenli biçimde çözülür; JavaScript çalıştırılmaz.

## Toplama ve güncelleme

Proje kökünden:

```bash
cd backend
.venv/bin/python -m app.ingest.personnel
# Toplama tamamlanınca kişi/görev kayıtlarını Chroma'ya da aktar:
.venv/bin/python -m app.ingest.personnel --index
```

Robots kuralları kontrol edilir; birim istekleri arasında en az bir saniye
beklenir. Bir sayfa başarısız veya beklenmeyen yapıda ise eksik küme yayımlanmaz.
Ham kişisel fotoğraflar indirilmez. Ayrıştırılmış metinler Git dışındaki
`data/processed/personnel/`, gerçek kaynak bağlantıları ise
`data/sitemap-personnel.json` altında bulunur. Genel `app.ingest.run` komutunun
ham belge taramasına dahil edilmez; personel için yukarıdaki özel komut kullanılır.

Her kayıt kişi + ana birim + alt birim + görev kimliğini korur. Dekan/bölüm başkanı
kartları da alınır. Aynı kişi farklı görevlerle birden çok kayıtta bulunabilir;
kayıt sayısı tekil çalışan sayısı değildir. E-posta, dahili ve oda bilgisi aynı
kişiyle birlikte tek parçada tutulur. Her metin kaynak adresini ve kontrol
tarihini içerir. Rehberde olmayan biyografi veya uzmanlık alanı üretilmez.

Güncelleme aynı kimliği upsert eder; iletişim değişikliği önceki parçayı çoğaltmaz.
Eski görevler yalnız tüm yeni parçalar başarıyla yazıldıktan sonra, sadece
`source_type=personnel_directory` kapsamından kaldırılır. Mevzuat ve diğer belgeler
silinmez. Yenilemede `data/processed/personnel/` altındaki eski metin dosyaları arşiv
olarak kalabilir; etkin küme kaynak haritası ve Chroma'daki kayıtlarla belirlenir.

Canlı indeks güncellemesinden önce mevcut yedeği koruyun. Backend ayrı süreçte
çalışıyorsa yeniden başlatılarak BM25 belleği ve vektör deposu birlikte yenilenir.
API anahtarı yenilemesi ayrı işlemdir; genel sağlık kontrolü sağlayıcı anahtarının
çalıştığını kanıtlamaz. Yeni uygulama commiti yayımlanacaksa AGENTS.md sürümleme
kuralı uygulanır. Bu dosyanın yazılması canlıya yayın anlamına gelmez.

## 2 Kasım 2026 yerel doğrulama

25 resmî birim sayfasından 1.034 kişi/görev kaydı toplandı. Yerel indeks
39.659 → 40.693 parçaya çıktı. Kişi/birim eşleştirme, güncel temas bilgisinde
sabit kimlik, başarısız güncellemede eski kayıtların korunması ve kaynak linkleri
için 8 test geçti. Yerel RAG erişiminde “Abdulkadir Şeker kurumsal e-posta adresi
nedir?” ve “Bilgisayar Mühendisliği Bölüm Başkanı kimdir?” sorularında doğru resmî
rehber kaydı ilk sırada bulundu. Bu, iki erişim kontrolüdür; LLM yanıt doğruluğu
ve kurum genelinde kapsam değerlendirmesi değildir. Farklı birim kartlarında
unvan/oda farklılığı bulunabilir; kaynakta görünmeyen tek bir güncel değer
varsayılmamalıdır.

Yeni Anthropic anahtarı canlıya bağlandı ve gerçek Haiku yanıtıyla doğrulandı.
Canlıdaki “abdulkadir şeker kimdir?” sorusu kaynak yetersiz yanıtı almıştı; yeni
yerel indekste aynı sorunun ilk iki sonucu ilgili resmî kişi kartlarıdır.
Personel verisinin canlıya aktarımı için yeniden SSH bağlantısı kurulması gerekiyor;
yerel hazırlık canlıya yayın olarak sunulmamalıdır.

## Ek kaynak: AXSİS akademik profilleri

Kaynak: https://publications.manas.edu.kg/ . 2 Kasım 2026 tarihinde normal
tarayıcıda güvenlik doğrulamasından sonra araştırmacı listesi ve profil sayfası
incelendi. Ana sayfa 643 araştırmacı ve 3.295 yayın gösteriyordu; bunlar sistemin
o tarihte görünen kayıt sayılarıdır, üniversitenin tüm personelini veya bütün
bilimsel üretimini kapsadığı varsayılmamalıdır.

Doğrulanan örnek: https://publications.manas.edu.kg/arastirmaci/abdulkadirseker .
Profilde ad, unvan, kurumsal e-posta, fakülte/bölüm, ad varyantları, çalışma
durumu, ORCID ve diğer akademik profil bağlantıları bulunuyor. Kurumsal e-posta
ve bölüm bilgisi personel rehberindeki kayıtla eşleşiyor. Yayınlar sekmesinde
dört makale kaydı (üçü 2026, biri 2025), başlık, özet, dergi ve kaynak sayfası
bağlantıları görüldü. Bu, kişinin toplam yayın sayısının dört olduğunu göstermez.

Bu kaynak henüz Chroma indeksine eklenmedi. 2 Kasım 2026 tarihinde
`https://publications.manas.edu.kg/robots.txt` HTTP 200 döndü; `User-agent: *`
için `Disallow: /` kuralı var. ChatGPT-User ve diğer bazı botlar ayrıca kapalı.
Googlebot/Bingbot gibi arama motorlarının istisnası Bakai için kullanılmaz.
Bu nedenle toplu web taraması başlatılmadı. Kurumdan alınan dışa aktarım için
`app.ingest.academic` hazırlandı; CAPTCHA çözmez ve siteye istek göndermez.
Tarayıcıdaki doğrulanmış oturumdan erişim, sunucudaki zamanlanmış toplayıcının
da erişebileceği anlamına gelmez.

Eşleştirmede yalnız ad benzerliğine dayanılmamalı; kurumsal e-posta veya ORCID
gibi doğrulanan alanlarla birim bilgisi birlikte kullanılmalı. Yayın künyeleri
ve profil bilgileri ayrı kaynak adresleri ve kontrol tarihleriyle korunmalı;
yayın konusundan doğrulanmamış özgeçmiş ya da uzmanlık unvanı üretilmemeli.

### Toplu dışa aktarımı yükleme

Kütüphaneden CSV/Excel/JSON dosyası alındığında aşağıdaki ara JSON şemasına
dönüştürülür. CSV/Excel'in gerçek sütunları görülmeden dönüşüm varsayılmamalı.
`expected_researchers` kurumun dışa aktarımda bildirdiği toplam olmalı;
elle eksik bir kümeye eşitlenerek tamlık beyanı üretilmemeli.

```json
{
  "schema_version": 1,
  "fetched_at": "2026-11-02",
  "complete": true,
  "expected_researchers": 1,
  "researchers": [{
    "url": "https://publications.manas.edu.kg/arastirmaci/ornek",
    "name": "Örnek Araştırmacı",
    "title": "Dr.",
    "faculty": "Örnek Fakülte",
    "department": "Örnek Bölüm",
    "email": "ornek@manas.edu.kg",
    "orcid": "",
    "publications": [{
      "url": "https://publications.manas.edu.kg/yayin/123",
      "title": "Örnek yayın başlığı",
      "year": "2026",
      "journal": "Örnek dergi",
      "doi": ""
    }]
  }]
}
```

Bu şema örneği kurgu veridir; üretim indeksine yüklenmez. `publications` boş
olabilir; yokluğu hata sayılır. Yıl metin olarak verilmelidir. Kaynak adresleri
kanonik `/arastirmaci/KIMLIK` ve `/yayin/SAYI` biçiminde olmalı; liste sayfasının
arama ekleri veya oturum belirteçleri taşınmamalı.

Backend dizininden:

```bash
# Önce doğrula ve Git dışına belge/kaynak haritası yaz:
.venv/bin/python -m app.ingest.academic /guvenli/yol/axsis.json
# Aynı doğrulamayla Chroma'ya upsert et:
.venv/bin/python -m app.ingest.academic /guvenli/yol/axsis.json --index
```

Eksik/boş küme, tekrarlanan profil, resmî olmayan adres, kurumsal olmayan e-posta
ve çelişen yayın künyesi yazmadan önce reddedilir. Ortak yayın adresleri tek
belgede birleştirilir; eşleşen araştırmacı adları birlikte tutulur. Profil ve
yayın kimlikleri kaynak URL'sinden gelir; güncelleme kopya üretmez. Önceki indeks
kayıtları otomatik silinmez; kaynakta kaldırılan profillerin arşiv/temizleme
kararı ayrıca verilmelidir. Yazma hatasından sonra aynı dosya tekrar yüklenebilir.

Çıktılar `data/processed/academic/`, `data/processed/academic-records.json` ve
`data/sitemap-academic.json` içindedir. Tam metin makale/PDF, kişisel fotoğraf ve
oturum bilgisi aktarılmaz. Testler yalnız geçici dizinlerde kurgu veri kullandı;
üretim indeksi değiştirilmedi. 12 personel/akademik/kaynak testi geçti.
