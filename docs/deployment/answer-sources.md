# Yanıt kaynakları düzeltmesi — 4 Kasım 2026

Canlı paneldeki “akademisyene zam yapıldı mı?” kaydı incelendi. Yanıt
“Bu konuda elimdeki belgelerde bilgi bulamadım.” olmasına rağmen beş kaynak
kartı kaydedilmişti. Kullanıcı yorumu: “hem bulamadım dedin, hem de kaynak verdin”.
Bu hata, üretimden önce bütün erişim sonuçlarının yanıt kaynağına çevrilmesinden
kaynaklanıyordu. Bağlantı kontrolü kaynak kartlarını etkilemiyordu.

Yeni davranış:

- Modelin açık yanıtsızlık çıktısı, sabit kısa yanıt ve boş kaynak listesiyle döner.
  Sistem istemindeki `[YANIT_YOK]` işareti kullanıcıya gösterilmez. Eski modellerin
  doğal dildeki açık yanıtsızlık ifadeleri için de koruma vardır.
- Kaynaklar yanıt üretildikten sonra seçilir. Yanıtta belge başlığı anılmışsa
  yalnız o belgeler seçilir; aksi halde erişim sırasından en fazla üç ayrı belge
  gösterilir. Aynı belgenin farklı parçaları tekrar kart oluşturmaz.
- Bağlantı seçimi aynı listeyi kullanır. Açık yanıtsızlıkta modelin eklediği
  bağlantılar da sabit yanıtla temizlenir. Kaynak doğrulaması açıkken başarısız
  doğrulama kaynaklı iddia olarak sunulmaz.
- Yalnız öğrenim düzeyi sorulan ve hüküm aktarılmayan yanıtta kaynak gösterilmez.
- Hazır cevaplarda da aynı üç belge sınırı geçerlidir. Erişim kapsamı ve
  üretim bağlamı küçültülmez; yeni LLM çağrısı eklenmez.
- JSON, SSE ve telemetri aynı son kaynak listesini kullanır.

Doğal dil koruması ilk paragraftaki açık bilgi yokluğu beyanlarını tanır;
semantik doğruluk garantisi değildir. Son paragrafta yalnız ek bir ayrıntının
bilinmediğini söylemek, dayanaklı kısmi yanıtın kaynaklarını kaldırmaz.
Geçmiş sorgu kayıtları denetim amacıyla değiştirilmez.

Kullanıcının isteğiyle `2de47ac` düzeltmesi, bak.ai marka yayını üzerine
v0.4.3 paketine alındı. Yeni sürüm için arayüz yeniden derlenir; Linux testleri,
canlı API/arayüz sürümü ve gerçek yanıtsız/yeterli soru davranışı doğrulanır.
