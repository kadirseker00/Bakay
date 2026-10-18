# BAKAI rektörlük sunumu ve demo akışı

18 Ekim 2026. Yaklaşık 7 dakika anlatım ve 2 dakika canlı gösterim.
Sunumu yapan: Yrd. Doç. Dr. Abdulkadir Şeker.

## Sunumun ana cümlesi

“BAKAI, üniversitemizin resmî belgelerinden yararlanarak Türkçe sorulara kaynaklarıyla yanıt veren, KTMÜ BAP kapsamında geliştirdiğim kurumsal bilgi asistanıdır.”

## İki dakikalık canlı demo

1. **00.00–00.20:** [BAKAI’yi açın](https://bakai.manas.edu.kg/). Kaynaklı soru-cevap amacını bir cümleyle anlatın.
2. **00.20–01.10:** “Lisansta daha önce aldığım dersleri saydırabilir miyim?” sorusunu sorun veya kayıtlı mevcut görüşmeyi gösterin. Soruda öğrenim düzeyinin belirtilmesine dikkat çekin. Yanıtın gelmesini beklerken ilgili belge bölümlerinin kullanıldığını açıklayın.
3. **01.10–01.40:** Yanıtın sonundaki belge bağlantısını ve kaynak parçalarını açın. Kaynak sayısı sorguya göre değişebilir. Asıl belgede ilgili maddeyi gösterin. Benzerlik yüzdesini yanıt doğruluğu veya güven puanı olarak anlatmayın.
4. **01.40–02.00:** Önceden giriş yaptığınız [yönetim ekranında](https://bakai.manas.edu.kg/monitor) yalnız sağlık, maliyet ve yedek özetini gösterin. Soru-cevap ayrıntılarını ve kişisel bilgileri toplantı ekranına yansıtmayın.

Yanıt gecikirse veya bağlantı kesilirse 4. slayttaki gerçek arayüz görüntüsünü gösterin. Bu görüntünün kayıtlı bir örnek olduğunu açıkça belirtin. Sonra 9. slayttaki birim katkısı talebiyle kapatın. Gizli pencere yeni görüşmeyi mevcut tarayıcı geçmişinden ayırmak için kullanılabilir. Demo öncesi mevcut konuşmayı silmek zorunlu değildir.

## Toplantı öncesi

- Sunumun PPTX dosyasını ve çevrimdışı PDF kopyasını açık tutun.
- BAKAI ana sayfasını ve örnek kaynak belgesini ayrı sekmelerde hazırlayın.
- Yönetim ekranına özel olarak giriş yapın. Parolayı slayta, notlara veya yansıtılan bir alana yazmayın.
- Bildirimleri ve kişisel posta kutularını toplantı ekranından uzak tutun.

## Sorulabilecek sorular

**Her cevabı doğru mu?** Kaynakları gösterir, ancak hata veya eksik koşul oluşabilir. Birim uzmanlarının soruları ve kaynaklı beklenen cevaplarıyla kurum içi değerlendirme bir sonraki adımdır. Genel doğruluk yüzdesi henüz yoktur.

**Bilgi ne kadar güncel?** Yanıtlar indekse alınmış belgelere dayanır. Belgenin yürürlükteki sürümünü ilgili birim doğrulamalı, değişen kaynaklar yeniden işlenmelidir. Tüm kaynakların otomatik olarak her an güncellendiği söylenmemelidir.

**Veriler nerede?** Uygulama ve belge indeksi KTMÜ sunucusundadır. Üretimde yanıt modeli haricî Anthropic API hizmetidir. Yanıt üretiminde soru ve ilgili belge alıntıları bu hizmete iletilir. Öğrenciye özel gizli dosyaların kullanımını bu sunum kapsamına eklemeyin.

**Maliyeti nedir?** 9 Ekim’deki 30 soruluk Haiku adaptive/medium pilotunun token tüketimi yaklaşık 0,0383 USD olarak hesaplandı. Aynı ortalamayı 1.000 yanıta ölçeklemek yaklaşık 1,28 USD eder. Bu yalnız LLM kullanımı için tarihli bir tahmindir. Sunucu ve diğer hizmet giderleri ile gelecekteki tarife değişikliklerini kapsamaz. Günlük 1 USD eşiği bildirim üretir, harcamayı durdurmaz.

**Yedek ve alarm var mı?** Her gece 02.00 Bişkek saatinde şifreli Drive yedeği, gerçek geri yükleme kontrolü ve okul adresinden yöneticiye e-posta bildirimi vardır. Kurulum testi alıcıya ulaşmıştır.

**Şimdi rektörlükten ne isteniyor?** İlgili birimlerden gerçek sorular, beklenen cevaplar ve güncel resmî kaynak bağlantılarının istenmesi. Kaynak güncelliği için birim irtibat kişileri belirlenmesi de önerilir. Bu talep henüz gönderilmiş değildir.

## Personelden daha sonra alınabilecek kayıt

Soru, ilgili birim, beklenen yanıt, belge/sayfa bağlantısı, madde veya bölüm, kaynağın güncellik tarihi. Örnekler kimlik numarası ve kişiye özel dosya içermemelidir. Bu kayıtlar henüz toplanmamıştır.

## Slayt bazında konuşmacı notları


### 1. BAKAI

Yaklaşık 35 saniye. Sayın Rektörüm, BAKAI üniversitemizin resmî belgelerine dayanarak Türkçe sorulara kaynaklarıyla cevap veren kurumsal bilgi asistanıdır. KTMÜ BAP projemiz kapsamında geliştirdiğim uygulama üniversite sunucusunda çalışıyor. Bugün çalışan sistemi ve personelimizin katılımıyla ilerletebileceğimiz değerlendirme adımını sunacağım.

Kaynaklar: https://bakai.manas.edu.kg/hakkinda, frontend/app/lib/project.ts, docs/deployment/ktmu.md

### 2. Projenin kimliği

Yaklaşık 40 saniye. BAKAI adını Manas Destanı’ndaki bilge danışman Bakay’dan alıyor. BAP başvurusundaki tarihsel ad BAKAY, aynı zamanda Bütünleşik Akıllı Kurumsal Asistan Yazılımı açılımına sahip. Ürün adını BAKAI olarak kullanıyoruz. Resmî BAP adı ve numarası değişmiyor. Uygulamayı Bilgisayar Mühendisliği Bölümünde yürütülen bu araştırma projesi kapsamında geliştirdim.

Kaynaklar: https://bakai.manas.edu.kg/hakkinda, frontend/app/lib/project.ts, BAP_Files/BAP_Basvuru_Formu_TR.pdf

### 3. Kurumsal bilgiye erişim

Yaklaşık 45 saniye. Öğrencilerimiz, adaylarımız ve personelimiz bir sorunun cevabını farklı web sayfalarında veya uzun yönetmeliklerde arayabiliyor. BAKAI’nin amacı, doğal dilde sorulan soruyu ilgili belge bölümleriyle buluşturmak ve cevabın dayanağını görünür kılmak. Beklenen fayda bilgi arama ve tekrarlanan yönlendirme yükünü azaltmak. Bu faydanın büyüklüğünü henüz ölçtüğümüzü iddia etmiyoruz. İndeks sayısı belge veya kullanıcı sayısı değildir.

Kaynaklar: README.md, backend/app/rag/pipeline.py, Canlı /api/health: 18 Ekim 2026, indexed_chunks=39659

### 4. Yanıt ve dayandığı kaynak

Yaklaşık 50 saniye. Burada canlı sitede kayıtlı gerçek bir görüşmenin ekran görüntüsü var. Örnek soru, lisansta daha önce alınan derslerin saydırılması. Sistem ilgili belge bölümlerini buluyor, yanıtı hazırlıyor ve kaynak parçalarını belge bağlantısıyla birlikte sunuyor. Ekran görüntüsü genel doğruluk oranının kanıtı değildir. Kullanıcı kaynak belgesine geçerek koşulları kontrol edebiliyor. Sonucun doğruluğu, kaynağın yürürlüğü ve eksik koşullar birim uzmanları tarafından değerlendirilmelidir. Model eğitiminden söz etmek yerine belgeye dayalı yanıt üretimini anlatın.

Kaynaklar: https://bakai.manas.edu.kg/, assets/bakai-ornek-yanit.png: 18 Ekim 2026 canlı arayüz görüntüsü, backend/app/rag/pipeline.py

### 5. Canlı işletim ve koruma

Yaklaşık 50 saniye. Uygulama üniversite sunucusunda çalışıyor. Dakikalık izleme sistem sağlığını, yanıt sürelerini, hata ve maliyet kayıtlarını takip ediyor. Yönetim ekranı parola korumalı. Soru sınırı IP başına dakikada 30, başka ortak kotalar da var. Bu kural her kullanıcı için ayrı hesap kotası anlamına gelmez. Şüpheli trafikte Turnstile doğrulaması devreye giriyor. Her gece Bişkek saatiyle 02.00’de şifreli yedek Drive’a aktarılıyor. Drive’dan indirilen kopyayla gerçek geri yükleme doğrulandı. E-posta alarmı kurulumu bugün gerçek gelen kutusu teslimatıyla doğrulandı. Koruma önlemleri sıfır risk garantisi vermez.

Kaynaklar: docs/deployment/operations.md, collab/board.md: canlı rate limit 30/dakika, 13 Ekim, backend/app/alerts.py

### 6. Maliyet ve bütçe takibi

Yaklaşık 50 saniye. Canlı yanıt üretiminde Haiku 5.5 kullanıyoruz. Buradaki tutar, 9 Ekim tarihli geliştirme pilotunda adaptive/medium ayarında bulunan 30 yanıtın toplam token maliyeti tahmini. 0,0382614 USD toplamını bin yanıta ölçeklediğimizde yaklaşık 1,28 USD çıkıyor. Bu, güncel tarife taahhüdü veya gelecekteki kullanım bütçesi değildir. Yanıt uzunluğu, düşünme tokenları ve sağlayıcı tarifesi maliyeti değiştirir. Sunucu ve diğer hizmet giderlerini kapsamaz. Canlı panel kullanım sayaçlarından maliyeti tahmin ediyor. Günlük 1 USD eşiği e-posta uyarısı gönderiyor, harcamayı otomatik durdurmuyor.

Kaynaklar: docs/evaluation/2026-10-09-haiku/report.md: 30 soru, adaptive/medium, 0.0382614 USD, docs/deployment/operations.md, Canlı /api/health: llm_model=claude-haiku-5-5

### 7. Birimlerle yanıt değerlendirmesi

Yaklaşık 50 saniye. Sunum sonrasında rektörlüğün yönlendirmesiyle personelimizden kendi alanlarında gerçek sorular ve beklenen cevapları isteyebiliriz. Her cevap için yürürlükteki belge veya resmî sayfa bağlantısı da gerekir. BAKAI yanıtlarını bu beklentilerle karşılaştırır, hata veya eksik koşulları ilgili birimle inceleriz. Sonra kaynakları ve sistemi düzeltip aynı soruları tekrar değerlendiririz. Bu aşama planlanan kurum içi değerlendirmedir, tamamlanmış bir doğruluk testi değildir. Pilot deneyleri genel doğruluk yüzdesi olarak sunmayın. Kimlik numarası ve öğrenciye özel kişisel dosyalar yerine anonimleştirilmiş örnekler isteyin.

Kaynaklar: Kullanıcı yönlendirmesi: kalite değerlendirmesi sunumdan sonra personelin soru-cevaplarıyla, docs/evaluation/gold-v1/README.md

### 8. Canlı gösterim

Yaklaşık 2 dakika. Sunumdan tarayıcıya geçin ve bakai.manas.edu.kg adresini açın. Önce mevcut kayıtlı örneği gösterebilir veya yeni bir soru sorabilirsiniz. Örnek: “Lisansta daha önce aldığım dersleri saydırabilir miyim?” Yanıt gelince koşullara ve metnin sonundaki belge bağlantısına dikkat çekin. “5 kaynak parçası” düğmesini açıp ilgili bölümün başlığını gösterin. Sayı her sorguda değişebilir. Bağlantıyı yeni sekmede açıp belgenin dayanağını gösterin. Yönetim paneli kullanılacaksa sunum öncesi özel giriş yapın ve yalnız toplu sağlık/maliyet alanlarını gösterin. Sorgu ayrıntılarındaki kişisel bilgileri yansıtmayın. Yanıt gecikirse kaydedilmiş örneğe veya önceki slayttaki gerçek ekran görüntüsüne dönün. Sonraki slayta geçerek birimlerin katkı talebiyle kapatın.

Kaynaklar: https://bakai.manas.edu.kg/, Demo-ve-konusma-notlari.md

### 9. Birimlerin katılımıyla kurumsal pilot

Yaklaşık 35 saniye. BAKAI’nin çalışan uygulaması hazır. Bir sonraki adımımız personelimizin soruları ve uzman bilgisiyle yanıt kalitesini kurum içinde değerlendirmek. Rektörlüğümüzün ilgili birimlerden soruları, beklenen cevapları ve güncel kaynakları istemesi bu aşamayı başlatabilir. İlgili birimlerde kaynakları güncel tutacak bir irtibat kişisi belirlemek de süreci sürdürülebilir kılar. Bu aşamada geniş kapsamlı veya kesin bir doğruluk oranı taahhüt etmiyoruz. Teşekkür edip soruları alın.

Kaynaklar: Kullanıcının rektörlük sunumu ve personel soru-cevap değerlendirmesi planı, https://bakai.manas.edu.kg/hakkinda
