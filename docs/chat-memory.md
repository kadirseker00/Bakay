# BAKAY sohbet hafızası — ilk sürüm

Bu sürüm aynı sohbet içindeki takip sorularına bağlam sağlar. Arayüz geçmişi
`bakay_history` anahtarıyla bu tarayıcıda saklar; sayfa yenilendiğinde geri yükler.
Hesap, sunucu tarafında sohbet deposu veya sohbetler arası kullanıcı profili yoktur.

## Akış ve sınırlar

- `/chat` isteğinin isteğe bağlı `history` alanı, `role` (`user` / `assistant`)
  ve `content` taşıyan tamamlanmış soru/yanıt çiftlerinden oluşur.
- En çok **6 tur / 12 mesaj**, mesaj başına **2.000 karakter** aktarılır. Son soru
  ayrı `question` alanındadır; onun da üst sınırı 2.000 karakterdir.
- Eski, yalnızca `question` gönderen istemciler çalışmaya devam eder.
- Tarayıcı en son **100 mesajı** saklar. Başarısız ve henüz yanıtlanmamış istekler
  API bağlamına girmez. Depolama engellenirse sohbet çalışır ve arayüz kaydetme
  sorununu bildirir. Bozuk kayıtlar arayüzü çökertmez.
- Türkçe gönderme/düzeltme kalıpları ve kısa takip soruları bağlam çözümünü açar.
  Çözücü yalnızca kullanıcının önceki sorularını görür; asistan yanıtları çıkarılır.
  Örneğin yüksek lisans konuşmasının ardından “Peki hangi belgeler gerekli?”
  önceki konu ile bağımsız soruya dönüştürülür. “Öğrenci yurtlarına nasıl
  başvururum?” gibi açık konulu sorular doğrudan aranır; eski konu eklenmez.
- Bağlam çözücü yalnızca gerekli turlarda bir ek LLM çağrısı yapar. Çözücü hata
  verirse veya belirsizlik bildirirse belge araması yerine açıklama istenir.
- Yönlendirme, arama ve üretim açılmış soruyu kullanır. Her turda belgeler yeniden
  bulunur; skor kapısı ve mevcut kaynak doğrulama ayarları uygulanır. Sohbet
  metninin tamamı yanıt üretim prompt'una eklenmez. Önceki asistan yanıtı resmî
  bilgi kaynağı sayılmaz.
- “Yeni sohbet” tarayıcı kaydını ve aktif bağlamı temizler, süren isteği iptal eder.
  Eski isteğin geç gelen yanıtı yeni sohbete eklenmez.

## API örneği

```json
{
  "question": "Peki hangi belgeler gerekli?",
  "history": [
    {"role": "user", "content": "KTMÜ yüksek lisans başvurusu nasıl yapılır?"},
    {"role": "assistant", "content": "Başvuru koşulları ilgili yönetmelikte açıklanır."}
  ]
}
```

Yanıt sözleşmesi değişmez: `query_id`, `answer`, `sources`, `latency_ms`.
Sırası bozuk, tamamlanmamış, `system` rolü taşıyan veya sınırı aşan geçmiş 422 alır.

## Telemetri ve kısıtlar

Asıl kullanıcı sorusu mevcut telemetride korunur; açılmış soru
`rewritten_query` alanına yazılır. `memory:resolved` ve `memory:needs_context`
adımları akışı izlemeye yardım eder. Toplam gecikme bağlam çözümünü kapsar.
“Yeni sohbet”, mevcut sunucu telemetri kayıtlarını silmez; bu sürümde geçmişi
yeniden kurmak için bu kayıtlar kullanılmaz.

Gönderme tanıma Türkçe kalıplarla sınırlıdır; bütün örtük takip sorularını kapsamaz.
Önceki yanıtın “ikinci maddesi” gibi yanıta özgü göndermeler bu sürümün kapsamı dışındadır.
LLM'nin bağlam çözümü ve kaynak bağlı yanıtları için insan onaylı doğruluk garantisi
yoktur. Daha kapsamlı çok turlu değerlendirme, uzun sohbet özeti, kimlikli kalıcı
sohbetler ve açık tercih yönetimiyle kullanıcı profili sonraki aşamalardır.

## Doğrulama

`.venv/bin/python -m unittest discover -s tests -v` (backend dizininden):
API uyumu/sınırları, takip sorusunun arama ve üretime taşınması, konu değişimi,
hatalı bağlam çözümü ve skor kapısı kontrolleri. Frontend TypeScript kontrolü ve
üretim derlemesi; geçmiş yardımcılarında tamamlanmış tur seçimi, sınırlar,
geri yükleme/temizleme ve bozuk/engellenmiş depolama kontrolleri.

Yerel Qwen + LaBSE + Chroma ile `/chat` takip sorusu ayrıca denenmiştir. Bu işlev
kontrolü, retrieval/generation başarı oranı veya <10 saniye hedefinin kanıtı değildir.
1 Ekim 2026 kontrolünde 57 backend testi, TypeScript kontrolü ve üretim derlemesi
geçti. Tarayıcıdan kaynaklı takip yanıtı, yenilemede geri yükleme ve “Yeni sohbet”
sonrasında yenilemede de boş kalma doğrulandı. Yerel API yeni kodla yeniden başlatıldı.
