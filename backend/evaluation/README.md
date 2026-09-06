# Yerel LLM karşılaştırması

Bu pilot, Turkish-Gemma ile Qwen'in **aynı geri getirilen metin parçalarından**
Türkçe yanıt üretmesini karşılaştırır. Üretim `.env` dosyasını değiştirmez;
LaBSE veya Chroma'yı yeniden indekslemez. Yeni Python bağımlılığı gerekmez.

## Tekrar çalıştırma

Komutları `backend/` dizininden çalıştırın. İlk komutun çıktısı değiştirilmeyen
bir kaynak anlık görüntüsüdür; mevcut dosyanın üzerine yazılmaz. Yeni deney
için yeni bir çıktı dizini kullanın. Önce Ollama'da iki model de yüklü olmalıdır.

```sh
ollama pull qwen3.5:9b
.venv/bin/python -m scripts.compare_models prepare --output ../docs/evaluation/2026-09-07/snapshot.json
.venv/bin/python -m scripts.compare_models run --snapshot ../docs/evaluation/2026-09-07/snapshot.json --model hf.co/ytu-ce-cosmos/Turkish-Gemma-9b-T1-GGUF:Q4_K_M --label gemma --output ../docs/evaluation/2026-09-07
.venv/bin/python -m scripts.compare_models run --snapshot ../docs/evaluation/2026-09-07/snapshot.json --model qwen3.5:9b --label qwen --output ../docs/evaluation/2026-09-07
.venv/bin/python -m scripts.compare_models summarize --snapshot ../docs/evaluation/2026-09-07/snapshot.json --results ../docs/evaluation/2026-09-07/gemma.answers.jsonl ../docs/evaluation/2026-09-07/qwen.answers.jsonl --output ../docs/evaluation/2026-09-07/metrics.json
```

## Ölçüm koşulları

- 25 temsilî kurumsal soru, 5 bulunmayan bilgi/kapsam dışı soru.
- Her soruda LaBSE ile getirilen ilk 5 parça, sıra ve prompt metni aynıdır.
- Mevcut uygulamanın generation prompt'u ve yanıt temizliği kullanılır.
- `think=false`; sıcaklık, bağlam ve çıktı sınırı mevcut ayarlardan okunur.
  Sabit tohum `42` kullanılır. Koşumdaki somut değerler `.meta.json` içindedir.
- Soru yeniden yazma, yönlendirme, doğrulama ve skor kapısı uygulanmaz. Bu,
  yalnızca üretim katmanını karşılaştırır. Üretimdeki skor kapısının her soruyu
  geçirip geçirmeyeceği ayrıca `production_gate_pass` alanında saklanır.
- Her model bir kez kısa bir istekle ısıtılır. Bu süre ana ölçümden ayrıdır.
  Modeller aynı anda çalıştırılmaz. İstekler sırayla, tek istemciden gönderilir.
- Süre, ısıtılmış modelde bütün yanıtın dönmesine kadardır; arama, HTTP API,
  arayüz ve ilk token süresi değildir. Üretim hedefi olan 10 saniyeyle kıyas
  bu nedenle yalnızca generation katmanı için anlamlıdır.
- p95, sıralı ölçümlerde `ceil(0.95 * n)` konumudur. Token/s Ollama'nın üretim
  sayacıyla hesaplanır; tokenizer'lar farklı olduğu için tek başına hız kararı
  verilmez. Yanıt uzunluğu ve tamamlanma süresi birlikte incelenir.
- Model etiketi yanında ağırlık özeti (digest), Ollama sürümü, donanım,
  şablon/parametreler, kaynak ve prompt SHA-256 değerleri saklanır.
- Kesilen koşum aynı komutla sürdürülür. Başarılı sorular atlanır; hatalı
  sorular yeniden denenir. Farklı model/ayar/kaynakla eski koşuma devam edilmez.

## Kalite değerlendirmesi

Yanıtlar incelendikten sonra `summarize` komutuna
`--reviews ../docs/evaluation/2026-09-07/gemma.review.json ../docs/evaluation/2026-09-07/qwen.review.json`
eklenerek kalite sayımları da hesaplanır. Yeni kaynak anlık görüntüsüyle eski
inceleme dosyaları kullanılamaz. `answers.md` karşılıklı yanıt dökümüdür.

`context_expectations.json`, yalnızca sabitlenen kaynaklar okunarak hazırlanır.
Bu beklentiler tüm üniversite mevzuatı için doğrulanmış bir altın veri seti
değildir. Kaynakların güncelliği ayrıca incelenmelidir. Eksik arama sonuçları
özellikle korunur: modelin bilgi yokken uydurmaması da ölçülür.

Son yanıtlara yönelik inceleme şu alanlarda yapılır:

- `grounded`: Somut iddialar, doğru konu ve öğrenci grubu için verilen
  kaynaklarla destekleniyor mu? Kaynakta olmayan tarih, puan, tutar veya belge
  listesi; başka grubun kuralını uygulama; kişisel kayıt uydurma başarısızdır.
- `complete`: Kaynakta mevcut olan temel yanıt verilmiş mi? Bilgi yoksa açık
  çekimserlik, bilgi kısmi ise bulunan kısmın açıklanması ve sınırın belirtilmesi
  beklenir. Kaynakta yanıt varken bütünüyle çekimser kalmak başarısızdır.
- `citation_correct`: Anılan başlık gerçekten ilgili parçanın başlığı mı?
  Çekimser yanıtın kaynak adı vermesi zorunlu değildir.
- `turkish_clear`: Kullanıcıya gösterilen yanıt açık Türkçe mi; yabancı dilde
  iç muhakeme, anlamsız tekrar veya yarım metin içeriyor mu?

Bu ilk inceleme Codex tarafından yapılır; bağımsız insan değerlendirmesi veya
kör değerlendirme değildir. Küçük ve tek koşumlu bir pilotun sonuçları genel
model sıralaması ya da bilimsel olarak kesin üstünlük şeklinde yorumlanmaz.
`done_reason=length` ve boş yanıtlar kalite incelemesinden çıkarılmaz.
