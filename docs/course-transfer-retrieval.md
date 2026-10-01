# Ders saydırma: kaynak erişimi ve kapsam düzeltmesi

2026-10-01. İncelenen soru: **“başka kurumdan aldığım dersi saydırabilir miyim”**.

## Kaynak sistemde var mı?

Evet. [Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf) yerelde `data/raw/web/upload_global_Onlisans_20ve_20lisans_20egitim.pdf_528e6665.pdf` olarak mevcut; PDF 18 sayfa. PDF'nin 7. sayfasındaki Madde 25 (basılı sayfa 159) metin olarak çıkarılmış ve 39.659 parçalık Chroma koleksiyonunda kayıtlı.

Hedef kayıt: `upload_global_Onlisans_20ve_20lisans_20egitim.pdf_528e6665.pdf::23::51898048`. Aynı metin mevzuat derlemesinde `docs_mevzuattr.pdf::473::51898048` olarak da var. Saklanan embedding yeniden üretilen embedding ile yaklaşık 1,0 kosinüs benzerliği veriyor; bu örnekte embedding bozulması bulunmadı.

## Kök neden ve değişiklik

Önceki erişim yalnız vektör benzerliğini kullanıyordu. Hedef Madde 25'in soruyla kosinüs benzerliği 0,3729; ilk 40 sonuç arasında bulunmuyordu. Daha yüksek benzerlikli faaliyet raporu, tekrarlanan Rusça sayfa ve farklı öğrenim düzeyinin eski hükmü öne çıkıyordu. Bu yüzden dosyanın sistemde olması doğru bağlamın modele ulaşmasını sağlamıyordu.

`retrieval.py` ve `vectorstore.py` artık vektör aramasını BM25 kelime aramasıyla RRF üzerinden birleştiriyor. Türkçe büyük/küçük harf dönüşümü, 4/6 harf önekleri ve ardışık kelime önekleri ekli kelimeler için ek erişim sağlıyor. Bu yaklaşım tam morfolojik çözümleme değildir. Normalize edilmiş birebir aynı metinler tekilleştiriliyor; mevzuat derlemesiyle aynı pasajda bağımsız yönetmelik tercih ediliyor. Belirli sorulara özel cevap veya belge listesi eklenmedi.

Açıkça belirtilen öğrenim düzeyi sıralamada kullanılıyor. Aynı terim lisans ve lisansüstü kaynaklarda eşleşiyorsa ve soru düzeyi belirtmiyorsa pipeline açıklama istiyor; sayısal şartları modele üretmiyor. Bu karar kaynaklarla birlikte `scope:needs_level` olarak loglanıyor. Açık düzey belirtildiğinde normal üretim sürüyor. Model bağlamında kaynakların öğrenim kapsamı da gösteriliyor. Kendi kapsam sorumuza verilen kısa seçim (örneğin “Lisans için soruyorum”) ilk kullanıcı sorusuyla doğrudan birleştiriliyor; LLM'nin konuyu yeniden yazarken kritik terimi kaybetmesi önleniyor.

Eski 1.000 karakterlik parçalar bazı kelimeleri ve koşulları ortadan kesiyor. En üstteki parçanın kesilmiş başlangıç/sonu aynı belgedeki komşu parçalarla tamamlanıyor. Örneğin lisansüstü dış kurum dersleri için öğrenim dili ve yüzde sınırının bağlantısı korunuyor. Tam bir madde bazlı yeniden parçalama yapılmadı.

API'nin `score` alanı ve yeterlilik kapısı gerçek kosinüs benzerliğini kullanmaya devam ediyor; RRF sıralama puanı güven puanı gibi sunulmuyor. LaBSE, Chroma koleksiyonu ve LLM değişmedi; yeni paket bağımlılığı eklenmedi.

## Ölçüm

Tekrar üretme (`backend/` içinden):

```bash
.venv/bin/python -m unittest discover -s tests -q
.venv/bin/python -m scripts.check_course_transfer --benchmark --api-url http://127.0.0.1:8000
```

69 test geçti; bunların 12'si yeni erişim/kapsam regresyonları. Testler yanlış dense adayların önüne doğru maddenin gelmesini, gerçek kosinüsün korunmasını, Türkçe ekli ifadeleri, kopya kaynakları, öğrenim düzeylerini, kapsam seçiminin ilk soruyu korumasını, parçalanmış koşulları, boş/küçük koleksiyonu ve indeks güncellemelerini kapsıyor.

Sekiz ders saydırma sorusunda hedef madde eski dense aramada ilk 10'a girmedi. Hibrit sıraları sırasıyla **1, 4, 2, 5, 1, 1, 1, 2**; sekizinin tamamı ilk 5'te.

Mevcut `data/eval/v1` geliştirme verisindeki cevaplanabilir sorular ve varyantlarıyla 90 sorgu karşılaştırıldı:

| Kaynak erişimi ölçümü | Dense | Hibrit |
|---|---:|---:|
| En az bir hedef alıntı ilk 5'te | 27/90 | 65/90 |
| Hedef alıntıların tamamı ilk 5'te | 16/90 | 54/90 |
| Soru başına ortalama alıntı recall@5 | %23,52 | %65,93 |
| Isınmış erişim medyanı | 15,82 ms | 16,54 ms |

Eşleşme normalize edilmiş alıntıların 80 karakterlik bölümleriyle; kısa alıntılarda ayrıca belge adıyla ölçülüyor. Bu veri uzman onaylı bağımsız test değildir; bu sonuçlar cevap doğruluğu, kullanıcı başarı oranı veya halüsinasyon oranı değildir. İlk BM25 kurulumunun maliyeti ve LLM üretimi gecikme tablosuna dahil değil. Tam sonuçlar, veri hash'leri, kaynaklar ve canlı cevaplar `docs/course-transfer-retrieval.json` içinde.

## Canlı API ve kalan sınırlar

Orijinal soru artık ilk sırada doğru bağımsız yönetmeliği getiriyor ve öğrenim düzeyini soruyor. İkinci genel varyantta da lisans/lisansüstü karışması açıklama kapısıyla durduruldu. Açık lisans sorusu Madde 25'ten başvuru, son 5 yıl, CC ve üçte bir sınırını; yüksek lisans sorusu kendi hükmünden CB/BB ve ilgili kredi sınırlarını getirdi. Ardından “Lisans için soruyorum” takibi de Madde 25'i ilk sırada buldu; ilk kayıt, başvuru belgeleri, AKTS/içerik uygunluğu ve CC koşullarını aktardı. Yerel FastAPI servisi bu değişikliklerle yeniden başlatıldı.

**Cevap üretimi tamamen çözülmedi.** Tek turlu lisans cevabı AKTS ve içerik uygunluğu koşulunu açıkça saymadı ve toplam muafiyet sınırını tek ders gibi ifade etti. Takip cevabı bu uygunluğu aktardı ama birim yönetim kurulu kabulünü eksiltti. Önceki model denemelerinde lisans/lisansüstü şartlarının karışması da görüldü. Kapsam kapısı belirsiz sorulardaki bu riski azaltıyor; tüm koşulların eksiksiz aktarılmasını garanti etmiyor. Sonuçlar olduğu gibi JSON'da korunuyor; takip sorusunun önceki başarısız cevabı da `api_followup_before_scope_resolution` alanında saklandı.

25 geliştirme sorgusunda hedef alıntı ilk 5'e hâlâ gelmiyor. Öğrenim düzeyi tanıma iki geniş sınıf ve terim eşleşmesi kullanan bir sezgisel yöntem; tam mevzuat ontolojisi değil. Eski/yeni yönetmelik sürüm önceliği ayrıca çözülmeli. Sonraki kalite işi, madde bazlı parçalama ve kaynak/sürüm/kapsam ilişkileriyle uzman denetimli değerlendirme.

BM25 indeksi bellekte tutuluyor. Aynı süreçteki `add()` ve koleksiyon sayısındaki değişiklikler önbelleği yeniliyor. Başka süreç aynı sayıda kaydı upsert ederse değişiklik otomatik tespit edilmiyor; indeksleme sonrası API servisini yeniden başlatmak gerekiyor.
