"""Ajansal RAG orkestrasyonu (referans diyagrama göre uyarlanmış).

Akış:  (1) sorgu yeniden yazma → (2) retrieval → (3) yönlendirme/yeterlilik
kapısı → (4) grounded üretim → (5) dayanak doğrulama → kullanıcıya yanıt.

Düğümler modüler ve flag'lerle açılır (bkz. config). Skor-tabanlı kapı bedavadır
(ekstra LLM yok) ve kapsam-dışı sorularda belge uydurmayı engeller. LLM-ağırlıklı
düğümler (yeniden yazma, doğrulama) varsayılan kapalıdır. Her düğüm kararı
telemetriye (JSONL) loglanır.

Yanıt yalnızca geri çağrılan belge parçalarına dayanır (anti-halüsinasyon) ve her
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

ROUTE_PROMPT = """Aşağıdaki soru, Kırgızistan-Türkiye Manas Üniversitesi'nin (KTMÜ) \
kurumsal/idari konularıyla (yönetmelik, kayıt, burs, sınav, akademik takvim, öğrenci \
işleri, bölümler, başvuru vb.) ilgili mi? Sadece 'EVET' veya 'HAYIR' yaz.

Soru: {question}
Karar:"""

REWRITE_PROMPT = """Aşağıdaki kullanıcı sorusunu, bir üniversitenin resmi belge \
arşivinde vektör arama için en uygun hâle getir. Eş anlamlıları ekle, kısaltmaları \
aç, gereksiz kelimeleri at. SADECE yeniden yazılmış soruyu tek satırda döndür.

Soru: {question}
Yeniden yazılmış:"""

# Soru kapsam dışı / yetersiz olduğunda (skor kapısı) verilen güvenli yanıt.
OUT_OF_SCOPE = (
    "Bu konuda KTMÜ belgelerinde yeterli bilgi bulamadım. Lütfen sorunuzu "
    "üniversite yönetmelikleri, kayıt, burs, sınav veya akademik takvim gibi "
    "kurumsal konularla ilgili ve daha açık biçimde sorun."
)


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


def _route_in_scope(question: str, llm) -> bool:
    """Düğüm 0: Soru KTMÜ kapsamında mı? (LLM). Hata olursa True (engelleme yapma)."""
    try:
        verdict = _strip_reasoning(llm.generate(ROUTE_PROMPT.format(question=question))).upper()
        return "HAYIR" not in verdict
    except Exception:
        return True


def _rewrite_query(question: str, llm) -> str:
    """Düğüm 1: Sorguyu retrieval için yeniden yazar (LLM). Hata olursa orijinali döner."""
    try:
        rewritten = _strip_reasoning(llm.generate(REWRITE_PROMPT.format(question=question)))
        # İlk satırı al, makul uzunlukta değilse orijinale dön
        rewritten = rewritten.splitlines()[0].strip() if rewritten else ""
        return rewritten if 3 <= len(rewritten) <= 300 else question
    except Exception:
        return question


def _verify_grounding(answer_text: str, context: str, llm) -> bool:
    """Düğüm 5: Yanıtın kaynaklara dayandığını LLM ile doğrular. Hata olursa True (engelleme)."""
    prompt = (
        "Aşağıdaki YANIT, yalnızca verilen KAYNAKLAR'daki bilgilere mi dayanıyor? "
        "Sadece 'EVET' veya 'HAYIR' yaz.\n\n"
        f"KAYNAKLAR:\n{context}\n\nYANIT:\n{answer_text}\n\nKarar:"
    )
    try:
        verdict = _strip_reasoning(llm.generate(prompt)).upper()
        return "HAYIR" not in verdict
    except Exception:
        return True


def answer(question: str, top_k: int | None = None) -> ChatResponse:
    start = time.perf_counter()
    qid = telemetry.new_query_id()
    k = top_k or settings.top_k
    store = get_store()
    llm = get_llm()
    steps: list[str] = []

    # --- Düğüm 0: Kapsam yönlendirmesi (opsiyonel, LLM) ---
    if settings.agent_route and not _route_in_scope(question, llm):
        steps.append("route:out_of_scope")
        total_ms = int((time.perf_counter() - start) * 1000)
        _log(qid, question, k, sources=[], retrieval_ms=0, generation_ms=0,
             total_ms=total_ms, prompt=None, raw=None, text=OUT_OF_SCOPE,
             route="out_of_scope", top_score=0.0, rewritten=None, steps=steps)
        return ChatResponse(query_id=qid, answer=OUT_OF_SCOPE, sources=[], latency_ms=total_ms)

    # --- Düğüm 1: Sorgu yeniden yazma (opsiyonel) ---
    search_query = question
    rewritten_query = None
    if settings.agent_rewrite:
        search_query = _rewrite_query(question, llm)
        rewritten_query = search_query
        steps.append("rewrite")

    # --- Düğüm 2: Retrieval ---
    t0 = time.perf_counter()
    hits = store.query(search_query, top_k=k)
    retrieval_ms = int((time.perf_counter() - t0) * 1000)
    top_score = hits[0]["score"] if hits else 0.0

    # --- Düğüm 3: Yönlendirme / yeterlilik kapısı (bedava, ekstra LLM yok) ---
    if not hits or top_score < settings.score_threshold:
        steps.append("gate:out_of_scope")
        total_ms = int((time.perf_counter() - start) * 1000)
        _log(qid, question, k, sources=[], retrieval_ms=retrieval_ms,
             generation_ms=0, total_ms=total_ms, prompt=None, raw=None,
             text=OUT_OF_SCOPE, route="out_of_scope", top_score=top_score,
             rewritten=rewritten_query, steps=steps)
        return ChatResponse(query_id=qid, answer=OUT_OF_SCOPE, sources=[], latency_ms=total_ms)

    steps.append("gate:in_scope")

    # --- Düğüm 4: Grounded üretim ---
    context = _build_context(hits)
    prompt = SYSTEM_PROMPT.format(context=context, question=question)
    t1 = time.perf_counter()
    raw = llm.generate(prompt)
    generation_ms = int((time.perf_counter() - t1) * 1000)
    text = _strip_reasoning(raw)
    steps.append("generate")

    # --- Düğüm 5: Dayanak doğrulama (opsiyonel) ---
    grounded = True
    if settings.agent_verify:
        grounded = _verify_grounding(text, context, llm)
        steps.append(f"verify:{'ok' if grounded else 'ungrounded'}")
        if not grounded:
            text += "\n\n_(Not: Bu yanıtın kaynak belgelerle tam örtüştüğü doğrulanamadı.)_"

    sources = [
        Source(document=h["document"], snippet=h["text"][:300], score=h["score"])
        for h in hits
    ]
    total_ms = int((time.perf_counter() - start) * 1000)
    _log(qid, question, k, sources=sources, retrieval_ms=retrieval_ms,
         generation_ms=generation_ms, total_ms=total_ms, prompt=prompt, raw=raw,
         text=text, route="answered", top_score=top_score,
         rewritten=rewritten_query, steps=steps)

    return ChatResponse(query_id=qid, answer=text, sources=sources, latency_ms=total_ms)


def _log(qid, question, k, *, sources, retrieval_ms, generation_ms, total_ms,
         prompt, raw, text, route, top_score, rewritten, steps) -> None:
    telemetry.log_query({
        "id": qid, "question": question, "provider": settings.llm_provider,
        "model": _model_name(), "embedding_model": settings.embedding_model,
        "top_k": k, "n_sources": len(sources), "retrieval_ms": retrieval_ms,
        "generation_ms": generation_ms, "total_ms": total_ms, "prompt": prompt,
        "raw_answer": raw, "answer": text,
        "sources": [s.model_dump() for s in sources],
        # ajansal metaveri (JSONL'e işlenir)
        "route": route, "top_score": round(top_score, 4),
        "rewritten_query": rewritten, "steps": steps,
    })


def _model_name() -> str:
    return (
        settings.ollama_model
        if settings.llm_provider == "ollama"
        else settings.gemini_model
    )
