# Haiku 5.5 — Sonnet 5.5 karşılaştırma pilotu

9 Ekim 2026. Kullanıcı Haiku denemesini istedi. Önceki Sonnet pilotunun
30 üretim kaynağı ve 12 tanısal referans kaynaklı sorusu, prompt metinleri
değiştirilmeden yeniden kullanılır. Referans yanıtlar modele gönderilmez.
Uygulamanın `.env` ayarları bu deney için değiştirilmez.

Kaynak/soru dosyaları önceki pilotta:
[30 üretim sorusu](../2026-10-09-sonnet/retrieved.snapshot.json),
[12 kritik soru](../2026-10-09-sonnet/oracle.snapshot.json).
Sonuçlar ve örnek hatalar [raporda](report.md).

## Ayarlar ve sınırlar

- İlk Haiku teşhisi: `claude-haiku-5-5`, Messages API, `thinking=adaptive`, `effort=medium`,
  en çok 4096 çıktı tokenı. Düşünme tokenları da bu bütçeye dahil olduğundan
  yanıt metnine yer kalması için 4096 seçildi. Sıcaklık/top_p/top_k,
  araç, önbellek, ısıtma veya otomatik tekrar kullanılmaz.
- Araçsız Haiku karşılaştırması: `thinking=disabled`, `effort=high`, en çok
  2048 çıktı tokenı. İlk adaptive koşusunda düşünme tokenları süreyi artırdı;
  araçsız Sonnet'e daha yakın bu ayar ayrıca 30+12 soruda ölçülür.
  Araçsız ayarın kritik koşulları eksiltmesi üzerine adaptive ayarın da
  aynı 12 kritik sorusu tamamlanır; kalite/hız farkı ayrı değerlendirilir.
- Sonnet karşılaştırması: önceki `sonnet-retrieved-2k` ve `sonnet-oracle`
  kayıtları; `thinking=between_tools`, `effort=high`, en çok 2048 çıktı tokenı.
  Sorular ve kaynaklar aynı; düşünme modları farklıdır. İlk adaptive teşhisinde
  çaba ve çıktı bütçesi de farklıdır.
  Bu, pratik sağlayıcı ayarlarının pilotudur; eşit düşünme/çıktı bütçeli
  model karşılaştırması değildir. Süreler farklı zamanlarda ölçülür.
- 12 kritik sorunun etiketleri insan onayı bekliyor. Tek Codex incelemesi
  genel doğruluk yüzdesi, bağımsız test veya gold başarısı değildir.
- Bu deney üretimi ölçer; kaynak erişimi, sohbet hafızası ve frontend
  başarısı olarak yorumlanmaz. Kaynaklar önceki pilotta sabitlendi.
- Prompt ve snapshot SHA-256, API kullanım sayaçları, bitiş nedeni,
  istek/mesaj kimlikleri ve süreler ham kayıtlarda korunur.

## Tekrar çalıştırma

API anahtarı kök `.env` dosyasında olmalıdır; sohbete/repoya eklenmez.
Aşağıdaki komutlar `backend/` içinden çalışır. Aynı komut tamamlanan soruları
atlar; değişen ayar veya kod için yeni etiket kullanın.

```sh
ANTHROPIC_THINKING=adaptive ANTHROPIC_EFFORT=medium ANTHROPIC_MAX_TOKENS=4096 .venv/bin/python -m scripts.compare_models run-anthropic --snapshot ../docs/evaluation/2026-10-09-sonnet/retrieved.snapshot.json --model claude-haiku-5-5 --label haiku-retrieved --output ../docs/evaluation/2026-10-09-haiku
ANTHROPIC_THINKING=adaptive ANTHROPIC_EFFORT=medium ANTHROPIC_MAX_TOKENS=4096 .venv/bin/python -m scripts.compare_models run-anthropic --snapshot ../docs/evaluation/2026-10-09-sonnet/oracle.snapshot.json --model claude-haiku-5-5 --label haiku-oracle --output ../docs/evaluation/2026-10-09-haiku
ANTHROPIC_THINKING=disabled ANTHROPIC_EFFORT=high ANTHROPIC_MAX_TOKENS=2048 .venv/bin/python -m scripts.compare_models run-anthropic --snapshot ../docs/evaluation/2026-10-09-sonnet/retrieved.snapshot.json --model claude-haiku-5-5 --label haiku-direct-retrieved --output ../docs/evaluation/2026-10-09-haiku
ANTHROPIC_THINKING=disabled ANTHROPIC_EFFORT=high ANTHROPIC_MAX_TOKENS=2048 .venv/bin/python -m scripts.compare_models run-anthropic --snapshot ../docs/evaluation/2026-10-09-sonnet/oracle.snapshot.json --model claude-haiku-5-5 --label haiku-direct-oracle --output ../docs/evaluation/2026-10-09-haiku
```

9 Ekim standart [API tarifesi](https://platform.claude.com/docs/en/about-claude/pricing):
Haiku 5.5, 100.000 token ve altı girişler için 0,10 USD/milyon giriş ve
0,50 USD/milyon çıktı tokenı; daha uzun girişlerde 0,50/2,50 USD.
Sonnet 5.5, 2/10 USD. Sayaç temelli maliyet tahmini kuruluş faturası değildir.
İstek hatasında sayaç dönmezse gerçek maliyet yerel kayıtta görünmeyebilir.

Model/ayar kaynakları: [Haiku 5.5](https://platform.claude.com/docs/en/models/haiku-5-5/overview),
[API geçişi](https://platform.claude.com/docs/en/models/haiku-5-5/migration-guide).
Düşünmeyi kapatma desteği: [Haiku API yenilikleri](https://platform.claude.com/docs/en/models/haiku-5-5/whats-new-haiku-5-5).
