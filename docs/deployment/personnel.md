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
