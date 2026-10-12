"""Systemd timer'dan hafif sağlık ölçümü; backend kapalıyken de kayıt bırakır."""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

from app.config import settings
from app import monitoring


def check(url: str, health: bool = False) -> dict:
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            result = {'ok': response.status == 200, 'status': response.status,
                      'latency_ms': round((time.perf_counter() - started) * 1000)}
            if health:
                data = json.loads(response.read(16384))
                result['ok'] = result['ok'] and data.get('status') == 'ok'
                result['indexed_chunks'] = data.get('indexed_chunks')
                result['model'] = data.get('llm_model')
            return result
    except (OSError, ValueError, urllib.error.URLError) as error:
        return {'ok': False, 'status': getattr(error, 'code', None),
                'latency_ms': round((time.perf_counter() - started) * 1000)}


def run() -> None:
    monitoring.initialize()
    checks = {'backend': check('http://127.0.0.1:8000/health', health=True),
              'frontend': check('http://127.0.0.1:3000/')}
    if settings.monitor_public_url:
        checks['https'] = check(settings.monitor_public_url.rstrip('/') + '/api/health', health=True)
    monitoring.save_sample({'checks': checks, 'resources': monitoring.resources()})


if __name__ == '__main__':
    run()
