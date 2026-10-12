"""Panel erişimi, eski verinin korunması ve gerçek sayaçlı maliyetin sınırları."""
from __future__ import annotations

import json
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

import httpx
from fastapi.testclient import TestClient

from app import main, monitor_auth, monitor_probe, monitoring, telemetry
from app.config import Settings
from app.rag import llm


class MonitoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.encoded = monitor_auth.password_hash('test-monitor-password')

    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.directory = self.stack.enter_context(tempfile.TemporaryDirectory())
        self.config = Settings(_env_file=None, db_path=str(Path(self.directory) / 'monitor.db'),
                               monitor_username='adminbakai', monitor_password_hash=self.encoded,
                               monitor_session_secret='s' * 64, monitor_public_url='https://testserver',
                               anthropic_api_key='fake-key', anthropic_model='claude-haiku-5-5')
        for module in (main, monitoring, monitor_auth, monitor_probe, telemetry, llm):
            self.stack.enter_context(patch.object(module, 'settings', self.config))
        monitor_auth._attempts.clear()
        self.client = self.stack.enter_context(TestClient(main.app, base_url='https://testserver', raise_server_exceptions=False))

    def login(self):
        response = self.client.post('/monitor/login', json={'username': 'adminbakai', 'password': 'test-monitor-password'}, headers={'Origin': 'https://testserver'})
        self.assertEqual(response.status_code, 200)
        return response

    def query(self, query_id='1' * 32, ts='2026-01-01T00:00:00+00:00'):
        telemetry.log_query({'id': query_id, 'ts': ts, 'question': 'Özel soru', 'answer': 'Özel yanıt',
                             'model': 'claude-haiku-5-5', 'n_sources': 1, 'total_ms': 1000,
                             'retrieval_ms': 300, 'generation_ms': 700, 'sources': []})

    def test_metrics_stats_and_details_require_login_and_disable_cache(self):
        for url in ('/monitor/metrics', '/stats', '/monitor/queries/' + '1' * 32):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.headers['cache-control'], 'no-store')
            self.assertNotIn('Özel soru', response.text)

    def test_session_cookie_secure_http_only_and_logout(self):
        response = self.login()
        cookie = response.headers['set-cookie']
        self.assertIn('HttpOnly', cookie)
        self.assertIn('Secure', cookie)
        self.assertIn('SameSite=strict', cookie)
        self.assertEqual(self.client.get('/monitor/metrics?days=7').status_code, 200)
        self.assertEqual(self.client.get('/monitor/metrics?days=999').status_code, 422)
        self.client.post('/monitor/logout')
        self.assertEqual(self.client.get('/monitor/metrics').status_code, 401)

    def test_tampered_and_expired_sessions_fail(self):
        self.login()
        token = self.client.cookies.get(monitor_auth.COOKIE)
        self.client.cookies.clear()
        self.client.cookies.set(monitor_auth.COOKIE, token[:-1] + ('0' if token[-1] != '0' else '1'))
        self.assertEqual(self.client.get('/monitor/metrics').status_code, 401)
        self.client.cookies.clear()
        with patch.object(monitor_auth.time, 'time', return_value=time.time() - 36000):
            self.login()
        self.assertEqual(self.client.get('/monitor/metrics').status_code, 401)

    def test_wrong_password_rate_limit_and_foreign_origin(self):
        body = {'username': 'adminbakai', 'password': 'wrong-password'}
        for _ in range(5):
            self.assertEqual(self.client.post('/monitor/login', json=body).status_code, 401)
        self.assertEqual(self.client.post('/monitor/login', json=body).status_code, 429)
        monitor_auth._attempts.clear()
        self.assertEqual(self.client.post('/monitor/login', json=body, headers={'Origin': 'https://other.example'}).status_code, 403)

    def test_missing_secret_disables_panel_and_secrets_are_not_repr(self):
        self.config.monitor_session_secret = ''
        self.assertEqual(self.client.get('/monitor/metrics').status_code, 503)
        self.assertNotIn(self.encoded, repr(self.config))
        self.assertNotIn('fake-key', repr(self.config))

    def test_legacy_query_stays_unknown_and_details_are_private(self):
        self.query(ts=monitoring.utc_now())
        with monitoring.connect() as connection:
            connection.execute("UPDATE monitor_meta SET value='2999-01-01T00:00:00+00:00' WHERE key='metering_since'")
        self.login()
        metrics = self.client.get('/monitor/metrics?days=1').json()
        self.assertEqual(metrics['summary']['queries'], 1)
        self.assertEqual(metrics['cost']['unmetered_queries'], 1)
        self.assertIsNone(metrics['recent_queries'][0]['cost_usd'])
        detail = self.client.get('/monitor/queries/' + '1' * 32).json()
        self.assertEqual(detail['answer'], 'Özel yanıt')
        self.assertNotIn('prompt', detail)
        self.config.monitor_show_query_details = False
        metrics = self.client.get('/monitor/metrics').json()
        self.assertNotIn('question', metrics['recent_queries'][0])
        self.assertEqual(self.client.get('/monitor/queries/' + '1' * 32).status_code, 404)

    def test_no_llm_call_after_metering_is_zero_not_unknown(self):
        self.query(ts=monitoring.utc_now())
        self.login()
        row = self.client.get('/monitor/metrics').json()['recent_queries'][0]
        self.assertEqual(row['cost_usd'], 0)

    def test_failure_is_recorded_without_request_body(self):
        with patch.object(main.pipeline, 'answer', side_effect=RuntimeError('internal-error')):
            response = self.client.post('/chat', json={'question': 'Gizli soru'})
        self.assertEqual(response.status_code, 500)
        self.login()
        metrics = self.client.get('/monitor/metrics').json()
        self.assertEqual(metrics['summary']['server_errors'], 1)
        self.assertEqual(metrics['summary']['requests'], 1)
        self.assertNotIn('Gizli soru', json.dumps(metrics))

    def test_probe_survives_backend_failure_and_is_persisted(self):
        with patch.object(monitor_probe.urllib.request, 'urlopen', side_effect=URLError('offline')):
            monitor_probe.run()
        self.login()
        metrics = self.client.get('/monitor/metrics').json()
        self.assertFalse(metrics['sample']['checks']['backend']['ok'])
        self.assertEqual(metrics['summary']['probe_availability_percent'], 0)

    def test_contexts_do_not_mix_concurrent_llm_usage(self):
        def record(query_id):
            with telemetry.query_scope(query_id):
                monitoring.record_llm_call('claude-haiku-5-5', 'ok', 10,
                                           {'input_tokens': 100, 'output_tokens': 200})
            self.assertIsNone(telemetry.current_query_id())
        with ThreadPoolExecutor(max_workers=2) as executor:
            list(executor.map(record, ('a' * 32, 'b' * 32)))
        with monitoring.connect() as connection:
            rows = connection.execute('SELECT query_id,cost_usd FROM llm_calls').fetchall()
        self.assertEqual({row['query_id'] for row in rows}, {'a' * 32, 'b' * 32})
        self.assertTrue(all(abs(row['cost_usd'] - 0.00011) < 1e-10 for row in rows))

    def test_real_response_usage_and_error_are_metered(self):
        messages = [{'type': 'message', 'model': 'claude-haiku-5-5', 'content': [{'type': 'text', 'text': 'Yanıt'}],
                     'usage': {'input_tokens': 100, 'output_tokens': 200}}]
        client = llm.AnthropicLLM()
        client.http.close()
        client.http = httpx.Client(base_url='https://api.anthropic.com', transport=httpx.MockTransport(
            lambda _: httpx.Response(200, json=messages[0])))
        self.addCleanup(client.http.close)
        with telemetry.query_scope('c' * 32):
            self.assertEqual(client.generate('Soru'), 'Yanıt')
        messages[0] = {'error': 'busy'}
        client.http.close()
        client.http = httpx.Client(base_url='https://api.anthropic.com', transport=httpx.MockTransport(
            lambda _: httpx.Response(429, json=messages[0])))
        with telemetry.query_scope('d' * 32), self.assertRaises(httpx.HTTPStatusError):
            client.generate('Soru')
        with monitoring.connect() as connection:
            rows = connection.execute('SELECT * FROM llm_calls ORDER BY id').fetchall()
        self.assertEqual(rows[0]['input_tokens'], 100)
        self.assertEqual(rows[1]['error_type'], 'HTTP_429')
        self.assertIsNone(rows[1]['cost_usd'])
        self.login()
        cost = self.client.get('/monitor/metrics').json()['cost']
        self.assertEqual(cost['priced_calls'], 1)
        self.assertEqual(cost['unknown_calls'], 1)
        self.assertEqual(cost['by_model'][0]['priced_calls'], 1)


class PricingTests(unittest.TestCase):
    def test_haiku_threshold_counts_cache_tokens_and_raises_both_prices(self):
        cost = monitoring.cost_estimate('claude-haiku-5-5', {'input_tokens': 100000, 'output_tokens': 1000})
        self.assertAlmostEqual(cost, 0.0105)
        long = monitoring.cost_estimate('claude-haiku-5-5', {'input_tokens': 100000, 'output_tokens': 1000, 'cache_read_input_tokens': 1})
        self.assertAlmostEqual(long, 0.05250005)

    def test_cache_write_ttl_and_sonnet_cache_read_pricing(self):
        usage = {'input_tokens': 0, 'output_tokens': 0, 'cache_read_input_tokens': 1000,
                 'cache_creation_input_tokens': 2000, 'cache_creation': {'ephemeral_1h_input_tokens': 1000}}
        self.assertAlmostEqual(monitoring.cost_estimate('claude-sonnet-5-5', usage), 0.0066)

    def test_unknown_model_missing_and_invalid_usage_are_unknown(self):
        for model, usage in [('unknown', {'input_tokens': 1, 'output_tokens': 1}),
                             ('claude-haiku-5-5', {}), ('claude-haiku-5-5', None),
                             ('claude-haiku-5-5', {'input_tokens': -1, 'output_tokens': 1})]:
            self.assertIsNone(monitoring.cost_estimate(model, usage))


if __name__ == '__main__':
    unittest.main()
