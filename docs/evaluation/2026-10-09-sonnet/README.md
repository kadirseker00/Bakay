# Sonnet 5.5 ve Qwen3.5 9B pilotu

9 Ekim 2026, Bişkek. Kullanıcı yalnız Sonnet ile denemeyi seçti.
Team API kredisi 500 USD; kullanıcıdaki fatura kaydı 7 Kasım 2026 son
kullanım tarihini gösteriyor. Kredinin ayrıntıları/anahtarı repoya eklenmez.

## Deney tasarımı

- `retrieved.snapshot.json`: mevcut 39.659 parçalık üretim koleksiyonundan
  30 soruya getirilen ilk beş parça. Hibrit arama, sıralama ve metinleri sabit.
- `oracle.snapshot.json`: 1 Ekim kaynak bağlı pilotundan 12 kritik soru ve
  doğru referans alıntıları. Güncel `SYSTEM_PROMPT` ile yeniden hazırlanmıştır;
  kaynak/önceki snapshot özeti dosyada kayıtlıdır. Arşiv belgelerinin güncel
  yürürlüğü ve etiketleri insan onayı bekliyor.
- İki model, her koşulda aynı prompt metnini ve aynı kaynak sırasını kullanır.
  Referans cevaplar ve inceleme ölçütleri prompt'a eklenmez.
- Qwen: Ollama, `think=false`, sıcaklık 0,3, tohum 42, 8192 bağlam,
  en çok 1024 çıktı tokenı. Sonnet: `claude-sonnet-5-5`, Messages API,
  `thinking=between_tools`, `effort=high`, en çok 2048 çıktı tokenı.
  İlk 1024-token Sonnet koşusu uzun cevaplarda kesilme gösterdi; dosyaları
  teşhis kaydı olarak korunur. Nihai karşılaştırmada `sonnet-retrieved-2k`
  etiketi kullanılır. Çıktı bütçeleri farklıdır; eşit bütçeli bir ablasyon
  veya salt model ağırlığı karşılaştırması değildir.
- Sonnet 5.5 özel sıcaklık/top_p/top_k ayarlarını kabul etmediği için bu
  alanlar gönderilmez. Araçsız `between_tools` isteği yalnız yanıt metni
  döndürür. Tokenizer/servis şablonları ve örnekleme aynı değildir;
  bu pratik sağlayıcı değişimi pilotudur.
- Bütün cevaplar, süreler, prompt SHA-256, kullanım tokenları ve API istek
  kimlikleri dosyalara kaydedilir. Sonnet'te ek ücretli ısıtma/otomatik tekrar
  yoktur. Hata olduğunda koşum durur; aynı komut başarılı soruları atlar.
- Bu iki koşul cevap üretimini ölçer. Üretimin düzey sorma, kapsam kapısı,
  hafıza çözümü, vurgu/bağlantı adımları ve frontend ayrıca canlı sınanır.
  Kaynak erişimi veya bağımsız gold doğruluk başarısı olarak sunulmaz.

## Tekrar çalıştırma

Proje kökündeki `.env` dosyasına `ANTHROPIC_API_KEY` ekleyin. Aşağıdaki
komutlar `backend/` içinden çalıştırılır; `LLM_PROVIDER` değişmesi gerekmez.
Yeni model/ayar/kaynak denemelerinde yeni etiket veya çıktı dizini kullanın.

```sh
.venv/bin/python -m scripts.compare_models run-anthropic --snapshot ../docs/evaluation/2026-10-09-sonnet/retrieved.snapshot.json --model claude-sonnet-5-5 --label sonnet-retrieved-2k --output ../docs/evaluation/2026-10-09-sonnet
.venv/bin/python -m scripts.compare_models run-anthropic --snapshot ../docs/evaluation/2026-10-09-sonnet/oracle.snapshot.json --model claude-sonnet-5-5 --label sonnet-oracle --output ../docs/evaluation/2026-10-09-sonnet
.venv/bin/python -m scripts.compare_models run --snapshot ../docs/evaluation/2026-10-09-sonnet/retrieved.snapshot.json --model qwen3.5:9b --label qwen-retrieved --output ../docs/evaluation/2026-10-09-sonnet
.venv/bin/python -m scripts.compare_models run --snapshot ../docs/evaluation/2026-10-09-sonnet/oracle.snapshot.json --model qwen3.5:9b --label qwen-oracle --output ../docs/evaluation/2026-10-09-sonnet
.venv/bin/python -m scripts.compare_models summarize --snapshot ../docs/evaluation/2026-10-09-sonnet/retrieved.snapshot.json --results ../docs/evaluation/2026-10-09-sonnet/qwen-retrieved.answers.jsonl ../docs/evaluation/2026-10-09-sonnet/sonnet-retrieved-2k.answers.jsonl --output ../docs/evaluation/2026-10-09-sonnet/retrieved/metrics.json
.venv/bin/python -m scripts.compare_models summarize --snapshot ../docs/evaluation/2026-10-09-sonnet/oracle.snapshot.json --results ../docs/evaluation/2026-10-09-sonnet/qwen-oracle.answers.jsonl ../docs/evaluation/2026-10-09-sonnet/sonnet-oracle.answers.jsonl --output ../docs/evaluation/2026-10-09-sonnet/oracle/metrics.json
```

Tarife kaynağı: [Claude API fiyatları](https://platform.claude.com/docs/en/about-claude/pricing).
9 Ekim standart Sonnet fiyatı: giriş 2 USD/milyon token, çıkış 10 USD/milyon
token. Önbellek kullanılmaz. `estimated_cost_usd`, API'nin döndürdüğü kullanım
sayaçlarından hesaplanan tahmindir; kuruluş faturası değildir. İstek zaman
aşımında sunucuda tamamlandıysa dönen kullanım sayacı olmayabilir; böyle bir
durumda yerel toplam gerçek harcamayı eksik gösterebilir.

Model davranışı: [Sonnet 5.5 API değişiklikleri](https://platform.claude.com/docs/en/models/sonnet-5-5/whats-new-sonnet-5-5).

Sonuçlar ve kaynak karşılaştırması [raporda](report.md) tutulur.
