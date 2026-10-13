"""Saldırı girdileri LLM'e ulaşamaz; kalıcı kotalar atomik ve işler sınırlı."""
from __future__ import annotations

import asyncio
import importlib.util
import sqlite3
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app import main, monitor_auth, monitoring, telemetry
from app.abuse import AbuseGuard, AbuseMiddleware, Denied
from app.config import Settings
from app.schemas import ChatResponse


class GuardTests(unittest.TestCase):
    def setUp(self):
        directory = self.enterContext(tempfile.TemporaryDirectory())
        self.config = Settings(_env_file=None, db_path=str(Path(directory) / 'test.db'),
                               monitor_session_secret='test-persistent-secret')
        self.now = time.time()
        self.guard = AbuseGuard(self.config, clock=lambda: self.now)
        self.client = self.guard.client_key('192.0.2.1')

    def test_sliding_minute_and_hour_windows_with_retry(self):
        self.config.rate_chat_per_minute = 2
        self.config.rate_chat_per_hour = 3
        for _ in range(2):
            self.guard.admit('chat', self.client)
        self.now += 12
        with self.assertRaises(Denied) as blocked:
            self.guard.admit('chat', self.client)
        self.assertEqual((blocked.exception.reason, blocked.exception.retry), ('ip_minute', 48))
        self.guard.admit('chat', self.guard.client_key('192.0.2.2'))
        self.now += 48
        self.guard.admit('chat', self.client)
        with self.assertRaises(Denied) as blocked:
            self.guard.admit('chat', self.client)
        self.assertEqual((blocked.exception.reason, blocked.exception.retry), ('ip_hour', 3540))
        self.now += 3600
        self.guard.admit('chat', self.client)

    def test_restart_does_not_reset_quota_and_table_contains_no_plain_ip(self):
        self.config.rate_chat_per_minute = 1
        self.guard.admit('chat', self.client)
        restarted = AbuseGuard(self.config, clock=lambda: self.now)
        self.assertEqual(restarted.client_key('192.0.2.1'), self.client)
        with self.assertRaises(Denied):
            restarted.admit('chat', self.client)
        with self.guard.connect() as connection:
            row = connection.execute('SELECT client FROM rate_hits').fetchone()
        self.assertEqual(row[0], self.client)
        self.assertNotIn('192.0.2.1', row[0])

    def test_ipv6_rotation_and_ipv4_mapped_addresses_share_limits(self):
        self.assertEqual(self.client, self.guard.client_key('::ffff:192.0.2.1'))
        self.assertEqual(self.guard.client_key('2001:db8::1'), self.guard.client_key('2001:db8::ffff'))
        self.assertNotEqual(self.guard.client_key('2001:db8::1'), self.guard.client_key('2001:db8:0:1::1'))

    def test_atomic_global_quota_across_multiple_guards(self):
        self.config.rate_chat_global_per_minute = 7
        guards = [AbuseGuard(self.config) for _ in range(4)]
        def attempt(index):
            guard = guards[index % len(guards)]
            try:
                guard.admit('chat', guard.client_key(f'192.0.2.{index}'))
                return True
            except Denied:
                return False
        with ThreadPoolExecutor(max_workers=8) as pool:
            self.assertEqual(sum(pool.map(attempt, range(32))), 7)
        with self.guard.connect() as connection:
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM rate_hits').fetchone()[0], 7)

    def test_daily_budget_survives_restart_and_releases_failed_work(self):
        self.config.rate_chat_global_per_day = 1
        with self.assertRaises(RuntimeError):
            with self.guard.processing(self.client):
                raise RuntimeError('model-error')
        self.assertEqual((self.guard.active, self.guard.clients), (0, {}))
        restarted = AbuseGuard(self.config, clock=lambda: self.now)
        with self.assertRaises(HTTPException) as error:
            with restarted.processing('different-client'):
                self.fail('Kota aşılınca LLM çalışmamalı')
        self.assertEqual(error.exception.status_code, 429)
        self.assertEqual(restarted.active, 0)
        self.now += 86400
        with restarted.processing(self.client):
            pass

    def test_busy_slot_does_not_consume_daily_budget(self):
        self.config.rate_chat_concurrent_per_ip = 1
        with self.guard.processing(self.client):
            with self.assertRaises(HTTPException):
                with self.guard.processing(self.client):
                    self.fail('Aynı IP kotası aşılmamalı')
            with self.guard.processing('another-client'):
                self.assertEqual(self.guard.active, 2)
                with self.assertRaises(HTTPException):
                    with self.guard.processing('third-client'):
                        self.fail('Global eşzamanlı iş sınırı aşılmamalı')
        self.assertEqual(self.guard.snapshot()['daily_used'], 2)
        self.assertEqual(self.guard.active, 0)

    def test_storage_failure_stops_new_llm_work(self):
        with patch.object(self.guard, 'connect', side_effect=sqlite3.OperationalError('unavailable')):
            with self.assertRaises(HTTPException) as blocked:
                with self.guard.processing(self.client):
                    self.fail('Kota deposu olmadan ücretli iş başlatılmamalı')
        self.assertEqual(blocked.exception.status_code, 503)
        self.assertEqual(self.guard.active, 0)

    def test_rejections_are_aggregated_and_pending_memory_is_bounded(self):
        for _ in range(1000):
            self.guard.block('chat', 'ip_minute')
        self.guard.flush()
        with self.guard.connect() as connection:
            self.assertEqual(connection.execute('SELECT COUNT(*),SUM(count) FROM rate_blocks').fetchone(), (1, 1000))
        self.assertEqual(self.guard.snapshot(1)['blocked_requests'], 1000)
        with patch.object(self.guard, 'connect', side_effect=sqlite3.OperationalError('unavailable')):
            for index in range(300):
                self.guard.block('chat', str(index))
            self.guard.flush()
        self.assertEqual(len(self.guard.pending), 256)


class AbuseAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.encoded = monitor_auth.password_hash('test-monitor-password')

    def setUp(self):
        directory = self.enterContext(tempfile.TemporaryDirectory())
        self.config = Settings(_env_file=None, db_path=str(Path(directory) / 'test.db'),
                               log_dir=str(Path(directory) / 'logs'), monitor_username='test-admin',
                               monitor_password_hash=self.encoded, monitor_session_secret='s' * 64)
        for module in (main, monitoring, monitor_auth, telemetry):
            self.enterContext(patch.object(module, 'settings', self.config))
        monitor_auth._attempts.clear()
        self.client = self.enterContext(TestClient(main.app, raise_server_exceptions=False))
        self.answer = self.enterContext(patch.object(main.pipeline, 'answer', return_value=
            ChatResponse(query_id='1'*32, answer='Test yanıtı', sources=[], latency_ms=1)))

    def test_forged_proxy_headers_cannot_bypass_limit_or_reach_llm(self):
        for index in range(30):
            response = self.client.post('/chat', json={'question': 'Kayıt nasıl yapılır?'},
                                        headers={'X-Forwarded-For': f'192.0.2.{index}',
                                                 'Forwarded': f'for=192.0.2.{index}'})
            self.assertEqual(response.status_code, 200)
        response = self.client.post('/chat', json={'question': 'Yeni soru'},
                                    headers={'Origin': 'http://localhost:3000', 'X-Forwarded-For': '192.0.2.99'})
        self.assertEqual(response.status_code, 429)
        self.assertGreater(int(response.headers['retry-after']), 0)
        self.assertEqual(response.headers['cache-control'], 'no-store')
        self.assertEqual(response.headers['access-control-allow-origin'], 'http://localhost:3000')
        self.assertIn('Retry-After', response.headers['access-control-expose-headers'])
        self.assertEqual(self.answer.call_count, 30)
        with monitoring.connect() as connection:
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM monitor_events').fetchone()[0], 30)

    def test_large_and_encoded_bodies_are_stopped_before_validation(self):
        for content, headers, status in [
            (b'x'*131073, {}, 413),
            ((part for part in [b'x'*65536, b'x'*65537]), {}, 413),
            (b'not-json', {'Content-Encoding': 'gzip'}, 415),
            (b'{}', {'Content-Length': '-1'}, 400),
        ]:
            response = self.client.post('/chat', content=content, headers=headers)
            self.assertEqual(response.status_code, status)
        self.answer.assert_not_called()
        self.assertEqual(main.app.state.abuse.snapshot()['daily_used'], 0)

    def test_invalid_schema_does_not_consume_daily_budget(self):
        for top_k in (0, -1, 9, 1000000):
            self.assertEqual(self.client.post('/chat', json={'question': 'Soru', 'top_k': top_k}).status_code, 422)
        for feedback in ({'query_id': 'bad', 'rating': 'up'},
                         {'query_id': '1'*32, 'rating': 'up', 'comment': 'x'*2001}):
            self.assertEqual(self.client.post('/feedback', json=feedback).status_code, 422)
        self.answer.assert_not_called()
        self.assertEqual(main.app.state.abuse.snapshot()['daily_used'], 0)

    def test_two_real_workers_block_third_without_extra_budget(self):
        started, release = threading.Event(), threading.Event()
        lock = threading.Lock()
        calls = 0
        def slow_answer(*args, **kwargs):
            nonlocal calls
            with lock:
                calls += 1
                if calls == 2:
                    started.set()
            if not release.wait(10):
                raise RuntimeError('Test zaman aşımı')
            return ChatResponse(query_id='1'*32, answer='Test', sources=[], latency_ms=1)
        self.answer.side_effect = slow_answer
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(self.client.post, '/chat', json={'question': 'Soru'}) for _ in range(2)]
            try:
                self.assertTrue(started.wait(5))
                response = self.client.post('/chat', json={'question': 'Üçüncü soru'})
                self.assertEqual(response.status_code, 429)
                self.assertEqual(main.app.state.abuse.snapshot()['daily_used'], 2)
            finally:
                release.set()
            self.assertEqual([future.result().status_code for future in futures], [200, 200])
        self.assertEqual(calls, 2)
        self.assertEqual(main.app.state.abuse.active, 0)

    def test_feedback_spam_updates_one_existing_vote_and_unknown_query_writes_nothing(self):
        telemetry.log_query({'id': '1'*32, 'question': 'Test sorusu'})
        for index in range(30):
            response = self.client.post('/feedback', json={'query_id': '1'*32, 'rating': 'down' if index else 'up'})
            self.assertEqual(response.json(), {'ok': True})
        self.assertEqual(self.client.post('/feedback', json={'query_id': '1'*32, 'rating': 'up'}).status_code, 429)
        self.assertFalse(telemetry.log_feedback('2'*32, 'up'))
        with telemetry._connect() as connection:
            self.assertEqual(connection.execute('SELECT COUNT(*),MAX(rating) FROM feedback').fetchone(), (1, 'down'))

    def test_metrics_protection_is_private_and_reports_blocked_requests(self):
        self.assertEqual(self.client.get('/monitor/metrics').status_code, 401)
        self.config.rate_chat_per_minute = 1
        self.client.post('/chat', json={'question': 'Soru'})
        self.client.post('/chat', json={'question': 'Soru'})
        self.assertEqual(self.client.post('/monitor/login', json={'username': 'test-admin', 'password': 'test-monitor-password'}).status_code, 200)
        data = self.client.get('/monitor/metrics?days=1').json()['protection']
        self.assertEqual(data['blocked_by_reason']['ip_minute'], 1)
        self.assertEqual(data['daily_used'], 1)


class BodyAndProxyTests(unittest.TestCase):
    def setUp(self):
        directory = self.enterContext(tempfile.TemporaryDirectory())
        config = Settings(_env_file=None, db_path=str(Path(directory) / 'test.db'))
        self.guard = AbuseGuard(config)

    def call_middleware(self, receive):
        messages = []
        called = []
        async def target(*args):
            called.append(True)
        async def send(message):
            messages.append(message)
        scope = {'type': 'http', 'method': 'POST', 'path': '/chat', 'headers': [],
                 'client': ('192.0.2.1', 1234), 'app': SimpleNamespace(state=SimpleNamespace(abuse=self.guard))}
        asyncio.run(AbuseMiddleware(target)(scope, receive, send))
        self.assertEqual(called, [])
        self.assertEqual(self.guard.readers, 0)
        return messages

    def test_slow_body_times_out_and_disconnect_releases_reader(self):
        self.guard.config.rate_body_timeout = 0.01
        async def slow():
            await asyncio.sleep(1)
        messages = self.call_middleware(slow)
        self.assertEqual(messages[0]['status'], 408)
        async def disconnect():
            return {'type': 'http.disconnect'}
        self.assertEqual(self.call_middleware(disconnect), [])
        self.assertEqual(self.guard.snapshot()['daily_used'], 0)

    def test_reader_capacity_rejects_before_receiving_body(self):
        self.guard.readers = 16
        async def receive():
            self.fail('Gövde okuyucu sınırı aşılmamalı')
        self.guard.readers = 16
        messages = []
        async def send(message):
            messages.append(message)
        scope = {'type': 'http', 'method': 'POST', 'path': '/chat', 'headers': [],
                 'app': SimpleNamespace(state=SimpleNamespace(abuse=self.guard))}
        asyncio.run(AbuseMiddleware(None)(scope, receive, send))
        self.assertEqual(messages[0]['status'], 429)
        self.assertEqual(self.guard.readers, 16)

    def test_apache_render_is_idempotent_preserves_tls_and_strips_forged_ip(self):
        root = Path(__file__).resolve().parents[2]
        spec = importlib.util.spec_from_file_location('render_apache', root/'deploy/render-apache.py')
        renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderer)
        original = '<VirtualHost *:80>\nRedirect permanent / https://bakai.manas.edu.kg/\n</VirtualHost>\n<VirtualHost *:443>\nServerName bakai.manas.edu.kg\nSSLCertificateFile /private/cert.pem\nSSLCertificateKeyFile /private/key.pem\nProxyPass / http://old/\n</VirtualHost>\n'
        proxy = (root/'deploy/apache-proxy.inc').read_text()
        rendered = renderer.render(original, proxy)
        self.assertEqual(renderer.render(rendered, proxy), rendered)
        self.assertIn('SSLCertificateKeyFile /private/key.pem', rendered)
        self.assertIn('Redirect permanent / https://bakai.manas.edu.kg/', rendered)
        self.assertEqual(rendered.count('RequestHeader unset X-Forwarded-For'), 1)
        self.assertIn('ProxyAddHeaders On', rendered)
        self.assertIn('LimitRequestBody 131072', rendered)
        self.assertIn('RequestReadTimeout', rendered)


if __name__ == '__main__':
    unittest.main()
