"""RAG orkestrasyonu: retrieve → prompt → generate → kaynak eşleme.

BAKAY'ın çekirdeği. Yanıt yalnızca geri çağrılan belge parçalarına dayanır;
model "bilmiyorsa" uydurmaması (halüsinasyon) için sıkı talimat verilir ve her
yanıt kaynaklarıyla birlikte döner (açıklanabilirlik / XAI).
"""
from __future__ import annotations

import re
import time

from app import telemetry
from app.config import settings
from app.rag.llm import get_llm
from app.rag.vectorstore import get_store
from app.schemas import ChatResponse, Source

SYSTEM_PROMPT = """Sen BAKAY'sın: Kırgızistan-Türkiye Manas Üniversitesi'nin (KTMÜ) \
resmi belgelerine dayanarak yanıt veren kurumsal bilgi asistanısın.

Kurallar:
- YALNIZCA aşağıda verilen KAYNAK parçalarındaki bilgilere dayan.
- Kaynaklarda yanıt yoksa, açıkça "Bu konuda elimdeki belgelerde bilgi bulamadım." de. UYDURMA.
- Türkçe, açık ve resmi bir dille yanıtla.
- İlgili olduğunda hangi belgeye dayandığını belirt.
- ÖNEMLİ: Akıl yürütme adımlarını veya <think> bloğu YAZMA. Düşünme sürecini gösterme;
  doğrudan, öz ve net bir yanıt ver.

KAYNAKLAR:
{context}

SORU: {question}

YANIT:"""


def _strip_reasoning(text: str) -> str:
    """Reasoning modellerinin <think>...</think> bloğunu son yanıttan çıkarır."""
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    # Kapanmamış <think> (model kesilirse) — etiket sonrasını al
    if "<think>" in cleaned.lower():
        cleaned = re.split(r"</think>", cleaned, flags=re.IGNORECASE)[-1]
    return cleaned.strip()


def _build_context(hits: list[dict]) -> str:
    blocks = []
    for i, h in enumerate(hits, 1):
        blocks.append(f"[{i}] ({h['document']})\n{h['text']}")
    return "\n\n".join(blocks)


def answer(question: str, top_k: int | None = None) -> ChatResponse:
    start = time.perf_counter()
    qid = telemetry.new_query_id()
    k = top_k or settings.top_k
    store = get_store()
    llm = get_llm()

    # --- Retrieval ---
    t0 = time.perf_counter()
    hits = store.query(question, top_k=k)
    retrieval_ms = int((time.perf_counter() - t0) * 1000)

    if not hits:
        total_ms = int((time.perf_counter() - start) * 1000)
        no_info = "Bu konuda elimdeki belgelerde bilgi bulamadım."
        telemetry.log_query({
            "id": qid, "question": question, "provider": settings.llm_provider,
            "model": _model_name(), "embedding_model": settings.embedding_model,
            "top_k": k, "n_sources": 0, "retrieval_ms": retrieval_ms,
            "generation_ms": 0, "total_ms": total_ms, "prompt": None,
            "raw_answer": None, "answer": no_info, "sources": [],
        })
        return ChatResponse(query_id=qid, answer=no_info, sources=[], latency_ms=total_ms)

    # --- Generation ---
    prompt = SYSTEM_PROMPT.format(context=_build_context(hits), question=question)
    t1 = time.perf_counter()
    raw = llm.generate(prompt)
    generation_ms = int((time.perf_counter() - t1) * 1000)
    text = _strip_reasoning(raw)

    sources = [
        Source(document=h["document"], snippet=h["text"][:300], score=h["score"])
        for h in hits
    ]
    total_ms = int((time.perf_counter() - start) * 1000)

    telemetry.log_query({
        "id": qid, "question": question, "provider": settings.llm_provider,
        "model": _model_name(), "embedding_model": settings.embedding_model,
        "top_k": k, "n_sources": len(sources), "retrieval_ms": retrieval_ms,
        "generation_ms": generation_ms, "total_ms": total_ms, "prompt": prompt,
        "raw_answer": raw, "answer": text,
        "sources": [s.model_dump() for s in sources],
    })

    return ChatResponse(
        query_id=qid, answer=text, sources=sources, latency_ms=total_ms
    )


def _model_name() -> str:
    return (
        settings.ollama_model
        if settings.llm_provider == "ollama"
        else settings.gemini_model
    )
