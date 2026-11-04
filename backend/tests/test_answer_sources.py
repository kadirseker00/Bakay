"""Cevapsızlıkta sıfır kaynak; yeterli yanıtta en fazla üç ayrı belge."""
import unittest
from unittest.mock import Mock, patch

from app.rag import pipeline, source_links
from app.rag.answer_sources import NO_ANSWER, answer_hits, lacks_answer


class AnswerSourcesTests(unittest.TestCase):
    def setUp(self):
        self.hits = [dict(document=f'https://manas.edu.kg/doc/{i}',
                          title=f'Belge {i}', text='Başvuru belgeleri ilan edilir.', score=0.8)
                     for i in range(5)]

    def run_answer(self, raw, verify=False, prepared=None):
        llm = Mock()
        llm.generate.side_effect = [raw, 'HAYIR'] if verify else [raw]
        with patch.object(pipeline.knowledge, 'lookup', return_value=prepared), \
             patch.object(pipeline, 'get_llm', return_value=llm), \
             patch.object(pipeline, 'get_store') as store, \
             patch.object(pipeline, '_log') as log, \
             patch.object(pipeline.telemetry, 'log_query'), \
             patch.object(pipeline, 'needs_education_level', return_value=False), \
             patch.multiple(pipeline.settings, agent_route=False, agent_rewrite=False,
                            agent_verify=verify, score_threshold=0.3):
            store.return_value.query.return_value = self.hits
            response = pipeline.answer('akademisyene zam yapıldı mı?', top_k=8)
        return response, log, llm

    def test_live_feedback_no_answer_has_no_sources_or_links(self):
        # 04.11.2026 canlı geri bildirimi: “hem bulamadım dedin, hem de kaynak verdin”.
        response, log, _ = self.run_answer('Bu konuda elimdeki belgelerde bilgi bulamadım.')
        self.assertEqual(response.answer, NO_ANSWER)
        self.assertEqual(response.sources, [])
        self.assertEqual(log.call_args.kwargs['sources'], [])
        self.assertEqual(log.call_args.kwargs['route'], 'insufficient_evidence')

    def test_abstention_variants_strip_model_links_and_citations(self):
        for raw in ['[YANIT_YOK]', '', '<think>bakıyorum</think>[YANIT_YOK]',
                    'Bu konuda yeterli bilgi bulunmamaktadır.',
                    'Belgelerde doğrudan bilgi yoktur.',
                    'Bu soruya cevap veremiyorum.',
                    'Bu konuda bilgi bulamadım.\n\nKaynak: [Belge](https://manas.edu.kg/doc/1)']:
            with self.subTest(raw=raw):
                response, _, _ = self.run_answer(raw)
                self.assertEqual(response.answer, NO_ANSWER)
                self.assertEqual(response.sources, [])
                self.assertEqual(source_links.append_source_reading(raw, self.hits), raw)

    def test_three_distinct_documents_and_cited_low_rank_source_preserved(self):
        self.hits.insert(1, dict(self.hits[0], text='Aynı belgenin ikinci parçası.'))
        response, log, llm = self.run_answer('Belge 4 başvuru şartlarını açıklar.')
        self.assertEqual(len(response.sources), 1)
        self.assertEqual(len({s.document for s in response.sources}), 1)
        self.assertEqual(response.sources[0].title, 'Belge 4')
        self.assertIn('/doc/4)', response.answer)
        self.assertEqual(len(log.call_args.kwargs['sources']), 1)
        self.assertIn('Belge 3', llm.generate.call_args.args[0])

    def test_multiple_chunks_are_not_multiple_sources(self):
        self.hits.insert(1, dict(self.hits[0], text='İkinci parça.'))
        response, _, _ = self.run_answer('Başvuru belgeleri ilan edilir.')
        self.assertEqual(len(response.sources), 3)
        self.assertEqual(len({source.document for source in response.sources}), 3)

    def test_level_question_without_any_quoted_provision_has_no_sources(self):
        with patch.object(pipeline, 'needs_education_level', return_value=True), \
             patch.object(pipeline, '_scope_preanswer', return_value=pipeline.NEEDS_LEVEL):
            # run_answer içindeki kapsam mock'unu bu dal için ayrıca kur.
            llm = Mock()
            with patch.object(pipeline.knowledge, 'lookup', return_value=None), \
                 patch.object(pipeline, 'get_store') as store, \
                 patch.object(pipeline, 'get_llm', return_value=llm), \
                 patch.object(pipeline, '_log'), \
                 patch.multiple(pipeline.settings, agent_route=False, agent_rewrite=False,
                                agent_verify=False, score_threshold=0.3):
                store.return_value.query.return_value = self.hits
                response = pipeline.answer('Ders saydırabilir miyim?')
            self.assertEqual(response.sources, [])
            self.assertEqual(response.answer, pipeline.NEEDS_LEVEL)
            llm.generate.assert_not_called()

    def test_failed_grounding_does_not_present_answer_as_sourced(self):
        response, log, _ = self.run_answer('Dayanaksız bir iddia.', verify=True)
        self.assertEqual(response.answer, NO_ANSWER)
        self.assertEqual(response.sources, [])
        self.assertEqual(log.call_args.kwargs['route'], 'insufficient_evidence')

    def test_partial_answer_keeps_sources_when_only_additional_detail_is_unknown(self):
        text = 'Belge 0 başvuru belgelerini listeler.\n\nGüncel ücret konusunda bilgi bulamadım.'
        self.assertFalse(lacks_answer(text))
        self.assertEqual(len(answer_hits(text, self.hits)), 1)

    def test_prepared_answer_uses_same_source_limit_for_cards_and_links(self):
        prepared = dict(answer='Başvuru belgeleri ilan edilir.', sources=[
            dict(url=h['document'], title=h['title'], snippet=h['text']) for h in self.hits],
            reviewed_on='2026-11-04', id='test', revision=1)
        response, _, llm = self.run_answer('', prepared=prepared)
        self.assertEqual(len(response.sources), 3)
        self.assertEqual(response.answer.count('](https://'), 3)
        llm.generate.assert_not_called()

class AnswerSourceAPITests(unittest.TestCase):
    def test_json_and_sse_apply_same_policy_and_persist_empty_sources(self):
        import json
        from pathlib import Path
        import tempfile
        from fastapi.testclient import TestClient
        from app import main, monitoring, telemetry
        from app.config import Settings

        with tempfile.TemporaryDirectory() as directory:
            config = Settings(_env_file=None, db_path=str(Path(directory) / 'test.db'),
                              log_dir=str(Path(directory) / 'logs'))
            for module in (main, monitoring, telemetry, pipeline):
                self.enterContext(patch.object(module, 'settings', config))
            llm = Mock()
            llm.generate.return_value = NO_ANSWER
            self.enterContext(patch.object(pipeline, 'get_llm', return_value=llm))
            store = self.enterContext(patch.object(pipeline, 'get_store'))
            store.return_value.query.return_value = [dict(document='x.pdf', title='Faaliyet raporu',
                                                         text='Başka bir konu.', score=0.8)]
            with TestClient(main.app) as client:
                for accept in ('application/json', 'text/event-stream'):
                    response = client.post('/chat', json={'question': 'akademisyene zam yapıldı mı?'},
                                           headers={'Accept': accept})
                    self.assertEqual(response.status_code, 200)
                    if accept == 'text/event-stream':
                        frame = response.text.strip().split('\n\n')[-1]
                        result = json.loads(frame.split('data: ', 1)[1])
                    else:
                        result = response.json()
                    self.assertEqual(result['sources'], [])
                    self.assertEqual(result['answer'], NO_ANSWER)
                    with monitoring.connect() as connection:
                        row = connection.execute('SELECT n_sources,sources_json FROM queries WHERE id=?',
                                                 (result['query_id'],)).fetchone()
                        self.assertEqual(row['n_sources'], 0)
                        self.assertEqual(json.loads(row['sources_json']), [])


if __name__ == '__main__':
    unittest.main()
