"""Canlı aşamalar, normal JSON uyumu ve iş kotasının gerçek iş ömrü."""
import asyncio
import json
from pathlib import Path
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app import main, monitoring, telemetry
from app.abuse import AbuseGuard
from app.config import Settings
from app.rag import pipeline
from app.rag.progress import progress_scope, report
from app.schemas import ChatRequest, ChatResponse


class ChatStreamTests(unittest.TestCase):
    def setUp(self):
        directory = self.enterContext(tempfile.TemporaryDirectory())
        self.config = Settings(_env_file=None, db_path=str(Path(directory) / 'test.db'),
                               log_dir=str(Path(directory) / 'logs'), rate_chat_concurrent_per_ip=1)
        for module in (main, monitoring, telemetry):
            self.enterContext(patch.object(module, 'settings', self.config))
        self.client = self.enterContext(TestClient(main.app))
        self.result = ChatResponse(query_id='1' * 32, answer='Örnek yanıt', sources=[], latency_ms=42)

    def test_stream_contract_and_json_compatibility(self):
        def answer(*args, **kwargs):
            report('searching', 'Belgelere bakıyorum', 'İlgili bilgileri arıyorum.')
            return self.result
        with patch.object(main.pipeline, 'answer', side_effect=answer):
            streamed = self.client.post('/chat', json={'question': 'Kayıt nasıl yapılır?'},
                                        headers={'Accept': 'text/event-stream'})
            normal = self.client.post('/chat', json={'question': 'Kayıt nasıl yapılır?'})
        self.assertEqual(normal.json(), self.result.model_dump())
        self.assertTrue(streamed.headers['content-type'].startswith('text/event-stream'))
        frames = streamed.text.strip().split('\n\n')
        self.assertEqual(frames[0].splitlines()[0], 'event: status')
        self.assertIn('İlgili bilgileri', frames[0])
        self.assertEqual(json.loads(frames[-1].split('data: ', 1)[1]), normal.json())
        self.assertEqual(main.app.state.abuse.active, 0)
        with monitoring.connect() as connection:
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM monitor_events').fetchone()[0], 2)

    def test_busy_and_captcha_errors_stay_http_errors(self):
        guard = main.app.state.abuse
        key = guard.client_key('testclient')
        with guard.processing(key), patch.object(pipeline, 'answer') as answer:
            response = self.client.post('/chat', json={'question': 'Soru'},
                                        headers={'Accept': 'text/event-stream'})
            self.assertEqual(response.status_code, 429)
            self.assertIn('Retry-After', response.headers)
            answer.assert_not_called()
        with patch.object(main.captcha, 'require', side_effect=HTTPException(
            403, {'code': 'captcha_required', 'site_key': 'test-key'},
        )), patch.object(pipeline, 'answer') as answer:
            response = self.client.post('/chat', json={'question': 'Soru'},
                                        headers={'Accept': 'text/event-stream'})
            self.assertEqual(response.status_code, 403)
            answer.assert_not_called()

    def test_worker_failure_sends_safe_error_and_releases_slot(self):
        with patch.object(pipeline, 'answer', side_effect=RuntimeError('PRIVATE-DETAIL')), \
             self.assertLogs('app.main', level='ERROR'):
            response = self.client.post('/chat', json={'question': 'Soru'},
                                        headers={'Accept': 'text/event-stream'})
        self.assertIn('event: error', response.text)
        self.assertNotIn('PRIVATE-DETAIL', response.text)
        self.assertNotIn('event: result', response.text)
        self.assertEqual(main.app.state.abuse.active, 0)
        with monitoring.connect() as connection:
            self.assertEqual(connection.execute('SELECT status FROM monitor_events').fetchone()[0], 500)

    def test_status_arrives_before_answer_and_disconnect_keeps_slot_until_work_finishes(self):
        guard = AbuseGuard(self.config)
        release, finished = threading.Event(), threading.Event()
        request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(abuse=guard)),
                                  state=SimpleNamespace(rate_client='test-key'))
        def answer(*args, **kwargs):
            report('searching', 'Belgelere bakıyorum', 'Arıyorum.')
            if not release.wait(3):
                raise TimeoutError('Test yanıtı serbest bırakılmadı')
            return self.result

        async def check():
            response = main.stream_chat(ChatRequest(question='Soru'), request, '192.0.2.1')
            try:
                first = await asyncio.wait_for(anext(response.body_iterator), 1)
                self.assertIn('event: status', first)
                self.assertFalse(release.is_set())
                await response.body_iterator.aclose()
                self.assertEqual(guard.active, 1)
            finally:
                release.set()
                self.assertTrue(await asyncio.to_thread(finished.wait, 2))
            self.assertEqual(guard.active, 0)

        original_processing = guard.processing
        from contextlib import contextmanager
        @contextmanager
        def processing(client):
            try:
                with original_processing(client):
                    yield
            finally:
                finished.set()
        with patch.object(pipeline, 'answer', side_effect=answer), patch.object(guard, 'processing', processing):
            asyncio.run(check())

    def test_real_pipeline_reports_only_executed_steps(self):
        llm = Mock()
        llm.generate.return_value = 'Ödünç süresi 14 gündür.'
        hits = [{'document': 'test.pdf', 'title': 'Kütüphane Yönergesi',
                 'text': 'Ödünç süresi 14 gündür.', 'score': 0.9}]
        with patch.object(pipeline, 'get_llm', return_value=llm), \
             patch.object(pipeline, 'get_store') as store, patch.object(pipeline, '_log'), \
             patch.multiple(pipeline.settings, agent_route=False, agent_rewrite=False,
                            agent_verify=False, score_threshold=0.3):
            stages = []
            store.return_value.query.return_value = hits
            with progress_scope(lambda event: stages.append(event['stage'])):
                pipeline.answer('Kütüphanede ödünç süresi kaç gündür?')
            self.assertEqual(stages, ['preparing', 'searching', 'evaluating', 'generating', 'finishing'])
            stages.clear()
            store.return_value.query.return_value = []
            with progress_scope(lambda event: stages.append(event['stage'])):
                pipeline.answer('Kaynak bulunamayan soru')
            self.assertEqual(stages, ['preparing', 'searching', 'evaluating'])


if __name__ == '__main__':
    unittest.main()
