"""Panelden değiştirilen hız sınırları ve kalıcı değişiklik geçmişi."""
from __future__ import annotations

from datetime import datetime, timezone
import json

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Limits(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    rate_chat_per_minute: int = Field(ge=1, le=1000)
    rate_chat_per_hour: int = Field(ge=1, le=10000)
    rate_chat_global_per_minute: int = Field(ge=1, le=1000)
    rate_chat_global_per_day: int = Field(ge=1, le=100000)
    rate_chat_concurrent: int = Field(ge=1, le=16)
    rate_chat_concurrent_per_ip: int = Field(ge=1, le=16)

    @model_validator(mode='after')
    def coherent(self):
        if self.rate_chat_per_minute > self.rate_chat_per_hour:
            raise ValueError('IP başına dakika sınırı saat sınırını aşamaz.')
        if self.rate_chat_concurrent_per_ip > self.rate_chat_concurrent:
            raise ValueError('IP başına eşzamanlı sınır sistem toplamını aşamaz.')
        return self


class Update(Limits):
    revision: int = Field(ge=0)


class Conflict(ValueError):
    pass


SCHEMA = '''
CREATE TABLE IF NOT EXISTS rate_settings (
 id INTEGER PRIMARY KEY CHECK(id=1), payload TEXT NOT NULL,
 revision INTEGER NOT NULL, updated_at TEXT NOT NULL, updated_by TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS rate_settings_history (
 revision INTEGER PRIMARY KEY, payload TEXT NOT NULL,
 updated_at TEXT NOT NULL, updated_by TEXT NOT NULL);
'''


def defaults(config) -> dict:
    return {name: getattr(config, name) for name in Limits.model_fields}


def read(connection, config) -> dict:
    row = connection.execute('SELECT payload,revision,updated_at,updated_by FROM rate_settings WHERE id=1').fetchone()
    if row is None:
        return {'limits': defaults(config), 'revision': 0, 'updated_at': None, 'updated_by': None}
    # Bozuk veriyle korumayı sessizce gevşetme; istek 503 ile durur.
    limits = Limits.model_validate_json(row[0]).model_dump()
    return {'limits': limits, 'revision': row[1], 'updated_at': row[2], 'updated_by': row[3]}


def save(connection, config, body: Update, actor: str) -> dict:
    connection.execute('BEGIN IMMEDIATE')
    previous = read(connection, config)
    if previous['revision'] != body.revision:
        raise Conflict('Ayarlar başka bir oturumda değişti. Güncel ayarları yükleyip yeniden deneyin.')
    payload = body.model_dump_json(exclude={'revision'})
    revision = previous['revision'] + 1
    now = datetime.now(timezone.utc).isoformat()
    connection.execute('''INSERT INTO rate_settings VALUES (1,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
        payload=excluded.payload,revision=excluded.revision,updated_at=excluded.updated_at,updated_by=excluded.updated_by''',
                       (payload, revision, now, actor))
    connection.execute('INSERT INTO rate_settings_history VALUES (?,?,?,?)', (revision, payload, now, actor))
    return {'limits': json.loads(payload), 'revision': revision, 'updated_at': now, 'updated_by': actor}
