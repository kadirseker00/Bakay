"""Düzeltme → taslak → kaynaklı onay → golden dataset zinciri."""
import json
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import golden, knowledge, main, monitor_auth, monitoring, telemetry
from app.config import Settings
from app.schemas import ChatResponse


class GoldenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.password = monitor_auth.password_hash('golden-test-password')

    def setUp(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.config = Settings(_env_file=None, db_path=str(root / 'test.db'), log_dir=str(root / 'logs'),
                               monitor_password_hash=self.password, monitor_session_secret='s' * 64)
        for module in (main, monitor_auth, monitoring, telemetry):
            self.enterContext(patch.object(module, 'settings', self.config))
        self.client = self.enterContext(TestClient(main.app))
        self.query_id = 'a' * 32
        self.history = [{'role': 'user', 'content': 'Ders saydırma koşulları nelerdir?'},
                        {'role': 'assistant', 'content': 'Hangi öğrenim düzeyi için?'}]
        telemetry.log_query({'id': self.query_id, 'question': 'Lisans için?', 'answer': 'Yanlış yanıt',
                             'history': self.history, 'model': 'test-model', 'client_ip': '192.0.2.42',
                             'prompt': 'Gizli prompt', 'sources': [{'document': 'eski.pdf'}]})
        self.body = {'query_id': self.query_id, 'rating': 'down', 'reason': 'incorrect',
                     'correction_question': 'Lisans ders saydırma koşulları nelerdir?',
                     'correction_answer': 'Önerilen düzeltme',
                     'correction_source': 'https://manas.edu.kg/tr/mevzuat',
                     'respondent_name': 'Test kullanıcı'}

    def submit(self, **changes):
        return self.client.post('/feedback', json={**self.body, **changes})

    def login(self):
        self.assertEqual(self.client.post('/monitor/login', json={
            'username': 'adminbakai', 'password': 'golden-test-password'}).status_code, 200)

    def approve(self, answer_id, **changes):
        item = next(item for item in knowledge.list_answers(self.config.db_file) if item['id'] == answer_id)
        body = {key: item[key] for key in knowledge.KnowledgeInput.model_fields}
        body.update(status='published', answer='Yönetici tarafından düzeltilmiş yanıt',
                    reviewed_on=knowledge.today().isoformat(),
                    valid_until=(knowledge.today() + timedelta(days=30)).isoformat())
        return knowledge.save(self.config.db_file, knowledge.KnowledgeInput(**{**body, **changes}), 'reviewer', answer_id)

    def test_public_submission_creates_private_draft_and_preserves_provenance(self):
        response = self.submit()
        self.assertEqual(response.json(), {'ok': True})
        self.assertNotIn('knowledge_id', response.text)
        items = knowledge.list_answers(self.config.db_file)
        self.assertEqual(len(items), 1)
        self.assertEqual((items[0]['status'], items[0]['approved_by']), ('draft', None))
        self.assertEqual(items[0]['question'], self.body['correction_question'])
        self.assertEqual(items[0]['answer'], self.body['correction_answer'])
        self.assertIsNone(knowledge.lookup(self.config.db_file, items[0]['question']))
        proposal = golden.list_candidates(self.config.db_file)[0]
        self.assertEqual(proposal['original_question'], 'Lisans için?')
        self.assertEqual(proposal['history'], self.history)
        self.assertEqual(proposal['original_answer'], 'Yanlış yanıt')
        self.assertEqual(proposal['review_status'], 'pending')
        self.assertEqual(golden.export_dataset(self.config.db_file), '')
        for path in ('/monitor/golden', '/monitor/golden/export'):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.headers['cache-control'], 'no-store')
        self.login()
        self.assertEqual(self.client.get('/monitor/golden').json()['items'][0]['knowledge_id'], items[0]['id'])

    def test_on_approval_export_uses_reviewed_answer_and_revision_without_identity_metadata(self):
        self.submit()
        entry = knowledge.list_answers(self.config.db_file)[0]
        self.approve(entry['id'], question='Yöneticinin açık sorusu?')
        self.login()
        response = self.client.get('/monitor/golden/export')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['cache-control'], 'no-store')
        self.assertIn('attachment', response.headers['content-disposition'])
        record = json.loads(response.text)
        self.assertEqual(record['question'], 'Yöneticinin açık sorusu?')
        self.assertEqual(record['reference_answer'], 'Yönetici tarafından düzeltilmiş yanıt')
        self.assertEqual(record['knowledge_revision'], 2)
        self.assertEqual(record['approved_by'], 'reviewer')
        self.assertEqual(record['proposed_answer'], self.body['correction_answer'])
        self.assertEqual(record['split'], 'development')
        for value in ('192.0.2.42', 'Test kullanıcı', 'Gizli prompt', 'fingerprint'):
            self.assertNotIn(value, response.text)
        self.assertEqual(golden.list_candidates(self.config.db_file)[0]['review_status'], 'approved')

    def test_expired_archived_and_unpublished_are_not_exported(self):
        self.submit()
        entry = knowledge.list_answers(self.config.db_file)[0]
        published = self.approve(entry['id'])
        with patch.object(knowledge, 'today', return_value=knowledge.today() + timedelta(days=31)):
            self.assertEqual(golden.export_dataset(self.config.db_file), '')
            self.assertEqual(golden.list_candidates(self.config.db_file)[0]['review_status'], 'pending')
        body = {key: published[key] for key in knowledge.KnowledgeInput.model_fields}
        for status in ('draft', 'archived'):
            published = knowledge.save(self.config.db_file, knowledge.KnowledgeInput(**{**body,
                'status': status, 'revision': published['revision']}), 'reviewer', entry['id'])
            self.assertEqual(golden.export_dataset(self.config.db_file), '')

    def test_retries_do_not_duplicate_or_overwrite_administrator_changes(self):
        self.submit()
        entry = knowledge.list_answers(self.config.db_file)[0]
        self.approve(entry['id'])
        self.assertTrue(self.submit().json()['ok'])
        self.assertEqual(len(knowledge.list_answers(self.config.db_file)), 1)
        current = knowledge.list_answers(self.config.db_file)[0]
        self.assertEqual(current['revision'], 2)
        self.assertEqual(current['status'], 'published')
        self.assertEqual(current['answer'], 'Yönetici tarafından düzeltilmiş yanıt')
        self.submit(correction_answer='Farklı bir öneri')
        self.assertEqual(len(knowledge.list_answers(self.config.db_file)), 2)
        self.assertEqual(len(golden.list_candidates(self.config.db_file)), 2)

    def test_parallel_retries_are_atomic(self):
        def save(_):
            return telemetry.log_feedback(**self.body)
        with ThreadPoolExecutor(max_workers=4) as pool:
            self.assertTrue(all(pool.map(save, range(8))))
        self.assertEqual(len(knowledge.list_answers(self.config.db_file)), 1)
        self.assertEqual(len(golden.list_candidates(self.config.db_file)), 1)
        with knowledge.connect(self.config.db_file) as connection:
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM feedback').fetchone()[0], 1)

    def test_failure_rolls_back_feedback_candidate_and_knowledge_revision_together(self):
        with knowledge.connect(self.config.db_file) as connection:
            connection.execute("CREATE TRIGGER fail_candidate BEFORE INSERT ON feedback_corrections BEGIN SELECT RAISE(ABORT, 'test'); END")
        self.assertEqual(self.submit().json(), {'ok': False})
        self.assertEqual(knowledge.list_answers(self.config.db_file), [])
        self.assertIsNone(monitoring.query_detail(self.query_id)['feedback'])
        with knowledge.connect(self.config.db_file) as connection:
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM knowledge_revisions').fetchone()[0], 0)

    def test_legacy_votes_unknown_queries_optional_source_and_invalid_input(self):
        for change in ({'rating': 'up'}, {'correction_question': None}, {'correction_answer': None},
                       {'correction_question': '  '}, {'correction_answer': 'x' * 12001},
                       {'correction_source': 'https://manas.edu.kg.evil.test/x'},
                       {'correction_source': 'javascript:alert(1)'}):
            self.assertEqual(self.submit(**change).status_code, 422)
        self.assertFalse(self.submit(query_id='b' * 32).json()['ok'])
        self.assertEqual(knowledge.list_answers(self.config.db_file), [])
        self.assertTrue(self.client.post('/feedback', json={'query_id': self.query_id, 'rating': 'down'}).json()['ok'])
        self.assertEqual(golden.list_candidates(self.config.db_file), [])
        self.assertTrue(self.submit(correction_source=None).json()['ok'])
        self.assertEqual(knowledge.list_answers(self.config.db_file)[0]['sources'], [])
        self.assertEqual(golden.export_dataset(self.config.db_file), '')

    def test_history_is_recorded_for_json_and_streamed_chat(self):
        def answer(question, **kwargs):
            query_id = telemetry.new_query_id()
            telemetry.log_query({'id': query_id, 'question': question, 'answer': 'Test'})
            return ChatResponse(query_id=query_id, answer='Test', sources=[], latency_ms=1)
        with patch.object(main.pipeline, 'answer', side_effect=answer):
            for headers in ({}, {'Accept': 'text/event-stream'}):
                response = self.client.post('/chat', json={'question': 'Lisans için?', 'history': self.history}, headers=headers)
                self.assertEqual(response.status_code, 200)
        with knowledge.connect(self.config.db_file) as connection:
            rows = connection.execute('SELECT history_json FROM queries WHERE id<>?', (self.query_id,)).fetchall()
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(json.loads(row[0]) == self.history for row in rows))
        telemetry.log_query({'id': 'c' * 32, 'question': 'Bağlam dışında'})
        with knowledge.connect(self.config.db_file) as connection:
            self.assertEqual(json.loads(connection.execute('SELECT history_json FROM queries WHERE id=?', ('c' * 32,)).fetchone()[0]), [])

    def test_legacy_history_column_is_added_without_data_loss(self):
        with knowledge.connect(self.config.db_file) as connection:
            connection.execute('ALTER TABLE queries DROP COLUMN history_json')
        with telemetry._connect() as connection:
            self.assertIsNone(connection.execute('SELECT history_json FROM queries WHERE id=?', (self.query_id,)).fetchone()[0])
        self.assertTrue(self.submit().json()['ok'])
        self.assertEqual(golden.list_candidates(self.config.db_file)[0]['history'], [])
