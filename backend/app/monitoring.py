"""Kalıcı izleme kayıtları, gerçek API sayaçları ve yönetici özetleri."""
from __future__ import annotations

import json
import math
import os
import shutil
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from app.config import ROOT, settings
from app.telemetry import _SCHEMA as QUERY_SCHEMA, current_query_id

STARTED = time.monotonic()
PRICING_VERSION = "anthropic-2026-10-12"
PRICING_URL = "https://platform.claude.com/docs/en/about-claude/pricing"
SCHEMA = """
CREATE INDEX IF NOT EXISTS queries_ts ON queries(ts);
CREATE INDEX IF NOT EXISTS feedback_ts ON feedback(ts);
CREATE TABLE IF NOT EXISTS monitor_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS monitor_events (
 id INTEGER PRIMARY KEY, ts TEXT NOT NULL, method TEXT NOT NULL,
 path TEXT NOT NULL, status INTEGER NOT NULL, duration_ms INTEGER NOT NULL);
CREATE INDEX IF NOT EXISTS monitor_events_ts ON monitor_events(ts);
CREATE TABLE IF NOT EXISTS monitor_samples (
 id INTEGER PRIMARY KEY, ts TEXT NOT NULL, data TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS monitor_samples_ts ON monitor_samples(ts);
CREATE TABLE IF NOT EXISTS llm_calls (
 id INTEGER PRIMARY KEY, ts TEXT NOT NULL, query_id TEXT NOT NULL,
 model TEXT NOT NULL, status TEXT NOT NULL, latency_ms INTEGER NOT NULL,
 input_tokens INTEGER, output_tokens INTEGER, cache_read_tokens INTEGER,
 cache_write_tokens INTEGER, cost_usd REAL, pricing_version TEXT,
 usage_json TEXT, error_type TEXT);
CREATE INDEX IF NOT EXISTS llm_calls_ts ON llm_calls(ts);
CREATE INDEX IF NOT EXISTS llm_calls_query_id ON llm_calls(query_id);
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(settings.db_file, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def initialize() -> None:
    settings.db_file.parent.mkdir(parents=True, exist_ok=True)
    with connect() as connection:
        connection.executescript(QUERY_SCHEMA + SCHEMA)
        connection.execute("INSERT OR IGNORE INTO monitor_meta VALUES ('metering_since', ?)", (utc_now(),))


def _integer(value) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def cost_estimate(model: str, usage: dict | None) -> float | None:
    """12 Ekim tarifesi; çıktı sayacı düşünme tokenlarını da kapsar, fatura değildir."""
    if not isinstance(usage, dict):
        return None
    incoming, outgoing = _integer(usage.get("input_tokens")), _integer(usage.get("output_tokens"))
    reads = _integer(usage.get("cache_read_input_tokens", 0))
    writes = _integer(usage.get("cache_creation_input_tokens", 0))
    if any(value is None for value in (incoming, outgoing, reads, writes)):
        return None
    cache = usage.get("cache_creation") or {}
    if not isinstance(cache, dict):
        return None
    one_hour = _integer(cache.get("ephemeral_1h_input_tokens", 0))
    if one_hour is None or one_hour > writes:
        return None
    five_minutes = writes - one_hour
    if model == "claude-haiku-5-5" or model.startswith("claude-haiku-5-5-"):
        rates = (0.1, 0.5, 0.01, 0.125, 0.2)
        if incoming + reads + writes > 100000:
            rates = (0.5, 2.5, 0.05, 0.625, 1.0)
    elif model == "claude-sonnet-5-5" or model.startswith("claude-sonnet-5-5-"):
        rates = (2.0, 10.0, 0.1, 2.5, 4.0)
    else:
        return None
    return round(sum(tokens * rate for tokens, rate in zip(
        (incoming, outgoing, reads, five_minutes, one_hour), rates
    )) / 1_000_000, 10)


def record_llm_call(model: str, status: str, elapsed_ms: int, usage: dict | None = None,
                    error_type: str | None = None) -> None:
    query_id = current_query_id()
    if query_id is None:
        return  # Ayrı deney araçlarını canlı uygulamanın faturası gibi sayma.
    try:
        counters = usage if isinstance(usage, dict) else {}
        with connect() as connection:
            connection.execute("""INSERT INTO llm_calls
              (ts,query_id,model,status,latency_ms,input_tokens,output_tokens,
               cache_read_tokens,cache_write_tokens,cost_usd,pricing_version,usage_json,error_type)
              VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
                utc_now(), query_id, model, status, elapsed_ms,
                _integer(counters.get("input_tokens")), _integer(counters.get("output_tokens")),
                _integer(counters.get("cache_read_input_tokens", 0)) if usage is not None else None,
                _integer(counters.get("cache_creation_input_tokens", 0)) if usage is not None else None,
                cost_estimate(model, usage), PRICING_VERSION,
                json.dumps(counters) if usage is not None else None, error_type,
            ))
    except (OSError, sqlite3.Error):
        pass  # İzleme arızası kullanıcı yanıtını düşürmez.


def record_event(method: str, path: str, status: int, duration_ms: int) -> None:
    try:
        with connect() as connection:
            connection.execute("INSERT INTO monitor_events (ts,method,path,status,duration_ms) VALUES (?,?,?,?,?)",
                               (utc_now(), method, path, status, duration_ms))
    except (OSError, sqlite3.Error):
        pass


def resources() -> dict:
    memory = {}
    try:
        for line in Path('/proc/meminfo').read_text().splitlines():
            key, value = line.split(':', 1)
            if key in ('MemTotal', 'MemAvailable'):
                memory[key] = int(value.split()[0]) * 1024
    except (OSError, ValueError):
        pass
    disk = shutil.disk_usage(ROOT)
    return {
        'memory_total_bytes': memory.get('MemTotal'),
        'memory_used_bytes': memory.get('MemTotal', 0) - memory.get('MemAvailable', 0) if memory else None,
        'disk_total_bytes': disk.total, 'disk_used_bytes': disk.used,
        'disk_free_bytes': disk.free, 'load_1m': round(os.getloadavg()[0], 2),
        'cpu_count': os.cpu_count(),
    }


def save_sample(data: dict) -> None:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=31)).isoformat()
    with connect() as connection:
        connection.execute('INSERT INTO monitor_samples (ts,data) VALUES (?,?)', (utc_now(), json.dumps(data)))
        connection.execute('DELETE FROM monitor_samples WHERE ts < ?', (cutoff,))
        connection.execute('DELETE FROM monitor_events WHERE ts < ?', (cutoff,))


def percentile(values: list, fraction: float) -> int | None:
    ordered = sorted(value for value in values if value is not None)
    if not ordered:
        return None
    rank = (len(ordered) - 1) * fraction
    low, high = math.floor(rank), math.ceil(rank)
    return round(ordered[low] + (ordered[high] - ordered[low]) * (rank - low))


def _model() -> str:
    return {'anthropic': settings.anthropic_model, 'ollama': settings.ollama_model,
            'gemini': settings.gemini_model}.get(settings.llm_provider.lower(), settings.llm_provider)


def _query_cost(connection, query_id: str, ts: str, metering_since: str) -> dict:
    row = connection.execute('''SELECT COUNT(*) count, SUM(cost_usd) cost,
        SUM(CASE WHEN cost_usd IS NULL THEN 1 ELSE 0 END) unknown FROM llm_calls WHERE query_id=?''', (query_id,)).fetchone()
    known = (row['count'] > 0 and not row['unknown']) or (row['count'] == 0 and ts >= metering_since)
    return {'llm_calls': row['count'], 'cost_usd': round(row['cost'] or 0, 8) if known else None}


def metrics(days: int) -> dict:
    local_now = datetime.now(ZoneInfo('Asia/Bishkek'))
    beginning = (local_now - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
    cutoff = beginning.astimezone(timezone.utc).isoformat()
    with connect() as connection:
        queries = connection.execute('''SELECT id,ts,question,model,n_sources,total_ms,retrieval_ms,generation_ms
            FROM queries WHERE ts>=? ORDER BY ts DESC''', (cutoff,)).fetchall()
        events = connection.execute('SELECT status,path,ts FROM monitor_events WHERE ts>=? ORDER BY id', (cutoff,)).fetchall()
        calls = connection.execute('SELECT * FROM llm_calls WHERE ts>=?', (cutoff,)).fetchall()
        feedback = connection.execute('''SELECT rating,COUNT(*) count FROM feedback
            WHERE ts>=? GROUP BY rating''', (cutoff,)).fetchall()
        latest = connection.execute('SELECT ts,data FROM monitor_samples ORDER BY id DESC LIMIT 1').fetchone()
        samples = connection.execute('SELECT ts,data FROM monitor_samples WHERE ts>=? ORDER BY id', (cutoff,)).fetchall()
        metering_since = connection.execute("SELECT value FROM monitor_meta WHERE key='metering_since'").fetchone()['value']
        recent = []
        for row in queries[:20]:
            item = dict(row)
            item.update(_query_cost(connection, row['id'], row['ts'], metering_since))
            if not settings.monitor_show_query_details:
                item.pop('question')
            else:
                item['question'] = item['question'][:400]
            recent.append(item)
        legacy = connection.execute('''SELECT COUNT(*) FROM queries q WHERE q.ts>=? AND q.ts<?
            AND NOT EXISTS (SELECT 1 FROM llm_calls c WHERE c.query_id=q.id)''', (cutoff, metering_since)).fetchone()[0]
    daily = {}
    for offset in range(days):
        key = (beginning + timedelta(days=offset)).date().isoformat()
        daily[key] = {'date': key, 'queries': 0, 'errors': 0, 'cost_usd': 0.0}
    def day_key(ts):
        return datetime.fromisoformat(ts).astimezone(ZoneInfo('Asia/Bishkek')).date().isoformat()
    for row in queries:
        daily[day_key(row['ts'])]['queries'] += 1
    for row in events:
        if row['status'] >= 400:
            daily[day_key(row['ts'])]['errors'] += 1
    for row in calls:
        daily[day_key(row['ts'])]['cost_usd'] += row['cost_usd'] or 0
    for item in daily.values():
        item['cost_usd'] = round(item['cost_usd'], 8)
    healthy_samples = sum(all(component.get('ok') for component in json.loads(row['data'])['checks'].values()) for row in samples)
    sample = {'checked_at': latest['ts'], **json.loads(latest['data'])} if latest else None
    by_model = {}
    for row in calls:
        item = by_model.setdefault(row['model'], {'model': row['model'], 'calls': 0, 'priced_calls': 0, 'cost_usd': 0.0})
        item['calls'] += 1
        item['priced_calls'] += row['cost_usd'] is not None
        item['cost_usd'] += row['cost_usd'] or 0
    error_rows = [dict(row) for row in reversed(events) if row['status'] >= 400][:10]
    return {
        'generated_at': utc_now(), 'days': days, 'timezone': 'Asia/Bishkek',
        'active_model': _model(), 'embedding_model': settings.embedding_model,
        'version': (ROOT / 'VERSION').read_text().strip(), 'backend_uptime_seconds': round(time.monotonic() - STARTED),
        'summary': {
            'queries': len(queries), 'requests': len(events),
            'errors': sum(row['status'] >= 400 for row in events),
            'server_errors': sum(row['status'] >= 500 for row in events),
            'median_ms': percentile([row['total_ms'] for row in queries], 0.5),
            'p95_ms': percentile([row['total_ms'] for row in queries], 0.95),
            'avg_retrieval_ms': round(sum(row['retrieval_ms'] or 0 for row in queries) / len(queries)) if queries else None,
            'avg_generation_ms': round(sum(row['generation_ms'] or 0 for row in queries) / len(queries)) if queries else None,
            'sourced_queries': sum((row['n_sources'] or 0) > 0 for row in queries),
            'feedback': {row['rating']: row['count'] for row in feedback},
            'probe_availability_percent': round(healthy_samples * 100 / len(samples), 2) if samples else None,
            'probe_count': len(samples),
        },
        'cost': {
            'estimated_usd': round(sum(row['cost_usd'] or 0 for row in calls), 8),
            'input_tokens': sum(row['input_tokens'] or 0 for row in calls),
            'output_tokens': sum(row['output_tokens'] or 0 for row in calls),
            'cache_tokens': sum((row['cache_read_tokens'] or 0) + (row['cache_write_tokens'] or 0) for row in calls),
            'priced_calls': sum(row['cost_usd'] is not None for row in calls),
            'unknown_calls': sum(row['cost_usd'] is None for row in calls),
            'unmetered_queries': legacy, 'metering_since': metering_since,
            'pricing_version': PRICING_VERSION, 'pricing_url': PRICING_URL,
            'by_model': [{**item, 'cost_usd': round(item['cost_usd'], 8) if item['priced_calls'] else None} for item in by_model.values()],
        },
        'resources': resources(), 'sample': sample, 'daily': list(daily.values()),
        'recent_queries': recent, 'recent_errors': error_rows,
        'details_enabled': settings.monitor_show_query_details,
    }


def query_detail(query_id: str) -> dict | None:
    if not settings.monitor_show_query_details:
        return None
    with connect() as connection:
        row = connection.execute('''SELECT id,ts,question,answer,model,n_sources,total_ms,
            retrieval_ms,generation_ms,sources_json FROM queries WHERE id=?''', (query_id,)).fetchone()
        if row is None:
            return None
        result = dict(row)
        result['sources'] = json.loads(result.pop('sources_json') or '[]')
        metering_since = connection.execute("SELECT value FROM monitor_meta WHERE key='metering_since'").fetchone()['value']
        result.update(_query_cost(connection, row['id'], row['ts'], metering_since))
        result['calls'] = [dict(call) for call in connection.execute('''SELECT model,status,input_tokens,output_tokens,
            cost_usd,latency_ms,error_type FROM llm_calls WHERE query_id=? ORDER BY id''', (query_id,))]
        return result
