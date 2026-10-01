# Deneyi tekrar çalıştırma

Komutlar `backend/` içinden çalışır. Yeni retrieval için mevcut olmayan bir
çıktı dizini seçin. Üretim `.env` ve koleksiyonunu değiştirmez. E5 ilk kullanımda
Hugging Face önbelleğine indirilir; üretim indeksi yeniden oluşturulmaz.

```sh
OMP_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false .venv/bin/python -m evaluation.system_audit retrieve --output ../docs/evaluation/yeni-deney
OMP_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false .venv/bin/python -m evaluation.system_audit embedding --output ../docs/evaluation/yeni-deney --model sentence-transformers/LaBSE --label labse
OMP_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false .venv/bin/python -m evaluation.system_audit embedding --output ../docs/evaluation/yeni-deney --model intfloat/multilingual-e5-small --label e5-small
OMP_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false .venv/bin/python -m evaluation.system_audit embedding --output ../docs/evaluation/yeni-deney --model sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 --label minilm
.venv/bin/python -m scripts.compare_models run --snapshot ../docs/evaluation/yeni-deney/live.snapshot.json --model qwen3.5:9b --label qwen-live --output ../docs/evaluation/yeni-deney
.venv/bin/python -m scripts.compare_models run --snapshot ../docs/evaluation/yeni-deney/oracle.snapshot.json --model qwen3.5:9b --label qwen-oracle --output ../docs/evaluation/yeni-deney
.venv/bin/python -m scripts.compare_models run --snapshot ../docs/evaluation/yeni-deney/oracle.snapshot.json --model hf.co/ytu-ce-cosmos/Turkish-Gemma-9b-T1-GGUF:Q4_K_M --label gemma-oracle --output ../docs/evaluation/yeni-deney
.venv/bin/python -m scripts.compare_models summarize --snapshot ../docs/evaluation/yeni-deney/live.snapshot.json --results ../docs/evaluation/yeni-deney/qwen-live.answers.jsonl --output ../docs/evaluation/yeni-deney/live/metrics.json
.venv/bin/python -m scripts.compare_models summarize --snapshot ../docs/evaluation/yeni-deney/oracle.snapshot.json --results ../docs/evaluation/yeni-deney/qwen-oracle.answers.jsonl ../docs/evaluation/yeni-deney/gemma-oracle.answers.jsonl --output ../docs/evaluation/yeni-deney/oracle/metrics.json
.venv/bin/python -m unittest evaluation.test_system_audit -v
.venv/bin/python -m scripts.dataset validate --verify-raw
```

LLM ve embedding sürelerini kontrollü karşılaştırmak için işleri sırayla çalıştırın.
Model sonuçları kaldığı yerden devam eder; başarılı satırlar yeniden üretilmez.
Embedding komutu aynı etiketli çıktıyı yeniden yazabilir; farklı deneyde yeni dizin kullanın.

- [Rapor](report.md): kararlar, ölçümler ve sınırlılıklar.
- [Örnek soru–cevaplar](examples.md): beklenen cevaplar, 36 gerçek yanıt ve inceleme gerekçeleri.
- `*.assessment.json`: cevap ve bağlam hash'leriyle tek Codex incelemesi.
- `retrieval-metrics.json`: tam koleksiyonun nihai erişim ölçümleri.
- `document-only-retrieval-metrics.json`: yalnız kanonik belgeleri kabul eden ilk ölçüm.
- `*.retrieval.json`: 100 sorgunun ilk 10 sonucu, skorları ve alıntı kapsamı.
- `pilot-corpus.json`, `*.embedding.json`: üç modelin aynı havuzdaki girdileri/sonuçları.
- `live.snapshot.json`, `oracle.snapshot.json`: 12 soru, beklenen cevaplar,
  kaynaklar, tam prompt'lar ve SHA-256 değerleri.
- `*.answers.jsonl`, `*.meta.json`: Ollama ham/temiz yanıtları ve model/ayar kayıtları.
- `production-top5-check.json`: 12 örneğin üretim aramasıyla eşitlik kontrolü.
