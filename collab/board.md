# Görev Panosu

> Format: `| durum | görev | sahip | tarih | kilitli dosya/dizinler |`
> Durum: 🔄 devam, ✅ bitti, ⏸ beklemede. Protokol: `collab/PROTOCOL.md`

| Durum | Görev | Sahip | Tarih | Kilitli dosyalar |
|---|---|---|---|---|
| ✅ | IP başına sorgu sınırı canlıda 30/dakika; özel ortam korundu, panel metriği ve HTTPS health doğrulandı. Yerel 150/Linux 17 test geçti | codex | 2026-10-13 | — |
| ✅ | BAKAI operasyon koruması: 1 USD alarm/panel, canlı Cloudflare Turnstile, günlük şifreli yedek; 150 test, gerçek 39.659 parçalık indeks geri yükleme doğrulandı. SMTP ve Drive hesap bağlantısı kullanıcı tarafından sonraya bırakıldı | codex | 2026-10-13 | — |
| ✅ | BAKAI kötüye kullanım koruması canlı: IP 10/dk + 120/saat, global 30/dk + 1.000/24 sa, 2 eşzamanlı iş; kalıcı atomik kotalar, 128 KiB/yavaş gövde sınırı ve güvenilir proxy IP. Panel sayaçları ve bekleme mesajı hazır. Yerel/Linux 136 test ve üretim derlemesi; canlı 429/sahte IP/413/401, sıfır saldırı LLM çağrısı, normal 200 + 5 kaynak ve son üç sağlık yoklaması geçti | codex | 2026-10-13 | — |
| ✅ | BAKAI ürün adı ve /hakkinda canlı: Manas/Bakay kökeni, BAP KTMU-BAP-2026.FB.05 ve Yrd. Doç. Dr. Abdulkadir Şeker yürütücü/geliştirici bilgisi. Ana sayfa/sohbet/panel/API kimliği güncellendi; 119 test, üretim derlemesi, masaüstü/mobil menü/taşma, HTTPS sayfa/CSS/API ve özel uçlar 401 geçti. Son sağlık yoklaması başarılı | codex | 2026-10-12 | — |
| ✅ | Monitoring paneli canlı: ayrı adminbakai parolası, korumalı metrik/sorgu ayrıntıları ve dakikalık sağlık timer'ı. Linux 40 test, HTTPS giriş/çıkış/401 ve gerçek Haiku sayaçları geçti: 5.440 giriş + 1.357 çıkış, 0,0012225 USD, 5 kaynak. Son backend/frontend/HTTPS yoklaması sağlıklı; 7 eski sorgu maliyeti bilinmiyor | codex | 2026-10-12 | — |
| ✅ | Canlı KTMÜ LLM'i Haiku 5.5'e geçirildi (adaptive/medium, 4096 token); özel ortam root 600 ile yedeklendi, backend yeniden başlatıldı. HTTPS health/chat 200, 39.659 parça, 5 kaynak/PDF bağlantısı; telemetri Haiku modelini doğruladı. İlk sorgu 54,8 sn (erişim 44,4, üretim 10,1); yayın ayarları ve rehber güncellendi | codex | 2026-10-12 | — |
| ✅ | KTMÜ canlı yayın tamamlandı: /opt/bakay, systemd active/enabled, Apache configtest, HTTPS sayfa/API/CSS 200, 39.659 parça ve tarayıcıdan kaynaklı Sonnet yanıtı (5 kaynak, PDF 200). Apache yedeği korundu; kod Git main üzerinden güncellendi | codex | 2026-10-12 | — |
| ✅ | KTMÜ root SSH girişi başarılı; uid=0 doğrulandı, kök birimde 4 GB boş alan var. Yalnız salt okunur kontrol yapıldı; yayın adımı yöneticiye bırakıldı | codex | 2026-10-12 | — |
| ✅ | KTMÜ hazırlığı: 18 GB disk, kod/veri/LaBSE/CPU runtime ve çevrimdışı wheel'ler /home/adminbakai/bakay altında hazır. 39.659 parça/hash, canlı Sonnet kaynaklı yanıt, frontend/CSS 200 ve npm audit 0 geçti; geçici test süreçleri kapatıldı. Root hazırlık/yayın araçları ve Git main akışı hazır; yayına almayı yönetici yapacak, Apache değiştirilmedi | codex | 2026-10-12 | — |
| ✅ | KTMÜ mevzuat + doküman PDF'lerinin indirilip indekslenmesi (103 PDF → 23.666 parça) | claude | 2026-09-01 | — |
| ✅ | Site geneli haritalama + Türkçe doküman taraması (5.993 sayfa + 514 belge → koleksiyon 59.321 parça) | claude | 2026-09-01 | — |
| ✅ | Kurumsal bilgi merkezi arayüzünün tasarlanması ve uygulanması | codex | 2026-09-01 | — |
| ✅ | Frontend geliştirme önbelleğinin temizlenmesi ve sunucunun kurtarılması | codex | 2026-09-01 | — |
| ✅ | Arama alanı odaklanınca örnek soru animasyonunun durdurulması | codex | 2026-09-01 | — |
| ✅ | Yerel FastAPI servisinin başlatılması ve sohbet akışının doğrulanması | codex | 2026-09-01 | — |
| ✅ | Yanıtlarda Markdown gösterimi ve görüşme kaydırma davranışının düzeltilmesi | codex | 2026-09-01 | — |
| ✅ | Kaynak katlama sırasında görüşme paneli kaydırmasının düzeltilmesi | codex | 2026-09-01 | — |
| ✅ | Belge başlıklarının metadata, API, prompt ve arayüze taşınması | codex | 2026-09-01 | — |
| ✅ | Footer metninin BAP dosyasındaki BAKAY açılımıyla güncellenmesi | codex | 2026-09-01 | — |
| ✅ | Aday öğrenci rehberi menüsü ve etkileşimli soru alanı | codex | 2026-09-01 | — |
| ✅ | Aday öğrenci rehberi kapsamlı QA, üretim derlemesi ve hata düzeltmeleri | codex | 2026-09-01 | — |
| ✅ | Aday öğrenci veri desteği: kapsam testi, turksam temizliği (−19.6k parça), oidb taraması, uçtan uca doğrulama | claude | 2026-09-01 | — |
| ✅ | Turkish-Gemma 9B ve Qwen3.5 9B için sabit kaynaklı 30 soruluk karşılaştırma, ölçüm aracı ve sonuç raporu | codex | 2026-09-07 | — |
| ✅ | Qwen3.5 9B varsayılanı ve 50 soruluk kaynak bağlı uzman inceleme paketi, gold şeması, doğrulama/testler; yanıltıcı doğrulama etiketi | codex | 2026-09-07 | — |
| ✅ | İlk altı aylık BAP gelişme raporu: Ocak-Haziran kayıtlarıyla İP1 ve İP2 tamamlandı, İP3 devam; 5 sayfalık Word taslağı, mali/idari alanlar doldurulacak | codex | 2026-09-07 | — |
| ✅ | İlk altı aylık raporun Kırgızca formda hazırlanması ve TR/KG dosyalarının report-1 altında toplanması; kullanıcının proje no ve 12.02.2026-12.08.2026 dönemi iki dilde eşleştirildi, görsel kontrol tamam | codex | 2026-09-07 | — |

| ✅ | Sohbet hafızası: son 6 turdan kullanıcı sorularıyla bağlam çözümü, tarayıcı geçmişi ve yeni sohbet; 57 test + frontend derlemesi geçti, yerel API yenilendi, Qwen ve tarayıcı kontrolleri tamam | codex | 2026-10-01 | — |

| ✅ | Yerel backend ve arayüz başlatıldı; health ve sayfa/CSS 200, Qwen3.5 9B ile /chat yanıtı alındı (konum sorusunda doğru kaynak bulunamadı; kalite kusuru sürüyor) | codex | 2026-10-01 | — |

## Bekleyen işler (sahipsiz — ToDoTask.md'den)

| ✅ | Ders saydırma → “lisans için?” hafıza hatası düzeltildi; asistan metninden bağımsız konu koruma, 73 test ve canlı Madde 25 erişimi. Canlı yanıttaki 1/3 koşulunun ters ifadesi ayrı üretim kusuru olarak kaydedildi | codex | 2026-10-01 | — |

| ✅ | Üniversite RAG/KG araştırması: DomainRAG, WikiRAG-TR, KG-RAGdataset ve HCMUT; gerçek dosya, şema ve lisans sınırları raporlandı | codex | 2026-10-01 | — |

| ✅ | Ders saydırma: PDF ve indeks doğrulandı; hibrit erişim, tekilleştirme, kapsam kapısı ve kapsam takibi düzeltildi. 69 test; 8/8 hedef ilk 5; 90 geliştirme sorgusunda alıntı erişimi 27→65; canlı API, kalan üretim kusurları ve rapor | codex | 2026-10-01 | — |

| ✅ | 100 sorguda RAG; 3 embedding/1.983 parça; 12 soruda canlı Qwen ve ortak oracle kaynaklı Qwen/Gemma, 36 cevap incelemesi ve rapor. Hibrit/E5 güçlü aday; örnek belge, kısa SSS cevap kaybı ve kapsam kusurları saptandı | codex | 2026-10-01 | — |

- İlk 50 taslağa iki bağımsız insan incelemesi ve güncel kaynak sürümü kontrolü; henüz gold kayıt yok
- Öncelikli kalite kusuru: lisansüstü kabul/mazeret sorularında yanlış madde retrieval; `docs/evaluation/gold-v1/verification.md`
- Belirsiz "vize"/"muafiyet"/sınav itirazı sorularında anlam ve öğrenim düzeyi açıklaması isteme
- Onaylı ayrı train verisiyle LoRA, kural tabanlı knowledge graph pilotu ve kavram sözlüğü; kapsam `docs/evaluation/gold-v1/README.md`

- Görev #6: karşılaştırmalı deneyler (embedding + LLM, MRR@10/Recall@5/latency/halüsinasyon)
- Kırgızca dil desteği
- Kullanıcının arayüzden kendi belgesini yükleyebilmesi (İP5 ek)
- Taranmış PDF'ler (akademik takvimler) için OCR desteği
- Fakülte alt alanları robots.txt kapalı — kurum içi tarama izni alınırsa eklenecek

| ✅ | Uygulama ve raporlar v0.2.0 olarak commit edildi; ortak VERSION ve ad altında sürüm. v0.2.1 kaynaklı ön cevap + düzey sorusu denendi; 75 test, canlı iki soru/takip ve API/UI sürümü doğrulandı | codex | 2026-10-01 | — |

| ✅ | v0.2.2: temel şartlar ayrı maddeler, süre/not/oran değerlerine otomatik kalın vurgu; 78 test, canlı iki ders saydırma sunumu ve API/UI sürümü doğrulandı. Eksik koşul üretimi ayrı kusur olarak raporda | codex | 2026-10-01 | — |

| ✅ | v0.3.0: DomainRAG yöntemi KTMÜ Türkçe kaynaklarına uyarlandı; 106 taslak senaryo/21 kaynak birimi, ölçüm CLI ve 87 test. 94 cevaplanabilir sorguda alıntı erişimi 69/94; altı canlı Qwen deneyi ve kalan üretim kusurları raporlandı | codex | 2026-10-01 | — |

| ✅ | v0.3.0 canlı ders saydırma + lisans takibi: doğru Madde 25, 5 yıl/CC/1/3 aktarımı; AKTS/içerik uygunluğu ve son kurul onayları eksik, ham cevaplar ve kaynak karşılaştırması tmp altında | codex | 2026-10-01 | — |

| ✅ | v0.3.1: cevabın sonunda gerçek kaynak PDF/SSS bağlantısı; tarama haritasından adres, 90 test, canlı ders saydırma cevabı ve API/UI sürümü doğrulandı | codex | 2026-10-01 | — |
