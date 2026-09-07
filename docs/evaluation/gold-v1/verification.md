# Qwen ve İlk Soru Paketi: Teslim Kontrolü

Tarih: 7 Eylül 2026. Bu rapor uygulama/veri altyapısının kontrolüdür, gold kalite değerlendirmesi değildir.

## Değişiklikler

- Önce mevcut ilgili kod `9c4d24c` kontrol noktası commit'iyle sabitlendi. İlgili kod zaten önceki commit'teydi;
  bu nedenle kontrol noktası boş commit'tir. Kullanıcının `TEZ/` dosyaları ve mevcut referans PDF silinmesi dahil edilmedi.
- `7332da6`: Qwen3.5 9B hem kod varsayılanı hem `.env.example` hem yerel `.env` içinde varsayılan oldu.
  Yerel `.env` Git'e alınmadı. Turkish-Gemma kaldırılmadı.
- Sağlık API'si etkin model adını bildiriyor. Gerçek yanıtta `ollama / qwen3.5:9b`, LaBSE ve 39.659 parça görüldü.
- Kaynak alanındaki “N kaynakta doğrulandı” metni “N kaynak parçası” oldu. Retrieval sonucu, cevap doğrulaması değildir.
- 50 soru + 50 farklı söyleyiş, 5 kaynak, 21 metin birimi, insan inceleme paketi, JSON Schema ve dışa aktarım kapısı eklendi.

## Teknik doğrulama

| Kontrol | Sonuç |
|---|---|
| Backend unittest | 47 test başarılı |
| JSON Schema / Python şema eşitliği | Başarılı |
| Kaynak görüntüsü ve ham dosya hash'leri | Başarılı |
| Bütün alıntıların ham sayfa/HTML metnine eşleşmesi | Başarılı |
| Onaysız veriyi LoRA dışa aktarımı | Beklendiği gibi reddedildi; train bölümü boş, dosya oluşturulmadı |
| Bozuk alıntı, yinelenen ID/soru, grup sızıntısı | Testlerde reddediliyor |
| Tek insan / aynı insan / AI onayı / eski onay | Gold için reddediliyor |
| LoRA'ya dev/test aktarımı | Reddediliyor |
| `npx tsc --noEmit` | Başarılı |
| `GET /health`, frontend `/` | HTTP 200 |
| Canlı API smoke | 4/4 istek teknik olarak tamamlandı; kalite kusurları aşağıda |
| Masaüstü 1280×720, mobil 390×844 | Kaynak aç/kapa, iç kaydırma, soru korunması ve taşma kontrolü başarılı |
| Tarayıcı konsolu | Test sekmesinde warning/error yok |

Masaüstü kaynak paneli açık/kapalıyken mesaj alanı yüksekliği 453 px olarak kaldı; açılınca içerik
927 px oldu ve iç kaydırma 474,5 px'e ilerledi. Mobilde yükseklik 612 px olarak kaldı; içerik 1147 px,
iç kaydırma 534,5 px oldu. Pencere kaydırması her iki testte 0, yatay taşma yoktu.
Ekran görüntülerinde soru/cevap ayrımı ve yeni kaynak etiketi görüldü. Mobil viewport testi sonunda sıfırlandı.
Bu turda üretim derlemesi çalıştırılmadı; değişiklik tek UI metniydi, TypeScript ve çalışan dev arayüzü sınandı.

Testlerde mevcut FastAPI/Starlette `httpx` geçiş uyarısı ve PyMuPDF/SWIG deprecation uyarıları çıktı.
Hata değil; bu iş kapsamında bağımlılık sürümleri değiştirilmedi.
İki yönetmeliğin kapsam/not/başvuru/devam/itiraz sayfalarından sekizinin PDF görüntüsü de incelendi.
Bu görsel kontrol belge güncelliğine veya tüm yanıtların anlam doğruluğuna insan onayı yerine geçmez.

## Canlı Qwen kalite bulguları

Ham istek, cevap, kaynak parçaları ve süreler: [qwen-smoke.json](qwen-smoke.json).
Komut: `backend/` içinde `.venv/bin/python -m scripts.smoke_chat --output /tmp/bakay-smoke-next.json`.
Başlangıçta Ollama'nın aktif model listesi boştu; ilk istek soğuk başlangıç içerebilir.
Süreler tek koşuma aittir, performans dağılımı veya model karşılaştırması değildir.

| Soru | Duvar süresi | Codex gözlemi; insan puanı değil |
|---|---:|---|
| BAKAY-025, ALES 55 ve muafiyet | 11,258 sn | Yazılı/sözlü ayrımı doğru; başvuruda beyan koşulu eksik, gereksiz sınav hesabı eklenmiş. Tam cevap sayılmamalı. |
| BAKAY-036, lisansüstü mazeret başvurusu | 10,477 sn | Yanlış kaynaklar geldi; doktora yeterliğine kaydı ve “bilgi yok” dedi. Tam kaynak Madde 31(5)'te 3 iş günü var. Retrieval kusuru. |
| BAKAY-046, “Vize için ne yapmam gerekiyor?” | 6,551 sn | Ara sınav/giriş vizesi anlamını sormadan giriş vizesi prosedürü anlattı. Açıklama isteme beklentisini karşılamadı. |
| BAKAY-050, kurum dışı kek tarifi | 5,213 sn | Tarif uydurmadı, kapsam dışı yanıt verdi. İlgisiz kurumsal parçalar yine retrieval sonucunda dönüyor. |

Ayrıca tarayıcıdan “Yüksek lisans başvurusu için en az kaç not ortalaması gerekir?” soruldu.
Yaklaşık 12,0 sn'de **yanlış 3,00** cevabı geldi. Kaynaklar arasında Orhun değişimi, tez/yeterlik,
görevde yükselme ve burs parçaları vardı; lisansüstü kabul Madde 10(5) gelmedi. İnceleme paketindeki
BAKAY-021'in tam kaynağı genel eşikleri yüksek lisans için 2,00 ve doktora için 2,50 olarak veriyor,
daha yüksek program şartlarına izin veriyor. UI görünümü çalışıyor olması bu cevabı doğru yapmıyor.
Bu bulgu önceki pilotun güçlü kaynak kapsamı sorununun farklı soru biçimlerinde sürdüğünü gösteriyor.

Bu hataları belirli test sorularına sabit cevap yazarak gizleyen bir değişiklik yapılmadı.
İlk sonraki teknik iş; kabul/ilerleme/burs/personel kurallarını ayıran kaynak erişimi, hibrit arama ve
yeniden sıralama deneyi ile anlam belirsizliğinde açıklama isteme davranışıdır. Etkisi ayrı dev verisiyle ölçülmelidir.

## Açık tamamlanma koşulları

50 sorunun insan onayı ve kaynakların güncel yürürlük kontrolü yok. Saklı test seti, LoRA eğitimi,
adapter, knowledge graph indeksi veya üretim kavram sözlüğü henüz üretilmedi. Plan ve onay kuralları
[protokolde](README.md); yanlış kaynak erişimi/anlam ayrımı bulguları işbirliği panosuna taşındı.
Sistem “hatasız kurumsal danışman” olarak sunulmaya hazır değildir.

Yerel deneme: `http://127.0.0.1:3000/`; API: `http://127.0.0.1:8000/health`.
Servisler geliştirme süreçleridir; bilgisayar uyursa veya yeniden başlarsa yeniden başlatılmaları gerekebilir.
