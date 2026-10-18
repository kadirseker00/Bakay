"""BAKAI FastAPI uygulaması (İP5).

Uçlar:
  GET  /health     — sağlık kontrolü + indeks durumu
  POST /chat       — RAG tabanlı soru-yanıt (kaynaklarıyla)
"""
from __future__ import annotations

import asyncio
import time
from contextlib import suppress
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from app import abuse, alerts, captcha, monitor_auth, monitoring, telemetry
from app.config import ROOT, settings
from app.rag import pipeline
from app.schemas import ChatRequest, ChatResponse, FeedbackRequest

@asynccontextmanager
async def lifespan(app: FastAPI):
    monitoring.initialize()
    app.state.abuse = abuse.AbuseGuard(settings)
    async def flush_blocks():
        while True:
            await asyncio.sleep(5)
            await run_in_threadpool(app.state.abuse.flush)
    flushing = asyncio.create_task(flush_blocks())
    try:
        yield
    finally:
        flushing.cancel()
        with suppress(asyncio.CancelledError):
            await flushing
        await run_in_threadpool(app.state.abuse.flush)


app = FastAPI(
    title="BAKAI API",
    description="KTMÜ için RAG tabanlı kurumsal bilgi asistanı",
    version=(ROOT / "VERSION").read_text(encoding="utf-8").strip(),
    lifespan=lifespan,
)

# Yönetici çerezi yalnız izin verilen arayüz kaynağından okunabilir.
app.add_middleware(abuse.AbuseMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.monitor_public_url] if settings.monitor_public_url else
                  ["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Retry-After"],
)


@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    started = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        if request.url.path.startswith('/monitor') or request.url.path == '/stats':
            response.headers['Cache-Control'] = 'no-store'
            response.headers['X-Content-Type-Options'] = 'nosniff'
        return response
    finally:
        # Sağlık yoklamaları ve panel yenilemeleri kullanıcı trafiğini şişirmez.
        if (request.url.path in ('/chat', '/feedback') and
                getattr(request.state, 'rate_admitted', False) and status not in (429, 413, 408, 415)):
            await run_in_threadpool(monitoring.record_event, request.method, request.url.path, status,
                                    int((time.perf_counter() - started) * 1000))


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
def chat(req: ChatRequest, request: Request) -> ChatResponse:
    captcha.require(request.app.state.abuse, request.state.rate_client, req.captcha_token)
    # Uvicorn güvenilir proxy bilgisini uygular; ham istemci başlıklarına güvenme.
    client_ip = request.client.host if request.client else None
    with request.app.state.abuse.processing(request.state.rate_client), telemetry.client_scope(client_ip):
        return pipeline.answer(req.question, top_k=req.top_k, history=req.history)


@app.post("/feedback")
def feedback(req: FeedbackRequest) -> dict:
    ok = telemetry.log_feedback(req.query_id, req.rating, req.comment, req.reason, req.respondent_name)
    return {"ok": ok}


@app.get("/stats")
def stats(_user: str = Depends(monitor_auth.require_monitor)) -> dict:
    """Loglanan sorgu/gecikme/geri bildirim özeti (izleme + makale için)."""
    return telemetry.stats()


class MonitorLogin(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=1024, repr=False)


@app.post('/monitor/login')
def monitor_login(body: MonitorLogin, request: Request, response: Response) -> dict:
    token = monitor_auth.authenticate(request, body.username, body.password)
    monitor_auth.set_session(response, request, token)
    return {'username': body.username}


@app.post('/monitor/logout')
def monitor_logout(request: Request, response: Response) -> dict:
    monitor_auth.check_origin(request)
    response.delete_cookie(monitor_auth.COOKIE, path='/')
    return {'ok': True}


@app.get('/monitor/metrics')
def monitor_metrics(request: Request, days: int = 7, _user: str = Depends(monitor_auth.require_monitor)) -> dict:
    if days not in (1, 7, 30):
        raise HTTPException(422, 'Dönem 1, 7 veya 30 gün olmalıdır.')
    result = monitoring.metrics(days)
    result['protection'] = request.app.state.abuse.snapshot(days)
    result['alerts'] = alerts.snapshot(settings)
    return result


@app.get('/monitor/queries/{query_id}')
def monitor_query(query_id: str, _user: str = Depends(monitor_auth.require_monitor)) -> dict:
    if len(query_id) != 32 or any(character not in '0123456789abcdef' for character in query_id):
        raise HTTPException(404, 'Sorgu bulunamadı.')
    detail = monitoring.query_detail(query_id)
    if detail is None:
        raise HTTPException(404, 'Sorgu bulunamadı.')
    return detail
