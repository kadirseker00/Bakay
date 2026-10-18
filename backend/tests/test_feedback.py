"""Geri bildirim ayrıntıları, eski kayıt geçişi ve yöneticiye özel IP bilgisi."""
from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from unittest.mock import patch

from fastapi.testclient import TestClient
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app import main, monitor_auth, monitoring, telemetry
from app.config import Settings
from app.schemas import ChatResponse


class FeedbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.password_hash = monitor_auth.password_hash('test-feedback-password')

    def setUp(self):
        directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.config = Settings(_env_file=None, db_path=str(directory / 'test.db'),
                               log_dir=str(directory / 'logs'), monitor_username='test-admin',
                               monitor_password_hash=self.password_hash, monitor_session_secret='s' * 64)
        for module in (main, monitoring, monitor_auth, telemetry):
            self.enterContext(patch.object(module, 'settings', self.config))
        self.client = self.enterContext(TestClient(main.app))
        self.query_id = 'a' * 32
        telemetry.log_query({'id': self.query_id, 'question': 'Test sorusu', 'answer': 'Test yanıtı',
                             'client_ip': '2001:db8::42'})

    def login(self):
        response = self.client.post('/monitor/login', json={
            'username': 'test-admin', 'password': 'test-feedback-password'})
        self.assertEqual(response.status_code, 200)

    def test_reasons_optional_name_and_admin_visibility(self):
        for reason in ('outdated', 'irrelevant', 'incomplete', 'sources', 'other', 'incorrect'):
            with self.subTest(reason=reason):
                response = self.client.post('/feedback', json={
                    'query_id': self.query_id, 'rating': 'down', 'reason': reason,
                    'comment': '  Sorunun ayrıntısı  ',
                    'respondent_name': '  Test Kullanıcı  ' if reason == 'incorrect' else '  '})
                self.assertEqual(response.json(), {'ok': True})
                self.assertEqual(monitoring.query_detail(self.query_id)['feedback']['reason'], reason)
        for path in ('/monitor/metrics', '/monitor/queries/' + self.query_id, '/stats'):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 401)
            self.assertNotIn('2001:db8::42', response.text)
            self.assertNotIn('Test Kullanıcı', response.text)
        self.login()
        recent = self.client.get('/monitor/metrics').json()['recent_queries'][0]
        detail = self.client.get('/monitor/queries/' + self.query_id).json()
        for result in (recent, detail):
            self.assertEqual(result['client_ip'], '2001:db8::42')
            self.assertEqual(result['feedback']['reason'], 'incorrect')
            self.assertEqual(result['feedback']['respondent_name'], 'Test Kullanıcı')
            self.assertEqual(result['feedback']['comment'], 'Sorunun ayrıntısı')
        self.config.monitor_show_query_details = False
        hidden = self.client.get('/monitor/metrics').json()['recent_queries'][0]
        self.assertNotIn('client_ip', hidden)
        self.assertNotIn('feedback', hidden)
        self.assertEqual(self.client.get('/monitor/queries/' + self.query_id).status_code, 404)

    def test_anonymous_legacy_votes_and_updates_clear_old_details(self):
        body = {'query_id': self.query_id, 'rating': 'down', 'reason': 'outdated'}
        self.assertEqual(self.client.post('/feedback', json=body).json(), {'ok': True})
        self.assertIsNone(monitoring.query_detail(self.query_id)['feedback']['respondent_name'])
        self.assertEqual(self.client.post('/feedback', json={
            'query_id': self.query_id, 'rating': 'up'}).json(), {'ok': True})
        saved = monitoring.query_detail(self.query_id)['feedback']
        self.assertEqual(saved['rating'], 'up')
        self.assertIsNone(saved['reason'])
        with monitoring.connect() as connection:
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM feedback').fetchone()[0], 1)
        self.assertEqual(self.client.post('/feedback', json={
            'query_id': 'b' * 32, 'rating': 'down'}).json(), {'ok': False})

    def test_invalid_reason_name_and_positive_reason_are_rejected(self):
        for extra in ({'reason': 'unknown'}, {'respondent_name': 'x' * 121},
                      {'reason': 'other'}, {'reason': 'other', 'comment': '  '},
                      {'reason': 'other', 'comment': 'x' * 2001},
                      {'rating': 'up', 'reason': 'incorrect'}):
            response = self.client.post('/feedback', json={
                'query_id': self.query_id, 'rating': 'down', **extra})
            self.assertEqual(response.status_code, 422)
        self.assertIsNone(monitoring.query_detail(self.query_id)['feedback'])

    def test_chat_ip_uses_trusted_connection_and_stays_out_of_public_response(self):
        def answer(question, **kwargs):
            telemetry.log_query({'id': self.query_id, 'question': question, 'answer': 'Test'})
            return ChatResponse(query_id=self.query_id, answer='Test', sources=[], latency_ms=1)
        proxy_app = ProxyHeadersMiddleware(main.app, trusted_hosts=['127.0.0.1'])
        cases = [('203.0.113.10', '198.51.100.99', '203.0.113.10'),
                 ('127.0.0.1', '2001:db8::42', '2001:db8::42')]
        with patch.object(main.pipeline, 'answer', side_effect=answer):
            for peer, forwarded, expected in cases:
                with TestClient(proxy_app, client=(peer, 50000)) as client:
                    response = client.post('/chat', json={'question': 'Test sorusu'},
                                           headers={'X-Forwarded-For': forwarded, 'X-Real-IP': '192.0.2.99'})
                self.assertEqual(response.status_code, 200)
                self.assertNotIn('client_ip', response.json())
                self.assertEqual(monitoring.query_detail(self.query_id)['client_ip'], expected)
                saved = json.loads((self.config.log_path / 'queries.jsonl').read_text().splitlines()[-1])
                self.assertEqual(saved['client_ip'], expected)

    def test_parallel_requests_do_not_mix_ips_and_context_is_reset(self):
        barrier = Barrier(2)
        def record(pair):
            query_id, ip = pair
            with telemetry.client_scope(ip):
                barrier.wait(timeout=5)
                telemetry.log_query({'id': query_id, 'question': 'Test'})
            telemetry.log_query({'id': query_id.upper(), 'question': 'İstek dışında'})
        pairs = [('b' * 32, '192.0.2.1'), ('c' * 32, '2001:db8::1')]
        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(record, pairs))
        for query_id, ip in pairs:
            self.assertEqual(monitoring.query_detail(query_id)['client_ip'], ip)
            self.assertIsNone(monitoring.query_detail(query_id.upper())['client_ip'])


class FeedbackMigrationTests(unittest.TestCase):
    def test_legacy_database_migrates_idempotently_without_losing_votes(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Settings(_env_file=None, db_path=str(Path(directory) / 'legacy.db'),
                              log_dir=str(Path(directory) / 'logs'))
            old_schema = telemetry._SCHEMA.replace(',\n    client_ip       TEXT', '')
            old_schema = old_schema.replace('    reason    TEXT,\n    respondent_name TEXT,\n', '')
            with sqlite3.connect(config.db_file) as connection:
                connection.executescript(old_schema)
                connection.execute('INSERT INTO queries (id,ts,question,answer) VALUES (?,?,?,?)',
                                   ('a' * 32, monitoring.utc_now(), 'Eski soru', 'Eski yanıt'))
                connection.execute('INSERT INTO feedback (query_id,rating,comment,ts) VALUES (?,?,?,?)',
                                   ('a' * 32, 'down', 'Eski yorum', monitoring.utc_now()))
            with patch.object(telemetry, 'settings', config), patch.object(monitoring, 'settings', config):
                monitoring.initialize()
                monitoring.initialize()
                detail = monitoring.query_detail('a' * 32)
                self.assertEqual(detail['question'], 'Eski soru')
                self.assertIsNone(detail['client_ip'])
                self.assertEqual(detail['feedback']['comment'], 'Eski yorum')
                self.assertIsNone(detail['feedback']['reason'])
                self.assertTrue(telemetry.log_feedback('a' * 32, 'down', reason='outdated'))
                self.assertEqual(monitoring.query_detail('a' * 32)['feedback']['reason'], 'outdated')


if __name__ == '__main__':
    unittest.main()
