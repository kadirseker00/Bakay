"""BAKAY FastAPI uygulaması (İP5).

Uçlar:
  GET  /health     — sağlık kontrolü + indeks durumu
  POST /chat       — RAG tabanlı soru-yanıt (kaynaklarıyla)
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import telemetry
from app.config import ROOT, settings
from app.rag import pipeline
from app.schemas import ChatRequest, ChatResponse, FeedbackRequest

app = FastAPI(
    title="BAKAY API",
    description="KTMÜ için RAG tabanlı kurumsal bilgi asistanı",
    version=(ROOT / "VERSION").read_text(encoding="utf-8").strip(),
)

# Geliştirme aşamasında frontend'in (Next.js) erişebilmesi için CORS açık.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    from app.rag.vectorstore import get_store

    return {
        "status": "ok",
        "version": app.version,
        "llm_provider": settings.llm_provider,
        "llm_model": pipeline._model_name(),
        "embedding_model": settings.embedding_model,
        "indexed_chunks": get_store().count(),
    }


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    return pipeline.answer(req.question, top_k=req.top_k, history=req.history)


@app.post("/feedback")
def feedback(req: FeedbackRequest) -> dict:
    ok = telemetry.log_feedback(req.query_id, req.rating, req.comment)
    return {"ok": ok}


@app.get("/stats")
def stats() -> dict:
    """Loglanan sorgu/gecikme/geri bildirim özeti (izleme + makale için)."""
    return telemetry.stats()
