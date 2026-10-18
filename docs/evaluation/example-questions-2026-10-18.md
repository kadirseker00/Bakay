# Ana sayfadaki altı soru ve hazır cevap bankası

18 Ekim 2026, Bişkek. Altı soru, yerel `/chat` üzerinden geçmişsiz birer kez
soruldu. Sağlık yanıtı: v0.3.1, Sonnet 5.5, LaBSE, 39.659 parça.
Bu inceleme canlı Haiku yanıtlarının testi değildir. Tek Codex incelemesidir;
yetkili birim/uzman onayı yerine geçmez. Ham yanıtlar
`example-questions-2026-10-18/answers.json` dosyasındadır.

| Örnek soru | Gerçek sonuç | Değerlendirme |
|---|---|---|
| Daha önce aldığım dersleri saydırabilir miyim? | Lisans Madde 25 girişini gösterip öğrenim düzeyini sordu. | Kaynakla uyumlu bir ön cevap; tam koşullar henüz verilmedi. Bu çağrıda üretim yapılmadı. |
| Manas Üniversitesine nasıl başvurabilirim? | Değişim programı anlaşması ve aday gösterilme koşullarını anlattı. | Genel öğrenci kabulü yerine değişim programına yöneldi. Yanlış kapsam; ana sayfa örneği için yetersiz. |
| Kayıt için hangi belgeleri hazırlamalıyım? | Belge listesinin elinde olmadığını söyleyip Öğrenci İşlerine yönlendirdi. | Kesin listeyi uydurmuyor, ancak asıl belge listesi cevaplanmadı. İlgili dönemin kabul/kayıt ilanı gerekli. |
| Hazırlık sınıfından muaf olabilir miyim? | Okulun eğitim dili, diğer dilin sınavı, programın İngilizce/Rusça ön şartı ve takvimi anlattı. | Ana koşullar SSS ile uyumlu. İlk maddesindeki okul mezuniyeti ifadesi tüm muafiyet yollarının zorunlu ön şartı gibi okunabiliyor; taslakta yollar ayrıldı. |
| Hangi burslardan yararlanabilirim? | Üniversite ve KYK bilgisinin yanına eski faaliyet raporundan Türkiye Burslarını ekledi. | Üniversite/SSS kısmı kaynaklı, kişisel uygunluk belirlenmedi. Eski rapordan eklenen burs güncel hak gibi sunulmamalı. |
| Başka bir üniversiteden yatay geçiş yapabilir miyim? | Yalnız öğrenim düzeyini sordu. | Yanlış bir kabul vaadi vermiyor; fakat önlisans/lisans için bilinen kuralı göstermedi. Tam cevap değil. Üretim yapılmadı. |

## Kaynak kontrolü

Resmî sayfalar 18 Ekim'de web üzerinden incelendi:

- [Üniversiteye kabul](https://oidb.manas.edu.kg/tr/faq/2): vatandaşlığa göre farklı yollar var; genel kabul sorusuna değişim anlaşması şartı uygulanamaz.
- [Kayıt işlemleri](https://oidb.manas.edu.kg/tr/faq/3): tam belge listesi yerine ilgili ilana yönlendiriyor.
- [Hazırlık](https://oidb.manas.edu.kg/tr/faq/7): dilden doğrudan muafiyet ile sorumlu olunan dillerin sınavları ayrılmalı.
- [Burslar](https://oidb.manas.edu.kg/tr/faq/6): kısa genel açıklama, kişisel uygunluk/tutar/takvim için yeterli değil.
- [Önlisans/lisans yönetmeliği](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf#page=7): ders saydırma Madde 25, kurum dışından geçiş Madde 26. Öğrenim kapsamı korunmalı.

Sonuç: Altısının da konuya ilişkin dayanağı var; mevcut akışta altısı da eksiksiz
ve doğru cevaplanmış sayılamaz. Altı kaynaklı, kapsamı belirtilmiş cevap taslağı
`backend/app/knowledge_examples.json` içine hazırlandı. Tam belge listesi veya
kişisel burs hakkı bulunmadığı yerlerde açıklama ve yönlendirme korunur.

## Hazır cevap panelinin kullanımı

`/monitor` → **Hazır cevaplar**. Mevcut yönetici oturumu kullanılır.

1. **6 örneği ekle** ile kaynaklı taslaklar alınır. Tekrar basmak düzenlemeleri
   sıfırlamaz. Yeni soru ve cevap elle de eklenebilir.
2. Soruyu, aynı anlama gelen varyantlarını, cevabı ve kaynakları düzenleyin.
   Sorgu ayrıntısındaki **Hazır cevap taslağı oluştur** düğmesi mevcut bir
   cevabı ve bilinen resmî kaynak adreslerini düzenleyiciye taşır.
3. Kaynağı açıp güncelliği/kapsamı kontrol edin; kaynak kontrol tarihi ve
   geçerlilik sonunu girip **Onayla ve yayımla** seçin.
4. Yeni, geçmişsiz sorularda tam soru/varyant eşleşmesi doğrudan cevabı getirir.
   Türkçe büyük/küçük harf, boşluk ve sondaki soru işareti farkları normalize
   edilir. Yakın anlamı tahmin ederek cevap seçilmez; varyantlar açıkça eklenir.
5. Geçerlilik sonu Bişkek gün sonudur. Süresi dolan, taslak veya arşiv kayıtlar
   kullanılmaz. Geçmiş taşıyan sorgular bağlamı kaybetmemek için RAG'a gider.

Eşleşmede embedding/vektör araması ve LLM çağrısı yapılmaz. Kaynaklar, sorgu
kimliği ve geri bildirim korunur; panelde model **Onaylı hazır cevap**, API
çağrı sayısı ve maliyeti sıfır görünür. Sayaç, banka eşleşmelerini sayar; tahmini
bir token tasarrufu veya varsayımsal dolar tasarrufu hesaplamaz.

Taslak kaydetmek yayımdaki cevabı yayından kaldırır; yeniden yayın açık onay
gerektirir. Sürüm numarasıyla eşzamanlı düzenleme çatışması ve aynı soruya iki
yayımlanmış cevap bağlanması engellenir. SQLite revizyon geçmişi, onaylayan
kullanıcı ve cevaplanan sürümün JSONL kaydı tutulur. Banka, mevcut veritabanı
yedekleme düzenine dahildir. Kaynağın uzaktan değişmesi otomatik izlenmez;
yeniden kontrol aralığını geçerlilik tarihi belirler.

## Doğrulama

- Yeni 12 test: oturum/origin, yayın koşulları, olumsuzluk/düzey/sayı ayrımı,
  süre dolumu, sürüm çatışması, atomik eşzamanlı yayın, taslak örnekler,
  JSON/SSE, sıfır LLM/embedding, geri bildirim, maliyet ve geçmiş/RAG dönüşü.
- Genel backend paketi: 189 test geçti (diğer oturumun metin temizliği testleri dahil).
- Son kaynak URL değişikliğinden sonra genel paket yeniden çalıştırıldı: 189 test ve Next.js üretim derlemesi geçti.
- Ayrı QA veritabanında gerçek tarayıcı girişi, altı taslağın eklenmesi,
  cevap/kaynak önizlemesi, onay ve yayın doğrulandı. Gerçek HTTP çağrısı tek
  kaynaklı hazır cevabı döndürdü; panelde 0 LLM çağrısı / 0 USD ve eşleşme sayacı görüldü.
- Masaüstü ve 390 px mobil görünüm incelendi; mobil sayfa genişliği 390 px,
  yatay taşma yok. Görseller: `output/knowledge-panel/panel.png`, `mobile.png`.
- Yerel backend ve arayüz yeni kodla yeniden başlatıldı; altı örnek yerel ana
  veritabanına taslak olarak eklendi. Gerçek yayına alınmış cevap yok.

Durum: yerel kod ve `/monitor` arayüzü hazır; ana yerel ortamın yönetici sırları
tanımlı olmadığı için korumalı API 503 veriyor. Mevcut güvenlik davranışı korunur.
[Ayrı inceleme paneli](http://127.0.0.1:3007/monitor#knowledge) geçici QA hesabı
ve ayrı veritabanıyla çalışır; gerçek sunucu/parola/veriler kullanılmaz.
Tarayıcıdaki inceleme oturumu açık bırakıldı. Canlı sunucuya bu görev
kapsamında yayın yapılmadı.
