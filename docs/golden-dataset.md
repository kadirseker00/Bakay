# Geri bildirimden golden dataset'e

Olumsuz düğmesi mevcut neden formunu açar. **Doğru yanıt nasıl olmalı?** alanı
isteğe bağlıdır; doğru cevabı bilmeyen kullanıcı yalnız sorun bildirebilir.
Düzeltme yazılırsa tam soru zorunlu, resmî kaynak bağlantısı isteğe bağlıdır.
Takip sorusunun bağımsız anlaşılabilmesi için soru düzenlenebilir.

`POST /feedback` ek alanları: `correction_question` (3–2.000 karakter),
`correction_answer` (1–12.000 karakter), `correction_source` (en fazla 2.000
karakter, yalnız manas.edu.kg ve alt alanlarında HTTP/HTTPS). Eski istemcilerin
sadece oy göndermesi desteklenir. Düzeltme yalnız olumsuz oyda kabul edilir.
Geri bildirim, aday ve hazır cevap taslağı aynı SQLite işlemiyle kaydedilir.
Hata olursa tümü geri alınır; istemci yeniden deneyebilir. Aynı sorguya aynı
düzeltmenin tekrar gönderimi yeni taslak oluşturmaz ve yönetici düzenlemesini
değiştirmez. Farklı öneri ayrı aday olarak korunur.

Taslak, **Hazır cevaplar** listesine hemen düşer. **Golden dataset →
Düzeltmeler** bölümünde özgün soru, yanıt, varsa kısa sohbet geçmişi ve öneri
birlikte görülür. **Hazır cevapta incele** ilgili taslağı açar. Yönetici soruyu,
cevabı ve kaynakları düzenler; kaynak kontrolü ve geçerlilik tarihini girip
onaylar. Arşivleme öneriyi silmez. Özgün öneri değişmez; güncel yönetici cevabı
ve kaynaklar hazır cevap sürümleriyle izlenir.

`GET /monitor/golden` ve `GET /monitor/golden/export` yönetici oturumu
gerektirir ve önbelleğe alınmaz. JSONL dışa aktarımı yalnız yayımlanmış,
onaylanmış, süresi dolmamış düzeltmeleri içerir. `reference_answer` güncel
yönetici cevabıdır; kullanıcı önerisi ayrıca `proposed_answer` alanındadır.
Kaynaklar, onaylayan, onay tarihi, kaynak kontrol tarihi, geçerlilik tarihi,
hazır cevap kimliği/sürümü ve özgün soru/yanıt/bağlam korunur. IP, geri bildirim
sahibinin adı ve sistem promptu dışa aktarılmaz. Serbest soru/yanıt metinlerinde
kişisel bilgi bulunabileceği için kurum dışı paylaşım öncesi içerik kontrolü
gerekir. Boş havuz boş JSONL döndürür.

Bu havuz insan incelemesinden geçmiş **geliştirme** referanslarıdır:
`split=development`, `origin=user_correction`, `schema_version=1`.
Hazır cevaplarda kullanılmış aynı sorular üzerinde model başarısı ölçmek,
bağımsız test başarısı değildir. Makale değerlendirmesi için ayrı tutulmuş
test seti ve gerekiyorsa ikinci bağımsız uzman incelemesi ayrıca hazırlanmalı.
Mevcut `docs/evaluation/gold-v1` dosyaları değiştirilmez.

Yeni sorgularda JSON ve SSE akışında son 12 mesajdan oluşan istek bağlamı
telemetriye kaydedilir. Önceki sorguların eksik bağlamı tahmin edilmez;
geçişte `history_json` alanı veri kaybı olmadan eklenir.
