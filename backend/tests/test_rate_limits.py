"""Kalıcı panel sınırları, çalışan işler ve atomik yönetici güncellemeleri."""
import json
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app import main, monitor_auth, monitoring, rate_limits, telemetry
from app.abuse import AbuseGuard, Denied
from app.config import Settings


class RateLimitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.password = monitor_auth.password_hash('rate-test-password')

    def setUp(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.config = Settings(_env_file=None, db_path=str(root / 'test.db'), log_dir=str(root / 'logs'),
                               monitor_password_hash=self.password, monitor_session_secret='s' * 64)
        for module in (main, monitor_auth, monitoring, telemetry):
            self.enterContext(patch.object(module, 'settings', self.config))
        self.client = self.enterContext(TestClient(main.app))
        self.guard = main.app.state.abuse
        self.now = 1800000000.0
        self.guard.clock = lambda: self.now

    def update(self, **changes):
        current = self.guard.limit_settings()
        return self.guard.update_limits(rate_limits.Update(**{
            **current['limits'], 'revision': current['revision'], **changes}), 'adminbakai')

    def login(self):
        self.assertEqual(self.client.post('/monitor/login', json={
            'username': 'adminbakai', 'password': 'rate-test-password'}).status_code, 200)

    def test_private_api_origin_validation_and_stale_revision(self):
        body = {**rate_limits.defaults(self.config), 'revision': 0}
        for method in ('GET', 'PUT'):
            response = self.client.request(method, '/monitor/rate-limits', json=body if method == 'PUT' else None)
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.headers['cache-control'], 'no-store')
        self.login()
        self.assertEqual(self.client.put('/monitor/rate-limits', json=body,
                         headers={'Origin': 'https://foreign.example'}).status_code, 403)
        for change in ({'rate_chat_per_minute': 0}, {'rate_chat_concurrent': 17},
                       {'rate_chat_per_minute': '2'}, {'rate_chat_per_minute': True},
                       {'rate_chat_per_minute': 121}, {'rate_chat_concurrent_per_ip': 3}, {'extra': 1}):
            self.assertEqual(self.client.put('/monitor/rate-limits', json={**body, **change}).status_code, 422)
        response = self.client.put('/monitor/rate-limits', json=body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['updated_by'], 'adminbakai')
        self.assertEqual(self.client.put('/monitor/rate-limits', json=body).status_code, 409)

    def test_changes_take_effect_without_resetting_minute_or_hour_counts(self):
        self.guard.admit('chat', 'client')
        self.update(rate_chat_per_minute=1, rate_chat_per_hour=2)
        with self.assertRaises(Denied) as blocked:
            self.guard.admit('chat', 'client')
        self.assertEqual(blocked.exception.reason, 'ip_minute')
        self.update(rate_chat_per_minute=2)
        self.guard.admit('chat', 'client')
        self.now += 60
        with self.assertRaises(Denied) as blocked:
            self.guard.admit('chat', 'client')
        self.assertEqual(blocked.exception.reason, 'ip_hour')
        self.assertEqual(blocked.exception.retry, 3540)

    def test_global_minute_and_rolling_day_are_dynamic(self):
        self.guard.admit('chat', 'first')
        self.update(rate_chat_global_per_minute=1, rate_chat_global_per_day=1)
        with self.assertRaises(Denied) as blocked:
            self.guard.admit('chat', 'second')
        self.assertEqual(blocked.exception.reason, 'global_minute')
        with self.guard.processing('first'):
            pass
        self.update(rate_chat_global_per_minute=2)
        with self.assertRaises(HTTPException) as blocked:
            with self.guard.processing('second'):
                self.fail('Günlük kota kaybolmamalı')
        self.assertEqual(blocked.exception.status_code, 429)
        self.update(rate_chat_global_per_day=2)
        with self.guard.processing('second'):
            pass
        self.assertEqual(self.guard.snapshot()['daily_used'], 2)

    def test_lower_concurrency_preserves_running_work_and_releases_slots(self):
        with self.guard.processing('first'):
            with self.guard.processing('second'):
                self.update(rate_chat_concurrent=1, rate_chat_concurrent_per_ip=1)
                self.assertEqual(self.guard.active, 2)
                with self.assertRaises(HTTPException):
                    with self.guard.processing('third'):
                        self.fail('Yeni iş kabul edilmemeli')
            self.assertEqual(self.guard.active, 1)
        with self.guard.processing('third'):
            with self.assertRaises(HTTPException):
                with self.guard.processing('third'):
                    self.fail('IP sınırı geçerli olmalı')
        self.assertEqual((self.guard.active, self.guard.clients), (0, {}))

    def test_restart_and_another_guard_see_saved_policy_and_audit(self):
        self.guard.admit('chat', 'client')
        self.update(rate_chat_per_minute=1)
        self.config.rate_chat_per_minute = 50
        restarted = AbuseGuard(self.config, clock=lambda: self.now)
        self.assertEqual(restarted.limit_settings()['limits']['rate_chat_per_minute'], 1)
        with self.assertRaises(Denied):
            restarted.admit('chat', 'client')
        self.update(rate_chat_per_minute=2)
        restarted.admit('chat', 'client')
        with self.guard.connect() as connection:
            rows = connection.execute('SELECT revision,payload,updated_by FROM rate_settings_history ORDER BY revision').fetchall()
        self.assertEqual([row[0] for row in rows], [1, 2])
        self.assertEqual(json.loads(rows[0][1])['rate_chat_per_minute'], 1)
        self.assertEqual(rows[1][2], 'adminbakai')

    def test_concurrent_writers_have_one_winner(self):
        other = AbuseGuard(self.config)
        body = rate_limits.Update(**rate_limits.defaults(self.config), revision=0)
        def save(guard):
            try:
                guard.update_limits(body, 'admin')
                return True
            except rate_limits.Conflict:
                return False
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sorted(pool.map(save, [self.guard, other])), [False, True])

    def test_failed_audit_rolls_back_and_corrupt_settings_fail_closed(self):
        with self.guard.connect() as connection:
            connection.execute("CREATE TRIGGER fail_audit BEFORE INSERT ON rate_settings_history BEGIN SELECT RAISE(ABORT, 'test'); END")
        with self.assertRaises(sqlite3.Error):
            self.update(rate_chat_per_minute=1)
        self.assertEqual(self.guard.limit_settings()['revision'], 0)
        with self.guard.connect() as connection:
            connection.execute("INSERT INTO rate_settings VALUES (1,'{}',1,'now','admin')")
        with self.assertRaises(Denied) as blocked:
            self.guard.admit('chat', 'client')
        self.assertEqual(blocked.exception.status, 503)
        with self.assertRaises(HTTPException) as blocked:
            with self.guard.processing('client'):
                self.fail('Bozuk sınırlarla LLM çağrılmamalı')
        self.assertEqual(blocked.exception.status_code, 503)
        self.assertEqual(self.guard.active, 0)
