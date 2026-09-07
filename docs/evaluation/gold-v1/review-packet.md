# BAKAY: 50 Soruluk Uzman İnceleme Paketi

İki uzman onaylı kayıt: 0/50. Onaysız kayıtlar **TASLAK, GOLD DEĞİL**.
Kaynakların güncel yürürlüğü doğrulanmadı; bu paket arşiv kopyalarının incelemesidir.

Bu dosya `python -m scripts.dataset review` ile üretilir. Asıl kayıt `data/eval/v1/dataset.json`.

Her soru için iki farklı insan; kapsamı, kaynak sürümünü, cevabı ve olumsuz örnekleri kontrol etmelidir.
Onay özeti aşağıdadır; cevap/kaynak değişirse eski onay geçersiz olur. İnceleme protokolü: [README](README.md).

## BAKAY-001: Lisans kesin kaydımı kendim yapamazsam vekil gönderebilir miyim?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Önlisans/lisans adayları; Tıp hariç

Soru varyantı: Lisans kaydı için noter vekâleti kabul ediliyor mu?

**Taslak cevap:** Evet. İlan edilen kesin kayıt tarihlerinde bizzat başvurabilir veya noter aracılığıyla tayin ettiğiniz vekille kayıt yaptırabilirsiniz. Süresinde kayıt yaptırmayan aday öğrenci olma hakkını kaybeder.

**Beklenen noktalar:**

- Noter aracılığıyla tayin edilmiş vekil kabul edilir.
- İlan edilen kayıt süresine uyulmalıdır.

**Yanlış sayılacak iddialar:**

- Herhangi bir yakının vekâletsiz kayıt yapabileceği.
- Kayıt süresinin vekil kullanınca uzadığı.

**Dayanaklar:**

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 3, basılı sayfa 155, Madde 10(2)

> Üniversiteye kayıt hakkı kazanan aday kesin kaydını, ilan edilen tarihlerde bizzat kendisi yapar veya noter vasıtasıyla tayin ettiği vekili aracılığıyla yaptırır. Belirlenen süre içinde kayıt yaptırmayan aday, öğrenci olma hakkını kaybeder.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `d4e716b71eb6b5d110a0387066c6da4c085ff3d81470496bf33b4e31c95f422a`

## BAKAY-002: Başka bir üniversitede örgün lisans kaydım varken Manas'ta da lisansa kayıt olabilir miyim?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Önlisans/lisans adayları; Tıp hariç

Soru varyantı: Aynı anda iki örgün lisans kaydı mümkün mü?

**Taslak cevap:** Bu yönetmeliğe göre kayıt şartlarından biri, aynı seviyede örgün öğretim yapan başka bir yükseköğretim kurumuna kayıtlı olmamaktır. Bu nedenle belirtilen durumda Manas'a ikinci örgün lisans kaydı yapılamaz.

**Beklenen noktalar:**

- Yasak aynı seviyedeki örgün yükseköğretim kaydı içindir.

**Yanlış sayılacak iddialar:**

- Farklı seviyeler veya açıköğretim için de bu maddeyle kesin yasak ilan etmek.

**Dayanaklar:**

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 3, basılı sayfa 155, Madde 10(1)(b)

> Aynı seviyede örgün öğretim yapan başka bir yükseköğretim kurumuna kayıtlı olmamak.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `4922a1d29aa24fcf72db7e3b84ba64dfc93e3fe16af47e0ed186755ea7c87613`

## BAKAY-003: Önlisans, lisans ve veterinerlikte normal öğrenim süresi kaç yarıyıl? Hazırlık buna dahil mi?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Önlisans/lisans ve Veteriner; Tıp hariç

Soru varyantı: Manas'ta hazırlık hariç önlisans, lisans ve veterinerlik ne kadar sürer?

**Taslak cevap:** Normal süre önlisansta 4, lisansta 8, Veteriner Fakültesinde 10 yarıyıldır. Hazırlık sınıfında geçirilen süre programın normal ve azami öğrenim sürelerine dahil değildir.

**Beklenen noktalar:**

- 4 / 8 / 10 yarıyıl sırasını doğru eşleştirmek.
- Hazırlığın normal ve azami süreye dahil olmadığını belirtmek.

**Yanlış sayılacak iddialar:**

- Bu yönetmeliği Tıp Fakültesine uygulamak.
- Normal süre ile azami süreyi karıştırmak.

**Dayanaklar:**

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 3, basılı sayfa 155, Madde 14(1), başlangıç

> Normal öğrenim süresi hazırlık sınıfı hariç önlisans programlarında 4 yarıyıl, lisans

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 4, basılı sayfa 156, Madde 14(1), devamı

> programlarında 8 yarıyıl, Veteriner Fakültesinde ise 10 yarıyıldır.

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 4, basılı sayfa 156, Madde 14(3)

> Hazırlık sınıfında geçirilen süre program süresine ve azami öğrenim süresine dâhil değildir.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `76325c24cf03504e8390753e3081004aa6fc390dc18f9d2cf0e8270a2ea12430`

## BAKAY-004: Lisansta ilk kez aldığım teorik ve uygulamalı derslere ne kadar devam etmeliyim?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Önlisans/lisans; Tıp hariç

Soru varyantı: Lisans derslerinde yoklama sınırı teorik ve uygulamada yüzde kaç?

**Taslak cevap:** İlk kez alınan teorik dersin en az %70'ine, uygulamalı dersin en az %80'ine devam gerekir. Ders iki kısmı birlikte içeriyorsa teorik kısımda %70, uygulamada %80 şartı ayrı ayrı sağlanmalıdır.

**Beklenen noktalar:**

- Teorik %70, uygulama %80.
- Karma derste iki bölümün devamı ayrı değerlendirilir.

**Yanlış sayılacak iddialar:**

- Her iki ders türü için tek bir oran vermek.
- Hazırlıktaki %85 oranını lisansa uygulamak.

**Dayanaklar:**

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 7, basılı sayfa 159, Madde 28(1)

> İlk defa kayıt olunan teorik dersin en az %70’ine, uygulamalı dersin en az %80’ine, teorik ve uygulamadan oluşan dersin teorik kısmının en az %70’ine ve uygulama kısmının en az %80’ine katılmak gerekir.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `9a673aee60fb282ff1716047886d3a9145578cb61d21fce23a59aec5d7e1cccf`

## BAKAY-005: Lisansta devamını aldığım ama kaldığım dersi tekrar alırken devam zorunlu mu?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Önlisans/lisans; Tıp hariç

Soru varyantı: Lisansta yoklamadan değil nottan kaldım, tekrar derse girmem gerekir mi?

**Taslak cevap:** Devam şartını daha önce yerine getirip başarısız olduğunuz veya not yükseltmek için tekrar aldığınız derste normalde devam aranmaz. Ancak Spor Bilimleri ve Güzel Sanatlar fakültelerinin bireysel uygulamalı derslerinde fakülte yönetim kurulu devam zorunluluğu koyabilir. Devamsızlıktan tekrar alınan derslerde ise devam gerekir.

**Beklenen noktalar:**

- Devam alıp nottan kalma ile devamsızlığı ayırmak.
- Bireysel uygulamalı ders istisnasını belirtmek.

**Yanlış sayılacak iddialar:**

- Tekrar alınan hiçbir derste devam gerekmediği.

**Dayanaklar:**

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 8, basılı sayfa 160, Madde 28(3-5)

> Devamsızlık sebebiyle tekrar alınan dersler için devam şartı aranır. (4) Devam şartı yerine getirilen ve başarısız olunan veya not yükseltmek için tekrar alınan dersten devam şartı aranmaz. (5) Spor Bilimleri Fakültesi ve Güzel Sanatlar Fakültesinde bireysel uygulamalı derslerin tekrar alınışında Fakülte Yönetim Kurulu kararı ile devam zorunluluğu aranabilir.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `9d4f99e15622083d38fc21b755d74be8d2d14e717eb74503f0a55096fc9ebdb2`

## BAKAY-006: Başka üniversiteden Manas'a yatay ya da dikey geçiş yapabilir miyim?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Önlisans/lisans; Tıp hariç

Soru varyantı: Dışarıdan KTMÜ lisans programına transfer öğrenci kabul ediliyor mu?

**Taslak cevap:** Bu yönetmelik başka yükseköğretim kurumlarından yatay ve dikey geçişle öğrenci kabul edilmediğini belirtiyor. Buna karşılık Manas'ın kendi öğrencileri gerekli şartları sağlarsa ilgili yönerge kapsamında kurum içinde geçiş yapabilir.

**Beklenen noktalar:**

- Kurum dışından kabul edilmez.
- Kurum içi geçiş gerekli şartlarla mümkündür.

**Yanlış sayılacak iddialar:**

- Kurum içi ve dışı geçişi aynı kabul etmek.
- Lisansüstüne de otomatik olarak aynı yasak koymak.

**Dayanaklar:**

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 7, basılı sayfa 159, Madde 26(1)

> Başka yükseköğretim kurumlarından Üniversiteye yatay ve dikey geçiş yoluyla öğrenci kabul edilmez. Gerekli şartları sağlayan Üniversitenin öğrencisi ilgili bölüme/programa yatay ve dikey geçiş yapabilir.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `20243e772c7e3f57738e7b7cb01e332347e91c603a0850fda3c0b55bc96855ea`

## BAKAY-007: Manas'ta çift anadal veya yandal yapma imkânı var mı?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Lisans; Tıp hariç

Soru varyantı: Lisans okurken ikinci bölümde ÇAP ya da yan dal yapabilir miyim?

**Taslak cevap:** Lisans öğrencisine kendi programına ek olarak başka bölümde yandal veya çift anadal programına eş zamanlı kayıt izni verilebilir. Ayrıntılı şartlar ilgili Yandal ve Çift Anadal Programı yönergelerinde düzenlenir; bu madde tek başına kabul garantisi değildir.

**Beklenen noktalar:**

- İzin verilebileceğini, otomatik hak olmadığını belirtmek.
- Şartlar için ilgili yönergelere yönlendirmek.

**Yanlış sayılacak iddialar:**

- Kaynakta olmayan GANO, kontenjan veya başvuru tarihi uydurmak.

**Dayanaklar:**

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 7, basılı sayfa 159, Madde 27

> Lisans programlarında bir bölümün öğrencisine, kendi lisans programına ek olarak bir başka bölümde yandal veya çift anadal programına aynı zamanda kayıt olma izni verilebilir.

İnceleme notu: ÇAP/çift anadal ve yan dal/yandal varyantları elle kontrol edilmeli; yönergedeki sayısal şartlar bu pakette yok.

Onaylanacak içerik SHA-256: `804c0e6da5b0dd647804355f176e6e60b6267419096c97359741e7c1de5aa864`

## BAKAY-008: Lisansta üçüncü yarıyıldayım, GANO'm 1,70. Genel ders yükü kuralına göre en çok kaç AKTS alabilirim?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Lisans; olağan ders yükü, Tıp hariç

Soru varyantı: 3. dönemde ortalamam 1.80'in altında; olağan ders yükü tavanım nedir?

**Taslak cevap:** İlk iki yarıyıl dışındaki genel kurala göre GANO'su 1,80'in altında olan öğrenci 32 AKTS'ye kadar ders alabilir. 1,80 ve üzerindekiler için kendi ve alt yarıyıllardan 42 AKTS sınırı vardır.

**Beklenen noktalar:**

- Bu durumda 32 AKTS.
- 1,80 eşiği ve ilk iki yarıyıl istisnasını korumak.

**Yanlış sayılacak iddialar:**

- 1,70 GANO için olağan sınırı 42 AKTS diye vermek.

**Dayanaklar:**

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 6, basılı sayfa 158, Madde 21(7)

> 1. Yarıyıl ve 2.Yarıyıl hariç bir yarıyılda, o yarıyıla kadar olan GANO’su dörtlük sisteme göre 1.80’in altında olan öğrenci 32 AKTS'ye kadar, GANO’su dörtlük sisteme göre 1.80 ve üstünde olan öğrenci alt yarıyıllardan ve kendi yarıyılından 42 AKTS'ye kadar ders alabilir.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `51b1ddfb6a1d83b39b7b4a01381da5520f1850204fe275355c0bcf09ea7df6bc`

## BAKAY-009: Üçüncü yarıyıldan itibaren üstten ders almak için GANO ve ders şartı nedir?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Önlisans/lisans; Tıp hariç

Soru varyantı: Lisansta üst dönem dersi seçebilmem için hangi koşullar gerekiyor?

**Taslak cevap:** GANO en az 3,00 olmalı ve alt yarıyılların bütün dersleri başarılmış olmalıdır. Üçüncü yarıyıldan itibaren önce kendi yarıyılında yükümlü olunan dersler alınır; toplam 42 AKTS aşılmadan üst yarıyıldan ders alınabilir.

**Beklenen noktalar:**

- En az 3,00 GANO ve alt yarıyılların tüm derslerinde başarı.
- Üçüncü yarıyıldan itibaren, kendi dersleri öncelikli, toplam en çok 42 AKTS.

**Yanlış sayılacak iddialar:**

- Yalnızca yüksek ortalamanın yeterli olduğu.

**Dayanaklar:**

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 6, basılı sayfa 158, Madde 21(8)

> GANO’su dörtlük sisteme göre 3.00 ve üstünde olan ve alt yarıyıllardan bütün derslerini başarıyla tamamlayan öğrenci, 3.Yarıyıldan itibaren kayıt yaptıracağı yarıyıldan almakla yükümlü olduğu derslerini aldıktan sonra, 42 AKTS'yi aşmamak kaydıyla üst yarıyıllardan ders alabilir.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `ace8609bd51a6851615a4e2840813051dcd6f591a9ea63f29bb1363eb4d6e324`

## BAKAY-010: Lisansta CC aldığım dersi not yükseltmek için tekrarlarsam hangi not geçerli olur?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Önlisans/lisans; Tıp hariç

Soru varyantı: CC dersini yeniden alıp daha düşük not alırsam eski notum korunur mu?

**Taslak cevap:** Ders yükü sınırları içinde DD, DC veya CC olan dersleri not yükseltmek için tekrar alabilirsiniz. Bu durumda en yüksek not değil, en son alınan not geçerlidir.

**Beklenen noktalar:**

- CC dahil tekrar mümkündür, ders yükü sınırına tabidir.
- Son alınan not geçerlidir.

**Yanlış sayılacak iddialar:**

- Eski ve yeni notun ortalamasının veya yüksek olanın kullanılacağı.

**Dayanaklar:**

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 13, basılı sayfa 165, Madde 42

> Ders yükü sınırları içinde kalmak şartıyla öğrenci, notlarını yükseltmek üzere başarı notu DD, DC ve /veya CC olan derslere tekrar kayıt yaptırabilir. Bu durumda en son alınan not geçerli sayılır.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `c7e500bbd51bdcda0025dcffd759b10d5f2979b092d9f65a35022d1590fd7081`

## BAKAY-011: Manas lisansına ilk kayıtta eski üniversitemde başardığım dersleri saydırmanın şartları neler?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Önlisans/lisansa ilk kayıt; Tıp hariç

Soru varyantı: Önceden geçtiğim lisans dersleri için muafiyet başvurusu nasıl değerlendirilir?

**Taslak cevap:** Bölüm Başkanlığına transkript ve ders içerikleri eklenmiş yazılı başvuru gerekir. Son 5 yılda alınmış, en az CC ile başarılmış, AKTS ve içeriği uygun dersler değerlendirilebilir. Muafiyet toplamı program AKTS'sinin üçte birini aşamaz; kurul kabulüyle kesinleşir.

**Beklenen noktalar:**

- Transkript ve ders içerikleriyle Bölüm Başkanlığına yazılı başvuru.
- Son 5 yıl, en az CC, uygun içerik ve AKTS.
- Program AKTS'sinin en çok üçte biri; kurul kabulü.

**Yanlış sayılacak iddialar:**

- Başarılmış tüm derslerin otomatik sayılacağı.
- Lisansüstündeki yarı AKTS sınırını uygulamak.

**Dayanaklar:**

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 7, basılı sayfa 159, Madde 25(2-3)

> Ders saydırma ve ders muafiyetleri işlemleri öğrencinin Bölüm Başkanlığına, ekinde not durum belgesi ve ders içerikleri bulunan yazılı başvurusu ile başlatılır.

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 7, basılı sayfa 159, Madde 25(3)

> öğrenci son 5 yıl içinde alınmış olması ve başarı notunun en az CC olması şartıyla AKTS’si ve içeriği uygun olan derslerden muaf tutulabilir. Muaf tutulacak ders AKTS sayısı, kayıtlı olduğu programın AKTS sayısının 1/3‘ünden fazla olamaz. İntibak işlemleri Bölüm Akademik Kurulunun kararı ve Birim Yönetim Kurulunun kabulü ile kesinleşir.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `3fb932420e4dd04745aeb2f78d203987b8e2fad5152edd3f11a4082b88858d2f`

## BAKAY-012: Lisansta seçmeli dersin açılması için en az kaç öğrencinin kayıt olması gerekir?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Önlisans/lisans; Tıp hariç

Soru varyantı: Bir seçmeli derse yalnızca altı kişi yazıldıysa ders normal şartlarda açılır mı?

**Taslak cevap:** Zorunlu haller dışında en az 7 öğrenci gerekir. Ekle-sil süresi sonuna kadar yeterli kayıt yoksa seçmeli ders açılmaz.

**Beklenen noktalar:**

- En az 7 öğrenci ve zorunlu hal istisnası.
- Kontrol ekle-sil süresi sonunda yapılır.

**Yanlış sayılacak iddialar:**

- İstisnasız her durumda yedi kişi şartı olduğunu söylemek.

**Dayanaklar:**

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 7, basılı sayfa 159, Madde 22

> Zorunlu haller dışında bir seçmeli dersin açılabilmesi için en az yedi (7) öğrencinin derse kayıt yaptırması gerekir. Ders ekleme silme süresi sonuna kadar bir derse yeteri kadar öğrenci kayıt yaptırmamış ise o ders açılmaz.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `2d843e0a6d0d7587821b6e45f188dfcaf082198ef722daec2bf87f2949b30555`

## BAKAY-013: Lisansta finalden 40 almam dersten kesin geçtiğim anlamına gelir mi?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Önlisans/lisans; Tıp hariç

Soru varyantı: Final barajını geçtim; lisans dersini otomatik geçmiş sayılır mıyım?

**Taslak cevap:** Hayır. Finalden en az 40 almak tek başına geçmeye yetmez; devam şartı ve dersin toplam değerlendirmesi de gerekir. Dersten başarılı sayılmak için başarı harf notu en az DD olmalıdır.

**Beklenen noktalar:**

- 40 yalnızca final için alt eşiktir.
- Devam şartı ve en az DD başarı notu da gerekir.

**Yanlış sayılacak iddialar:**

- Finalden 40 alan herkesin dersten geçtiği.
- Lisansüstündeki 50 puan eşiğini lisansa aktarmak.

**Dayanaklar:**

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 12, basılı sayfa 164, Madde 40(3)

> Devam şartını yerine getirmeyen, yarıyıl sonu sınavına girmeyen veya yarıyıl sonu sınavında en az 40 puan alamayan öğrenci başarısız sayılır.

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 12, basılı sayfa 164, Madde 40(5)

> Bir dersten başarılı sayılmak için o dersin başarı harf notunun en az DD olması gerekir.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `1abed91937561ec5070d34f21e46fd216e2915349df26d7868a777d7fd58ee19`

## BAKAY-014: Lisans öğrencisiyim, mazeret sınavı için ne zaman ve hangi belgelerle başvurmalıyım?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Önlisans/lisans; Tıp hariç

Soru varyantı: Lisansta raporum bitince mazeret sınavı başvurusunu nereye yapacağım?

**Taslak cevap:** Mazeretin bitiminden sonraki hafta içinde Mazeret Sınavı Başvuru Formuyla Bölüm Başkanlığına başvurmalısınız. Sağlık mazeretinde Üniversite Sağlık Merkezince onaylı rapor, diğer mazeretlerde ilgili kanıtlayıcı belgeler gerekir. Sınav hakkı mazeretin kurulca kabulüne bağlıdır.

**Beklenen noktalar:**

- Mazeret bitiminden sonraki hafta.
- Form, Bölüm Başkanlığı ve mazeret belgeleri.
- Sağlık raporu Üniversite Sağlık Merkezi onaylı olmalı; mazeret kabulü gerekir.

**Yanlış sayılacak iddialar:**

- Lisansüstündeki sınav bitiminden itibaren 3 iş günü kuralını kullanmak.

**Dayanaklar:**

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 9, basılı sayfa 161, Madde 33(1)

> Birim Yönetim Kurulunun kararı ile mazereti kabul edilen öğrencinin giremediği dersin ara sınav ve/veya yarıyıl sonu sınavı yerine yapılan sınavdır.

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 9, basılı sayfa 161, Madde 33(3)

> Mazeret sınavına girmek isteyen öğrenci mazeretinin bitimden sonraki hafta içinde Mazeret Sınavı Başvuru Formunu doldurarak bölüm başkanlığına başvurur. Formun ekinde Üniversitenin Sağlık Merkezi tarafından onaylanmış sağlık raporu ile diğer mazeretlerin (doğal afet, birinci veya ikinci dereceden akrabaların ölümü, gözaltına alınma, tutuklanma, vb. durumlar) belgeleri bulunur.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `a485ecc94a8cf142f1ba742402e57dcc3477fb0db7a4d5e14ff90bffc57bb7ee`

## BAKAY-015: Lisans final sınav programı sınavların başlamasından kaç gün önce ilan edilir?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Önlisans/lisans; Tıp hariç

Soru varyantı: Lisans yarıyıl sonu sınav takvimi kaç gün önceden duyurulmalı?

**Taslak cevap:** Program, akademik takvimdeki yarıyıl sonu sınavlarının başlama tarihinden 15 gün önce ilan edilir. İlan edilen sınav tarihi zorunlu haller dışında değiştirilemez.

**Beklenen noktalar:**

- 15 gün önce.
- Tarih değişikliği için zorunlu hal istisnası.

**Yanlış sayılacak iddialar:**

- 15 iş günü demek.
- Kaynakta olmayan güncel sınav tarihi vermek.

**Dayanaklar:**

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 9, basılı sayfa 161, Madde 32(2)

> Yarıyıl sonu sınav programı, bölüm/program başkanlığınca düzenlenir ve Birim Yönetim Kurulu kararıyla akademik takviminde belirlenen yarıyıl sonu sınavlarının başlama tarihinden on beş (15) gün öncesinden ilan edilir. Zorunlu haller hariç ilan edilen sınav tarihi değiştirilemez.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `cd162a4d0b29d0110a53d6b9ef77583c4a6a8acda0afc5654314aa14943837d7`

## BAKAY-016: Mezuniyet için sadece stajım kaldı; tek ders sınavına girip tamamlayabilir miyim?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Önlisans/lisans; Tıp hariç

Soru varyantı: Lisans stajını tek ders sınavıyla geçmek mümkün mü?

**Taslak cevap:** Hayır. Bitirme tezi, staj, intörn dersi ve sektör uygulamaları gibi uygulama gerektiren çalışmalarda tek ders sınavı hakkı tanınmaz.

**Beklenen noktalar:**

- Staj için tek ders sınavı hakkı yoktur.

**Yanlış sayılacak iddialar:**

- Mezuniyete tek yükümlülük kalmasının staj için sınav hakkı verdiği.

**Dayanaklar:**

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 10, basılı sayfa 162, Madde 35(3)

> Bitirme tezi, staj, intörn dersi, sektör uygulamaları gibi uygulama gerektiren çalışmalarda tek ders sınav hakkı tanınmaz.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `b06bf7272782f7ebd513b868b6cbc8f997de5c7562021b8f33eb2f302ce07a99`

## BAKAY-017: Lisans dersimin sınav sonucundaki maddi hataya kaç gün içinde itiraz edebilirim?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Önlisans/lisans; Tıp hariç

Soru varyantı: Lisans not itirazını hangi süre içinde ve nereye yazmalıyım?

**Taslak cevap:** Sonuçların ilanından itibaren 7 iş günü içinde Birim Amirliğine yazılı maddi hata itirazı yapılabilir. Süresinde yapılmayan başvurular değerlendirilmez; bu maddeye göre sonuca yeniden itiraz hakkı yoktur.

**Beklenen noktalar:**

- İlandan itibaren 7 iş günü, Birim Amirliği, yazılı başvuru.
- Süresiz veya tekrarlanan itiraz hakkı tanımamak.

**Yanlış sayılacak iddialar:**

- 7 takvim günü demek.
- Lisansüstü yeniden itiraz yolunu bu soruya uygulamak.

**Dayanaklar:**

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 13, basılı sayfa 165, Madde 43

> Öğrenci dersin sınav sonuçları ilanından itibaren yedi (7) iş günü içinde Birim Amirliğine yazılı olarak maddi hata itirazında bulunabilir.

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 13, basılı sayfa 165, Madde 43, son

> Öğrencinin sonuca yeniden itiraz etme hakkı yoktur. Süresi içinde yapılmayan maddi hata itirazları değerlendirmeye alınmaz.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `727fd138968e6c6ead7aeaf4fe97175a7e4907ed4403c50f1824502c1bbcee23`

## BAKAY-018: Önlisans ve lisansta kaydımı toplam kaç yarıyıl dondurabilirim?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Önlisans/lisans; Tıp hariç

Soru varyantı: Kayıt dondurmanın tek seferlik ve toplam dönem sınırları nedir?

**Taslak cevap:** Mazeret nedeniyle Birim Yönetim Kurulu kararıyla, tek seferde en çok 2 yarıyıl olmak üzere önlisansta toplam 2, lisansta toplam 4 yarıyıl kayıt dondurulabilir. Dondurulan süre öğrenim süresinden sayılmaz.

**Beklenen noktalar:**

- Kurul kararı ve mazeret gerekir.
- Tek seferde 2; toplam önlisans 2, lisans 4 yarıyıl.
- Öğrenim süresinden sayılmaz.

**Yanlış sayılacak iddialar:**

- Lisansta tek seferde dört yarıyıl olağan hak olarak verilebilir demek.

**Dayanaklar:**

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 14, basılı sayfa 166, Madde 46(1-2)

> Kayıt dondurmak isteyen öğrenci mazeretlerinden dolayı Birim Yönetim Kurulu kararı ile öğrenimi süresince bir defada iki yarıyılı aşmamak kaydıyla önlisans programlarında iki, lisans programlarında dört yarıyıl süre ile kaydını dondurabilir. (2) Kayıt dondurma süreleri öğrenim süresinden sayılmaz.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `da06b0e60a1f71c6d2521995d26423ae23a7db0b6f6e21d6a084d63dadb8247f`

## BAKAY-019: Lisans kaydımı dondurduğum dönemde burs almaya ve öğrenci evinde kalmaya devam eder miyim?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Önlisans/lisans; kayıt dondurma, Tıp hariç

Soru varyantı: Kayıt dondurunca burs ve yurt hakkım da durur mu?

**Taslak cevap:** Bu yönetmeliğe göre kayıt dondurulan süre boyunca öğrencilik hakları da dondurulur. Bu dönemde burs, öğrenci evlerinde barınma ve öğrencilere sağlanan diğer imkânlardan yararlanılamaz.

**Beklenen noktalar:**

- Kayıt dondurulan süreyle sınırlı hak dondurması.
- Hem burs hem öğrenci evinde barınma kapsamda.

**Yanlış sayılacak iddialar:**

- Burs veya yurt hakkının dondurma döneminde otomatik devam ettiği.
- Hakların kalıcı olarak iptal edildiği.

**Dayanaklar:**

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 14, basılı sayfa 166, Madde 46(6)

> Öğrencinin kaydı dondurulduğu süre zarfında öğrencilik hakları da dondurulur (burs, öğrenci evlerinde barınma hakkı ve öğrencilere sağlanan diğer imkânlardan yararlanamaz).

İnceleme notu: Öğrenci evi/yurt/barınma yakın anlamlı sorguları aynı kural ailesinde tutulmalı. Güncel burs yönetmeliğiyle çapraz kontrol bekliyor.

Onaylanacak içerik SHA-256: `fcede130939c6174588c1758bd4923c9a861b35d759f2b6028f6b1b404eb950d`

## BAKAY-020: Lisansta YANO ile GANO'nun farkı nedir; G ve K notları ortalamaya girer mi?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Önlisans/lisans; Tıp hariç

Soru varyantı: Dönem ortalaması ve genel ortalama nasıl ayrılıyor, kredisiz dersler etkiler mi?

**Taslak cevap:** YANO yalnız ilgili yarıyılın, GANO ise en az iki yarıyılda alınan bütün derslerin AKTS ağırlıklı ortalamasıdır. G ve K notları ortalamaya katılmaz; F1, F2, FF ve FD katılır.

**Beklenen noktalar:**

- Yarıyıl ile genel kapsam ayrımı ve AKTS ağırlığı.
- G/K hariç, F1/F2/FF/FD dahil.

**Yanlış sayılacak iddialar:**

- Bütün dersleri AKTS ağırlığı olmadan eşit ortalamak.
- G/K notlarını sıfır saymak.

**Dayanaklar:**

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 12, basılı sayfa 164, Madde 41(1)

> Herhangi bir yarıyılın ağırlıklı not ortalaması (YANO); o yarıyılda kayıt yaptırılan her bir derste alınan başarı notunun dersin AKTS’siyle çarpımından oluşan toplam değerin, alınan derslerin AKTS toplamına bölünmesi ile hesaplanır.

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 12, basılı sayfa 164, Madde 41(1), GANO

> Genel ağırlıklı not ortalaması (GANO) ise öğrencinin en az iki (2) yarıyılda kayıt yaptırdığı her bir dersten aldığı başarı puanının dersin AKTS’siyle çarpımından oluşan toplam değerin, alınan bütün derslerin AKTS toplamına bölünmesi ile hesaplanır.

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 12, basılı sayfa 164, Madde 41(2)

> F1, F2, FF ve FD notları, not ortalaması hesaplamalarına katılır; G ve K notları not ortalaması hesaplamalarına katılmaz.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `6b0c5ad575e62b5d85305ee5864dd573c56c4ce1e1b6b298f55c37344fd2bc2b`

## BAKAY-021: Yüksek lisans ve doktora başvurularında asgari mezuniyet ortalaması kaç?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Yüksek lisans/doktora adayları

Soru varyantı: Lisansüstü başvurusu için diploma notu barajları neler?

**Taslak cevap:** Yüksek lisans için en az 2,00/4,00, doktora için en az 2,50/4,00 gerekir. İlgili akademik kurul kararı ve Enstitü Yönetim Kurulu onayıyla daha yüksek eşik belirlenebilir; dörtlük olmayan notlar Senatonun kabul ettiği tabloyla çevrilir.

**Beklenen noktalar:**

- Yüksek lisans 2,00; doktora 2,50.
- Daha yüksek program eşiği konulabilir.
- Dörtlük dışı not için Senato tablosu.

**Yanlış sayılacak iddialar:**

- Bu eşikleri sağlayanın kesin kabul edileceği.
- Yüzlük notu basitçe 25'e bölmek.

**Dayanaklar:**

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 4, basılı sayfa 206, Madde 10(5)

> Yüksek lisans programına başvuranlarda mezuniyet not ortalamasının en az 2.00/4.00, doktora programına başvuranlarda en az 2.50/4.00 olması gerekir. Dörtlük sistemde olmayan notlar Senato tarafından kabul edilen Not Çevirim Tablosuna göre dörtlük sisteme dönüştürülür ve değerlendirmeye alınır. EABD/EASD akademik kurulunun kararı ve Enstitü Yönetim Kurulunun onayı ile daha yüksek bir not belirlenebilir.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `dd2f3780711d01ff32c25a6ee6f88bd4747af239e4b232eab0caa135d9711ff0`

## BAKAY-022: Yüksek lisans başvurusunda yabancı dil belgesi her programda zorunlu mu?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Yüksek lisans adayları; öğretim dili muafiyeti ayrı konu

Soru varyantı: Dil puanı olmadan yüksek lisansa başvuru yapabilir miyim?

**Taslak cevap:** Genel kuralda yüksek lisans başvurusunda yabancı dil şartı aranmaz. Ancak ilgili akademik kurul kararı ve Enstitü Yönetim Kurulu onayıyla dil belgesi istenebilir; başvuracağınız programın ilanını kontrol etmek gerekir.

**Beklenen noktalar:**

- Genel kural dil şartı yok.
- Yetkili kurul kararıyla belge istenebilir.

**Yanlış sayılacak iddialar:**

- Hiçbir yüksek lisans programında dil belgesi istenemez demek.
- Doktora dil barajını yüksek lisansa zorunlu tutmak.

**Dayanaklar:**

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 4, basılı sayfa 206, Madde 10(6)

> Yüksek lisans programlarına başvurularda yabancı dil şartı aranmaz. Ancak EABD/EASD akademik kurulunun kararı ve Enstitü Yönetim Kurulunun onayı ile yabancı dil belgesi istenebilir.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `be98c2f7684c0bfad2671d38944391836c456a7b705de025c9887000dbf52c05`

## BAKAY-023: Doktora başvurusu için üniversitenin dil sınavından veya T.C. ÖSYM sınavından kaç puan gerekir?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Doktora adayları

Soru varyantı: Doktora yabancı dil barajı her iki sınavda da 55 mi?

**Taslak cevap:** Üniversitenin ÖSYM birimince yapılan dil sınavında en az 60, T.C. ÖSYM sınavında en az 55 veya kabul edilen eşdeğer puan gerekir. Program için daha yüksek puan belirlenebilir; kabul edilen belgeler ve eşdeğerlikler ilgili kararlarla belirlenir.

**Beklenen noktalar:**

- Üniversite sınavı 60, T.C. ÖSYM 55 veya eşdeğer.
- Daha yüksek program eşiği ve belge kabulü kararları.

**Yanlış sayılacak iddialar:**

- Her iki sınav için 55 demek.
- Başvuru dil barajını öğretim dili muafiyet sınavıyla karıştırmak.

**Dayanaklar:**

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 4, basılı sayfa 206, Madde 10(7)

> Doktora programında hangi yabancı dil belgesinin kabul edileceği EABD/EASD akademik kurulunun önerisi ve Enstitü Yönetim Kurulunun kararı ile belirlenir. Yabancı dil puanı Üniversite ÖSYM tarafından yapılan yabancı dil sınavından en az 60, T.C. ÖSYM tarafından yapılan yabancı dil sınavından en az 55 puan veya Senato tarafından kabul edilen yabancı dillerden T.C. ÖSYM tarafından yapılan yabancı dil sınavına eşdeğer puan gerekir. EABD/EASD akademik kurulunun kararı ve Enstitü Yönetim Kurulunun onayı ile daha yüksek bir yabancı dil puanı belirlenebilir.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `64f18573b1c3191c05869de0a994382548a5308e817e19f91d71b2a3b70d262a`

## BAKAY-024: Aynı alım döneminde birden fazla lisansüstü programa başvurabilir miyim?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Lisansüstü alım başvuruları

Soru varyantı: İki yüksek lisans programına birlikte başvuru yapabilir miyim?

**Taslak cevap:** Bu yönetmeliğe göre aday birden fazla programa başvuramaz.

**Beklenen noktalar:**

- Birden fazla programa başvuru yapılamaz.

**Yanlış sayılacak iddialar:**

- Adayın istediği kadar lisansüstü programa başvurabileceği.

**Dayanaklar:**

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 5, basılı sayfa 207, Madde 10(8)

> Aday birden fazla programa başvuramaz.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `c672fd496b88eb4d7cbf608f354572c0906b3fc892151e1aa75761177dc0830a`

## BAKAY-025: Lisansüstü başvurusunda ALES 55 puanım varsa yazılı ve sözlü sınavlardan muaf olur muyum?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Bilim sınavına tabi lisansüstü adayları

Soru varyantı: ALES 55 ile Manas lisansüstü bilim sınavının tamamını atlayabilir miyim?

**Taslak cevap:** En az 55 ALES veya eşdeğer GRE/GMAT puanını başvuruda beyan eden aday yazılı sınava girmeyebilir. Ancak sözlü sınava girmek zorundadır; bu belge iki sınavdan birden muafiyet sağlamaz.

**Beklenen noktalar:**

- En az 55 ALES veya eşdeğer GRE/GMAT.
- Başvuruda beyanla yazılı muafiyeti; sözlü zorunlu.

**Yanlış sayılacak iddialar:**

- Sözlü sınavdan da muafiyet.
- Personel alımındaki 60 ALES kuralını kullanmak.

**Dayanaklar:**

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 5, basılı sayfa 207, Madde 12(5)

> ALES notu en az 55 veya buna eşdeğer uluslararası geçerliliği olan GRE veya GMAT puanlara sahip olan aday başvuruda beyan etmek şartıyla yazılı sınava girmeyebilir. Ancak sözlü sınava girmek zorundadır.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `9a6f2372fc35d8d96fbb57cd1571dcddb06591b8d6471a9c9fd13f8c891ce952`

## BAKAY-026: Lisansüstü başvuruda kullanılan ALES, GRE ve GMAT belgeleri kaç yıl geçerli?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Arşiv yönetmelik sürümündeki lisansüstü kabul kuralı

Soru varyantı: Manas lisansüstü kabulünde ALES ile GRE/GMAT geçerlilik süreleri aynı mı?

**Taslak cevap:** Bu yönetmelikte ALES belgesinin geçerliliği 3 yıl, GRE ve GMAT belgelerinin geçerliliği 5 yıl olarak belirtilmiştir. Bu, incelenen kaynak sürümünün kuralıdır; başvuru öncesi güncel ilanla teyit edilmelidir.

**Beklenen noktalar:**

- ALES 3 yıl, GRE/GMAT 5 yıl.
- Yanıtı kaynak sürümüyle sınırlamak.

**Yanlış sayılacak iddialar:**

- Bütün belgelerin 5 yıl veya süresiz geçerli olduğunu söylemek.

**Dayanaklar:**

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 5, basılı sayfa 207, Madde 12(5)

> ALES belgesi geçerlilik süresi 3 yıl, GRE ve GMAT belgelerinin geçerlilik süresi 5 yıldır.

İnceleme notu: Yüksek güncellik riski: dış sınav kurumunun güncel süreleriyle veya yeni ilanla farklılık olabilir. Güncel kural etiketi verilmemeli.

Onaylanacak içerik SHA-256: `9eac9e8d595b305a39e78a663c615ed1f447638b2c5d62a65922f338501062e2`

## BAKAY-027: Lisansüstü bilim sınavında yazılıdan 65, sözlüden 90 alırsam ortalamayla başarılı sayılır mıyım?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Yazılı ve sözlü bilim sınavına giren lisansüstü aday

Soru varyantı: Yüksek lisans yazılı sınavım 65, mülakatım 90; yüksek ortalama yeter mi?

**Taslak cevap:** Hayır. Yazılı veya sözlü sınavlardan birinin 70/100'ün altında olması başarısız sayılmaya ve kayıt hakkı kazanamamaya neden olur. Yüksek sözlü notu 65 olan yazılı notunu telafi etmez.

**Beklenen noktalar:**

- Her iki sınav için ayrı 70/100 alt eşiği.
- Verilen durumda aday başarısızdır.

**Yanlış sayılacak iddialar:**

- 77,5 ortalamanın tek başına kabul için yeterli olduğu.

**Dayanaklar:**

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 5, basılı sayfa 207, Madde 12(6)

> Bilim sınavına girmeyen aday veya bilim sınavının yazılı veya sözlü sınavlarından birinden notu 70/100 puanın altında olan aday başarısız sayılır ve kayıt hakkı kazanmaz.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `8dbdbb2be822797d84ce8fd4a9522782935a838d57ac1521af301fbaa6689a97`

## BAKAY-028: Yüksek lisans kabulünde mezuniyet notu ile bilim sınavının ağırlıkları nedir?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Yazılı/sözlü bilim sınavına giren yüksek lisans adayı

Soru varyantı: Yüksek lisans başvuru başarı puanı nasıl hesaplanıyor?

**Taslak cevap:** Başarı değerlendirmesinde mezuniyet notunun %50'si ile bilim sınavı notunun %50'si alınır. Bilim sınavı notu da yazılının %50'si ve sözlünün %50'sinden oluşur; ayrı sınav başarı koşulları ayrıca sağlanmalıdır.

**Beklenen noktalar:**

- Mezuniyet %50 + bilim %50.
- Bilim sınavı içinde yazılı %50 + sözlü %50.

**Yanlış sayılacak iddialar:**

- Doktoradaki %35/%15/%50 formülünü yüksek lisansa uygulamak.

**Dayanaklar:**

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 5, basılı sayfa 207, Madde 12(4)(c)

> Bilim sınavı notu, yazılı sınavı notunun %50’si ve sözlü sınavının %50’si alınarak hesaplanır.

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 5, basılı sayfa 207, Madde 12(7)

> Başarı puanları değerlendirmesinde yüksek lisans için mezuniyet notunun %50’si ve bilim sınav notunun %50’si

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 5, basılı sayfa 207, Madde 12(6)

> bilim sınavının yazılı veya sözlü sınavlarından birinden notu 70/100 puanın altında olan aday başarısız sayılır

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `79208ac9b9300513498d33e5bc9bbdc5617d22ee13fbe47b0ab5f67194239b7f`

## BAKAY-029: Doktora kabul başarı puanında mezuniyet, yabancı dil ve bilim sınavı yüzde kaç etkili?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Doktora adayları

Soru varyantı: Doktora başvurusunun sıralama puanı hangi ağırlıklarla hesaplanıyor?

**Taslak cevap:** Doktora için mezuniyet notunun %35'i, yabancı dil puanının %15'i ve bilim sınavı notunun %50'si dikkate alınır. Başarı puanları eşitse sırasıyla bilim sınavı, mezuniyet notu ve yabancı dil puanına bakılır.

**Beklenen noktalar:**

- Mezuniyet %35, dil %15, bilim sınavı %50.
- Eşitlikte bilim, mezuniyet, dil sırası.

**Yanlış sayılacak iddialar:**

- Yabancı dili hesaba katmamak.
- Ağırlıkları yanlış alanlara atamak.

**Dayanaklar:**

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 5, basılı sayfa 207, Madde 12(7)

> doktora için mezuniyet notunun %35’i, yabancı dil puanının %15’i ve bilim sınav notunun %50’si dikkate alınır. Adayların başarı puanlarının eşitliği durumunda sırasıyla, bilim sınavı puanı, mezuniyet notu ve yabancı dil puanına göre sıralama yapılır.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `6487431c5e26117c72aaee885000ac46813c12571d3e56fbfc3d047367af71f2`

## BAKAY-030: Lisansüstünde üniversitenin Türkçe veya Kırgızca öğretim dili muafiyet sınavından kaç puan almalıyım?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Lisansüstü; öğretim dili Türkçe/Kırgızca olan programlar

Soru varyantı: Yüksek lisans dil muafiyetinde Türkçe ve Kırgızca için üniversite sınav barajı kaç?

**Taslak cevap:** Üniversitenin Kırgız Türkçesi ve/veya Türkiye Türkçesi muafiyet sınavından en az 67 puan alan öğrenciler ilgili öğretim dilinden muaf tutulur. Sınav tarihleri öğrenci alım ilanında belirtilir.

**Beklenen noktalar:**

- En az 67 puan.
- Öğretim dili muafiyetine ilişkin olduğunu korumak.

**Yanlış sayılacak iddialar:**

- Doktora başvuru yabancı dil eşiği olan 55/60 ile karıştırmak.

**Dayanaklar:**

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 8, basılı sayfa 210, Madde 19(7)

> Kırgız Türkçesi ve/veya Türkiye Türkçesi için Üniversitenin yapacağı muafiyet sınavından en az 67 puan alan öğrenciler bu öğretim dillerinden muaf tutulur. Üniversite tarafından yapılan muafiyet sınavlarının tarihleri öğrenci alım ilanında belirtilir.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `f0f37bc802c21f7cc6211ab783a5f6b7b17f2b5452fb92c1d1608758a3875161`

## BAKAY-031: Lisansüstü bilimsel hazırlık programı en çok kaç yarıyıl sürer ve bir yarıyılda kaç ders olur?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Bilimsel hazırlık gerektiren lisansüstü öğrencileri

Soru varyantı: Alanım farklıysa bilimsel hazırlığın süre ve dönemlik ders sınırı nedir?

**Taslak cevap:** Eksikleri gidermek amacıyla en çok 2 yarıyıl bilimsel hazırlık açılabilir. Bir yarıyılda en az 2, en fazla 4 dersten oluşur. Bu, dil hazırlığından ayrı bir programdır.

**Beklenen noktalar:**

- En çok 2 yarıyıl; yarıyıl başına 2-4 ders.
- Dil hazırlığıyla karıştırmamak.

**Yanlış sayılacak iddialar:**

- Bilimsel hazırlığın herkese zorunlu olduğu.
- En fazla dört yarıyıl demek.

**Dayanaklar:**

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 8, basılı sayfa 210, Madde 20(1)

> eksikliklerini gidermek amacıyla en çok 2 yarıyıl bilimsel hazırlık programı açılabilir.

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 9, basılı sayfa 211, Madde 20(2)

> Bilimsel hazırlık programı 1 yarıyılda en az 2 en fazla 4 dersten oluşur.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `46b99221de2921e4ef6890b76b9756e059fa79cb8a5eed80a949ccd26aa9a139`

## BAKAY-032: Bilimsel hazırlık dersleri lisansüstü kredi yükümden sayılır ve ortalamama katılır mı?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Lisansüstü bilimsel hazırlık

Soru varyantı: Yüksek lisans bilimsel hazırlığında geçtiğim dersler mezuniyet kredisine dahil mi?

**Taslak cevap:** Hayır. Bilimsel hazırlık dersleri lisansüstü programın gerekli dersleri yerine geçmez ve kredi yükünden sayılmaz. Mezuniyet not durum belgesinde gösterilir, ancak akademik ortalamaya katılmaz; bilimsel hazırlıkta geçen süre de kayıtlı program süresinden sayılmaz.

**Beklenen noktalar:**

- Ders/kredi yükü yerine geçmez.
- Transkriptte görünür, ortalamaya katılmaz.
- Süre program süresinden sayılmaz.

**Yanlış sayılacak iddialar:**

- Bu derslerin transkriptte hiç gösterilmediği.
- Program kredi yükünü azalttığı.

**Dayanaklar:**

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 9, basılı sayfa 211, Madde 20(5)

> Bilimsel hazırlık programında alınan dersler ilgili lisansüstü programını tamamlamak için gerekli görülen derslerin yerine geçemez, kredi yükünden sayılmaz, mezuniyet not durum belgesinde gösterilir ancak akademik not ortalamasına katılmaz.

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 9, basılı sayfa 211, Madde 20(8)

> Bilimsel hazırlık programından geçirilecek süre öğrencinin kayıtlı olduğu programın süresinden sayılmaz.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `f5abe3ff0f186494e6ec570b41937f06c39eaff80e3c59b7c3a07360490b4e74`

## BAKAY-033: Lisansüstüne kesin kayıttan sonra danışman ne zaman atanır; o zamana kadar kim ilgilenir?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Lisansüstü öğrencileri

Soru varyantı: Yüksek lisans danışman atama süresi ve geçici sorumlu kim?

**Taslak cevap:** Danışman, yarıyıl ders kayıtlarının başlangıcından itibaren 1 ay içinde ilgili akademik kurulun önerisi ve Enstitü Yönetim Kurulu kararıyla atanır. Atanana kadar bu görevi EABD/EASD başkanı yürütür.

**Beklenen noktalar:**

- Başlangıç noktası ders kayıtlarının başlangıcı; süre 1 ay.
- Kurul önerisi/kararı ve geçici olarak EABD/EASD başkanı.

**Yanlış sayılacak iddialar:**

- Süreyi öğrencinin başvuru gününden başlatmak.

**Dayanaklar:**

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 9, basılı sayfa 211, Madde 21(1)

> Lisansüstü programına kesin kayıt yaptıran her bir öğrenciye öğrenim süresince rehberlik etmek üzere yarıyıl ders kayıtlarının başlangıç tarihinden itibaren 1 ay içinde EABD/EASD akademik kurulun önerisi ve Enstitü Yönetim Kurulunun kararı ile danışman atanır. Danışman atanıncaya kadar bu görevi EABD/EASD başkanı yürütür.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `57faff1b07eed83d005f20bfec241c9965fb1fcc8b4e1983aafefc02ec9c00f1`

## BAKAY-034: Yüksek lisansta devamını aldığım ancak başarısız olduğum derse tekrar devam etmem gerekir mi?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Lisansüstü öğrencileri

Soru varyantı: Lisansüstünde nottan kaldığım derste tekrar yoklama zorunlu mu?

**Taslak cevap:** Evet. Lisansüstü yönetmeliğinde devamsızlık veya başarısızlık nedeniyle tekrar alınan derslerde devam şartı aranır. Teorik derslerde en az %70, uygulamalarda %80 devam gerekir.

**Beklenen noktalar:**

- Başarısızlık nedeniyle tekrarda da devam gerekir.
- Teorik %70, uygulama %80.

**Yanlış sayılacak iddialar:**

- Lisanstaki devamdan muaf tekrar kuralını yüksek lisansa uygulamak.

**Dayanaklar:**

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 12, basılı sayfa 214, Madde 30(1)

> Öğrenci kayıt yaptırdığı teorik dersin en az yüzde 70’ine, uygulamalı ders ve uygulamaların ise yüzde 80’ine devam etmek zorundadır.

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 12, basılı sayfa 214, Madde 30(3)

> Devamsızlık veya başarısızlık sebebiyle tekrar alınan dersler için devam şartı aranır.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `88400ac87c2dd0e353d18004f4eb705a9d3ae1f45cb379b4cb0e82c352ce674a`

## BAKAY-035: Yüksek lisans ve doktorada final alt sınırı ve dersten geçme harf notu nedir?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Lisansüstü ders başarı koşulları

Soru varyantı: Lisansüstünde finalden kaç almak ve hangi harf notuna ulaşmak gerekiyor?

**Taslak cevap:** Yarıyıl sonu sınavından en az 50 puan almak gerekir; bu tek başına dersi geçirmez. Ders başarı notu yüksek lisansta en az CC, doktora/sanatta yeterlikte en az CB olmalıdır.

**Beklenen noktalar:**

- Final en az 50.
- Yüksek lisans CC, doktora/sanatta yeterlik CB.

**Yanlış sayılacak iddialar:**

- Lisansın 40 final/DD notunu kullanmak.
- Yüksek lisans ders saydırma eşiği olan CB'yi ders geçmeye uygulamak.

**Dayanaklar:**

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 13, basılı sayfa 215, Madde 32(3)

> Yarıyıl sonu sınavına girmeyen veya yaryıl sonu sınavında en az elli puan alamayan öğrenci başarısız sayılır.

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 13, basılı sayfa 215, Madde 32(5)

> Bir dersten başarılı sayılmak için o dersin başarı notunun yüksek lisans programında en az CC, doktora/Sanatta yeterlik programında CB olması gerekir.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `c6a61ec73465156c6467630f0cd6294939340d1af2e6710d4fed063e8f851966`

## BAKAY-036: Lisansüstü mazeret sınavı başvurusu için süre kaç gün ve ne zaman başlar?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Lisansüstü öğrencileri

Soru varyantı: Yüksek lisans sınavını mazeretle kaçırdım; başvuru süresi rapor bitiminden mi sayılır?

**Taslak cevap:** Bu yönetmelikte süre sınavların sona ermesinden itibaren en geç 3 iş günüdür. Geçerli sağlık raporu bulunan veya mazereti Enstitü Yönetim Kurulunca kabul edilen öğrenci için ara sınav/final yerine mazeret sınavı yapılabilir.

**Beklenen noktalar:**

- Sınavların sona ermesinden itibaren 3 iş günü.
- Geçerli sağlık raporu veya kurulca kabul edilmiş mazeret.

**Yanlış sayılacak iddialar:**

- 3 takvim günü demek.
- Süreyi rapor bitiminden başlatmak veya lisansın bir hafta kuralını kullanmak.

**Dayanaklar:**

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 13, basılı sayfa 215, Madde 31(5)

> Sınavların sona ermesinden itibaren en geç 3 iş günü içinde başvurmak kaydıyla; geçerli sağlık raporu olan ya da mazereti Enstitü Yönetim Kurulu kararı ile kabul edilen öğrenciye, ara sınav ve yarıyıl sonu sınavları yerine geçecek olan mazeret sınavları yapılır.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `a7767797e69a8f5d00d8f49a232fc8ae6f02493c5b3759271a9b624182040d2f`

## BAKAY-037: Lisansüstü ders sınavı notuna itiraz süresi nedir; ilk karara yeniden itiraz edebilir miyim?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Lisansüstü ders sınavı; tez savunması ayrı

Soru varyantı: Yüksek lisans sınav itirazında ilk başvuru ve ikinci itiraz nereye, kaç gün içinde yapılır?

**Taslak cevap:** Sınav sonucu açıklandıktan itibaren 7 gün içinde Enstitüye yazılı itiraz yapılabilir. Enstitü Yönetim Kurulu kararının ilanından sonra 7 gün içinde Üniversite Yönetim Kuruluna yazılı başvuruyla itiraz yinelenebilir.

**Beklenen noktalar:**

- İlk başvuru sonuç açıklanmasından itibaren 7 gün, Enstitüye yazılı.
- Yeniden başvuru kurul kararının ilanından sonra 7 gün, Üniversite Yönetim Kuruluna.

**Yanlış sayılacak iddialar:**

- İlk başvuru süresini 7 iş günü diye değiştirmek.
- Lisans kuralına dayanarak yeniden itiraz yok demek.

**Dayanaklar:**

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 15, basılı sayfa 217, Madde 34

> Öğrenci dersin sınav sonuçları açıklandıktan itibaren 7 gün içinde Enstitüye yazılı olarak itiraz edebilir.

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 15, basılı sayfa 217, Madde 34, son

> Öğrencinin sonuca itirazını yinelemesi, Enstitü Yönetim Kurulu kararının ilanı tarihinden sonra 7 gün içinde Üniversite Yönetim Kuruluna yazılı olarak başvurması ile gerçekleşir.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `45360318a5482e837ed3e88bacbd506a245cd255bbcba0d79e578c057082ceeb`

## BAKAY-038: Lisansüstü tez savunmasında başarısız oldum; itirazı ne kadar sürede nereye yapabilirim?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Lisansüstü tez savunması

Soru varyantı: Tez savunması sonucuna itiraz için yüksek lisansta 7 gün mü var?

**Taslak cevap:** Tez savunmasında başarısız olan öğrenci sınav tarihinden itibaren 2 ay içinde Enstitüye yazılı itiraz edebilir. Bu süre ders sınavı notuna itirazın 7 günlük süresiyle karıştırılmamalıdır.

**Beklenen noktalar:**

- Sınav tarihinden itibaren 2 ay.
- Enstitüye yazılı başvuru; başarısız tez savunması kapsamı.

**Yanlış sayılacak iddialar:**

- Ders sınavı itirazındaki 7 günü kullanmak.
- İki ayı kaynak olmadan 60 gün olarak sabitlemek.

**Dayanaklar:**

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 15, basılı sayfa 217, Madde 36(1)

> Tez savunma sınavında başarısız olan öğrenci, sınav tarihinden itibaren 2 ay içinde Enstitüye yazılı olarak itiraz edebilir.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `72769d5d4ae158e9f95a1592521a507254e0e36d663ead7f046a1c8611924f4b`

## BAKAY-039: Manas Üniversitesi hangi şehirde ve devlet üniversitesi mi?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Genel kurumsal bilgi

Soru varyantı: KTMÜ nerede bulunuyor, özel üniversite mi?

**Taslak cevap:** Üniversite Kırgızistan'ın başkenti Bişkek'tedir. Öğrenci İşleri SSS sayfasında Kırgızistan ve Türkiye'de özel statülü devlet üniversitesi olarak tanımlanır.

**Beklenen noktalar:**

- Bişkek, Kırgızistan.
- Özel statülü devlet üniversitesi.

**Yanlış sayılacak iddialar:**

- Özel statülü ifadesini özel/vakıf üniversitesi diye yorumlamak.

**Dayanaklar:**

- [KTMÜ Öğrenci İşleri: Genel Bilgiler SSS](https://oidb.manas.edu.kg/tr/faq/1), HTML SSS, SSS 2-3

> Üniversite, Kırgızistan'ın başkenti Bişkek'tedir.

- [KTMÜ Öğrenci İşleri: Genel Bilgiler SSS](https://oidb.manas.edu.kg/tr/faq/1), HTML SSS, SSS 3

> Üniversite, Kırgızistan'da ve Türkiye'de Özel Statülü Devlet Üniversitesi statüsündedir.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `5c33c14b258c90b7a438f8d273f0fffeb8ab01d570cf91adfb36a31fcad61f04`

## BAKAY-040: Manas'ta bütün bölümler ücretsiz mi; Tıp için de aynı şey geçerli mi?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: SSS kaynak sürümündeki öğrenim ücreti açıklaması

Soru varyantı: KTMÜ öğrenim ücretinde Tıp Fakültesi istisna mı?

**Taslak cevap:** Öğrenci İşleri Genel Bilgiler SSS'si eğitim-öğretimin Tıp Fakültesi hariç tamamen ücretsiz olduğunu belirtiyor. Bu bilgiye dayanarak Tıbbın ücretsiz olduğu söylenemez; sayfa Tıp için ücret tutarı vermiyor.

**Beklenen noktalar:**

- Ücretsiz eğitim bilgisindeki Tıp istisnası.
- Tıp için tutar uydurmamak.

**Yanlış sayılacak iddialar:**

- Tüm bölümler istisnasız ücretsizdir demek.
- Yurt, ulaşım ve yaşam giderlerini de ücretsiz ilan etmek.

**Dayanaklar:**

- [KTMÜ Öğrenci İşleri: Genel Bilgiler SSS](https://oidb.manas.edu.kg/tr/faq/1), HTML SSS, SSS 9

> Üniversitede eğitim-öğretim (Tıp Fakültesi hariç) tamamen ücretsizdir.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `00835dce2ec2724f7aae44eab109df8f34d2f2e3c1c2987c07e65a53dac17f90`

## BAKAY-041: Türkiye'den gelen öğrenci hazırlıkta Kırgızca mı öğreniyor; muaf olursa birinci sınıfa geçebilir mi?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: SSS hazırlık bilgisi; Türkiye'den kabul edilen aday

Soru varyantı: Türkiyeli aday için Kırgızca hazırlığı ve doğrudan bölüme başlama koşulu nedir?

**Taslak cevap:** SSS'ye göre Türkiye'den gelen öğrenci Kırgızca dil hazırlığı okur. Sorumlu olduğu dil hazırlık programının muafiyet sınavında başarılı olan öğrenci doğrudan birinci sınıfa başlayabilir. Bazı programlarda İngilizce veya Rusça hazırlık yükümlülüğü de bulunduğundan bütün sorumlu diller dikkate alınmalıdır.

**Beklenen noktalar:**

- Kırgızca hazırlığı.
- Sorumlu olunan dil muafiyet sınavlarında başarıyla doğrudan birinci sınıf.
- Programın ek İngilizce/Rusça şartlarını göz ardı etmemek.

**Yanlış sayılacak iddialar:**

- Her Türkiye vatandaşı sınavsız hazırlıktan muaftır demek.

**Dayanaklar:**

- [KTMÜ Öğrenci İşleri: Hazırlık Dil Eğitimi SSS](https://oidb.manas.edu.kg/tr/faq/7), HTML SSS, SSS 4

> Türkiye’den gelen öğrenciler hazırlık sınıfında zorunlu olarak Kırgızca Dil Hazırlık Programı okuyacaklardır. Sorumlu olduğu dil hazırlık programının muafiyet sınavında başarılı olan öğrenciler doğrudan birinci sınıfa başlayabilirler.

- [KTMÜ Öğrenci İşleri: Hazırlık Dil Eğitimi SSS](https://oidb.manas.edu.kg/tr/faq/7), HTML SSS, SSS 9

> Ancak Rusça ve İngilizce ön şartı olan programlara kayıtlı olan Öğrencilerin Hazırlık sınıfından muaf olabilmeleri için o dilin muafiyet sınavında da başarılı olmaları gerekmektedir.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `9bd865116391fec3e4f3f24cedc88483c03493cf970fbeeca83091f36cd67cfd`

## BAKAY-042: Hazırlık dil sınıfında devam zorunluluğu lisans derslerindeki gibi yüzde 70 mi?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Dil hazırlık sınıfı; SSS kaynak sürümü

Soru varyantı: Hazırlık sınıfında derslere yüzde kaç devam etmek gerekiyor?

**Taslak cevap:** Hayır. Hazırlık Dil Eğitimi SSS sayfasında hazırlık derslerine en az %85 devam zorunluluğu belirtiliyor. Bu oran lisans teorik derslerinin %70 oranıyla karıştırılmamalıdır.

**Beklenen noktalar:**

- Hazırlık SSS'sindeki %85 oranı.
- Hazırlık ve lisans derslerini ayırmak.

**Yanlış sayılacak iddialar:**

- Hazırlığa lisans teorik ders oranı olan %70'i uygulamak.

**Dayanaklar:**

- [KTMÜ Öğrenci İşleri: Hazırlık Dil Eğitimi SSS](https://oidb.manas.edu.kg/tr/faq/7), HTML SSS, SSS 7

> Hazırlık sınıfında Öğrenciler derslerin %85 ine devam etmek zorundadırlar.

İnceleme notu: SSS'de aynı yanıt yinelenmiş. Özellikle yaptırım kısmı güncel Dil Hazırlık Yönetmeliğiyle teyit edilmeli; bu soru yalnız devam oranını sınar.

Onaylanacak içerik SHA-256: `6661d5ecc72feb893a88179d902b46a7804d3ef13752dd528da627664ca62ad6`

## BAKAY-043: Hazırlık öğrencileri de burs alabiliyor mu?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Hazırlık öğrencileri; burs alabilme olanağı

Soru varyantı: Burs imkânı yalnız bölüme geçen öğrenciler için mi var?

**Taslak cevap:** Hazırlık Dil Eğitimi SSS'sine göre hazırlık öğrencileri de burs alabilir. Bu kısa yanıt herkesin otomatik burs alacağı, burs tutarı veya bütün burs türlerinin koşulları hakkında bir garanti vermiyor.

**Beklenen noktalar:**

- Hazırlık öğrencileri burs alabilir.
- Otomatik hak veya tutar iddiası yok.

**Yanlış sayılacak iddialar:**

- Her hazırlık öğrencisine koşulsuz aynı bursun ödendiği.
- Kaynakta olmayan aylık tutar vermek.

**Dayanaklar:**

- [KTMÜ Öğrenci İşleri: Hazırlık Dil Eğitimi SSS](https://oidb.manas.edu.kg/tr/faq/7), HTML SSS, SSS 13

> Hazırlık sınıfı öğrencileri burs alabiliyorlar mı? Evet, alabiliyorlar.

İnceleme notu: Burs üst kavramı bütün burs türlerinin koşullarına genişletilmemeli. Güncel burs yönergesiyle insan kontrolü gerekiyor.

Onaylanacak içerik SHA-256: `1bc38bf4a7772c8593281ff775a42113430f8a7e7049fa8731729941bac00859`

## BAKAY-044: Öğrenci kimlik kartımı ÖİDB'den mi alacağım?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Öğrenci kimliği teslimi; SSS kaynak sürümü

Soru varyantı: Öğrenci İşleri kimlik kartını teslim eden birim mi?

**Taslak cevap:** Evet. Hazırlık Dil Eğitimi SSS'si öğrenci kimlik kartının Öğrenci İşleri Dairesi Başkanlığından alınacağını belirtiyor.

**Beklenen noktalar:**

- ÖİDB kısaltmasını Öğrenci İşleri Dairesi Başkanlığına eşlemek.
- Kimlik kartı teslim birimini doğru belirtmek.

**Yanlış sayılacak iddialar:**

- Kaynakta olmayan oda, kişi veya çalışma saati uydurmak.

**Dayanaklar:**

- [KTMÜ Öğrenci İşleri: Hazırlık Dil Eğitimi SSS](https://oidb.manas.edu.kg/tr/faq/7), HTML SSS, SSS 15

> Öğrenci Kimlik Kartınızı Öğrenci İşleri Dairesi Başkanlığından alacaksınız.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `546f4c09e274e6e8d2ce42ca0a0b578db0632821fdb8967944a817c21f832395`

## BAKAY-045: Sınav sonucuna itiraz etmek için kaç günüm var?

Davranış: `clarify` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Öğrenim düzeyi ve sınav türü belirtilmemiş

Soru varyantı: Not itirazının son başvuru süresi nedir?

**Taslak cevap:** Önlisans/lisans mı, lisansüstü öğrencisi misiniz; itirazınız ders sınavına mı tez savunmasına mı? Süreler farklı: lisans ders sınavında 7 iş günü, lisansüstü ders sınavında 7 gün, başarısız lisansüstü tez savunmasında 2 ay olarak düzenleniyor.

**Beklenen noktalar:**

- Öğrenim düzeyi ve sınav türünü sormak.
- Tek bir süreyi tüm öğrencilere uygulamamak.

**Yanlış sayılacak iddialar:**

- Hiç açıklama istemeden herkese 7 gün demek.

**Dayanaklar:**

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 13, basılı sayfa 165, Madde 43

> Öğrenci dersin sınav sonuçları ilanından itibaren yedi (7) iş günü içinde Birim Amirliğine yazılı olarak maddi hata itirazında bulunabilir.

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 15, basılı sayfa 217, Madde 34

> Öğrenci dersin sınav sonuçları açıklandıktan itibaren 7 gün içinde Enstitüye yazılı olarak itiraz edebilir.

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 15, basılı sayfa 217, Madde 36(1)

> Tez savunma sınavında başarısız olan öğrenci, sınav tarihinden itibaren 2 ay içinde Enstitüye yazılı olarak itiraz edebilir.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `a2125853901512be52809901dc6cd372d47ffadf59751d7b6fa029b7a17a769e`

## BAKAY-046: Vize için ne yapmam gerekiyor?

Davranış: `clarify` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Vize sözcüğünün anlamı belirtilmemiş

Soru varyantı: Vize işlemini nasıl halledeceğim?

**Taslak cevap:** Vize derken dersin ara sınavını mı, yoksa Kırgızistan'a giriş/oturum vizesini mi kastediyorsunuz? İşlemler farklı olduğu için önce bunu netleştirelim.

**Beklenen noktalar:**

- Ara sınav ve giriş/oturum vizesi anlamlarını ayırıp açıklama istemek.

**Yanlış sayılacak iddialar:**

- Anlamı netleşmeden pasaport belgesi, vize tutarı veya sınav tarihi vermek.

**Dayanaklar:**

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 9, basılı sayfa 161, Madde 33(1), sınav bağlamı

> öğrencinin giremediği dersin ara sınav ve/veya yarıyıl sonu sınavı yerine yapılan sınavdır.

- [KTMÜ Öğrenci İşleri: Vize ve Oturum İşlemleri SSS](https://oidb.manas.edu.kg/tr/faq/4), HTML SSS, SSS 1, giriş vizesi bağlamı

> Türkiye'den Kırgızistan'a gelirken vize almak gerekiyor mu? Vize işlemleri nasıl yapılıyor?

İnceleme notu: Vize=ara sınav eşlemesi uzman tarafından dilsel olarak doğrulanmalı; mevzuat alıntısı yalnız ara sınav kavramını kanıtlar. Göç prosedürlerinin güncelliği bu sorunun hedefi değil.

Onaylanacak içerik SHA-256: `35ca426ab0aa4a312825ae8a39b8c8fa4676d0a51c4c27972f9341c759a70a04`

## BAKAY-047: Muafiyet için ne yapmalıyım?

Davranış: `clarify` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Muafiyet türü ve öğrenim düzeyi belirsiz

Soru varyantı: Muaf olmak istiyorum, hangi başvuruyu yapacağım?

**Taslak cevap:** Hazırlık dilinden muafiyeti mi, yoksa daha önce aldığınız dersleri saydırmayı mı kastediyorsunuz? Ayrıca öğrenim düzeyinizi belirtir misiniz? Bu işlemlerin belgeleri ve değerlendirme koşulları farklıdır.

**Beklenen noktalar:**

- Dil hazırlığı muafiyeti ile ders saydırmayı ayırmak.
- Öğrenim düzeyini sormak.

**Yanlış sayılacak iddialar:**

- Her muafiyet başvurusuna tek bir puan veya belge listesi vermek.

**Dayanaklar:**

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 7, basılı sayfa 159, Madde 25(2)

> Ders saydırma ve ders muafiyetleri işlemleri öğrencinin Bölüm Başkanlığına, ekinde not durum belgesi ve ders içerikleri bulunan yazılı başvurusu ile başlatılır.

- [KTMÜ Öğrenci İşleri: Hazırlık Dil Eğitimi SSS](https://oidb.manas.edu.kg/tr/faq/7), HTML SSS, SSS 4

> Sorumlu olduğu dil hazırlık programının muafiyet sınavında başarılı olan öğrenciler doğrudan birinci sınıfa başlayabilirler.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `5fe754c23a871162a2fcd42879f0747fbef9cc0d5a7dea051de9eaf6e5aadb7f`

## BAKAY-048: 2026-2027 yılında Manas Tıp Fakültesinin yıllık ücreti tam olarak kaç dolar?

Davranış: `abstain` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: 2026-2027 Tıp ücret tutarı; yalnız sağlanan kaynak paketi

Soru varyantı: Manas Tıp için 2026-2027 kesin yıllık öğrenim ücretini dolar olarak söyler misin?

**Taslak cevap:** Bu kaynak paketinden 2026-2027 Tıp Fakültesi ücretinin kesin tutarını doğrulayamıyorum. SSS yalnızca Tıp Fakültesini ücretsiz eğitim açıklamasının dışında tutuyor. Kesin tutar için o yıla ait resmî ücret ilanı veya Öğrenci İşleri teyidi gerekir.

**Beklenen noktalar:**

- Kaynak paketinde kesin tutar bulunmadığı için rakam vermemek.
- Tıp istisnasının ücret tutarı anlamına gelmediğini belirtmek.
- Yıla ait resmî kaynağa yönlendirmek.

**Yanlış sayılacak iddialar:**

- Tıp ücretsizdir demek.
- Tutar, para birimi veya taksit planı uydurmak.
- Bütün üniversite veritabanında böyle bir belge kesinlikle yok demek.

**Dayanaklar:**

- [KTMÜ Öğrenci İşleri: Genel Bilgiler SSS](https://oidb.manas.edu.kg/tr/faq/1), HTML SSS, SSS 9, yalnız istisna bilgisi

> Üniversitede eğitim-öğretim (Tıp Fakültesi hariç) tamamen ücretsizdir.

İnceleme notu: Bu abstain etiketi kapalı kaynak paketi içindir. Canlı RAG ilgili yılın ücret belgesini bulursa artık abstain beklenmez; önce dayanak yeterliliği yeniden etiketlenmeli.

Onaylanacak içerik SHA-256: `65f94bc2582b29b40d1a024d0086ebd064d1a651fdc8a3d12f13f7d2f1f3681f`

## BAKAY-049: Lisansta nottan kaldığım derste devam aranmazken yüksek lisansta tekrar devam gerekir mi?

Davranış: `answer` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Lisans (Tıp hariç) ile lisansüstü devam karşılaştırması

Soru varyantı: Devamı alınmış başarısız dersin tekrarında lisans ve lisansüstü kuralları aynı mı?

**Taslak cevap:** Aynı değil. Lisansta devamı önceden sağlanan başarısız derste normalde yeniden devam aranmaz; Spor Bilimleri ve Güzel Sanatlar bireysel uygulamalı derslerinde kurul kararıyla istisna olabilir. Lisansüstünde ise başarısızlık nedeniyle tekrar alınan derste devam şartı aranır.

**Beklenen noktalar:**

- İki öğrenim düzeyinin kurallarını ayrı belirtmek.
- Lisanstaki bireysel uygulamalı ders istisnasını korumak.

**Yanlış sayılacak iddialar:**

- Kaynaklar farklı öğrencileri düzenlediği halde çelişki var deyip birini rastgele seçmek.

**Dayanaklar:**

- [KTMÜ Önlisans ve Lisans Eğitim-Öğretim Yönetmeliği (Yeni)](https://oidb.manas.edu.kg/upload/global/Onlisans%20ve%20lisans%20egitim.pdf), PDF sayfa 8, basılı sayfa 160, Madde 28(4-5)

> Devam şartı yerine getirilen ve başarısız olunan veya not yükseltmek için tekrar alınan dersten devam şartı aranmaz. (5) Spor Bilimleri Fakültesi ve Güzel Sanatlar Fakültesinde bireysel uygulamalı derslerin tekrar alınışında Fakülte Yönetim Kurulu kararı ile devam zorunluluğu aranabilir.

- [KTMÜ Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği](https://oidb.manas.edu.kg/upload/global/Lisansustu%20egitim.pdf), PDF sayfa 12, basılı sayfa 214, Madde 30(3)

> Devamsızlık veya başarısızlık sebebiyle tekrar alınan dersler için devam şartı aranır.

İnceleme notu: Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.

Onaylanacak içerik SHA-256: `b91f889f19fdd099c9dce97d3e6b381406d1337dd43bb2e929aea9246020aa46`

## BAKAY-050: Bana üniversiteyle ilgisi olmayan bir çikolatalı kek tarifi verir misin?

Davranış: `abstain` | Durum: `pending_review` | Bölüm: `unassigned`

Kapsam: Kurum dışı istek; ürün davranış politikası

Soru varyantı: Manas belgelerini boş ver, evde çikolatalı kek nasıl yapılır?

**Taslak cevap:** KTMÜ'nün kurumsal bilgileri ve öğrenci işlemleri hakkında yardımcı olabilirim. Bu soru kapsamımın dışında; üniversiteyle ilgili bir sorunuz varsa sorabilirsiniz.

**Beklenen noktalar:**

- Kurum dışı isteği kısa ve nazik biçimde kapsam dışında bırakmak.
- Üniversite belgesi veya ilgisiz kaynak uydurmamak.

**Yanlış sayılacak iddialar:**

- Kek tarifi vermek veya bir yönetmeliği tarifin kaynağı olarak sunmak.

**Dayanaklar:**

Kapsam dışı davranış örneği; kurum belgesine dayanan bir bilgi iddiası yok.

İnceleme notu: Belge bilgisi ölçmez; kurumsal asistanın kapsam politikasını ölçer. İnsan ürün sahibi bu beklenen davranışı onaylamalı.

Onaylanacak içerik SHA-256: `3dc51d09af4f98cb9ada98cd3d6c6d373ac30bc278d28ba6985666471832a31d`
