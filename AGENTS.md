# BAKAY — Codex Talimatları

BAKAY: KTMÜ için RAG tabanlı, kaynak gösteren Türkçe kurumsal bilgi asistanı.
Backend FastAPI (`backend/app/`), frontend Next.js 14 (`frontend/`), embedding
LaBSE, vektör DB ChromaDB (`data/chroma/`), LLM yerel Ollama (Qwen3.5 9B).
Turkish-Gemma 9B karşılaştırma modeli olarak korunur.

## Eş zamanlı çalışma (Claude ile)

Bu repoda Claude Code ajanı da çalışıyor. **Her oturumun başında**:

1. `collab/board.md` oku — Claude'un kilitlediği dosyalara dokunma.
2. `collab/to-codex.md` oku — mesajları `[x]` işaretle.
3. İş almadan panoya yaz; ayrıntılar: `collab/PROTOCOL.md`.

Commit mesajlarına `[codex]` öneki koy.

## Canlı yayın ve sürümleme

- Kullanıcı kuralı: canlıya çıkan her yeni committe sürüm numarasını artır.
  Varsayılan artış PATCH'tir (ör. `0.3.1` → `0.3.2`); kapsam gerektiriyorsa
  MINOR/MAJOR artır. Aynı commitin yeniden yayımlanması yeni sürüm gerektirmez.
- Yayın commitinde kökteki `VERSION`, `frontend/package.json` ve
  `frontend/package-lock.json` sürümlerini eşitle; `CHANGELOG.md` kaydını ekle.
- Canlıdaki sürümden daha yüksek bir numara kullan. Arayüzü yeni sürümle
  yeniden derle; yayın sonunda API ve arayüzün aynı yeni sürümü gösterdiğini
  doğrula. Sürüm artırılmadan yeni commitin canlı yayınını tamamlanmış sayma.

## Notlar

- İndeksleme: `backend/` içinden `.venv/bin/python -m app.ingest.run`
  (idempotent, upsert). Ham belgeler `data/raw/`, git'e girmez.
- Yol haritası: `ToDoTask.md`. Dil: kod yorumları ve dokümantasyon Türkçe.
