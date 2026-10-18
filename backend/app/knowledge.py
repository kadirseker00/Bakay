"""Kaynaklı hazır cevaplar; yalnız açıkça onaylanan, süresi dolmamış eşleşmeler."""
from __future__ import annotations

from datetime import date, datetime, timezone
import json
import logging
from pathlib import Path
import re
import sqlite3
import unicodedata
from uuid import uuid4, uuid5, NAMESPACE_URL
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing import Literal

from app.rag.source_links import _official_url


def today() -> date:
    return datetime.now(ZoneInfo('Asia/Bishkek')).date()


def question_key(question: str) -> str:
    # Anlamı değiştiren kelime, sayı ve işaretleri koru; bulanık eşleştirme yapma.
    text = unicodedata.normalize('NFC', question).translate(str.maketrans({'I': 'ı', 'İ': 'i'})).lower()
    return re.sub(r'\s+', ' ', text).strip().rstrip('?! .').strip()


class KnowledgeSource(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=300)
    url: str = Field(min_length=1, max_length=2000)
    snippet: str = Field(min_length=1, max_length=2000)

    @field_validator('url')
    @classmethod
    def official_source(cls, value: str) -> str:
        if not _official_url(value) or any(c.isspace() for c in value):
            raise ValueError('Kaynak, manas.edu.kg veya alt alanlarında bir HTTP/HTTPS adresi olmalıdır.')
        return value


class KnowledgeInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    question: str = Field(min_length=3, max_length=2000)
    variants: list[str] = Field(default_factory=list, max_length=30)
    answer: str = Field(default='', max_length=12000)
    sources: list[KnowledgeSource] = Field(default_factory=list, max_length=8)
    status: Literal['draft', 'published', 'archived'] = 'draft'
    reviewed_on: date | None = None
    valid_until: date | None = None
    revision: int | None = Field(default=None, ge=1)

    @field_validator('variants')
    @classmethod
    def validate_variants(cls, values: list[str]) -> list[str]:
        if any(not 3 <= len(value.strip()) <= 2000 for value in values):
            raise ValueError('Her soru varyantı 3–2000 karakter olmalıdır.')
        return [value.strip() for value in values]

    @model_validator(mode='after')
    def publishable(self):
        keys = [question_key(value) for value in [self.question, *self.variants]]
        if any(len(key) < 3 for key in keys) or len(set(keys)) != len(keys):
            raise ValueError('Sorular boş veya birbirinin tekrarı olamaz.')
        if self.status == 'published':
            if not self.answer or not self.sources or not self.reviewed_on or not self.valid_until:
                raise ValueError('Yayın için cevap, kaynak, kaynak kontrol tarihi ve geçerlilik tarihi gereklidir.')
            if self.reviewed_on > today() or self.valid_until < max(today(), self.reviewed_on):
                raise ValueError('Kontrol tarihi gelecekte, geçerlilik tarihi geçmişte olamaz.')
        return self


SCHEMA = '''
CREATE TABLE IF NOT EXISTS knowledge_answers (
 id TEXT PRIMARY KEY, payload TEXT NOT NULL, status TEXT NOT NULL,
 revision INTEGER NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
 updated_by TEXT NOT NULL, approved_by TEXT, approved_at TEXT,
 hits INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS knowledge_keys (
 question_key TEXT PRIMARY KEY, answer_id TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS knowledge_keys_answer ON knowledge_keys(answer_id);
CREATE TABLE IF NOT EXISTS knowledge_revisions (
 id INTEGER PRIMARY KEY, answer_id TEXT NOT NULL, revision INTEGER NOT NULL,
 ts TEXT NOT NULL, actor TEXT NOT NULL, snapshot TEXT NOT NULL);
'''


def connect(db_file: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_file, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def initialize(db_file: Path) -> None:
    db_file.parent.mkdir(parents=True, exist_ok=True)
    with connect(db_file) as connection:
        connection.executescript(SCHEMA)


def unpack(row) -> dict:
    result = dict(row)
    result.update(json.loads(result.pop('payload')))
    result['expired'] = bool(result.get('valid_until') and result['valid_until'] < today().isoformat())
    return result


def list_answers(db_file: Path) -> list[dict]:
    with connect(db_file) as connection:
        return [unpack(row) for row in connection.execute('SELECT * FROM knowledge_answers ORDER BY updated_at DESC, id')]


class Conflict(ValueError):
    pass


def save(db_file: Path, body: KnowledgeInput, actor: str, answer_id: str | None = None) -> dict:
    creating = answer_id is None
    answer_id = answer_id or uuid4().hex
    now = datetime.now(timezone.utc).isoformat()
    payload = body.model_dump(mode='json', exclude={'revision', 'status'})
    with connect(db_file) as connection:
        connection.execute('BEGIN IMMEDIATE')
        previous = connection.execute('SELECT * FROM knowledge_answers WHERE id=?', (answer_id,)).fetchone()
        if not creating and previous is None:
            raise KeyError(answer_id)
        if previous and body.revision != previous['revision']:
            raise Conflict('Bu cevap başka bir oturumda değişti. Listeyi yenileyip tekrar açın.')
        revision = previous['revision'] + 1 if previous else 1
        connection.execute('DELETE FROM knowledge_keys WHERE answer_id=?', (answer_id,))
        # Taslak ve arşiv kayıtları aynı sorunun yeniden kullanımını engellemez.
        if body.status == 'published':
            for question in [body.question, *body.variants]:
                key = question_key(question)
                existing = connection.execute('SELECT answer_id FROM knowledge_keys WHERE question_key=?', (key,)).fetchone()
                if existing:
                    raise Conflict('Bu soru veya varyant başka bir yayımlanmış cevaba bağlı. Önce o cevabı yayından kaldırın.')
                connection.execute('INSERT INTO knowledge_keys VALUES (?,?)', (key, answer_id))
        connection.execute('''INSERT INTO knowledge_answers
            (id,payload,status,revision,created_at,updated_at,updated_by,approved_by,approved_at)
            VALUES (?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
            payload=excluded.payload,status=excluded.status,revision=excluded.revision,
            updated_at=excluded.updated_at,updated_by=excluded.updated_by,
            approved_by=excluded.approved_by,approved_at=excluded.approved_at''',
            (answer_id, json.dumps(payload, ensure_ascii=False), body.status, revision,
             now, now, actor, actor if body.status == 'published' else None,
             now if body.status == 'published' else None))
        result = unpack(connection.execute('SELECT * FROM knowledge_answers WHERE id=?', (answer_id,)).fetchone())
        connection.execute('INSERT INTO knowledge_revisions (answer_id,revision,ts,actor,snapshot) VALUES (?,?,?,?,?)',
                           (answer_id, revision, now, actor, json.dumps(result, ensure_ascii=False)))
    return result


def lookup(db_file: Path, question: str) -> dict | None:
    if not db_file.exists():
        return None
    try:
        with connect(db_file) as connection:
            row = connection.execute('''SELECT a.* FROM knowledge_answers a JOIN knowledge_keys k ON k.answer_id=a.id
                WHERE k.question_key=? AND a.status='published' ''', (question_key(question),)).fetchone()
            if row is None:
                return None
            result = unpack(row)
            if result['expired'] or not result['approved_by']:
                return None
            connection.execute('UPDATE knowledge_answers SET hits=hits+1 WHERE id=?', (row['id'],))
            return result
    except sqlite3.OperationalError as exc:
        if 'no such table' not in str(exc):
            logging.getLogger(__name__).warning('Hazır cevap okunamadı; kaynak araması kullanılacak: %s', type(exc).__name__)
        return None


def seed_examples(db_file: Path, actor: str) -> list[dict]:
    """Örnekleri yalnız ilk kez, taslak halinde ekle; kullanıcı düzenlemelerini koru."""
    examples = json.loads(Path(__file__).with_name('knowledge_examples.json').read_text())
    with connect(db_file) as connection:
        connection.execute('BEGIN IMMEDIATE')
        for example in examples:
            body = KnowledgeInput(**example)
            answer_id = uuid5(NAMESPACE_URL, 'bakai:example:' + body.question).hex
            now = datetime.now(timezone.utc).isoformat()
            payload = json.dumps(body.model_dump(mode='json', exclude={'revision', 'status'}), ensure_ascii=False)
            inserted = connection.execute('''INSERT OR IGNORE INTO knowledge_answers
                (id,payload,status,revision,created_at,updated_at,updated_by) VALUES (?,?,'draft',1,?,?,?)''',
                (answer_id, payload, now, now, actor)).rowcount
            if inserted:
                snapshot = unpack(connection.execute('SELECT * FROM knowledge_answers WHERE id=?', (answer_id,)).fetchone())
                connection.execute('INSERT INTO knowledge_revisions (answer_id,revision,ts,actor,snapshot) VALUES (?,1,?,?,?)',
                                   (answer_id, now, actor, json.dumps(snapshot, ensure_ascii=False)))
    return list_answers(db_file)
