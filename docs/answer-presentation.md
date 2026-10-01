# Yanıtlarda temel şartların sunumu — 0.2.2

2026-10-01. Kullanıcı ders saydırma cevabındaki “son 5 yıl” ve “en az CC”
şartlarının parantez içinde geri planda kaldığını bildirdi. Bunlar başvurunun
uygunluğunu belirleyen temel şartlar olduğundan yanıt düzeni güncellendi.

## Değişiklik

Üretim talimatı önce tek bir kısa sonuç cümlesi, ardından **Temel şartlar:**
altında ayrı maddeler ister. Süre, asgari not, kredi/AKTS sınırı, içerik uygunluğu
ve gerekli belgeler ilgili olduklarında açıkça gösterilir. Kritik değerin kendisi
kalınlaştırılır; yalnız madde etiketinin kalın olması yeterli sayılmaz. Başvuru
yeri ve kurul/onay süreci ayrı kısa paragrafta açıklanır. Temel şartları paranteze
gömme ve “gibi” ile belirsizleştirme davranışı caydırılır.

İlk canlı denemede model bu düzene kısmen uydu; bazı sayısal değerleri veya CC
notunu düz metin bıraktı. Bu nedenle `_highlight_key_details` son işlem adımı
eklendi. Metindeki süreler, “en az CC” gibi harf notu eşikleri, yüzdeler ve kesir
oranları kalınlaştırılır. Hüküm metnine yeni bilgi eklenmez veya sayı değiştirilmez.
Mevcut kalın metin, kod ve bağlantılar korunur; tekrar çalıştırmak yeni kalın
işaretleri biriktirmez. İşlem fazladan LLM çağrısı gerektirmez. Arayüz mevcut
ReactMarkdown ve kalın metin stilleriyle bu vurguları gösterir.

## Kontroller ve sınırlar

78 backend testi geçti. Üç yeni kontrol eşik/olumsuzluk metninin aynen
korunmasını, mevcut Markdown/bağlantıların korunmasını ve tarih/madde
numaralarının gelişigüzel vurgulanmamasını doğruluyor. Son regex düzenlemesinden
sonra bu üç kontrol tekrar geçti.

Canlı örnekler ve sunum kontrolleri `docs/answer-presentation.json` içinde.
`initial_attempt` ilk talimat denemesini, `final_cases` otomatik vurgu ve
netleştirilmiş talimattan sonraki denemeleri içerir. API ve arayüz sürümü 0.2.2
olarak kontrol edildi.

Bu bir sunum düzeltmesidir. Vurgu adımı cevapta hiç bulunmayan bir koşulu geri
getirmez veya yanlış hükmü düzeltmez. Maddeli düzen üretim talimatına bağlıdır;
bütün sorularda zorunlu bir yapısal şema uygulanmaz. Kaynak bağlı doğruluk ve
koşulların eksiksizliği için uzman denetimli değerlendirme hâlâ gereklidir.
Son takip denemesi süre ve CC şartını görünür gösterdi, ancak 1/3 üst sınırını
üretmedi; bu kusur JSON'da başarısız `limit_emphasized` kontrolüyle korundu.
