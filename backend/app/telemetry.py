"""Dahili telemetri / loglama katmanı (sıfır ek servis).

Her sorguyu iki yere yazar:
  1. SQLite (data/bakay.db) — sorgulanabilir; makale metrikleri ve geri bildirim.
  2. JSONL (data/logs/queries.jsonl) — ham, eklemeli (append) kayıt; yedek/analiz.

Loglanan metaveriler: soru, getirilen kaynaklar+skorlar, tam prompt, ham ve
temizlenmiş yanıt, sağlayıcı/model, embedding modeli, retrieval/generation/toplam
gecikme, zaman damgası. Geri bildirim (👍/👎) ayrı tabloda query_id ile ilişkili.

Loglama hiçbir zaman ana akışı düşürmemeli; hatalar yutulur (best-effort).
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import settings

_SCHEMA = """
CREATE TABLE IF NOT EXISTS queries (
    id              TEXT PRIMARY KEY,
    ts              TEXT NOT NULL,
    question        TEXT NOT NULL,
    provider        TEXT,
    model           TEXT,
    embedding_model TEXT,
    top_k           INTEGER,
    n_sources       INTEGER,
    retrieval_ms    INTEGER,
    generation_ms   INTEGER,
    total_ms        INTEGER,
    prompt          TEXT,
    raw_answer      TEXT,
    answer          TEXT,
    sources_json    TEXT
);
CREATE TABLE IF NOT EXISTS feedback (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    query_id  TEXT NOT NULL,
    rating    TEXT NOT NULL,           -- 'up' | 'down'
    comment   TEXT,
    ts        TEXT NOT NULL,
    FOREIGN KEY (query_id) REFERENCES queries(id)
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    settings.db_file.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.db_file)
    conn.executescript(_SCHEMA)
    return conn


def new_query_id() -> str:
    return uuid.uuid4().hex


def log_query(record: dict[str, Any]) -> None:
    """Bir sorgu kaydını SQLite + JSONL'e yazar (best-effort)."""
    record.setdefault("ts", _now())
    # 1) JSONL (ham)
    try:
        settings.log_path.mkdir(parents=True, exist_ok=True)
        with (settings.log_path / "queries.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass
    # 2) SQLite
    try:
        with _connect() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO queries
                   (id, ts, question, provider, model, embedding_model, top_k,
                    n_sources, retrieval_ms, generation_ms, total_ms,
                    prompt, raw_answer, answer, sources_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    record["id"],
                    record["ts"],
                    record["question"],
                    record.get("provider"),
                    record.get("model"),
                    record.get("embedding_model"),
                    record.get("top_k"),
                    record.get("n_sources"),
                    record.get("retrieval_ms"),
                    record.get("generation_ms"),
                    record.get("total_ms"),
                    record.get("prompt"),
                    record.get("raw_answer"),
                    record.get("answer"),
                    json.dumps(record.get("sources", []), ensure_ascii=False),
                ),
            )
    except Exception:
        pass


def log_feedback(query_id: str, rating: str, comment: str | None = None) -> bool:
    """Kullanıcı geri bildirimini kaydeder. Başarılıysa True."""
    try:
        with _connect() as conn:
            conn.execute(
                "INSERT INTO feedback (query_id, rating, comment, ts) VALUES (?,?,?,?)",
                (query_id, rating, comment, _now()),
            )
        return True
    except Exception:
        return False


def stats() -> dict[str, Any]:
    """Hızlı özet istatistik (makale/izleme için)."""
    try:
        with _connect() as conn:
            row = conn.execute(
                """SELECT COUNT(*), AVG(total_ms), AVG(retrieval_ms), AVG(generation_ms)
                   FROM queries"""
            ).fetchone()
            fb = conn.execute(
                "SELECT rating, COUNT(*) FROM feedback GROUP BY rating"
            ).fetchall()
        return {
            "total_queries": row[0] or 0,
            "avg_total_ms": round(row[1]) if row[1] else None,
            "avg_retrieval_ms": round(row[2]) if row[2] else None,
            "avg_generation_ms": round(row[3]) if row[3] else None,
            "feedback": {r: c for r, c in fb},
        }
    except Exception:
        return {"total_queries": 0}
