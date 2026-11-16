"""Kısa, IP/tarayıcı bağlı ziyaretçi oturumu; kimlik doğrulaması değildir."""
from __future__ import annotations

import base64
import hashlib
import hmac
import ipaddress
import json
import secrets
import sqlite3
from urllib.parse import urlsplit

from fastapi import HTTPException

from app import captcha

COOKIE = 'bakai_visitor'
SCHEMA = '''
CREATE TABLE IF NOT EXISTS visitor_proofs (digest TEXT PRIMARY KEY, expires REAL NOT NULL);
CREATE TABLE IF NOT EXISTS visitor_queries (
 query_id TEXT PRIMARY KEY, session_id TEXT NOT NULL, expires REAL NOT NULL);
CREATE TABLE IF NOT EXISTS visitor_hits (session_id TEXT NOT NULL, ts REAL NOT NULL);
CREATE INDEX IF NOT EXISTS visitor_hits_session ON visitor_hits(session_id,ts);
CREATE TABLE IF NOT EXISTS visitor_trials (client TEXT NOT NULL, ts REAL NOT NULL);
CREATE INDEX IF NOT EXISTS visitor_trials_client ON visitor_trials(client,ts);
'''


def unavailable():
    return HTTPException(503, 'Güvenlik kontrolü şu anda hazır değil. Biraz sonra yeniden deneyin.',
                         headers={'Cache-Control': 'no-store'})


def origin(request, config):
    """Origin yardımcı savunmadır; taklit edilebilir ve oturum yerine geçmez."""
    expected = urlsplit(config.monitor_public_url)
    supplied = urlsplit(request.headers.get('origin', ''))
    if not expected.netloc or expected.scheme not in ('http', 'https'):
        raise unavailable()
    if (supplied.scheme, supplied.netloc) != (expected.scheme, expected.netloc):
        raise HTTPException(403, 'Bu kaynaktan istek kabul edilmiyor.')
    if request.headers.get('sec-fetch-site') == 'cross-site':
        raise HTTPException(403, 'Bu kaynaktan istek kabul edilmiyor.')


def signing_key(config):
    if len(config.monitor_session_secret) < 32:
        raise unavailable()
    return hmac.digest(config.monitor_session_secret.encode(), b'BAKAI-visitor-v1', 'sha256')


def binding(request, guard):
    return {'ip': request.state.rate_client,
            'ua': hmac.new(signing_key(guard.config), request.headers.get('user-agent', '')[:1024].encode(),
                           hashlib.sha256).hexdigest()}


def challenge(guard):
    guard.block('chat', 'visitor_required')
    if not captcha.configured(guard.config):
        raise unavailable()
    raise HTTPException(403, {'code': 'captcha_required', 'site_key': guard.config.captcha_site_key,
                              'message': 'Devam etmek için kısa güvenlik kontrolünü tamamlayın.'},
                        headers={'Cache-Control': 'no-store'})


def create(request, response, token):
    guard = request.app.state.abuse
    config = guard.config
    if not config.public_security_enabled:
        raise HTTPException(404, 'Bulunamadı.')
    origin(request, config)
    key = signing_key(config)
    if not captcha.configured(config):
        raise unavailable()
    now = guard.clock()
    digest = hashlib.sha256(token.encode()).hexdigest()
    # Sağlayıcının gecikmeli tekrar kontrolüne ek olarak yerel atomik tek kullanım.
    try:
        with guard.connect() as connection:
            connection.execute('BEGIN IMMEDIATE')
            connection.execute('DELETE FROM visitor_proofs WHERE expires<=?', (now,))
            connection.execute('INSERT INTO visitor_proofs VALUES (?,?)', (digest, now + 600))
    except sqlite3.IntegrityError:
        challenge(guard)
    except sqlite3.Error:
        raise unavailable() from None
    if not captcha.verify(config, token):
        challenge(guard)
    data = {'id': secrets.token_hex(24), 'exp': int(now + config.visitor_session_seconds),
            **binding(request, guard)}
    set_cookie(response, data, config)
    guard.pass_captcha(request.state.rate_client)
    return {'ok': True, 'expires_in': config.visitor_session_seconds}


def set_cookie(response, data, config):
    key = signing_key(config)
    payload = base64.urlsafe_b64encode(json.dumps(data, separators=(',', ':')).encode()).decode().rstrip('=')
    signed = payload + '.' + hmac.new(key, payload.encode(), hashlib.sha256).hexdigest()
    response.set_cookie(COOKIE, signed, max_age=config.visitor_session_seconds, httponly=True,
                        secure=urlsplit(config.monitor_public_url).scheme == 'https',
                        samesite='strict', path='/')
    response.headers['Cache-Control'] = 'no-store'


def trial(request, response):
    """İlk soru için tek kullanımlık imzalı oturum; çerez silme IP kotasını silmez."""
    guard = request.app.state.abuse
    config, now = guard.config, guard.clock()
    if guard.needs_captcha(request.state.rate_client):
        challenge(guard)
    try:
        with guard.connect() as connection:
            connection.execute('BEGIN IMMEDIATE')
            connection.execute('DELETE FROM visitor_trials WHERE ts<=?', (now-86400,))
            count = connection.execute('SELECT COUNT(*) FROM visitor_trials WHERE client=?',
                                       (request.state.rate_client,)).fetchone()[0]
            total = connection.execute('SELECT COUNT(*) FROM visitor_trials').fetchone()[0]
            if count >= config.visitor_trial_per_ip_day or total >= config.visitor_trial_global_day:
                challenge(guard)
            connection.execute('INSERT INTO visitor_trials VALUES (?,?)', (request.state.rate_client, now))
    except sqlite3.Error:
        raise unavailable() from None
    data = {'id': secrets.token_hex(24), 'exp': int(now + config.visitor_session_seconds),
            'trial': True, **binding(request, guard)}
    set_cookie(response, data, config)
    return data


def require(request, *, consume=False, response=None):
    guard = request.app.state.abuse
    if not guard.config.public_security_enabled:
        return None
    if not captcha.configured(guard.config):
        raise unavailable()
    origin(request, guard.config)
    key = signing_key(guard.config)
    token = request.cookies.get(COOKIE, '')
    first = not token and consume and response is not None
    if first:
        data = trial(request, response)
    try:
        if not first:
            if len(token) > 1024:
                raise ValueError
            payload, signature = token.split('.')
            if not hmac.compare_digest(signature, hmac.new(key, payload.encode(), hashlib.sha256).hexdigest()):
                raise ValueError
            data = json.loads(base64.urlsafe_b64decode(payload + '=' * (-len(payload) % 4)))
        bound = binding(request, guard)
        if (not isinstance(data['exp'], int) or data['exp'] <= guard.clock() or
                data['exp'] > guard.clock() + guard.config.visitor_session_seconds or
                not isinstance(data['id'], str) or len(data['id']) != 48 or
                any(data[name] != value for name, value in bound.items())):
            raise ValueError
    except (ValueError, KeyError, TypeError):
        challenge(guard)
    if consume and data.get('trial') and not first:
        challenge(guard)
    if guard.needs_captcha(request.state.rate_client):
        challenge(guard)
    if consume:
        now = guard.clock()
        try:
            with guard.connect() as connection:
                connection.execute('BEGIN IMMEDIATE')
                connection.execute('DELETE FROM visitor_hits WHERE ts<=?', (now-3600,))
                connection.execute('DELETE FROM visitor_queries WHERE expires<=?', (now,))
                for window, limit in ((60, 30), (3600, 120)):
                    count = connection.execute('SELECT COUNT(*) FROM visitor_hits WHERE session_id=? AND ts>?',
                                               (data['id'], now-window)).fetchone()[0]
                    if count >= limit:
                        raise HTTPException(429, 'Bu oturumun soru sınırına ulaşıldı. Biraz sonra yeniden deneyin.',
                                            headers={'Retry-After': str(window), 'Cache-Control': 'no-store'})
                connection.execute('INSERT INTO visitor_hits VALUES (?,?)', (data['id'], now))
        except sqlite3.Error:
            raise unavailable() from None
    request.state.visitor = data
    return data


def own_query(request, query_id):
    data = getattr(request.state, 'visitor', None)
    if data:
        with request.app.state.abuse.connect() as connection:
            connection.execute('INSERT OR REPLACE INTO visitor_queries VALUES (?,?,?)',
                               (query_id, data['id'], data['exp']))


def require_query(request, query_id):
    data = require(request)
    if data:
        with request.app.state.abuse.connect() as connection:
            row = connection.execute('SELECT session_id FROM visitor_queries WHERE query_id=? AND expires>?',
                                     (query_id, request.app.state.abuse.clock())).fetchone()
        if not row or row[0] != data['id']:
            raise HTTPException(403, 'Bu sorgu için geçerli oturum bulunamadı. Yeni bir soru sorup tekrar deneyin.')


def panel_allowed(request, config):
    if not config.public_security_enabled:
        return True
    try:
        address = ipaddress.ip_address(request.client.host)
        address = getattr(address, 'ipv4_mapped', None) or address
        networks = [ipaddress.ip_network(value.strip()) for value in config.monitor_allowed_networks.split(',') if value.strip()]
        return any(address in network for network in networks)
    except (ValueError, AttributeError):
        return False
