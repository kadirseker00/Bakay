"""BAKAI FastAPI uygulaması (İP5).

Uçlar:
  GET  /health     — sağlık kontrolü + indeks durumu
  POST /chat       — RAG tabanlı soru-yanıt (kaynaklarıyla)
"""
from __future__ import annotations

import asyncio
import json
import logging
from queue import Empty, Queue
from threading import Event, Thread
import time
from contextlib import suppress
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool
from starlette.responses import StreamingResponse

from app import abuse, alerts, captcha, golden, knowledge, monitor_auth, monitoring, rate_limits, telemetry
from app.config import ROOT, settings
from app.rag import pipeline
from app.rag.progress import progress_scope
from app.rag.source_links import resolve_source_url
from app.schemas import ChatRequest, ChatResponse, FeedbackRequest

@asynccontextmanager
async def lifespan(app: FastAPI):
    monitoring.initialize()
    knowledge.initialize(settings.db_file)
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
                getattr(request.state, 'rate_admitted', False) and
                not getattr(request.state, 'chat_stream', False) and status not in (429, 413, 408, 415)):
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
def chat(req: ChatRequest, request: Request) -> ChatResponse | StreamingResponse:
    captcha.require(request.app.state.abuse, request.state.rate_client, req.captcha_token)
    # Uvicorn güvenilir proxy bilgisini uygular; ham istemci başlıklarına güvenme.
    client_ip = request.client.host if request.client else None
    if 'text/event-stream' in request.headers.get('accept', ''):
        return stream_chat(req, request, client_ip)
    with request.app.state.abuse.processing(request.state.rate_client), telemetry.client_scope(client_ip, req.history):
        return pipeline.answer(req.question, top_k=req.top_k, history=req.history)


def stream_chat(req: ChatRequest, request: Request, client_ip: str | None) -> StreamingResponse:
    started = time.perf_counter()
    # Kabul hataları başlıklar gönderilmeden normal HTTP 429/503 olarak dönmeli.
    processing = request.app.state.abuse.processing(request.state.rate_client)
    processing.__enter__()
    events: Queue[tuple[str, dict]] = Queue()
    disconnected = Event()
    request.state.chat_stream = True

    def send(event: str, data: dict):
        if not disconnected.is_set():
            events.put((event, data))

    def work():
        try:
            with telemetry.client_scope(client_ip, req.history), progress_scope(lambda data: send('status', data)):
                result = pipeline.answer(req.question, top_k=req.top_k, history=req.history)
                data = result.model_dump()
        except Exception:
            logging.getLogger(__name__).exception('Canlı sohbet yanıtı hazırlanamadı')
            event, data = 'error', {'detail': 'Yanıt hazırlanırken bir sorun oluştu. Lütfen yeniden deneyin.'}
        else:
            event = 'result'
        finally:
            # Bağlantı kesilse de çalışan iş bitene kadar eşzamanlı iş kotasını tut.
            processing.__exit__(None, None, None)
        # Akış başladıktan sonraki model hataları da panelde görünmeli.
        monitoring.record_event('POST', '/chat', 500 if event == 'error' else 200,
                                int((time.perf_counter() - started) * 1000))
        send(event, data)

    def body():
        try:
            while True:
                try:
                    event, data = events.get(timeout=5)
                except Empty:
                    yield ': keep-alive\n\n'
                    continue
                yield f'event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n'
                if event in ('result', 'error'):
                    return
        finally:
            disconnected.set()

    try:
        Thread(target=work, name='chat-stream', daemon=True).start()
    except Exception:
        request.state.chat_stream = False
        processing.__exit__(None, None, None)
        raise
    return StreamingResponse(body(), media_type='text/event-stream', headers={
        'Cache-Control': 'no-cache, no-store, no-transform', 'X-Accel-Buffering': 'no',
    })


@app.post("/feedback")
def feedback(req: FeedbackRequest) -> dict:
    ok = telemetry.log_feedback(**req.model_dump())
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
    for source in detail['sources']:
        source['url'] = resolve_source_url(source['document'])
    return detail


@app.get('/monitor/knowledge')
def knowledge_list(_user: str = Depends(monitor_auth.require_monitor)) -> dict:
    return {'items': knowledge.list_answers(settings.db_file)}


def knowledge_writer(request: Request, user: str = Depends(monitor_auth.require_monitor)) -> str:
    monitor_auth.check_origin(request)
    return user


@app.get('/monitor/golden')
def golden_candidates(_user: str = Depends(monitor_auth.require_monitor)) -> dict:
    return {'items': golden.list_candidates(settings.db_file)}


@app.get('/monitor/golden/export')
def golden_export(_user: str = Depends(monitor_auth.require_monitor)) -> Response:
    return Response(golden.export_dataset(settings.db_file), media_type='application/x-ndjson',
                    headers={'Content-Disposition': 'attachment; filename="bakai-golden-development.jsonl"'})


@app.get('/monitor/rate-limits')
def rate_limit_settings(request: Request, _user: str = Depends(monitor_auth.require_monitor)) -> dict:
    return request.app.state.abuse.limit_settings()


@app.put('/monitor/rate-limits')
def rate_limit_update(body: rate_limits.Update, request: Request,
                      user: str = Depends(knowledge_writer)) -> dict:
    try:
        return request.app.state.abuse.update_limits(body, user)
    except rate_limits.Conflict as exc:
        raise HTTPException(409, str(exc)) from None


@app.post('/monitor/knowledge/examples')
def knowledge_examples(_user: str = Depends(knowledge_writer)) -> dict:
    return {'items': knowledge.seed_examples(settings.db_file, _user)}


@app.post('/monitor/knowledge', status_code=201)
def knowledge_create(body: knowledge.KnowledgeInput, _user: str = Depends(knowledge_writer)) -> dict:
    try:
        return knowledge.save(settings.db_file, body, _user)
    except knowledge.Conflict as exc:
        raise HTTPException(409, str(exc)) from None


@app.put('/monitor/knowledge/{answer_id}')
def knowledge_update(answer_id: str, body: knowledge.KnowledgeInput,
                     _user: str = Depends(knowledge_writer)) -> dict:
    try:
        return knowledge.save(settings.db_file, body, _user, answer_id)
    except KeyError:
        raise HTTPException(404, 'Hazır cevap bulunamadı.') from None
    except knowledge.Conflict as exc:
        raise HTTPException(409, str(exc)) from None
