"""Şüpheli bağlantılarda Turnstile doğrulaması; hız kotası hiçbir zaman aşılmaz."""
from __future__ import annotations

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fastapi import HTTPException


def configured(config):
    return bool(config.captcha_site_key and config.captcha_secret_key and config.captcha_hostname)


def verify(config, token, opener=None):
    if not token:
        return False
    request = Request('https://challenges.cloudflare.com/turnstile/v0/siteverify',
                      data=urlencode({'secret':config.captcha_secret_key,'response':token}).encode(),
                      headers={'Content-Type':'application/x-www-form-urlencoded'})
    try:
        with (opener or urlopen)(request, timeout=5) as response:
            result = json.loads(response.read(16384))
    except (OSError, ValueError) as error:
        raise HTTPException(503, 'Güvenlik doğrulama hizmetine ulaşılamıyor. Biraz sonra yeniden deneyin.',
                            headers={'Cache-Control':'no-store'}) from None
    return (isinstance(result, dict) and result.get('success') is True and
            result.get('hostname') == config.captcha_hostname and result.get('action') == 'bakai_chat')


def require(guard, client, token):
    if not configured(guard.config) or not guard.needs_captcha(client):
        return
    if not verify(guard.config, token):
        guard.block('chat','captcha')
        raise HTTPException(403, {'code':'captcha_required','site_key':guard.config.captcha_site_key,
                                  'message':'Devam etmeden önce kısa güvenlik doğrulamasını tamamlayın.'},
                            headers={'Cache-Control':'no-store'})
    guard.pass_captcha(client)
