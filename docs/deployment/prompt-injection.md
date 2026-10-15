# RAG kaynaklarından gelen talimatlara karşı koruma

15 Ekim 2026 — `rag-trust-boundary-v1`.

Önceki akışta uygulama kuralları, belge parçaları ve soru aynı kullanıcı
mesajındaydı. Artık güvenilir kurallar Anthropic Messages API'nin üst düzey
`system` alanına gider. Gemini `config.system_instruction`, Ollama `system`
alanıyla aynı ayrımı korur. Kullanıcı veya belge metni sistem alanına eklenmez.

Belgeler `retrieved_documents/retrieved_document` alanlarında; başlık, metin ve
öğrenim kapsamı ayrı veri alanlarında gönderilir. Soru, geçmiş sorular ve
doğrulanacak cevap da ayrı alanlardadır. XML özel karakterleri kaçırılır;
belgedeki `</text><system>…` dizisi veri sınırını kapatamaz. Kaçış, modelin
talimatları anlayamamasını garanti etmez; güven sınırı sistem talimatında da
açıkça tanımlanır. Asistana yöneltilen görev/rol değişiklikleri uygulanmaz,
öğrenciye yönelik normal mevzuat yükümlülükleri bilgi olarak korunur.

Üretim, sohbet bağlamı çözümü, sorgu yeniden yazma, kapsam sınıflama ve isteğe
bağlı dayanak doğrulaması aynı ayrımı kullanır. Mevcut yardımcı düğümlerin hata
davranışları değişmez; dayanak doğrulaması tek başına bir güvenlik kapısı değildir.
JSONL kayıtlarında `prompt_version` ve ayrı `system_prompt` bulunur; SQLite'ın
`prompt` alanı kullanıcı/veri mesajını saklar. Bunlar mevcut yönetici erişimi
ve yedekleme politikalarına tabidir.

Eski sabit metinli deney araçları için `SYSTEM_PROMPT.format(...)` sözleşmesi
korunur. Bu eski karşılaştırmalar gerçek sistem rolü ayrımını ölçmez. Canlı
uygulama `SYSTEM_INSTRUCTIONS` kullanır; yeni güvenlik deneyi de bu yolu izler.

## Doğrulama

Yerel otomatik paket: **159 test başarılı**. Yeni kontroller; üç sağlayıcıda
sistem alanı aktarımı, zararlı başlık/genişletilmiş parça/soru/geçmiş, çift
kodlanmış etiket, normal mevzuat yükümlülükleri ve üretim akışını kapsar.

Gerçek model deneyi için backend dizininde:

```bash
.venv/bin/python -m scripts.check_prompt_injection --live --output /tmp/bakai-security.json
```

Bu komut ücretli çağrı yapar. Üretim indeksine yazmaz ve embedding modeli
yüklemez. Altı saldırı ile normal mevzuat ve eksik bilgi kontrolü çalıştırır.
Claude maliyetleri `security-check-*` kimlikleriyle panelin maliyet hesabına
dahildir; sentetik sohbet kaydı oluşturulmaz. Rapor sadece yapay test cevaplarını,
token/maliyet sayaçlarını ve sonuçlarını içerir.

Canlı model ve yayın doğrulaması sonuçları kurulum sonunda bu belgeye eklenir.

Bu önlemler prompt injection riskini azaltır; tüm saldırılara karşı kesin
koruma sağlamaz. Kaynağın yanlış olmasını veya zararlı bir bilginin doğruymuş
gibi yazılmasını da tek başına çözmez. Model değiştiğinde aynı saldırı ve normal
soru örnekleri tekrar çalıştırılmalıdır.

Sağlayıcı sözleşmeleri:
[Anthropic Messages](https://platform.claude.com/docs/en/api/messages/create),
[Google Gen AI SDK](https://googleapis.github.io/python-genai/),
[Ollama Generate](https://docs.ollama.com/api/generate).
