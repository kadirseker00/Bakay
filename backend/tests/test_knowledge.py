"""Hazır cevabın onayı, bağlam sınırı, atomik yayını ve sıfır model çağrısı."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient
from pydantic import ValidationError

from app import knowledge, main, monitor_auth, monitoring, telemetry
from app.config import Settings
from app.rag import pipeline
from app.schemas import ChatMessage


class KnowledgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.password = monitor_auth.password_hash('knowledge-test-password')

    def setUp(self):
        directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.config = Settings(_env_file=None, db_path=str(directory / 'test.db'), log_dir=str(directory / 'logs'),
                               monitor_password_hash=self.password, monitor_session_secret='s' * 64,
                               monitor_public_url='https://testserver')
        for module in (main, monitor_auth, monitoring, telemetry, pipeline):
            self.enterContext(patch.object(module, 'settings', self.config))
        self.client = self.enterContext(TestClient(main.app, base_url='https://testserver'))
        monitor_auth._attempts.clear()
        self.body = {'question': 'Hazırlık sınıfından muaf olabilir miyim?', 'variants': ['Hazırlığı atlayabilir miyim?'],
                     'answer': 'Dil muafiyet koşullarını sağlamanız gerekir.', 'status': 'published',
                     'sources': [{'url': 'https://oidb.manas.edu.kg/tr/faq/7', 'title': 'Hazırlık', 'snippet': 'Dil muafiyeti koşulları.'}],
                     'reviewed_on': knowledge.today().isoformat(), 'valid_until': (knowledge.today() + timedelta(days=30)).isoformat()}

    def login(self):
        response = self.client.post('/monitor/login', json={'username': 'adminbakai', 'password': 'knowledge-test-password'})
        self.assertEqual(response.status_code, 200)

    def create(self, **changes):
        return knowledge.save(self.config.db_file, knowledge.KnowledgeInput(**{**self.body, **changes}), 'adminbakai')

    def test_private_crud_and_origin(self):
        for method, path, body in [('GET', '', None), ('POST', '', self.body), ('PUT', '/missing', self.body), ('POST', '/examples', None)]:
            response = self.client.request(method, '/monitor/knowledge' + path, json=body)
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.headers['cache-control'], 'no-store')
        self.login()
        self.assertEqual(self.client.post('/monitor/knowledge', json=self.body, headers={'Origin': 'https://foreign.example'}).status_code, 403)
        response = self.client.post('/monitor/knowledge', json=self.body)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['approved_by'], 'adminbakai')
        self.assertEqual(len(self.client.get('/monitor/knowledge').json()['items']), 1)
        self.assertEqual(self.client.put('/monitor/knowledge/missing', json=self.body).status_code, 404)

    def test_publish_requires_source_answer_review_and_validity(self):
        self.login()
        for changes in ({'sources': []}, {'answer': ''}, {'reviewed_on': None}, {'valid_until': None},
                        {'valid_until': (knowledge.today() - timedelta(days=1)).isoformat()},
                        {'reviewed_on': (knowledge.today() + timedelta(days=1)).isoformat()}):
            self.assertEqual(self.client.post('/monitor/knowledge', json={**self.body, **changes}).status_code, 422)
        self.assertEqual(self.client.post('/monitor/knowledge', json={**self.body, 'status': 'draft', 'sources': [], 'answer': ''}).status_code, 201)

    def test_sources_and_duplicate_variants_validated(self):
        for url in ('https://manas.edu.kg.evil.test/a', 'javascript:alert(1)', 'https://user:pass@manas.edu.kg/a'):
            with self.assertRaises(ValidationError):
                knowledge.KnowledgeInput(**{**self.body, 'sources': [{**self.body['sources'][0], 'url': url}]})
        with self.assertRaises(ValidationError):
            knowledge.KnowledgeInput(**{**self.body, 'variants': [self.body['question'].translate(str.maketrans({'i': 'İ', 'ı': 'I'})).upper()]})

    def test_exact_turkish_matching_keeps_negations_numbers_and_scope(self):
        self.create()
        for question in (' HAZIRLIK SINIFINDAN MUAF OLABİLİR MİYİM?! ', 'Hazırlığı atlayabilir miyim', self.body['question']):
            self.assertIsNotNone(knowledge.lookup(self.config.db_file, question))
        for question in ('Hazırlık sınıfından muaf olamaz mıyım?', 'Lisansüstü hazırlık sınıfından muaf olabilir miyim?', 'Hazırlık sınıfından 2 defa muaf olabilir miyim?'):
            self.assertIsNone(knowledge.lookup(self.config.db_file, question))

    def test_unpublished_expired_and_archived_answers_do_not_match(self):
        entry = self.create(status='draft')
        self.assertIsNone(knowledge.lookup(self.config.db_file, self.body['question']))
        published = knowledge.save(self.config.db_file, knowledge.KnowledgeInput(**self.body, revision=entry['revision']), 'reviewer', entry['id'])
        with patch.object(knowledge, 'today', return_value=knowledge.today() + timedelta(days=31)):
            self.assertIsNone(knowledge.lookup(self.config.db_file, self.body['question']))
        knowledge.save(self.config.db_file, knowledge.KnowledgeInput(**{**self.body, 'status': 'archived', 'revision': published['revision']}), 'reviewer', entry['id'])
        self.assertIsNone(knowledge.lookup(self.config.db_file, self.body['question']))

    def test_conflict_rolls_back_keys_and_rejects_stale_edit(self):
        first = self.create()
        second = self.create(question='Başka soru?', variants=[])
        with self.assertRaises(knowledge.Conflict):
            knowledge.save(self.config.db_file, knowledge.KnowledgeInput(**{**self.body, 'revision': second['revision']}), 'admin', second['id'])
        self.assertEqual(knowledge.lookup(self.config.db_file, 'Başka soru?')['id'], second['id'])
        with self.assertRaises(knowledge.Conflict):
            knowledge.save(self.config.db_file, knowledge.KnowledgeInput(**{**self.body, 'revision': 99}), 'admin', first['id'])

    def test_concurrent_duplicate_publication_has_one_winner(self):
        def publish(_):
            try:
                self.create()
                return True
            except knowledge.Conflict:
                return False
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sorted(pool.map(publish, range(2))), [False, True])

    def test_edit_unpublishes_old_variants_and_keeps_revisions(self):
        first = self.create()
        knowledge.save(self.config.db_file, knowledge.KnowledgeInput(**{**self.body, 'status': 'draft', 'revision': 1}), 'editor', first['id'])
        self.assertIsNone(knowledge.lookup(self.config.db_file, self.body['variants'][0]))
        with knowledge.connect(self.config.db_file) as connection:
            rows = connection.execute('SELECT actor,snapshot FROM knowledge_revisions ORDER BY revision').fetchall()
        self.assertEqual([row['actor'] for row in rows], ['adminbakai', 'editor'])
        self.assertEqual(json.loads(rows[0]['snapshot'])['answer'], self.body['answer'])

    def test_seed_is_draft_idempotent_and_preserves_edits(self):
        items = knowledge.seed_examples(self.config.db_file, 'admin')
        self.assertEqual(len(items), 6)
        self.assertTrue(all(item['status'] == 'draft' for item in items))
        self.assertIsNone(knowledge.lookup(self.config.db_file, items[0]['question']))
        edited = knowledge.KnowledgeInput(question=items[0]['question'], answer='Düzenlenmiş cevap', revision=1)
        knowledge.save(self.config.db_file, edited, 'admin', items[0]['id'])
        again = knowledge.seed_examples(self.config.db_file, 'admin')
        self.assertEqual(len(again), 6)
        self.assertEqual(next(item for item in again if item['id'] == items[0]['id'])['answer'], 'Düzenlenmiş cevap')

    def test_json_and_stream_skip_llm_and_embedding_keep_feedback_and_zero_cost(self):
        entry = self.create()
        with patch.object(pipeline, 'get_llm', side_effect=AssertionError('LLM açılmamalı')), \
             patch.object(pipeline, 'get_store', side_effect=AssertionError('Embedding açılmamalı')):
            normal = self.client.post('/chat', json={'question': self.body['question']})
            streamed = self.client.post('/chat', json={'question': self.body['variants'][0]}, headers={'Accept': 'text/event-stream'})
        self.assertEqual(normal.status_code, 200)
        self.assertIn('Onaylı hazır cevap', normal.json()['answer'])
        self.assertIn(self.body['sources'][0]['url'], normal.json()['answer'])
        self.assertIn('event: result', streamed.text)
        self.assertNotIn('event: error', streamed.text)
        query_id = normal.json()['query_id']
        self.assertTrue(self.client.post('/feedback', json={'query_id': query_id, 'rating': 'up'}).json()['ok'])
        detail = monitoring.query_detail(query_id)
        self.assertEqual(detail['llm_calls'], 0)
        self.assertEqual(detail['cost_usd'], 0)
        self.assertEqual(detail['model'], 'approved-answer')
        self.assertEqual(detail['feedback']['rating'], 'up')
        self.assertEqual(knowledge.list_answers(self.config.db_file)[0]['hits'], 2)
        logs = [json.loads(line) for line in (self.config.log_path / 'queries.jsonl').read_text().splitlines()]
        self.assertEqual(logs[0]['knowledge_revision'], entry['revision'])

    def test_history_and_unknown_question_fall_back_to_rag(self):
        self.create()
        llm = Mock()
        llm.generate.return_value = 'Yeni kaynaklı cevap'
        hits = [{'document': 'https://oidb.manas.edu.kg/tr/faq/7', 'title': 'Hazırlık', 'text': 'Dil muafiyeti', 'score': 0.9}]
        history = [ChatMessage(role='user', content='Lisansüstü için soruyorum.'), ChatMessage(role='assistant', content='Buyurun.')]
        with patch.object(pipeline, 'get_store') as store, patch.object(pipeline, 'get_llm', return_value=llm), \
             patch.object(pipeline, '_resolve_question', return_value=self.body['question']), \
             patch.object(pipeline, 'needs_education_level', return_value=False):
            store.return_value.query.return_value = hits
            pipeline.answer(self.body['question'], history=history)
            pipeline.answer('Farklı bir soru')
        self.assertEqual(store.return_value.query.call_count, 2)
        self.assertEqual(llm.generate.call_count, 2)

    def test_missing_legacy_table_falls_back(self):
        with knowledge.connect(self.config.db_file) as connection:
            connection.execute('DROP TABLE knowledge_keys')
        self.assertIsNone(knowledge.lookup(self.config.db_file, 'Soru'))


if __name__ == '__main__':
    unittest.main()
