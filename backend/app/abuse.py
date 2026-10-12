"""Kalıcı hız kotaları, çalışan iş sınırı ve sınırlı ASGI gövde okuma."""
from __future__ import annotations

import asyncio
import hashlib
import hmac
import ipaddress
import math
import secrets
import sqlite3
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse

SCHEMA = """
CREATE TABLE IF NOT EXISTS rate_hits (kind TEXT NOT NULL, client TEXT NOT NULL, ts REAL NOT NULL);
CREATE INDEX IF NOT EXISTS rate_hits_kind_ts ON rate_hits(kind,ts);
CREATE INDEX IF NOT EXISTS rate_hits_client ON rate_hits(kind,client,ts);
CREATE TABLE IF NOT EXISTS rate_blocks (
 minute TEXT NOT NULL, kind TEXT NOT NULL, reason TEXT NOT NULL, count INTEGER NOT NULL,
 PRIMARY KEY(minute,kind,reason));
CREATE TABLE IF NOT EXISTS captcha_clients (
 client TEXT PRIMARY KEY, blocked INTEGER NOT NULL, updated_at REAL NOT NULL,
 required_until REAL NOT NULL DEFAULT 0, passed_until REAL NOT NULL DEFAULT 0);
"""
PATHS = {'/chat': 'chat', '/feedback': 'feedback', '/monitor/login': 'login'}


class Denied(Exception):
    def __init__(self, reason: str, detail: str, retry: int = 10, status: int = 429):
        self.reason, self.detail, self.retry, self.status = reason, detail, retry, status


class AbuseGuard:
    def __init__(self, config, clock=None):
        self.config = config
        self.clock = clock or time.time
        # Panelin kalıcı sırrından ayrı amaçlı HMAC; düz IP kaydedilmez.
        self.salt = hmac.digest((config.monitor_session_secret or secrets.token_hex(32)).encode(),
                               b'BAKAI-rate-client-v1', 'sha256')
        self.lock = threading.Lock()
        self.active = 0
        self.clients: dict[str, int] = {}
        self.readers = 0
        self.pending: dict[tuple, int] = {}
        config.db_file.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.executescript(SCHEMA)

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.config.db_file, timeout=2)
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def client_key(self, address: str) -> str:
        try:
            ip = ipaddress.ip_address(address)
            if isinstance(ip, ipaddress.IPv6Address):
                address = str(ip.ipv4_mapped or ipaddress.ip_network(f'{ip}/64', strict=False))
            else:
                address = str(ip)
        except ValueError:
            pass
        return hmac.new(self.salt, address.encode(), hashlib.sha256).hexdigest()

    def policies(self, kind):
        c = self.config
        return {
            'chat': [(True, 60, c.rate_chat_per_minute, 'ip_minute'),
                     (True, 3600, c.rate_chat_per_hour, 'ip_hour'),
                     (False, 60, c.rate_chat_global_per_minute, 'global_minute')],
            'generation': [(False, 86400, c.rate_chat_global_per_day, 'global_day')],
            'feedback': [(True, 60, 30, 'ip_minute'), (False, 60, 120, 'global_minute')],
            'login': [(True, 300, 5, 'login_attempts'), (False, 60, 30, 'global_minute')],
        }[kind]

    def admit(self, kind: str, client: str):
        now = self.clock()
        denied = None
        try:
            with self.connect() as connection:
                # Kontrol + yazma aynı işlemde; eşzamanlı istekler kotayı aşamaz.
                connection.execute('BEGIN IMMEDIATE')
                connection.execute('DELETE FROM captcha_clients WHERE updated_at<=?', (now-86400,))
                for stored, age in (('chat', 3600), ('generation', 86400), ('login', 300), ('feedback', 60)):
                    connection.execute('DELETE FROM rate_hits WHERE kind=? AND ts<=?', (stored, now-age))
                for per_ip, window, limit, reason in self.policies(kind):
                    sql = 'SELECT COUNT(*),MIN(ts) FROM rate_hits WHERE kind=? AND ts>?'
                    args = [kind, now-window]
                    if per_ip:
                        sql += ' AND client=?'
                        args.append(client)
                    count, oldest = connection.execute(sql, args).fetchone()
                    if count >= limit:
                        retry = max(1, math.ceil(oldest + window - now))
                        detail = ('Sistemin günlük soru kotası doldu. Daha sonra tekrar deneyin.'
                                  if reason == 'global_day' else
                                  'Kısa sürede çok fazla istek gönderildi. Lütfen bekleyip tekrar deneyin.')
                        denied = Denied(reason, detail, retry)
                        break
                if not denied:
                    connection.execute('INSERT INTO rate_hits VALUES (?,?,?)', (kind, client, now))
        except sqlite3.Error:
            denied = Denied('storage', 'Şu anda yeni bir istek kabul edilemiyor. Biraz sonra tekrar deneyin.', status=503)
        if denied:
            self.block('chat' if kind == 'generation' else kind, denied.reason)
            if kind == 'chat' and denied.reason in ('ip_minute','ip_hour'):
                self.note_abuse(client)
            raise denied

    def note_abuse(self, client):
        now = self.clock()
        try:
            with self.connect() as connection:
                connection.execute('BEGIN IMMEDIATE')
                row = connection.execute('SELECT * FROM captcha_clients WHERE client=?', (client,)).fetchone()
                count = row[1]+1 if row and row[2] > now-600 else 1
                required = now+3600 if count >= 3 else row[3] if row else 0
                connection.execute('INSERT OR REPLACE INTO captcha_clients VALUES (?,?,?,?,?)',
                                   (client,count,now,required,row[4] if row else 0))
        except sqlite3.Error:
            pass  # Reddedilmiş isteğin hız kotası zaten geçerlidir.

    def needs_captcha(self, client):
        with self.connect() as connection:
            row = connection.execute('SELECT required_until,passed_until FROM captcha_clients WHERE client=?', (client,)).fetchone()
        now = self.clock()
        return bool(row and row[0]>now and row[1]<=now)

    def pass_captcha(self, client):
        with self.connect() as connection:
            connection.execute('UPDATE captcha_clients SET passed_until=? WHERE client=?', (self.clock()+1800,client))

    def block(self, kind: str, reason: str):
        minute = datetime.fromtimestamp(self.clock(), timezone.utc).replace(second=0, microsecond=0).isoformat()
        with self.lock:
            key = (minute, kind, reason)
            # Disk yazılamazken saldırı, bellekten de sınırsız yer alamaz.
            if len(self.pending) < 256 or key in self.pending:
                self.pending[key] = self.pending.get(key, 0) + 1

    def flush(self):
        with self.lock:
            pending, self.pending = self.pending, {}
        try:
            with self.connect() as connection:
                connection.executemany('''INSERT INTO rate_blocks VALUES (?,?,?,?)
                    ON CONFLICT(minute,kind,reason) DO UPDATE SET count=count+excluded.count''',
                                       [(*key, value) for key, value in pending.items()])
                cutoff = (datetime.now(timezone.utc)-timedelta(days=31)).isoformat()
                connection.execute('DELETE FROM rate_blocks WHERE minute<?', (cutoff,))
        except sqlite3.Error:
            with self.lock:
                for key, value in pending.items():
                    if len(self.pending) < 256 or key in self.pending:
                        self.pending[key] = self.pending.get(key, 0) + value

    @contextmanager
    def processing(self, client: str):
        with self.lock:
            busy = (self.active >= self.config.rate_chat_concurrent or
                    self.clients.get(client, 0) >= self.config.rate_chat_concurrent_per_ip)
            if not busy:
                self.active += 1
                self.clients[client] = self.clients.get(client, 0) + 1
        if busy:
            self.block('chat', 'busy')
            raise HTTPException(429, 'Sistem şu anda diğer soruları yanıtlıyor. Biraz sonra tekrar deneyin.',
                                headers={'Retry-After': '10', 'Cache-Control': 'no-store'})
        try:
            try:
                self.admit('generation', client)
            except Denied as error:
                raise HTTPException(error.status, error.detail,
                                    headers={'Retry-After': str(error.retry), 'Cache-Control': 'no-store'}) from None
            yield
        finally:
            # Sınır, HTTP bağlantısının değil gerçek worker işinin ömrünü izler.
            with self.lock:
                self.active -= 1
                self.clients[client] -= 1
                if not self.clients[client]:
                    del self.clients[client]

    def snapshot(self, days=7):
        from app.captcha import configured
        from zoneinfo import ZoneInfo
        local = datetime.now(ZoneInfo('Asia/Bishkek'))
        cutoff = (local-timedelta(days=days-1)).replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc).isoformat()
        self.flush()
        with self.connect() as connection:
            rows = connection.execute('SELECT reason,SUM(count) FROM rate_blocks WHERE minute>=? GROUP BY reason', (cutoff,)).fetchall()
            daily = connection.execute("SELECT COUNT(*) FROM rate_hits WHERE kind='generation' AND ts>?", (self.clock()-86400,)).fetchone()[0]
        with self.lock:
            active = self.active
        c = self.config
        return {'enabled': True, 'chat_per_minute': c.rate_chat_per_minute,
                'captcha_configured': configured(c),
                'chat_per_hour': c.rate_chat_per_hour, 'global_per_minute': c.rate_chat_global_per_minute,
                'global_per_day': c.rate_chat_global_per_day, 'daily_used': daily,
                'concurrent_limit': c.rate_chat_concurrent, 'active_queries': active,
                'max_body_bytes': c.rate_max_body_bytes, 'blocked_requests': sum(row[1] for row in rows),
                'blocked_by_reason': dict(rows)}


class AbuseMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        kind = PATHS.get(scope.get('path'))
        if scope['type'] != 'http' or scope.get('method') != 'POST' or not kind:
            return await self.app(scope, receive, send)
        guard = getattr(scope['app'].state, 'abuse', None)
        if guard is None:
            return await JSONResponse({'detail': 'Servis henüz hazır değil.'}, status_code=503)(scope, receive, send)
        headers = dict(scope['headers'])
        reader = False
        try:
            if kind == 'login':
                # Yabancı Origin, kota/parola kontrolünden önce reddedilir.
                from app.monitor_auth import check_origin
                from starlette.requests import Request
                try:
                    check_origin(Request(scope))
                except HTTPException as error:
                    raise Denied('origin', error.detail, status=403) from None
            try:
                length = int(headers.get(b'content-length', b'0'))
                if length < 0:
                    raise ValueError
            except ValueError:
                raise Denied('body_invalid', 'İstek boyutu geçersiz.', status=400) from None
            if length > guard.config.rate_max_body_bytes:
                raise Denied('body_large', 'İstek çok büyük. Soruyu veya sohbet geçmişini kısaltın.', status=413)
            if headers.get(b'content-encoding', b'identity').lower() != b'identity':
                raise Denied('encoding', 'Bu istek biçimi desteklenmiyor.', status=415)
            with guard.lock:
                if guard.readers < 16:
                    guard.readers += 1
                    reader = True
            if not reader:
                raise Denied('busy', 'Sistem yoğun. Biraz sonra tekrar deneyin.')
            deadline = time.monotonic() + guard.config.rate_body_timeout
            body = bytearray()
            while True:
                remaining = deadline-time.monotonic()
                if remaining <= 0:
                    raise TimeoutError
                message = await asyncio.wait_for(receive(), timeout=remaining)
                if message['type'] == 'http.disconnect':
                    return
                chunk = message.get('body', b'')
                if len(body)+len(chunk) > guard.config.rate_max_body_bytes:
                    raise Denied('body_large', 'İstek çok büyük. Soruyu veya sohbet geçmişini kısaltın.', status=413)
                body.extend(chunk)
                if not message.get('more_body', False):
                    break
            address = scope.get('client') or ('unknown', 0)
            client = guard.client_key(address[0])
            # Uvicorn yalnız güvenilir Apache'nin düzelttiği client bilgisini verir.
            await run_in_threadpool(guard.admit, kind, client)
            scope['state'] = {**scope.get('state', {}), 'rate_client': client, 'rate_admitted': True}
        except (Denied, TimeoutError) as error:
            if isinstance(error, TimeoutError):
                error = Denied('body_timeout', 'İstek zamanında tamamlanmadı. Yeniden deneyin.', status=408)
            # admit, kendi reddini sayar; gövde ve Origin retlerini burada say.
            if error.reason in ('body_large', 'body_timeout', 'body_invalid', 'encoding', 'origin', 'busy'):
                guard.block(kind, error.reason)
            response = JSONResponse({'detail': error.detail, 'code': error.reason}, status_code=error.status,
                                    headers={'Retry-After': str(error.retry), 'Cache-Control': 'no-store'})
            return await response(scope, receive, send)
        finally:
            if reader:
                with guard.lock:
                    guard.readers -= 1
        first = True
        async def replay():
            nonlocal first
            if first:
                first = False
                return {'type': 'http.request', 'body': bytes(body), 'more_body': False}
            return await receive()
        await self.app(scope, replay, send)
