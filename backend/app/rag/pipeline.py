"""RAG orkestrasyonu: retrieve → prompt → generate → kaynak eşleme.

BAKAY'ın çekirdeği. Yanıt yalnızca geri çağrılan belge parçalarına dayanır;
model "bilmiyorsa" uydurmaması (halüsinasyon) için sıkı talimat verilir ve her
yanıt kaynaklarıyla birlikte döner (açıklanabilirlik / XAI).
"""
from __future__ import annotations

import re
import time

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
    store = get_store()
    llm = get_llm()

    hits = store.query(question, top_k=top_k or settings.top_k)

    if not hits:
        return ChatResponse(
            answer="Bu konuda elimdeki belgelerde bilgi bulamadım.",
            sources=[],
            latency_ms=int((time.perf_counter() - start) * 1000),
        )

    prompt = SYSTEM_PROMPT.format(
        context=_build_context(hits), question=question
    )
    text = _strip_reasoning(llm.generate(prompt))

    sources = [
        Source(document=h["document"], snippet=h["text"][:300], score=h["score"])
        for h in hits
    ]
    return ChatResponse(
        answer=text,
        sources=sources,
        latency_ms=int((time.perf_counter() - start) * 1000),
    )
