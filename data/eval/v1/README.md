# BAKAY v1 inceleme verisi

Bu klasör gold değil, **50 insan onaysız Codex taslağı** içerir.

- `dataset.json`: soru, varyant, taslak cevap, gerekli/yanlış iddialar, alıntılar ve kural aileleri.
- `schema.json`: `backend/evaluation/dataset.py` modelinden üretilen JSON Schema.
- `catalog.json`: resmî URL, başlık, yerel ham belge yolu ve çıkarılacak sayfa/bölümler.
- `evidence.json`: ham dosya hash'leri ve normalleştirilmiş kaynak sayfa/bölümleri.

İnceleme alanları yazılmamışsa şema varsayılanı `pending_review`, `unassigned`,
`development_exposed`, `codex_draft`, boş `reviews` listesidir. Eksik alan onay anlamına gelmez.

[İnceleme paketi](../../../docs/evaluation/gold-v1/review-packet.md) ve
[protokol/komutlar](../../../docs/evaluation/gold-v1/README.md).
Yerel doğrulama: `backend/` içinde `.venv/bin/python -m scripts.dataset validate --verify-raw`.
