"""Doğrulama, oturum tekrarı, sahiplik, ağ sınırı ve atomik bütçe."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import httpx
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app import budget, captcha, main, monitoring, telemetry, visitor
from app.abuse import AbuseGuard
from app.config import Settings
from app.rag import llm
from app.schemas import ChatResponse


class VisitorTests(unittest.TestCase):
    def setUp(self):
        directory = self.enterContext(tempfile.TemporaryDirectory())
        self.config = Settings(_env_file=None, db_path=str(Path(directory)/'test.db'),
            log_dir=str(Path(directory)/'logs'), public_security_enabled=True,
            monitor_session_secret='S'*48, monitor_public_url='https://bakai.example',
            captcha_site_key='public-site', captcha_secret_key='PRIVATE-TEST', captcha_hostname='bakai.example',
            rate_chat_per_minute=100, rate_chat_per_hour=1000, rate_chat_global_per_minute=1000)
        for module in (main, monitoring, telemetry):
            self.enterContext(patch.object(module, 'settings', self.config))
        self.client = self.enterContext(TestClient(main.app, base_url='https://bakai.example', client=('192.0.2.1', 50000)))
        self.client.headers['Origin'] = 'https://bakai.example'
        self.result = ChatResponse(query_id='1'*32, answer='Kaynaklı yanıt', sources=[], latency_ms=1)
        self.answer = self.enterContext(patch.object(main.pipeline, 'answer', return_value=self.result))
        self.verify = self.enterContext(patch.object(captcha, 'verify', return_value=True))

    def proof(self, token='unique-proof'):
        return self.client.post('/session', json={'token': token})

    def chat(self, **kwargs):
        return self.client.post('/chat', json={'question': 'Kayıt nasıl yapılır?'}, **kwargs)

    def test_first_request_and_fake_captcha_never_reach_model_json_or_sse(self):
        for accept in ('application/json', 'text/event-stream'):
            response = self.client.post('/chat', json={'question': 'Soru', 'captcha_token': 'made-up'}, headers={'Accept': accept})
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()['detail']['code'], 'captcha_required')
        self.answer.assert_not_called()
        self.verify.assert_not_called()

    def test_valid_proof_sets_secure_cookie_allows_json_and_sse(self):
        proof = self.proof()
        self.assertEqual(proof.status_code, 200)
        for value in ('HttpOnly', 'Secure', 'SameSite=strict', 'Max-Age=1800'):
            self.assertIn(value, proof.headers['set-cookie'])
        self.assertEqual(self.chat().json()['answer'], self.result.answer)
        self.assertIn('event: result', self.chat(headers={'Accept': 'text/event-stream'}).text)
        self.assertEqual(self.verify.call_count, 1)

    def test_missing_foreign_origin_cross_site_rejected_even_with_cookie(self):
        self.proof()
        for origin in ('', 'https://evil.example'):
            self.assertEqual(self.chat(headers={'Origin': origin}).status_code, 403)
        self.assertEqual(self.chat(headers={'Sec-Fetch-Site': 'cross-site'}).status_code, 403)
        self.answer.assert_not_called()

    def test_forged_expired_different_ip_or_browser_cookie_rejected(self):
        self.proof()
        cookie = self.client.cookies.get(visitor.COOKIE)
        self.client.cookies.set(visitor.COOKIE, cookie[:-1]+'X', domain='bakai.example', path='/')
        self.assertEqual(self.chat().status_code, 403)
        self.client.cookies.set(visitor.COOKIE, cookie, domain='bakai.example', path='/')
        self.assertEqual(self.chat(headers={'User-Agent': 'other-browser'}).status_code, 403)
        guard = main.app.state.abuse
        now = guard.clock()
        with patch.object(guard, 'clock', return_value=now+1801):
            self.assertEqual(self.chat().status_code, 403)
        with patch.object(guard, 'client_key', return_value='another-ip'):
            self.assertEqual(self.chat().status_code, 403)
        self.answer.assert_not_called()

    def test_proof_replay_rejected_after_restart_without_provider_call(self):
        self.assertEqual(self.proof().status_code, 200)
        main.app.state.abuse = AbuseGuard(self.config)
        self.assertEqual(self.proof().status_code, 403)
        self.assertEqual(self.verify.call_count, 1)

    def test_invalid_proof_missing_configuration_fail_closed(self):
        self.verify.return_value = False
        self.assertEqual(self.proof().status_code, 403)
        self.assertEqual(self.chat().status_code, 403)
        self.config.captcha_secret_key = ''
        self.assertEqual(self.proof('different').status_code, 503)
        self.assertEqual(self.chat().status_code, 503)
        self.answer.assert_not_called()

    def test_missing_configuration_invalidates_already_valid_session(self):
        self.proof()
        self.config.captcha_secret_key = ''
        self.assertEqual(self.chat().status_code, 503)
        self.answer.assert_not_called()

    def test_parallel_identical_proofs_validate_only_once(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            statuses = list(pool.map(lambda _: self.proof().status_code, range(4)))
        self.assertEqual(statuses.count(200), 1)
        self.assertEqual(statuses.count(403), 3)
        self.assertEqual(self.verify.call_count, 1)

    def test_session_quota_and_ip_quota_survive_cookie_replacement(self):
        self.proof()
        for _ in range(30):
            self.assertEqual(self.chat().status_code, 200)
        self.assertEqual(self.chat().status_code, 429)
        self.config.rate_chat_per_minute = 32
        self.assertEqual(self.proof('second-proof').status_code, 200)
        self.assertEqual(self.chat().status_code, 200)
        self.assertEqual(self.chat().status_code, 429)
        self.assertEqual(self.answer.call_count, 31)

    def test_feedback_only_for_own_query_in_current_session(self):
        with patch.object(telemetry, 'log_feedback', return_value=True) as log:
            data = {'query_id': '1'*32, 'rating': 'up'}
            self.assertEqual(self.client.post('/feedback', json=data).status_code, 403)
            self.proof()
            self.assertEqual(self.client.post('/feedback', json=data).status_code, 403)
            self.chat()
            self.assertTrue(self.client.post('/feedback', json=data).json()['ok'])
            self.proof('another-proof')
            self.assertEqual(self.client.post('/feedback', json=data).status_code, 403)
            self.assertEqual(log.call_count, 1)

    def test_panel_docs_stats_restricted_independent_of_login(self):
        for path in ('/monitor/login', '/monitor/metrics', '/stats', '/stats/', '/docs', '/docs/oauth2-redirect', '/redoc', '/openapi.json'):
            self.assertEqual(self.client.get(path).status_code, 403)
        self.config.monitor_allowed_networks = '192.0.2.0/24'
        self.assertEqual(self.client.get('/openapi.json').status_code, 200)
        self.assertNotEqual(self.client.get('/monitor/metrics').status_code, 200)
        self.config.monitor_allowed_networks = ''
        self.assertEqual(self.client.get('/openapi.json').status_code, 403)

    def test_budget_message_preserved_in_stream(self):
        self.proof()
        self.answer.side_effect = HTTPException(429, {'code': 'budget_exhausted', 'message': 'Günlük bütçe doldu.'})
        response = self.chat(headers={'Accept': 'text/event-stream'})
        self.assertIn('Günlük bütçe doldu.', response.text)
        self.assertEqual(main.app.state.abuse.active, 0)

    def test_corrections_capped_atomically_per_query(self):
        with monitoring.connect() as connection:
            connection.execute('INSERT INTO queries (id,ts,question) VALUES (?,?,?)', ('1'*32, monitoring.utc_now(), 'Özgün soru'))
        def submit(index):
            return telemetry.log_feedback('1'*32, 'down', correction_question='Düzeltilecek soru', correction_answer=f'Öneri {index}')
        with ThreadPoolExecutor(max_workers=6) as pool:
            self.assertEqual(sum(pool.map(submit, range(12))), 3)
        with monitoring.connect() as connection:
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM feedback_corrections').fetchone()[0], 3)


class BudgetTests(unittest.TestCase):
    def setUp(self):
        directory = self.enterContext(tempfile.TemporaryDirectory())
        self.config = Settings(_env_file=None, db_path=str(Path(directory)/'test.db'), budget_enabled=True,
                               anthropic_api_key='TEST', anthropic_model='claude-haiku-5-5')
        self.enterContext(patch.object(monitoring, 'settings', self.config))
        monitoring.initialize()
        self.now = datetime(2026, 11, 14, 17, 59, tzinfo=timezone.utc)
        self.meter = budget.Budget(self.config, clock=lambda: self.now)

    def reserve(self):
        return self.meter.reserve('claude-haiku-5-5', 'soru', 'talimat', 100)

    def test_atomic_reservations_cannot_exceed_limit_across_connections(self):
        self.reserve()
        cost = self.meter.snapshot()['used_and_reserved_usd']
        self.config.budget_daily_usd = cost*5
        def attempt(_):
            try:
                return self.reserve() is not None
            except HTTPException as error:
                self.assertEqual(error.status_code, 429)
                return False
        with ThreadPoolExecutor(max_workers=8) as pool:
            self.assertEqual(sum(pool.map(attempt, range(30))), 4)
        self.assertLessEqual(self.meter.snapshot()['used_and_reserved_usd'], self.config.budget_daily_usd)

    def test_unknown_errors_stay_reserved_after_restart_and_day_rollover(self):
        self.reserve()
        original = self.meter.snapshot()
        restarted = budget.Budget(self.config, clock=lambda: self.now)
        self.assertEqual(restarted.snapshot(), original)
        self.now += timedelta(minutes=2)
        self.assertEqual(restarted.snapshot()['used_and_reserved_usd'], 0)
        self.assertEqual(restarted.snapshot()['timezone'], 'Asia/Bishkek')

    def test_settle_releases_only_known_usage_and_cannot_be_replayed(self):
        first = self.reserve()
        self.meter.settle(first, 'claude-haiku-5-5', {'input_tokens': 10, 'output_tokens': 2})
        charged = self.meter.snapshot()['used_and_reserved_usd']
        self.assertEqual(charged, 0.000002)
        self.meter.settle(first, 'claude-haiku-5-5', {'input_tokens': 0, 'output_tokens': 0})
        self.assertEqual(self.meter.snapshot()['used_and_reserved_usd'], charged)
        second = self.reserve()
        self.meter.settle(second, 'unknown-model', {})
        self.assertEqual(self.meter.snapshot()['pending_calls'], 1)

    def test_existing_spend_and_unknown_old_cost_not_ignored(self):
        self.now = datetime.now(timezone.utc)
        with monitoring.connect() as connection:
            connection.execute('INSERT INTO llm_calls (ts,query_id,model,status,latency_ms,cost_usd) VALUES (?,?,?,?,?,?)',
                               (self.now.isoformat(), '1'*32, 'claude-haiku-5-5', 'ok', 1, 4.999))
        with self.assertRaises(HTTPException) as error:
            self.reserve()
        self.assertEqual(error.exception.detail['code'], 'budget_exhausted')
        with monitoring.connect() as connection:
            connection.execute('UPDATE llm_calls SET cost_usd=NULL')
        with self.assertRaises(HTTPException):
            self.reserve()

    def test_unpriced_model_broken_database_and_overrun_fail_closed(self):
        with self.assertRaises(HTTPException):
            self.meter.reserve('new-unpriced-model', 'soru', None, 1)
        first = self.reserve()
        self.meter.settle(first, 'claude-haiku-5-5', {'input_tokens': 1000000, 'output_tokens': 1000000})
        with self.assertRaises(HTTPException):
            self.reserve()
        self.config.db_path = str(self.config.db_file/'no-directory'/'test.db')
        with self.assertRaises(HTTPException) as error:
            self.reserve()
        self.assertEqual(error.exception.status_code, 503)

    def test_each_provider_call_reserved_including_followup_and_timeout(self):
        self.now = datetime.now(timezone.utc)
        with patch.object(llm, 'settings', self.config):
            client = llm.AnthropicLLM()
            self.addCleanup(client.http.close)
            with patch.object(client, '_generate_result', side_effect=httpx.ReadTimeout('unknown outcome')) as provider:
                for _ in range(2):
                    with self.assertRaises(httpx.ReadTimeout):
                        client.generate('soru', system='talimat')
                self.assertEqual(provider.call_count, 2)
            self.assertEqual(self.meter.snapshot()['pending_calls'], 2)
            self.config.budget_daily_usd = 0.000001
            with patch.object(client, '_generate_result') as provider:
                with self.assertRaises(HTTPException):
                    client.generate('soru')
                provider.assert_not_called()
