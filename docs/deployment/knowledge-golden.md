# Hazır cevaplar, golden dataset ve panelden kotalar — v0.4.0

18 Ekim 2026: **v0.4.0 canlıya alındı**. HTTPS ve kayıtlı Chrome hesabıyla
[yönetim paneli](https://bakai.manas.edu.kg/monitor#knowledge) doğrulandı.

## Yayın kimliği

- Sunucuda `/opt/bakay`, dal `codex/knowledge-golden-live`.
- Yayın commit'i `c8e05b05c3489547569219d64ce6da52cc3cef18`; GitHub `main` içinde.
- Önceki canlı `61e183134b619d49ef081d30b8d849d878e38229` bu commit'in atasıdır.
  Geri bildirim/IP, karakter düzeltmesi ve canlı aşamalar korunur.
- VERSION, frontend paket/kilit sürümleri ve CHANGELOG: v0.4.0.
- Arayüz paketi SHA256:
  `9eed91088b2bd12e53cb0d801505793bd2161abb6bf0049f494f72c9d2dbcb4a`.

## Davranış

- Hazır cevap yönetimi: soru, varyant, kaynak, geçerlilik, onay ve arşiv.
  Onaylı ve geçerli eşleşmeler model çağrısı olmadan cevaplanır.
- Altı kaynaklı örnek **taslak** olarak eklendi; yayında onaylı cevap yok.
  Yerel QA kayıtları canlıya taşınmadı.
- Olumsuz geri bildirimde düzeltme formu; önerilen soru/cevap atomik olarak
  hazır cevap taslağı ve inceleme kaydı oluşturur. Onaylanan düzeltmeler
  JSONL golden geliştirme setine alınır; bağımsız test seti sayılmaz.
- Altı kota panelden kalıcı ve anında düzenlenebilir. Yayında mevcut değerler
  korundu: IP 30/dakika, 120/saat; sistem 30/dakika, 1.000/24 saat;
  sistem ve IP eşzamanlılığı 2. Sayaçlar sıfırlanmadı.

## Doğrulama

- Yerelde üretim derlemesi; sunucuda Linux üzerinde **205 backend testi** geçti.
- SQLite geçişi yedek kopyada denendi: 43 sorgu, 7 geri bildirim ve 23 kota
  satırı korundu. Canlı HTTPS sohbet denemesi sonrasında toplam 44 sorgu var.
- Aday arayüz önce 127.0.0.1:3008 üzerinde denendi; eski statik dosyalar
  açık sekmeler için yeni derlemeye eklendi.
- HTTPS ana sayfa, panel, hakkında ve **13 JS/CSS varlığı** başarılı.
  Altı özel uç oturumsuz **401/no-store**, yabancı Origin **403** verdi.
- Yetkili API: altı taslak, sıfır golden adayı, boş golden dışa aktarımı,
  kota değerleri ve sorgu ayrıntıları doğrulandı.
- Gerçek lisans sorusu 45,73 saniyede beş kaynakla cevaplandı; karakter
  bozulması yok. Bu bir işlev kontrolüdür, uzman doğruluk onayı değildir.
  Yanıtta son paragraf ilk hükümle çelişiyor; ayrıca Markdown bağlantısı
  üretilmediğinden bu denemede kaynak URL erişimi sınanmadı. Kaynak erişimi
  ve üretim kalitesi için bu örnek ayrıca incelenmelidir.
- Chrome'da v0.4.0, altı hazır cevap taslağı, golden bölümü ve kota formu
  görüntülendi. Backend/frontend `active`, yeniden çökme sayısı 0;
  Apache, izleme ve yedek timer'ları etkin.

Git dışındaki `output/knowledge-golden-live/` dizininde `https-checks.json`,
`verification.json`, `private-verification.json`, `deployment.json`,
`answer.json`, `live-panel.png` ve `live-golden.png` bulunur.
Yayın araçları `tmp/ktmu-deployment/knowledge-golden-live/` altındadır.
Bu çıktılar sorgu içeriği içerebilir; genel depoya eklenmedi.

## Yedek ve geri dönüş

- SQLite çevrimiçi yedeği (root'a özel):
  `/var/backups/bakay/knowledge.20261018T135400Z`.
- Önceki `.next`, kod commit/dal kimliği ve yedek yolu:
  `/opt/bakay/runtime/frontend-before-knowledge.20261018T135400Z`.
- Sunucu sonuçları: `/opt/bakay/runtime/knowledge-golden-live/`.
- Geri dönüşte önceki kod ve arayüz kullanılır; eklenen tablolar bırakılır.
  Yayın sonrasındaki kullanıcı kayıtları eski veritabanıyla ezilmez.

Özel ortam, API anahtarları, Apache ve Chroma indeksi değiştirilmedi.
