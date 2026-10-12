"""İzleme paneli için imzalı, HttpOnly oturum ve sınırlı parola denemeleri."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import threading
import time
from collections import OrderedDict, deque
from urllib.parse import urlsplit

from fastapi import HTTPException, Request, Response

from app.config import settings

COOKIE = "bakay_monitor"
SESSION_SECONDS = 8 * 60 * 60
_attempts: OrderedDict[str, deque] = OrderedDict()
_lock = threading.Lock()


def password_hash(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1)
    return "scrypt$" + salt.hex() + "$" + digest.hex()


def password_matches(password: str, encoded: str) -> bool:
    try:
        kind, salt, expected = encoded.split("$")
        if kind != "scrypt" or len(salt) != 32 or len(expected) != 128:
            return False
        digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1)
        return hmac.compare_digest(digest.hex(), expected)
    except (ValueError, TypeError):
        return False


def ready() -> bool:
    return bool(settings.monitor_password_hash and len(settings.monitor_session_secret) >= 32)


def check_origin(request: Request) -> None:
    origin = request.headers.get("origin")
    expected = settings.monitor_public_url or str(request.base_url).rstrip("/")
    if origin and (urlsplit(origin).scheme, urlsplit(origin).netloc) != (
        urlsplit(expected).scheme, urlsplit(expected).netloc
    ):
        raise HTTPException(403, "Bu kaynaktan giriş kabul edilmiyor.")


def authenticate(request: Request, username: str, password: str) -> str:
    check_origin(request)
    if not ready():
        raise HTTPException(503, "Panel giriş ayarları henüz tamamlanmadı.")
    address = request.client.host if request.client else "unknown"
    now = time.monotonic()
    with _lock:
        attempts = _attempts.setdefault(address, deque())
        while attempts and attempts[0] < now - 300:
            attempts.popleft()
        if len(attempts) >= 5:
            raise HTTPException(429, "Çok fazla giriş denemesi. Beş dakika sonra tekrar deneyin.",
                                headers={"Retry-After": "300"})
        attempts.append(now)
        _attempts.move_to_end(address)
        while len(_attempts) > 1024:
            _attempts.popitem(last=False)
    valid_password = password_matches(password, settings.monitor_password_hash)
    if not hmac.compare_digest(username.encode(), settings.monitor_username.encode()) or not valid_password:
        raise HTTPException(401, "Kullanıcı adı veya parola yanlış.")
    with _lock:
        _attempts.pop(address, None)
    payload = base64.urlsafe_b64encode(json.dumps({
        "user": username, "expires": int(time.time()) + SESSION_SECONDS,
        "nonce": secrets.token_hex(16),
    }, separators=(",", ":")).encode()).decode().rstrip("=")
    signature = hmac.new(settings.monitor_session_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return payload + "." + signature


def require_monitor(request: Request) -> str:
    if not ready():
        raise HTTPException(503, "Panel giriş ayarları henüz tamamlanmadı.")
    cookie = request.cookies.get(COOKIE, "")
    try:
        if len(cookie) > 1024:
            raise ValueError
        payload, signature = cookie.split(".")
        expected = hmac.new(settings.monitor_session_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError
        data = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        if data["expires"] <= time.time() or data["user"] != settings.monitor_username:
            raise ValueError
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        raise HTTPException(401, "Yönetici girişi gerekli.") from None
    return data["user"]


def set_session(response: Response, request: Request, token: str) -> None:
    response.set_cookie(COOKIE, token, max_age=SESSION_SECONDS, httponly=True,
                        secure=request.url.scheme == "https", samesite="strict", path="/")
    response.headers["Cache-Control"] = "no-store"
